from django.contrib import admin
from src.uploads.models import File, FileExtraction, FileSummary, UploadSession


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "original_filename", "mime_type", "size_bytes", "sha256", "created_at")
    list_filter = ("mime_type", "library_saved")
    search_fields = ("original_filename", "sha256")


@admin.register(UploadSession)
class UploadSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "upload_id", "file", "status", "created_at")


@admin.register(FileExtraction)
class FileExtractionAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "status", "extractor_version", "preview_ready_at", "ready_at", "created_at")
    list_filter = ("status",)


@admin.register(FileSummary)
class FileSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "file", "summary_type", "prompt_version", "created_at")
    list_filter = ("summary_type",)
