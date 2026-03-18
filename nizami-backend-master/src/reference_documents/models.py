import os
import uuid

from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_save
from django.dispatch import receiver
from pgvector.django import HnswIndex, VectorField

from src.users.models import User


class ReferenceDocument(models.Model):
    class Meta:
        indexes = [
            HnswIndex(
                name='description_embedding_hnsw_idx',  # Custom name for your index
                fields=['description_embedding'],
                m=12,  # The number of connections per layer
                ef_construction=120,  # The construction quality/speed trade-off
                opclasses=['vector_cosine_ops'],  # Operator class for similarity search (e.g., cosine)
            ),
        ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('processed', 'processed'),
        ('failed', 'Failed')
    ]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    name = models.CharField(max_length=350)

    file_name = models.CharField(max_length=350, null=True)
    size = models.PositiveIntegerField()
    extension = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='new', choices=STATUS_CHOICES)
    file = models.FileField(upload_to='uploads/', null=False, blank=False)
    text = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    description_embedding = VectorField(null=True, dimensions=1536)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reference_documents', default=None, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    parts: QuerySet['ReferenceDocumentPart']


@receiver(pre_save, sender=ReferenceDocument)
def modify_file_name(sender, instance, **kwargs):
    if instance.file and instance.file_name is None:
        instance.file_name = instance.file.name
        instance.size = instance.file.size
        instance.extension = os.path.splitext(instance.file.name)[-1].lower().lstrip('.')
        instance.file.name = f"{uuid.uuid4().hex}.{instance.extension}"


class ReferenceDocumentPart(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    reference_document = models.ForeignKey(ReferenceDocument, on_delete=models.CASCADE, related_name='parts')


class RagSourceDocument(models.Model):
    """
    Stores metadata for cleaned RAG source documents that live as JSON files in S3.
    """

    class Meta:
        indexes = [
            HnswIndex(
                name='rag_doc_desc_embedding_hnsw_idx',
                fields=['description_embedding'],
                m=12,
                ef_construction=120,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    uuid5 = models.UUIDField(unique=True)

    title = models.CharField(max_length=512)
    s3_bucket = models.CharField(max_length=255, null=True, blank=True)
    s3_key = models.CharField(max_length=1024, null=True, blank=True)

    description = models.TextField(blank=True, null=True)
    description_embedding = VectorField(null=True, dimensions=1536)

    processed_at = models.DateTimeField(null=True, blank=True)
    pulled_at = models.DateTimeField(null=True, blank=True)

    is_extracted = models.BooleanField(default=False)
    is_embedded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    chunks: QuerySet['RagSourceDocumentChunk']


class RagSourceDocumentChunk(models.Model):
    """
    Stores chunked text with vector embeddings for RAG source documents.
    Mirrors what langchain_pg_embedding does for ReferenceDocument/ReferenceDocumentPart.
    """

    class Meta:
        indexes = [
            HnswIndex(
                name='rag_chunk_embedding_hnsw_idx',
                fields=['embedding'],
                m=12,
                ef_construction=120,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rag_source_document = models.ForeignKey(
        RagSourceDocument, on_delete=models.CASCADE, related_name='chunks',
    )
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    chunk_index = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

