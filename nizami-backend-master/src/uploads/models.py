import uuid

from django.db import models
from django.db.models import Q

from src.users.models import User


class File(models.Model):
    """
    Canonical file record for chat attachments. Raw bytes stored in S3.
    Deduplicated per tenant by sha256.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="upload_files",
        db_column="tenant_id",
    )
    original_filename = models.CharField(max_length=512)
    mime_type = models.CharField(max_length=255)
    size_bytes = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    s3_bucket = models.CharField(max_length=255, null=True, blank=True)
    s3_key_raw = models.CharField(max_length=1024, null=True, blank=True)
    library_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "uploads_file"
        indexes = [
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["tenant", "sha256"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "sha256"],
                condition=Q(sha256__isnull=False) & ~Q(sha256=""),
                name="uploads_file_tenant_sha256_unique",
            ),
        ]


class UploadSession(models.Model):
    """
    Tracks presigned upload flow; used by POST /uploads/complete.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="upload_sessions",
    )
    upload_id = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "uploads_upload_session"


class FileExtraction(models.Model):
    """
    Per-file extraction state. Preview text in DB; full text in S3.
    """

    class Status(models.TextChoices):
        EXTRACTING = "EXTRACTING", "Extracting"
        PREVIEW_READY = "PREVIEW_READY", "Preview ready"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    id = models.BigAutoField(primary_key=True)
    file = models.OneToOneField(
        File,
        on_delete=models.CASCADE,
        related_name="extraction",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.EXTRACTING,
        db_index=True,
    )
    preview_text = models.TextField(blank=True)
    full_text_s3_key = models.CharField(max_length=1024, null=True, blank=True)
    pages_json_s3_key = models.CharField(max_length=1024, null=True, blank=True)
    extractor_version = models.CharField(max_length=32, default="1")
    error_message = models.TextField(null=True, blank=True)
    preview_ready_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uploads_file_extraction"
        indexes = [
            models.Index(fields=["file", "status"]),
        ]


class FileSummary(models.Model):
    """
    Cached summaries per file. Stored in Postgres (summary_text NOT in S3).
    """

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="file_summaries",
        db_column="tenant_id",
    )
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="summaries",
    )
    summary_type = models.CharField(max_length=64)
    prompt_version = models.CharField(max_length=64)
    summary_text = models.TextField()
    summary_json = models.JSONField(null=True, blank=True)
    model = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uploads_file_summary"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "file", "summary_type", "prompt_version"],
                name="uploads_file_summary_tenant_file_type_version_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "file"]),
        ]
