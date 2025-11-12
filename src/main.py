# pylint: disable=unused-variable, unused-import
"""Main entrypoint for the Artist Pulse ingestion job.

Cloud Function HTTP entrypoint that runs the Artist Pulse ingestion job.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from extract.fetch_christmas_artists import ChristmasArtistsExtractor
from load.upload_gcs import upload_to_gcs
from utils.logger import get_logger


logger = get_logger(__name__)


def artist_pulse_job(request):
    """
    Cloud Function HTTP entrypoint that runs the Artist Pulse ingestion job.
    This function computes a snapshot date in the "America/Sao_Paulo" timezone,
    instantiates a ChristmasArtistsExtractor to extract artist data for that
    snapshot date, and prepares a destination filename for a JSON snapshot
    (e.g. "bronze/artists/YYYY-MM-DD/snapshot.json"). The function currently
    contains commented logic to upload the snapshot to Google Cloud Storage.
    Success and error conditions are logged.
    Args:
        request (flask.Request): The incoming HTTP request object provided by
            Cloud Functions. The request body/parameters are not used by this
            function; it acts as a trigger to run the ingestion job.
    Returns:
        tuple[str, int]: A tuple with a response message and an HTTP status code.
            - On success: ("Artist Pulse ingested!", 200)
            - On failure: ("Error", 500) after logging the exception.
    Raises:
        None: Exceptions raised during extraction are caught and logged inside
        the function; they result in a 500 response and are not propagated.
    Side Effects:
        - Calls ChristmasArtistsExtractor.extract(snapshot_date).
        - Constructs a GCS destination filename for the snapshot.
        - May upload a JSON snapshot to Google Cloud Storage if upload logic is enabled.
        - Emits informational and error logs via the configured logger.
    """
    snapshot_date = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d")

    extractor = ChristmasArtistsExtractor()

    if request:
        logger.debug(
            "Triggered by request method: %s", getattr(request, "method", None)
        )

    try:
        data = extractor.extract(snapshot_date)
        filename = f"bronze/artists/{snapshot_date}/snapshot.json"

        # Log small summary so variables are used (avoids unused-variable warnings)
        logger.info(
            "Extracted %d artists and %d tracks",
            len(data.get("artists", [])),
            len(data.get("tracks", [])),
        )

        # upload_to_gcs(
        #     data=json.dumps(data, ensure_ascii=False, indent=2),
        #     bucket_name="your-spotify-raw-bucket",
        #     destination_blob_name=filename,
        # )
        # logger.info("Snapshot saved in gs://your-spotify-raw-bucket/%s", filename)
        return "Artist Pulse ingested!", 200
    except (ValueError, RuntimeError, OSError) as e:
        logger.error("Job error: %s", e, exc_info=True)
        return "Error", 500


if __name__ == "__main__":
    artist_pulse_job(None)
