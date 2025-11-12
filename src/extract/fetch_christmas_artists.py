"""Fetch metadata and top tracks for a set of Christmas artists.

This module provides ``ChristmasArtistsExtractor`` which uses Spotipy to
retrieve artist information and top tracks. It logs warnings on recoverable
errors rather than raising.
"""

import time
from typing import List, Dict

import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, ARTISTS
from utils.logger import get_logger

logger = get_logger(__name__)


class ChristmasArtistsExtractor:
    """Extract data for Christmas artists (basic info + top tracks + audio features).

    The extractor uses Spotipy with Client Credentials flow to fetch artist
    metadata and top tracks. Methods are resilient to partial failures and log
    warnings instead of raising for non-critical errors.
    """

    def __init__(self):
        self.sp = Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
            )
        )

    # ------------------------------
    # 1) ARTISTS
    # ------------------------------
    def get_artists(self, artist_ids: List[str]) -> List[Dict]:
        """Fetch basic artist information.

        Args:
            artist_ids: List of Spotify artist IDs.

        Returns:
            A list of dictionaries with artist fields: id, name, genres,
            followers and popularity.
        """
        artists: List[Dict] = []
        try:
            for i in range(0, len(artist_ids), 50):
                batch = self.sp.artists(artist_ids[i : i + 50])["artists"]
                artists.extend(batch)
                # Filter out any None entries returned by the API
                artists = [a for a in artists if a is not None]
                time.sleep(0.1)
        except (SpotifyException, requests.RequestException, KeyError) as e:
            logger.warning("Error fetching artists: %s", e, exc_info=True)
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "genres": a.get("genres", []),
                "followers": a.get("followers", {}).get("total", 0),
                "popularity": a.get("popularity", None),
            }
            for a in artists
        ]

    # ------------------------------
    # 2) TOP TRACKS
    # ------------------------------
    def get_top_tracks(self, artist_id: str) -> List[Dict]:
        """Fetch an artist's top tracks.

        Args:
            artist_id: Spotify artist ID.

        Returns:
            A list of track dictionaries with keys: artist_id, track_id,
            track_name, popularity and release_date. Returns an empty list on
            error.
        """
        try:
            results = self.sp.artist_top_tracks(artist_id)
            tracks = results.get("tracks", [])
            return [
                {
                    "artist_id": artist_id,
                    "track_id": t["id"],
                    "track_name": t["name"],
                    "popularity": t["popularity"],
                    "release_date": t["album"]["release_date"],
                }
                for t in tracks
            ]
        except (SpotifyException, requests.RequestException, KeyError) as e:
            logger.warning(
                "Error fetching top tracks for artist %s: %s",
                artist_id,
                e,
                exc_info=True,
            )
        return []

    # ------------------------------
    # MAIN EXTRACTION PIPELINE
    # ------------------------------
    def extract(self, snapshot_date: str) -> Dict:
        """Run the full extraction pipeline.

        The pipeline performs the following steps:
        1. Fetch artist metadata for configured artists.
        2. Fetch top tracks for each artist.

        Args:
            snapshot_date: The snapshot date to attach to the output.

        Returns:
            A dictionary containing keys: "snapshot_date", "artists" and
            "tracks".
        """
        artist_ids = [a["id"] for a in ARTISTS]
        logger.info("Starting extraction for %d Christmas artists...", len(artist_ids))

        # 1. Artist metadata
        artists_info = self.get_artists(artist_ids)
        # attach market info from ARTISTS config when available
        artists_info = [
            {
                **a,
                "market": next(
                    (ar.get("market") for ar in ARTISTS if ar["id"] == a["id"]), None
                ),
            }
            for a in artists_info
        ]

        # 2. Top tracks per artist
        all_tracks: List[Dict] = []
        for artist_id in artist_ids:
            tracks = self.get_top_tracks(artist_id)
            all_tracks.extend(tracks)

        logger.info("Extraction completed successfully.")
        return {
            "snapshot_date": snapshot_date,
            "artists": artists_info,
            "tracks": all_tracks,
        }
