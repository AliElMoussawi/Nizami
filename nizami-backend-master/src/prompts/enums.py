import enum

from django.db import models


class PromptType(enum.Enum):
    UPDATING_FILE_FROM_PREVIOUS_MESSAGES = "updating_file_from_previous_messages"
    REPHRASE_REVIEW_DOCX = "rephrase_review_docx"
    REVIEW_DOCX = "review_docx"
    LEGAL_ADVICE = "legal_advice"
    GENERATE_DESCRIPTION = "generate_description"
    FIND_REFERENCE_DOCUMENTS = "find_reference_documents"
    ROUTER = "router"


class PendingDocIntentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    DONE = "DONE", "Done"
    FAILED = "FAILED", "Failed"


class PendingDocIntentIntentType(models.TextChoices):
    SUMMARY = "SUMMARY", "Summary"
    QA = "QA", "Q&A"
