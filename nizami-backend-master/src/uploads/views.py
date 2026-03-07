import logging
import uuid

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.uploads.models import File, FileExtraction, UploadSession
from src.uploads.serializers import (
    CompleteUploadSerializer,
    InitUploadSerializer,
    UploadCompleteResponseSerializer,
)
from src.uploads.storage import (
    compute_sha256_from_s3,
    delete_object_best_effort,
    generate_presigned_put_url,
    get_s3_client,
    head_object,
    raw_s3_key,
)

logger = logging.getLogger(__name__)


def _enqueue_extract_file(*, file_id: str) -> None:
    from django_q.tasks import async_task
    from src.uploads.tasks import extract_file
    async_task(extract_file, str(file_id))


class InitUploadView(APIView):
    """
    POST /api/v1/attachments/init
    If sha256 provided and (tenant_id, sha256) exists: return file_id, reused: true.
    Else: create File + UploadSession, return upload_id, file_id, upload_url, required_headers.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def post(self, request):
        serializer = InitUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user
        tenant_id = user.id
        sha256 = (data.get("sha256") or "").strip() or None

        if sha256:
            existing = File.objects.filter(tenant_id=tenant_id, sha256=sha256).first()
            if existing:
                return Response({
                    "file_id": str(existing.id),
                    "reused": True,
                })

        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
        if not bucket:
            return Response(
                {"detail": "S3 storage is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        file_id = uuid.uuid4()
        key = raw_s3_key(tenant_id=tenant_id, file_id=str(file_id), filename=data["file_name"])

        file_record = File.objects.create(
            id=file_id,
            tenant_id=tenant_id,
            original_filename=data["file_name"],
            mime_type=data["mime_type"],
            size_bytes=data["file_size"],
            sha256=sha256,
            s3_bucket=bucket,
            s3_key_raw=key,
            library_saved=data.get("store_in_library", False),
        )

        upload_id = uuid.uuid4().hex[:16]
        UploadSession.objects.create(
            id=uuid.uuid4(),
            file=file_record,
            upload_id=upload_id,
            status=UploadSession.Status.PENDING,
        )

        use_localstack = getattr(settings, "USE_LOCALSTACK_S3", False)
        if use_localstack:
            # Avoid CORS/preflight issues: proxy upload through backend (local dev only).
            upload_url = request.build_absolute_uri(
                f"/api/v1/attachments/upload-proxy?upload_id={upload_id}"
            )
            required_headers = {}
            if data.get("mime_type"):
                required_headers["Content-Type"] = data["mime_type"]
        else:
            upload_url = generate_presigned_put_url(
                bucket=bucket,
                key=key,
                expires_in=600,
            )
            required_headers = {}
            if data.get("mime_type"):
                required_headers["Content-Type"] = data["mime_type"]

        return Response({
            "upload_id": upload_id,
            "file_id": str(file_id),
            "upload_url": upload_url,
            "upload_method": "PUT",
            "required_headers": required_headers,
        })


class UploadProxyView(APIView):
    """
    PUT /api/v1/attachments/upload-proxy?upload_id=...
    Proxy file upload to S3 (used when USE_LOCALSTACK_S3 to avoid CORS/preflight issues).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def put(self, request):
        upload_id = request.GET.get("upload_id")
        if not upload_id:
            return Response(
                {"detail": "Missing upload_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        session = (
            UploadSession.objects
            .select_related("file")
            .filter(
                file__tenant_id=request.user.id,
                upload_id=upload_id,
                status=UploadSession.Status.PENDING,
            )
            .first()
        )
        if not session:
            return Response(
                {"detail": "Upload session not found or already completed."},
                status=status.HTTP_404_NOT_FOUND,
            )
        file_record = session.file
        bucket = file_record.s3_bucket
        key = file_record.s3_key_raw
        body = request.body
        content_type = request.headers.get("Content-Type") or None
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        if getattr(settings, "USE_LOCALSTACK_S3", False):
            extra["ACL"] = "bucket-owner-full-control"
        client = get_s3_client()
        client.put_object(Bucket=bucket, Key=key, Body=body, **extra)
        return Response(status=status.HTTP_200_OK)


class CompleteUploadView(APIView):
    """
    POST /api/v1/attachments/complete
    Verify S3 object exists, compute sha256 if not provided, dedupe, finalize, enqueue extract_file.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def post(self, request):
        serializer = CompleteUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload_id = serializer.validated_data["upload_id"]
        user = request.user

        session = (
            UploadSession.objects
            .select_related("file")
            .filter(file__tenant_id=user.id, upload_id=upload_id, status=UploadSession.Status.PENDING)
            .first()
        )
        if not session:
            return Response(
                {"detail": "Upload session not found or already completed."},
                status=status.HTTP_404_NOT_FOUND,
            )

        file_record = session.file
        bucket = file_record.s3_bucket
        key = file_record.s3_key_raw

        if not head_object(bucket=bucket, key=key):
            return Response(
                {"detail": "File not found in storage. Upload may have failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not file_record.sha256:
            computed_sha256 = compute_sha256_from_s3(bucket=bucket, key=key)
        else:
            computed_sha256 = file_record.sha256

        existing = (
            File.objects
            .filter(tenant_id=user.id, sha256=computed_sha256)
            .exclude(id=file_record.id)
            .first()
        )

        if existing:
            # Only reuse if the existing file's object still exists in S3 (avoids NoSuchKey when bucket was recreated).
            try:
                existing_ok = bool(
                    existing.s3_bucket
                    and existing.s3_key_raw
                    and head_object(bucket=existing.s3_bucket, key=existing.s3_key_raw)
                )
            except Exception:
                existing_ok = False
            if existing_ok:
                delete_object_best_effort(bucket=bucket, key=key)
                session.delete()
                file_record.delete()
                file_id_to_return = existing.id
                if not FileExtraction.objects.filter(file_id=existing.id, status=FileExtraction.Status.READY).exists():
                    _enqueue_extract_file(file_id=str(existing.id))
                return Response(UploadCompleteResponseSerializer({
                    "file_id": file_id_to_return,
                    "status": "reused",
                }).data)
            # Existing file's object is missing (e.g. bucket was recreated). Clear its sha256 so we can save the new file (unique constraint).
            existing.sha256 = None
            existing.save(update_fields=["sha256"])

        file_record.sha256 = computed_sha256
        file_record.save(update_fields=["sha256"])
        session.status = UploadSession.Status.COMPLETED
        session.save(update_fields=["status"])

        _enqueue_extract_file(file_id=str(file_record.id))

        return Response(UploadCompleteResponseSerializer({
            "file_id": file_record.id,
            "status": "completed",
        }).data)
