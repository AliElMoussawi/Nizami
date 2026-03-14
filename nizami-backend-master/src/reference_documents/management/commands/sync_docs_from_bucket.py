import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from src.reference_documents.models import RagSourceDocument

logger = logging.getLogger(__name__)


def _parse_processed_at(value: Any) -> Optional[datetime]:
    if not value:
        return None

    if isinstance(value, (int, float)):
        # Assume Unix timestamp (seconds)
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, str):
        for parser in (
            lambda v: datetime.fromisoformat(v.replace("Z", "+00:00")),
        ):
            try:
                dt = parser(value)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone=timezone.utc)
                return dt
            except Exception:
                continue

    return None


def _get_title_from_payload(payload: Dict[str, Any], s3_key: str) -> str:
    # Your JSON: metadata.title (e.g. "الية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم")
    metadata = payload.get("metadata") or {}
    if isinstance(metadata, dict):
        title = metadata.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()

    # Top-level title/name
    for field in ("title", "name"):
        if field in payload and isinstance(payload[field], str) and payload[field].strip():
            return payload[field].strip()

    # filename (e.g. "آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم.docx" -> use as title)
    filename = payload.get("filename")
    if isinstance(filename, str) and filename.strip():
        base = filename.strip()
        if "." in base:
            base = ".".join(base.split(".")[:-1])
        if base:
            return base

    # Fallback: S3 key basename without extension
    base_name = os.path.basename(s3_key)
    if "." in base_name:
        base_name = ".".join(base_name.split(".")[:-1])
    return base_name or s3_key


class Command(BaseCommand):
    help = (
        "Scan an S3 bucket for cleaned RAG JSON files, compute uuid5 from clean_text, "
        "and insert new rows into RagSourceDocument. Existing uuid5 are skipped (no update)."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--bucket",
            type=str,
            default=getattr(settings, "RAG_S3_BUCKET", ""),
            help="S3 bucket name. Defaults to RAG_S3_BUCKET from settings (set via env in deploy).",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default=getattr(settings, "RAG_S3_PREFIX", ""),
            help="Optional S3 prefix to limit which objects are scanned. Defaults to RAG_S3_PREFIX.",
        )

    def handle(self, *args, **options):
        bucket: Optional[str] = options.get("bucket")
        prefix: str = options.get("prefix") or ""

        if not bucket:
            logger.error("Bucket name is required (use --bucket or RAG_S3_BUCKET env var).")
            return

        s3_client = boto3.client("s3")

        logger.info("Scanning bucket=%r prefix=%r for JSON files...", bucket, prefix)

        paginator = s3_client.get_paginator("list_objects_v2")
        total_seen = 0
        total_created = 0
        total_skipped = 0

        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            contents = page.get("Contents") or []
            for obj in contents:
                key = obj["Key"]

                if not key.lower().endswith(".json"):
                    continue

                total_seen += 1

                try:
                    body = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
                    payload = json.loads(body)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Skipping %r: failed to load/parse JSON (%s)", key, exc)
                    continue

                clean_text = payload.get("clean_text")
                if not isinstance(clean_text, str) or not clean_text.strip():
                    logger.warning("Skipping %r: missing or empty 'clean_text'", key)
                    continue

                # Deterministic UUID based on clean_text
                doc_uuid = uuid.uuid5(uuid.NAMESPACE_URL, clean_text)

                if RagSourceDocument.objects.filter(uuid5=doc_uuid).exists():
                    logger.info(
                        "Skipping key=%r: RagSourceDocument with same uuid5 already exists.",
                        key,
                    )
                    total_skipped += 1
                    continue

                processed_at = _parse_processed_at(payload.get("processing_timestamp"))
                title = _get_title_from_payload(payload, key)

                obj_instance = RagSourceDocument.objects.create(
                    uuid5=doc_uuid,
                    title=title,
                    s3_bucket=bucket,
                    s3_key=key,
                    processed_at=processed_at,
                    is_extracted=True,
                    pulled_at=timezone.now(),
                )

                total_created += 1
                logger.info("Created RagSourceDocument id=%s for key=%r", obj_instance.id, key)

        logger.info(
            "Done. JSON files seen=%s, created=%s, skipped (existing uuid5)=%s.",
            total_seen,
            total_created,
            total_skipped,
        )
