"""Upload to Google Cloud Storage with retry and logging.

This module exposes ``upload_to_gcs`` which uploads a JSON string to a
Google Cloud Storage bucket with retries and exponential backoff.
"""

# Standard library
import time
from typing import Optional

# Third-party
from google.api_core.exceptions import GoogleAPIError
from google.cloud import storage

# Local
from utils.logger import get_logger
from utils.config import GCS_BUCKET


logger = get_logger(__name__)


def upload_to_gcs(
    data: str,
    bucket_name: Optional[str] = None,
    destination_blob_name: str = "",
    retries: int = 3,
) -> None:
    """Uploads a JSON string to Google Cloud Storage with retry and logging.

    Args:
        data: JSON string to upload.
        bucket_name: Target GCS bucket. Defaults to GCS_BUCKET from config.
        destination_blob_name: Full path inside the bucket (e.g.,
        bronze/christmas/2025-11-06/snapshot.json).
        retries: Number of retry attempts with exponential backoff.

    Raises:
        Exception: If upload fails after all retries.
    """
    target_bucket = bucket_name or GCS_BUCKET
    if not target_bucket:
        raise ValueError("GCS bucket name is required (check GCS_BUCKET config).")

    client = storage.Client()
    bucket = client.bucket(target_bucket)
    blob = bucket.blob(destination_blob_name)

    for attempt in range(1, retries + 1):
        try:
            blob.upload_from_string(data, content_type="application/json")
            logger.info(
                "Upload successful: gs://%s/%s", target_bucket, destination_blob_name
            )
            return
        except (GoogleAPIError, OSError, TimeoutError) as exc:
            logger.warning("Upload attempt %d failed: %s", attempt, exc, exc_info=True)
            if attempt < retries:
                sleep_time = 2**attempt
                logger.info("Retrying in %d seconds...", sleep_time)
                time.sleep(sleep_time)
            else:
                logger.error("Upload failed after %d attempts", retries)
                raise
