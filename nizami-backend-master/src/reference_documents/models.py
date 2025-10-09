import os
import uuid

from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import pre_save
from django.dispatch import receiver
from pgvector.django import VectorField

from src.users.models import User


class ReferenceDocument(models.Model):
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
    description_embedding = VectorField(null=True)

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

