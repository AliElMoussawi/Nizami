"""
Chat attachment flow: soft-wait, branch READY / PREVIEW_READY / processing, build prompt, post message or PendingDocIntent.
"""

import logging
import time
import uuid
from typing import List, Tuple

from django.conf import settings
from django.db import transaction
from src.chats.models import Message, MessageAttachment
from src.chats.utils import create_llm, detect_language
from django_q.tasks import async_task

from src.prompts.enums import PendingDocIntentIntentType
from src.uploads.models import File, FileExtraction, FileSummary
from src.uploads.storage import download_text_from_s3
from src.uploads.tasks import extract_file

logger = logging.getLogger(__name__)

# How long to wait for extraction when user sends a message (configurable; default 60s if queue is busy)
SOFT_WAIT_TIMEOUT_SEC = getattr(
    settings,
    "ATTACHMENT_EXTRACTION_WAIT_TIMEOUT_SEC",
    60,
)
SOFT_WAIT_POLL_INTERVAL_SEC = getattr(
    settings,
    "ATTACHMENT_EXTRACTION_POLL_INTERVAL_SEC",
    0.5,
)
MAX_DOC_CONTEXT_CHARS = 12000
SUMMARY_PROMPT_VERSION = "1"
SUMMARY_TYPE_DEFAULT = "general"


def _ensure_extraction_enqueued(*, file_ids: List[str], user_id: int) -> None:
    """Enqueue extract_file for any file that is not READY or FAILED and has no extraction or not EXTRACTING."""
    from src.uploads.models import FileExtraction
    for fid in file_ids:
        try:
            file_record = File.objects.filter(id=fid, tenant_id=user_id).first()
            if not file_record:
                continue
            ext = getattr(file_record, "extraction", None)
            if ext:
                if ext.status == FileExtraction.Status.READY or ext.status == FileExtraction.Status.FAILED:
                    continue
                if ext.status == FileExtraction.Status.EXTRACTING:
                    continue
            async_task(extract_file, str(fid))
        except Exception as e:
            logger.warning("Could not enqueue extract_file for %s: %s", fid, e)


def _run_extraction_sync(*, file_ids: List[str], user_id: int) -> None:
    """Run extraction synchronously for each file that is not yet READY (so we can use full text/summary in context)."""
    for fid in file_ids:
        ext = FileExtraction.objects.filter(file_id=fid, file__tenant_id=user_id).first()
        if ext and ext.status == FileExtraction.Status.READY:
            continue
        try:
            extract_file(file_id=fid)
        except Exception as e:
            logger.warning("Sync extraction failed for file %s: %s", fid, e)


def _poll_extraction_statuses(*, file_ids: List[str], user_id: int) -> Tuple[str, dict]:
    """
    Poll extraction status until all files are READY/FAILED, or timeout.
    When the user sends a message we wait (up to ATTACHMENT_EXTRACTION_WAIT_TIMEOUT_SEC) so that
    even with a busy queue we give extraction time to complete before returning preliminary/processing.
    Returns (overall_status, status_by_file_id) where overall is READY | PREVIEW_READY | PROCESSING.
    """
    statuses = {}
    deadline = time.monotonic() + SOFT_WAIT_TIMEOUT_SEC
    while time.monotonic() < deadline:
        all_ready = True
        any_preview = False
        for fid in file_ids:
            ext = FileExtraction.objects.filter(file_id=fid, file__tenant_id=user_id).first()
            if not ext:
                statuses[fid] = "PROCESSING"
                all_ready = False
                continue
            statuses[fid] = ext.status
            if ext.status != FileExtraction.Status.READY and ext.status != FileExtraction.Status.FAILED:
                all_ready = False
            if ext.status == FileExtraction.Status.PREVIEW_READY or ext.status == FileExtraction.Status.READY:
                any_preview = True
        if all_ready:
            return "READY", statuses
        if any_preview:
            return "PREVIEW_READY", statuses
        time.sleep(SOFT_WAIT_POLL_INTERVAL_SEC)
    return "PROCESSING", statuses


