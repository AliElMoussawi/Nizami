import os
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ReferenceDocument, RagSourceDocument
from .serializers import ListReferenceDocumentSerializer, CreateReferenceDocumentSerializer, \
    UpdateReferenceDocumentSerializer
from .. import settings
from ..common.mixins import ForceDatatablesFormatMixin
from ..common.permissions import IsAdminPermission
from ..settings import vectorstore

# Presigned URL expiry (seconds). Max 604800 (7 days) for SigV4.
RAG_S3_PRESIGNED_EXPIRY = 3600  # 1 hour


class ListReferenceDocumentViewSet(ForceDatatablesFormatMixin, ReadOnlyModelViewSet):
    queryset = ReferenceDocument.objects.all().order_by('-created_at').select_related('created_by')
    serializer_class = ListReferenceDocumentSerializer
    pagination_class = DatatablesPageNumberPagination
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def filter_queryset(self, queryset):
        search_term = self.request.data.get('search_term', None)
        if search_term is not None:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(extension__icontains=search_term) |
                Q(language__icontains=search_term) |
                Q(created_by__first_name__icontains=search_term) |
                Q(created_by__last_name__icontains=search_term)
            )

        return queryset


class CreateReferenceDocumentViewSet(ModelViewSet):
    queryset = ReferenceDocument.objects.all()
    serializer_class = CreateReferenceDocumentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]


class UpdateReferenceDocumentViewSet(ModelViewSet):
    queryset = ReferenceDocument.objects.all()
    serializer_class = UpdateReferenceDocumentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]


class RetrieveReferenceDocumentViewSet(ReadOnlyModelViewSet):
    queryset = ReferenceDocument.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def retrieve(self, request, *args, **kwargs):
        doc = self.get_object()

        full_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)

        if os.path.exists(full_path):
            return FileResponse(open(full_path, 'rb'), as_attachment=True)
        raise Http404("File not found")


class DeleteReferenceDocumentViewSet(ModelViewSet):
    queryset = ReferenceDocument.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminPermission]

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        doc: ReferenceDocument = self.get_object()

        if doc.status not in ("processed", "failed", "new", "initial") and doc.created_at < now() - timedelta(hours=2):
            raise APIException("The reference document is being processed at the moment. try again later!")

        parts = list(doc.parts.all())

        vectorstore.delete(ids=[part.id for part in parts])

        doc.delete()

        return Response(status=HTTP_204_NO_CONTENT)


class RagSourceDocumentViewRedirect(APIView):
    """
    Redirects to a short-lived presigned S3 URL so the JSON can be opened in the browser.
    """
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAdminPermission]

    def get(self, request, pk):
        doc = get_object_or_404(RagSourceDocument, pk=pk)
        if not doc.s3_bucket or not doc.s3_key:
            raise APIException("This document has no S3 location; re-run the import command with bucket/key.")
        region = getattr(settings, "RAG_S3_REGION", None) or ""
        if not region:
            raise APIException(
                "RAG_S3_REGION or AWS_DEFAULT_REGION must be set in env for presigned URLs (bucket is not in us-east-1)."
            )
        try:
            s3_client = boto3.client(
                "s3",
                region_name=region,
                endpoint_url=f"https://s3.{region}.amazonaws.com",
            )
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": doc.s3_bucket, "Key": doc.s3_key},
                ExpiresIn=RAG_S3_PRESIGNED_EXPIRY,
            )
        except ClientError as e:
            raise APIException(f"Failed to generate presigned URL: {e}")
        return HttpResponseRedirect(redirect_to=url)


