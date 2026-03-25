"""
Generate final answer for PendingDocIntent: summary cache or LLM, then post assistant message.
Idempotent: PENDING -> DONE under lock.
"""

import logging
import uuid
from typing import List

from django.db import transaction
from src.prompts.enums import PendingDocIntentStatus
from src.chats.flow import update_chat_summary
from src.chats.models import  Message, PendingDocIntent
from src.chats.utils import create_llm, detect_language
from src.uploads.models import File, FileExtraction, FileSummary
from src.uploads.storage import download_text_from_s3

logger = logging.getLogger(__name__)

SUMMARY_PROMPT_VERSION = "1"
SUMMARY_TYPE_DEFAULT = "general"
MAX_DOC_CONTEXT_CHARS = 12000  # token budget: do not inject huge docs


def _load_full_text_for_files(*, file_ids: List[str], tenant_id: int) -> str:
    """Load and concatenate full extracted text from S3 for given file IDs (truncated per file)."""
    parts = []
    total = 0
    for fid in file_ids:
        if total >= MAX_DOC_CONTEXT_CHARS:
            break
        try:
            ext = FileExtraction.objects.filter(file_id=fid, status=FileExtraction.Status.READY).first()
            if not ext or not ext.full_text_s3_key:
                continue
            file_record = File.objects.filter(id=fid, tenant_id=tenant_id).first()
            if not file_record or not file_record.s3_bucket:
                continue
            text = download_text_from_s3(bucket=file_record.s3_bucket, key=ext.full_text_s3_key)
            remaining = MAX_DOC_CONTEXT_CHARS - total
            if len(text) > remaining:
                text = text[:remaining] + "\n\n[Document truncated...]"
            parts.append(f"--- Document {file_record.original_filename} ---\n{text}")
            total += len(text)
        except Exception as e:
            logger.warning("Could not load full text for file %s: %s", fid, e)
    return "\n\n".join(parts)


def _get_cached_summary(*, tenant_id: int, file_id: str) -> str | None:
    """Return cached summary_text if exists."""
    row = FileSummary.objects.filter(
        tenant_id=tenant_id,
        file_id=file_id,
        summary_type=SUMMARY_TYPE_DEFAULT,
        prompt_version=SUMMARY_PROMPT_VERSION,
    ).first()
    return row.summary_text if row else None


def _generate_and_cache_summary(*, tenant_id: int, file_id: str, full_text: str) -> str:
    """Call LLM to summarize, insert into file_summaries, return summary_text."""
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = create_llm("gpt-4o-mini")
    truncated = full_text[:MAX_DOC_CONTEXT_CHARS] + ("\n[Truncated...]" if len(full_text) > MAX_DOC_CONTEXT_CHARS else "")
    prompt = f"""Summarize the following document in enough detail for legal Q&A and follow-up questions. Include:
- Main parties, roles, and dates
- Key obligations, rights, and conditions
- Important clauses or sections (with brief content)
- Definitions or terms that matter for interpretation
- Any numbers, deadlines, or amounts
Keep the summary structured (e.g. by section/topic) so that the user can ask "what does it say about X?" and get a useful answer from this summary alone.

Document:
{truncated}

Summary:"""
    messages_list = [
        SystemMessage(content="You are a document summarizer for legal context. Produce a detailed but structured summary suitable for answering follow-up questions."),
        HumanMessage(content=prompt),
    ]
    response = llm.invoke(messages_list)
    summary_text = (response.content or "").strip()
    FileSummary.objects.update_or_create(
        tenant_id=tenant_id,
        file_id=file_id,
        summary_type=SUMMARY_TYPE_DEFAULT,
        prompt_version=SUMMARY_PROMPT_VERSION,
        defaults={
            "summary_text": summary_text,
            "model": getattr(llm, "model_name", None) or "gpt-4o-mini",
        },
    )
    return summary_text


def run_generate_final_answer(*, pending_intent_id: int) -> None:
    """
    Load PendingDocIntent (tenant-scoped), transition PENDING -> DONE, build answer, post Message.
    """
    with transaction.atomic():
        intent = (
            PendingDocIntent.objects
            .select_for_update()
            .select_related("tenant", "conversation", "user_message")
            .filter(id=pending_intent_id)
            .first()
        )
        if not intent:
            return
        if intent.status != PendingDocIntentStatus.PENDING:
            return

        tenant_id = intent.tenant_id
        chat = intent.conversation
        user_message = intent.user_message
        file_ids = intent.file_ids if isinstance(intent.file_ids, list) else []
        file_ids = [str(f) for f in file_ids] if file_ids else []
        user_question = intent.user_question or ""
        intent_type = intent.intent_type

        doc_context = _load_full_text_for_files(file_ids=file_ids, tenant_id=tenant_id)

        if intent_type == PendingDocIntent.IntentType.SUMMARY:
            if len(file_ids) == 1:
                cached = _get_cached_summary(tenant_id=tenant_id, file_id=file_ids[0])
                if cached:
                    answer_text = cached
                else:
                    answer_text = _generate_and_cache_summary(
                        tenant_id=tenant_id,
                        file_id=file_ids[0],
                        full_text=doc_context or "(No text extracted)",
                    )
            else:
                from langchain_core.messages import HumanMessage, SystemMessage
                llm = create_llm("gpt-4o-mini")
                prompt = f"""Summarize the following documents for the user. Combine key points clearly.

Documents:
{doc_context or '(No text extracted)'}

Summary:"""
                messages_list = [
                    SystemMessage(content="You are a concise document summarizer."),
                    HumanMessage(content=prompt),
                ]
                response = llm.invoke(messages_list)
                answer_text = (response.content or "").strip()
        else:
            from langchain_core.messages import HumanMessage, SystemMessage
            llm = create_llm("gpt-4o-mini")
            prompt = f"""Answer the user's question based only on the following document context. If the answer is not in the documents, say so.

Document context:
{doc_context or '(No document text available)'}

User question: {user_question}

Answer:"""
            messages_list = [
                SystemMessage(content="You are a helpful legal assistant. Answer based on the provided documents only."),
                HumanMessage(content=prompt),
            ]
            response = llm.invoke(messages_list)
            answer_text = (response.content or "").strip()

        answer_language = detect_language(answer_text)
        system_message = Message.objects.create(
            chat_id=chat.id,
            parent=user_message,
            language=answer_language,
            text=answer_text,
            role="ai",
            uuid=uuid.uuid4(),
        )
        update_chat_summary(chat_id=chat.id, new_messages=[user_message, system_message])

        intent.status = PendingDocIntentStatus.DONE
        intent.save(update_fields=["status", "updated_at"])
