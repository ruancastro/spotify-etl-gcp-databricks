"""Configuration management for Spotify ETL project.

This module centralizes environment and secret loading for the project.
It prefers environment variables and falls back to Secret Manager when
configured.
"""

import os
from typing import Optional

# Third-party
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import secretmanager

# Local
from utils.logger import get_logger


load_dotenv()


logger = get_logger(__name__)

# === GCP Project ID  ===
PROJECT_ID = os.getenv("GCP_PROJECT")

# === GCS Bucket ===
GCS_BUCKET = os.getenv("GCS_BUCKET", "your-spotify-raw-bucket")

# === Spotify Credentials ===
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Artists monitored (Global + BR) – IDs validated in 11/11/2025
ARTISTS = [
    {"id": "4iHNK0tOyZPYnBU7nGAgpQ", "name": "Mariah Carey", "market": "GB"},
    {"id": "5lpH0xAS4fVfLkACg9DAuM", "name": "Wham!", "market": "GB"},
    {"id": "4cPHsZM98sKzmV26wlwD2W", "name": "Brenda Lee", "market": "GB"},
    {"id": "1GxkXlMwML1oSg5eLPiAz3", "name": "Michael Bublé", "market": "GB"},
    {"id": "66CXWjxzNUsdJxJ2JdwvnR", "name": "Ariana Grande", "market": "GB"},
    {"id": "0sgV4klGs1Y1dgbBi28JlD", "name": "Simone", "market": "BR"},
    {"id": "7fAKtXSdNInWAIf0jVUz65", "name": "Roberto Carlos", "market": "BR"},
]


def get_secret(secret_id: str, version: str = "latest") -> Optional[str]:
    """Fetches a secret from GCP Secret Manager."""
    if not PROJECT_ID:
        logger.warning("GCP_PROJECT not set. Skipping Secret Manager.")
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except (GoogleAPIError, DefaultCredentialsError, OSError) as e:
        # Use lazy formatting and include traceback for debugging
        logger.error("Failed to fetch secret %s: %s", secret_id, e, exc_info=True)
        return None


# === Load secrets  ===
if not SPOTIFY_CLIENT_ID:
    SPOTIFY_CLIENT_ID = get_secret("spotify-client-id")
if not SPOTIFY_CLIENT_SECRET:
    SPOTIFY_CLIENT_SECRET = get_secret("spotify-client-secret")

# === Final validation ===
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError(
        "Spotify credentials missing. Set SPOTIFY_CLIENT_ID/SECRET or use Secret Manager."
    )

if not GCS_BUCKET:
    raise ValueError("GCS_BUCKET not configured.")

logger.info("Config loaded: GCS=%s, Spotify=OK", GCS_BUCKET)
