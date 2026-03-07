"""
Presigned S3 URLs and key conventions for chat attachments.
S3 keys: tenants/{tenant_id}/files/{file_id}/raw/{filename}
         tenants/{tenant_id}/files/{file_id}/extracted/full.txt
         tenants/{tenant_id}/files/{file_id}/extracted/pages.json
"""

import hashlib
import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


def get_s3_client(*, endpoint_url: str | None = None):
    """Return boto3 S3 client. For LocalStack uses path-style and explicit credentials. For real AWS, uses regional endpoint (required for CORS preflight when bucket is outside us-east-1)."""
    import boto3
    from botocore.config import Config

    use_localstack = getattr(settings, "USE_LOCALSTACK_S3", False)
    custom_endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None) or endpoint_url
    region = getattr(settings, "AWS_S3_REGION_NAME", None) or "us-east-1"

    kwargs = {}
    if custom_endpoint:
        kwargs["endpoint_url"] = custom_endpoint
    elif not use_localstack and region != "us-east-1":
        # Force regional endpoint for buckets outside us-east-1. Browsers fail CORS preflight when the global endpoint redirects to the regional one.
        kwargs["endpoint_url"] = f"https://s3.{region}.amazonaws.com"

    # Explicit credentials: LocalStack requires them for backend/init consistency; real S3 can use env/IAM or pass from settings.
    access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    # Path-style for LocalStack/custom endpoint; default (virtual-hosted) for real AWS S3.
    config_kw = {"signature_version": "s3v4"}
    if use_localstack or custom_endpoint:
        config_kw["s3"] = {"addressing_style": "path"}
    config = Config(**config_kw)
    return boto3.client(
        "s3",
        region_name=region,
        config=config,
        **kwargs,
    )


def raw_s3_key(*, tenant_id: int, file_id: str, filename: str) -> str:
    """S3 key for raw uploaded file."""
    safe_name = filename.replace("..", "").strip() or "file"
    return f"tenants/{tenant_id}/files/{file_id}/raw/{safe_name}"


def extracted_full_text_s3_key(*, tenant_id: int, file_id: str) -> str:
    """S3 key for extracted full text."""
    return f"tenants/{tenant_id}/files/{file_id}/extracted/full.txt"


def extracted_pages_json_s3_key(*, tenant_id: int, file_id: str) -> str:
    """S3 key for extracted pages map."""
    return f"tenants/{tenant_id}/files/{file_id}/extracted/pages.json"


def generate_presigned_put_url(
    *,
    bucket: str,
    key: str,
    expires_in: int = 3600,
) -> str:
    """Generate presigned PUT URL for client upload. Do NOT sign Content-Type to avoid signature mismatch; validate MIME type at init and have frontend send Content-Type on upload."""
    endpoint = getattr(settings, "AWS_S3_ENDPOINT_URL", None) or ""
    if "localstack" in endpoint:
        endpoint = endpoint.replace("localstack", "localhost", 1)
    client = get_s3_client(endpoint_url=endpoint if endpoint else None)
    params = {"Bucket": bucket, "Key": key}
    if getattr(settings, "USE_LOCALSTACK_S3", False):
        params["ACL"] = "bucket-owner-full-control"
    url = client.generate_presigned_url(
        "put_object",
        Params=params,
        ExpiresIn=expires_in,
        HttpMethod="PUT",
    )
    logger.info("Generated presigned PUT URL for bucket=%s key=%s (host=%s)", bucket, key, _host_from_url(url))
    return url


def _host_from_url(url: str) -> str:
    """Extract host from URL for logging."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc or "(unknown)"
    except Exception:
        return "(unknown)"


def compute_sha256_from_s3(*, bucket: str, key: str) -> str:
    """Stream object from S3 and compute sha256 hex digest."""
    client = get_s3_client()
    hasher = hashlib.sha256()
    response = client.get_object(Bucket=bucket, Key=key)
    for chunk in response["Body"].iter_chunks(chunk_size=65536):
        hasher.update(chunk)
    return hasher.hexdigest()


def head_object(*, bucket: str, key: str) -> dict[str, Any] | None:
    """Return head object dict or None if not found. Raises on S3/client errors."""
    try:
        client = get_s3_client()
        return client.head_object(Bucket=bucket, Key=key)
    except Exception as e:
        logger.warning("S3 head_object failed for %s/%s: %s", bucket, key, e)
        raise


def delete_object_best_effort(*, bucket: str, key: str) -> None:
    """Delete S3 object. Logs and re-raises on errors."""
    try:
        client = get_s3_client()
        client.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        logger.warning("S3 delete_object failed for %s/%s: %s", bucket, key, e)
        raise


def upload_bytes_to_s3(*, bucket: str, key: str, body: bytes, content_type: str | None = None) -> None:
    """Upload bytes to S3 (used by worker for extracted full.txt etc.)."""
    client = get_s3_client()
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    client.put_object(Bucket=bucket, Key=key, Body=body, **extra)


def download_text_from_s3(*, bucket: str, key: str) -> str:
    """Download object from S3 and decode as UTF-8 text."""
    client = get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8", errors="replace")


def download_s3_to_temp_file(*, bucket: str, key: str, suffix: str = "") -> str:
    """Download S3 object to a temporary file; return path. Caller must unlink when done."""
    import tempfile
    client = get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read()
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        import os
        os.write(fd, body)
        os.close(fd)
        return path
    except Exception:
        import os
        try:
            os.close(fd)
        except Exception:
            raise
        try:
            os.unlink(path)
        except Exception:
            raise
        raise
