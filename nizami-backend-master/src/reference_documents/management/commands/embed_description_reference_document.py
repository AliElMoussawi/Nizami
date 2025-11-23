from django.core.management.base import BaseCommand

from src.reference_documents.models import ReferenceDocument
from src.settings import embeddings


class Command(BaseCommand):
    help = "Embed Description Reference Document"

    def handle(self, *args, **options):
        for reference_document in ReferenceDocument.objects.filter(description__isnull=False).all().iterator(chunk_size=100):
            reference_document.description_embedding = embeddings.embed_query(reference_document.description)
            reference_document.save()
