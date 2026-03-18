from rest_framework import serializers

# Allowed for chat attachments (plan: PDF, DOC, DOCX)
ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_UPLOAD_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


def validate_upload_file_params(*, file_name: str, file_size: int, mime_type: str) -> None:
    """Validate file name, size, and mime type for upload init."""
    if file_size <= 0 or file_size > MAX_UPLOAD_SIZE_BYTES:
        raise serializers.ValidationError("Invalid file size.")
    ext = (file_name.rsplit(".", 1)[-1].lower()) if "." in file_name else ""
    if ext not in ALLOWED_UPLOAD_EXTENSIONS or mime_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
        raise serializers.ValidationError("Unsupported file type. Allowed: PDF, DOC, DOCX.")


class InitUploadSerializer(serializers.Serializer):
    file_name = serializers.CharField(required=True, max_length=512)
    file_size = serializers.IntegerField(required=True, min_value=1)
    mime_type = serializers.CharField(required=True, max_length=255)
    sha256 = serializers.CharField(required=False, allow_blank=True, max_length=64)
    store_in_library = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        validate_upload_file_params(
            file_name=attrs["file_name"],
            file_size=attrs["file_size"],
            mime_type=attrs["mime_type"],
        )
        return attrs


class CompleteUploadSerializer(serializers.Serializer):
    upload_id = serializers.CharField(required=True, max_length=64)


class UploadInitResponseSerializer(serializers.Serializer):
    """Response when new upload is required."""
    upload_id = serializers.CharField()
    file_id = serializers.UUIDField()
    upload_url = serializers.URLField()
    required_headers = serializers.DictField(child=serializers.CharField())


class UploadReusedResponseSerializer(serializers.Serializer):
    """Response when file is reused (dedupe by sha256)."""
    file_id = serializers.UUIDField()
    reused = serializers.BooleanField(default=True)


class UploadCompleteResponseSerializer(serializers.Serializer):
    file_id = serializers.UUIDField()
    status = serializers.CharField()
