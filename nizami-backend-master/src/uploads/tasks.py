"""
Background tasks for chat attachments: extract_file, generate_final_answer.
"""

import json
import logging
import os
from datetime import datetime
from uuid import UUID

from django.db import transaction
from django_q.tasks import async_task

from src.uploads.extraction_utils import EXTRACTOR_VERSION, get_full_text, get_preview_text
from src.chats.models import PendingDocIntent
from src.uploads.models import File, FileExtraction
from src.uploads.storage import (
    download_s3_to_temp_file,
    extracted_full_text_s3_key,
    extracted_pages_json_s3_key,
    upload_bytes_to_s3,
)
from src.prompts.enums import PendingDocIntentStatus
logger = logging.getLogger(__name__)


def extract_file(*, file_id: str) -> None:
    """
    Idempotent extraction: if READY, exit. If EXTRACTING with same version, continue.
    Preview first (PREVIEW_READY), then full extraction (READY). Enqueue generate_final_answer for pending intents.
    """
    try:
        file_uuid = UUID(file_id)
    except (ValueError, TypeError):
        logger.warning("extract_file: invalid file_id %s", file_id)
        return

    with transaction.atomic():
        file_record = (
            File.objects
            .select_for_update()
            .filter(id=file_uuid)
            .first()
        )
        if not file_record:
            logger.warning("extract_file: File not found %s", file_id)
            return

        extraction, _ = FileExtraction.objects.get_or_create(
            file=file_record,
            defaults={
                "status": FileExtraction.Status.EXTRACTING,
                "extractor_version": EXTRACTOR_VERSION,
            },
        )

        if extraction.status == FileExtraction.Status.READY:
            return
        if extraction.status == FileExtraction.Status.EXTRACTING and extraction.extractor_version != EXTRACTOR_VERSION:
            return

        extraction.status = FileExtraction.Status.EXTRACTING
        extraction.extractor_version = EXTRACTOR_VERSION
        extraction.save(update_fields=["status", "extractor_version"])

    bucket = file_record.s3_bucket
    key_raw = file_record.s3_key_raw
    if not bucket or not key_raw:
        extraction.status = FileExtraction.Status.FAILED
        extraction.error_message = "Missing S3 location"
        extraction.save(update_fields=["status", "error_message"])
        return

    suffix = os.path.splitext(file_record.original_filename)[-1] or ".bin"
    temp_path = None
    try:
        temp_path = download_s3_to_temp_file(bucket=bucket, key=key_raw, suffix=suffix)
        mime = file_record.mime_type or ""

        preview_text = get_preview_text(file_path=temp_path, mime_type=mime)
        with transaction.atomic():
            extraction.refresh_from_db()
            extraction.preview_text = preview_text[:65535] if preview_text else ""
            extraction.status = FileExtraction.Status.PREVIEW_READY
            extraction.preview_ready_at = datetime.utcnow()
            extraction.save(update_fields=["preview_text", "status", "preview_ready_at"])

        full_text = get_full_text(file_path=temp_path, mime_type=mime)
        tenant_id = file_record.tenant_id
        full_key = extracted_full_text_s3_key(tenant_id=tenant_id, file_id=str(file_record.id))
        upload_bytes_to_s3(
            bucket=bucket,
            key=full_key,
            body=full_text.encode("utf-8", errors="replace"),
            content_type="text/plain; charset=utf-8",
        )

        pages_data = [{"page": i + 1, "text_preview": full_text[i : i + 200]} for i in range(0, min(len(full_text), 2000), 200)]
        pages_key = extracted_pages_json_s3_key(tenant_id=tenant_id, file_id=str(file_record.id))
        upload_bytes_to_s3(
            bucket=bucket,
            key=pages_key,
            body=json.dumps(pages_data, ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
        )

        with transaction.atomic():
            extraction.refresh_from_db()
            extraction.full_text_s3_key = full_key
            extraction.pages_json_s3_key = pages_key
            extraction.status = FileExtraction.Status.READY
            extraction.ready_at = datetime.utcnow()
            extraction.save(update_fields=["full_text_s3_key", "pages_json_s3_key", "status", "ready_at"])

        # Generate and cache summary for PDF/DOCX/image so message content uses summary instead of full text
        if full_text and full_text.strip():
            try:
                from src.uploads.final_answer import _generate_and_cache_summary
                _generate_and_cache_summary(
                    tenant_id=tenant_id,
                    file_id=str(file_record.id),
                    full_text=full_text,
                )
            except Exception as summary_exc:
                logger.warning("Could not cache summary for file %s: %s", file_id, summary_exc)

        # Find intents that reference this file (file_ids is a JSON list of UUID strings)
        pending = PendingDocIntent.objects.filter(
            status=PendingDocIntentStatus.PENDING,
            file_ids__contains=[str(file_record.id)],
        ).values_list("id", flat=True)
        for intent_id in pending:
            async_task(generate_final_answer, intent_id)

    except Exception as e:
        logger.exception("extract_file failed for %s: %s", file_id, e)
        with transaction.atomic():
            extraction.refresh_from_db()
            extraction.status = FileExtraction.Status.FAILED
            extraction.error_message = str(e)[:1024]
            extraction.save(update_fields=["status", "error_message"])
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning("Could not unlink temp file %s: %s", temp_path, e)


def generate_final_answer(*, pending_intent_id: int) -> None:
    """
    Load pending intent, build context (summary cache or full text), call LLM, post assistant message.
    Idempotent: only one transition PENDING -> DONE per intent.
    """
    from src.uploads.final_answer import run_generate_final_answer
    run_generate_final_answer(pending_intent_id=pending_intent_id)
