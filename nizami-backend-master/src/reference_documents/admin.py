from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import RagSourceDocument, RagSourceDocumentChunk


@admin.register(RagSourceDocument)
class RagSourceDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "view_in_browser_link",
        "processed_at",
        "is_extracted",
        "is_embedded",
        "chunk_count",
        "created_at",
    )
    list_filter = ("is_extracted", "is_embedded")
    search_fields = ("title", "s3_key")
    readonly_fields = (
        "uuid5", "s3_bucket", "s3_key", "view_in_browser_link",
        "is_embedded", "created_at", "updated_at",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("title", "uuid5", "view_in_browser_link")}),
        ("S3", {"fields": ("s3_bucket", "s3_key")}),
        ("Description", {"fields": ("description",)}),
        ("Status", {"fields": ("processed_at", "pulled_at", "is_extracted", "is_embedded")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="View in browser")
    def view_in_browser_link(self, obj):
        if not obj.pk or not obj.s3_bucket or not obj.s3_key:
            return mark_safe("<span style='color:#999'>—</span>")
        path = reverse("rag_source_document_view", args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">Open JSON</a>',
            path,
        )

    @admin.display(description="Chunks")
    def chunk_count(self, obj):
        return obj.chunks.count()


@admin.register(RagSourceDocumentChunk)
class RagSourceDocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "rag_source_document", "chunk_index", "content_preview", "created_at")
    list_filter = ("rag_source_document",)
    search_fields = ("content",)
    readonly_fields = ("id", "rag_source_document", "content", "chunk_index", "created_at")
    ordering = ("rag_source_document", "chunk_index")

    @admin.display(description="Content preview")
    def content_preview(self, obj):
        return obj.content[:120] + "…" if len(obj.content) > 120 else obj.content