def _infer_intent(*, text: str) -> str:
    """Infer SUMMARY vs QA from message content."""
    t = (text or "").strip().lower()
    if any(k in t for k in ("summarize", "summary", "summarise", "outline", "overview")):
        return PendingDocIntentIntentType.SUMMARY
    return PendingDocIntentIntentType.QA


def load_attached_docs_context_for_chat(*, chat_id: int, user_id: int) -> str:
    """
    Load document context (summary preferred) for all files attached to messages in this chat.
    Used so follow-up questions in the same chat can use the uploaded file info.
    """
    from src.chats.models import MessageAttachment
    file_ids = list(
        MessageAttachment.objects
        .filter(message__chat_id=chat_id)
        .values_list("file_id", flat=True)
        .distinct()
    )
    if not file_ids:
        return ""
    return _load_doc_context_for_response(
        file_ids=[str(fid) for fid in file_ids],
        user_id=user_id,
        use_summary_cache=True,
    )


def _load_doc_context_for_response(*, file_ids: List[str], user_id: int, use_summary_cache: bool) -> str:
    """Build document context: from summary cache if use_summary_cache else full text (truncated)."""
    parts = []
    total = 0
    for fid in file_ids:
        if total >= MAX_DOC_CONTEXT_CHARS:
            break
        try:
            file_record = File.objects.filter(id=fid, tenant_id=user_id).first()
            if not file_record:
                continue
            if use_summary_cache:
                row = FileSummary.objects.filter(
                    tenant_id=user_id,
                    file_id=fid,
                    summary_type=SUMMARY_TYPE_DEFAULT,
                    prompt_version=SUMMARY_PROMPT_VERSION,
                ).first()
                if row:
                    text = row.summary_text
                else:
                    ext = FileExtraction.objects.filter(file_id=fid, status=FileExtraction.Status.READY).first()
                    if not ext or not ext.full_text_s3_key or not file_record.s3_bucket:
                        continue
                    text = download_text_from_s3(bucket=file_record.s3_bucket, key=ext.full_text_s3_key)
                    remaining = MAX_DOC_CONTEXT_CHARS - total
                    text = text[:remaining] + "\n[Truncated...]" if len(text) > remaining else text
            else:
                ext = FileExtraction.objects.filter(file_id=fid, status=FileExtraction.Status.READY).first()
                if not ext or not ext.full_text_s3_key or not file_record.s3_bucket:
                    continue
                text = download_text_from_s3(bucket=file_record.s3_bucket, key=ext.full_text_s3_key)
                remaining = MAX_DOC_CONTEXT_CHARS - total
                if len(text) > remaining:
                    text = text[:remaining] + "\n\n[Document truncated...]"
            parts.append(f"--- {file_record.original_filename} ---\n{text}")
            total += len(text)
        except Exception as e:
            logger.warning("Load doc context for file %s failed: %s", fid, e)
    return "\n\n".join(parts)


def _build_answer_with_docs(*, user_question: str, doc_context: str, intent_type: str) -> str:
    """Call LLM with document context and user question."""
    from langchain_core.messages import HumanMessage, SystemMessage
    llm = create_llm("gpt-4o-mini")
    if intent_type == PendingDocIntentIntentType.SUMMARY:
        prompt = f"""Summarize the following document(s) clearly for the user.

Documents:
{doc_context}

User request: {user_question}

Summary:"""
    else:
        prompt = f"""Answer the user's question based only on the following document(s). If the answer is not in the documents, say so.

Documents:
{doc_context}

User question: {user_question}

Answer:"""
    messages_list = [
        SystemMessage(content="You are a helpful legal assistant. Use only the provided documents."),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages_list)
    return (response.content or "").strip()


