from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from src.reference_documents.models import ReferenceDocument
from src.reference_documents.tasks import analyze_reference_document


class Command(BaseCommand):
    help = "Embeds all referenced documents"

    def handle(self, *args, **options):
        for reference_document in ReferenceDocument.objects.all().iterator(chunk_size=100):
            async_task(analyze_reference_document, reference_document.id)
