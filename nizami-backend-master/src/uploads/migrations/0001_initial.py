# Generated manually for chat attachments (uploads app)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="File",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("original_filename", models.CharField(max_length=512)),
                ("mime_type", models.CharField(max_length=255)),
                ("size_bytes", models.PositiveBigIntegerField()),
                ("sha256", models.CharField(blank=True, db_index=True, max_length=64, null=True)),
                ("s3_bucket", models.CharField(blank=True, max_length=255, null=True)),
                ("s3_key_raw", models.CharField(blank=True, max_length=1024, null=True)),
                ("library_saved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="upload_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "uploads_file",
            },
        ),
        migrations.AddIndex(
            model_name="file",
            index=models.Index(fields=["tenant", "created_at"], name="uploads_file_tenant_created_idx"),
        ),
        migrations.AddIndex(
            model_name="file",
            index=models.Index(fields=["tenant", "sha256"], name="uploads_file_tenant_sha256_idx"),
        ),
        migrations.AddConstraint(
            model_name="file",
            constraint=models.UniqueConstraint(
                condition=models.Q(sha256__isnull=False) & ~models.Q(sha256=""),
                fields=("tenant", "sha256"),
                name="uploads_file_tenant_sha256_unique",
            ),
        ),
        migrations.CreateModel(
            name="UploadSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("upload_id", models.CharField(db_index=True, max_length=64, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("COMPLETED", "Completed")],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="upload_sessions",
                        to="uploads.file",
                    ),
                ),
            ],
            options={
                "db_table": "uploads_upload_session",
            },
        ),
        migrations.CreateModel(
            name="FileExtraction",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("EXTRACTING", "Extracting"),
                            ("PREVIEW_READY", "Preview ready"),
                            ("READY", "Ready"),
                            ("FAILED", "Failed"),
                        ],
                        db_index=True,
                        default="EXTRACTING",
                        max_length=32,
                    ),
                ),
                ("preview_text", models.TextField(blank=True)),
                ("full_text_s3_key", models.CharField(blank=True, max_length=1024, null=True)),
                ("pages_json_s3_key", models.CharField(blank=True, max_length=1024, null=True)),
                ("extractor_version", models.CharField(default="1", max_length=32)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("preview_ready_at", models.DateTimeField(blank=True, null=True)),
                ("ready_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "file",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extraction",
                        to="uploads.file",
                    ),
                ),
            ],
            options={
                "db_table": "uploads_file_extraction",
            },
        ),
        migrations.AddIndex(
            model_name="fileextraction",
            index=models.Index(fields=["file", "status"], name="uploads_fileextraction_file_status_idx"),
        ),
        migrations.CreateModel(
            name="FileSummary",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("summary_type", models.CharField(max_length=64)),
                ("prompt_version", models.CharField(max_length=64)),
                ("summary_text", models.TextField()),
                ("summary_json", models.JSONField(blank=True, null=True)),
                ("model", models.CharField(blank=True, max_length=128, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="summaries",
                        to="uploads.file",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="file_summaries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "uploads_file_summary",
            },
        ),
        migrations.AddConstraint(
            model_name="filesummary",
            constraint=models.UniqueConstraint(
                fields=("tenant", "file", "summary_type", "prompt_version"),
                name="uploads_file_summary_tenant_file_type_version_unique",
            ),
        ),
        migrations.AddIndex(
            model_name="filesummary",
            index=models.Index(fields=["tenant", "file"], name="uploads_filesummary_tenant_file_idx"),
        ),
    ]
