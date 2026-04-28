"""Sync app/s3 directory to an AWS S3 bucket.

Usage:
    uv run python -m app.scripts.sync_s3_content
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from loguru import logger


load_dotenv()

CONTENT_DIR = Path(__file__).resolve().parent.parent / "s3"
BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
REGION = os.getenv("AWS_DEFAULT_REGION")
S3_PREFIX = "guides-content"


def _require_env(name: str, value: str | None) -> str:
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


BUCKET = _require_env("AWS_S3_BUCKET_NAME", BUCKET)
s3 = boto3.client("s3", region_name=REGION)

files = list(CONTENT_DIR.rglob("*"))
local_files = [f for f in files if f.is_file()]

# Set of S3 keys that should exist (from local files).
local_keys = {
    f"{S3_PREFIX}/{str(f.relative_to(CONTENT_DIR)).replace(os.sep, '/')}"
    for f in local_files
}


def file_needs_update(file_path: Path, s3_key: str) -> bool:
    """Check if file needs upload (missing remotely or content changed)."""
    try:
        response = s3.head_object(Bucket=BUCKET, Key=s3_key)
        s3_etag = response.get("ETag", "").strip('"')

        md5 = hashlib.md5()
        with file_path.open("rb") as handle:
            md5.update(handle.read())
        local_etag = md5.hexdigest()

        return s3_etag != local_etag
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
            return True
        logger.error(f"S3 error checking {s3_key}: {exc}")
        raise


def main() -> None:
    if not CONTENT_DIR.exists():
        raise RuntimeError(f"Content directory does not exist: {CONTENT_DIR}")

    logger.info(f"Starting sync from {CONTENT_DIR} ({len(local_files)} files)")

    uploaded = 0
    skipped = 0
    failed = 0

    for file_path in local_files:
        relative = file_path.relative_to(CONTENT_DIR)
        key = f"{S3_PREFIX}/{str(relative).replace(os.sep, '/')}"

        try:
            if file_needs_update(file_path, key):
                with file_path.open("rb") as handle:
                    s3.put_object(Bucket=BUCKET, Key=key, Body=handle.read())
                logger.info(f"Uploaded: {relative}")
                uploaded += 1
            else:
                skipped += 1
        except Exception as exc:  # pragma: no cover
            logger.error(f"Failed to sync {relative}: {exc}")
            failed += 1

    # Delete S3 objects that no longer exist locally (disabled by default).
    # deleted = 0
    # paginator = s3.get_paginator("list_objects_v2")
    # for page in paginator.paginate(Bucket=BUCKET):
    #     for obj in page.get("Contents", []):
    #         key = obj["Key"]
    #         if key not in local_keys:
    #             try:
    #                 s3.delete_object(Bucket=BUCKET, Key=key)
    #                 logger.info(f"Deleted: {key}")
    #                 deleted += 1
    #             except Exception as exc:
    #                 logger.error(f"Failed to delete {key}: {exc}")
    #                 failed += 1
    deleted = 0

    logger.info(
        f"Sync complete: {uploaded} uploaded, {skipped} skipped, "
        f"{deleted} deleted, {failed} failed"
    )


if __name__ == "__main__":
    main()