def _build_preview_answer(*, user_question: str, preview_texts: List[str]) -> str:
    """Build preliminary answer from preview text only."""
    from langchain_core.messages import HumanMessage, SystemMessage
    llm = create_llm("gpt-4o-mini")
    combined = "\n\n".join(preview_texts) if preview_texts else "(Preview not available yet)"
    prompt = f"""The following is a PREVIEW (first part only) of document(s) still being processed. Give a brief preliminary response. Tell the user the full answer will follow once processing completes.

Preview:
{combined}

User question: {user_question}

Preliminary response:"""
    messages_list = [
        SystemMessage(content="You are a helpful assistant. This is partial document content only."),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages_list)
    return (response.content or "").strip()


def run_attachment_message_flow(
    *,
    user,
    chat_id: int,
    text: str,
    message_uuid: str,
    attachment_file_ids: List[str],
    intent: str | None,
) -> Message:
    """
    Create user message, MessageAttachments, soft-wait, branch, return assistant message (or preliminary/processing).
    """
    user_id = user.id

    with transaction.atomic():
        user_message = Message.objects.filter(uuid=message_uuid).first()
        if not user_message:
            user_message = Message.objects.create(
                role="user",
                language=detect_language(text),
                used_query=text,
                chat_id=chat_id,
                text=text,
                uuid=message_uuid,
            )

        for fid in attachment_file_ids:
            file_record = File.objects.filter(id=fid, tenant_id=user_id).first()
            if not file_record:
                continue
            MessageAttachment.objects.get_or_create(
                message=user_message,
                file_id=fid,
            )

    _ensure_extraction_enqueued(file_ids=attachment_file_ids, user_id=user_id)
    overall_status, _ = _poll_extraction_statuses(file_ids=attachment_file_ids, user_id=user_id)
    intent_type = intent or _infer_intent(text=text)

    # If not READY yet, run extraction synchronously so we have full text/summary for context (no placeholder message).
    if overall_status != "READY":
        _run_extraction_sync(file_ids=attachment_file_ids, user_id=user_id)
        # Re-check status after sync extraction (no wait)
        any_ready = any(
            FileExtraction.objects.filter(file_id=fid, file__tenant_id=user_id, status=FileExtraction.Status.READY).exists()
            for fid in attachment_file_ids
        )
        if any_ready:
            overall_status = "READY"

    if overall_status == "READY":
        # Always inject summary into message content when available (PDF/DOCX/image summarized at extraction)
        doc_context = _load_doc_context_for_response(
            file_ids=attachment_file_ids,
            user_id=user_id,
            use_summary_cache=True,
        )
        if not doc_context.strip():
            answer_text = "I couldn't extract text from the attached documents. Please check the file format and try again."
        else:
            answer_text = _build_answer_with_docs(
                user_question=text,
                doc_context=doc_context,
                intent_type=intent_type,
            )
        answer_language = detect_language(answer_text)
        from src.chats.flow import update_chat_summary
        system_message = Message.objects.create(
            chat_id=chat_id,
            parent=user_message,
            language=answer_language,
            text=answer_text,
            role="ai",
            uuid=uuid.uuid4(),
        )
        update_chat_summary(chat_id=chat_id, new_messages=[user_message, system_message])
        return system_message

    # Fallback: extraction failed for all files (e.g. timeout, or file missing in storage after bucket reset/dedupe)
    any_failed_storage = any(
        FileExtraction.objects.filter(
            file_id=fid,
            file__tenant_id=user_id,
            status=FileExtraction.Status.FAILED,
            error_message__icontains="NoSuchKey",
        ).exists()
        for fid in attachment_file_ids
    )
    if any_failed_storage:
        fallback_text = "The attached document is no longer in storage (it may have been removed). Please upload the file again."
    else:
        fallback_text = "I couldn't process the attached documents in time. Please try again or use a different file."
    from src.chats.flow import update_chat_summary
    system_message = Message.objects.create(
        chat_id=chat_id,
        parent=user_message,
        language=detect_language(fallback_text),
        text=fallback_text,
        role="ai",
        uuid=uuid.uuid4(),
    )
    update_chat_summary(chat_id=chat_id, new_messages=[user_message, system_message])
    return system_message
