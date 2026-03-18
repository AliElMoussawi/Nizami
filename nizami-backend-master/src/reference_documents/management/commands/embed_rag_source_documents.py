import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import close_old_connections
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.reference_documents.models import RagSourceDocument, RagSourceDocumentChunk
from src.reference_documents.utils import generate_description_for_text
from src.settings import embeddings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


class Command(BaseCommand):
    help = (
        "Fetch clean_text from S3 for RagSourceDocuments, chunk it, generate embeddings, "
        "generate a description + description embedding, and store everything in "
        "RagSourceDocumentChunk. Mirrors the ReferenceDocument pipeline but for S3 RAG docs."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--bucket",
            type=str,
            default=getattr(settings, "RAG_S3_BUCKET", ""),
            help="S3 bucket override (defaults to RAG_S3_BUCKET).",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of chunks to embed in a single OpenAI call (default 50).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-embed documents that are already marked is_embedded=True.",
        )

    def handle(self, *args, **options):
        bucket: Optional[str] = options.get("bucket")
        batch_size: int = options["batch_size"]
        force: bool = options["force"]

        if not bucket:
            logger.error("Bucket name is required (use --bucket or RAG_S3_BUCKET env var).")
            return

        if embeddings is None:
            logger.error("OpenAI embeddings not initialised (check OPENAI_API_KEY).")
            return

        qs = RagSourceDocument.objects.all()
        if not force:
            qs = qs.filter(is_embedded=False)

        total = qs.count()
        if total == 0:
            logger.info("No documents to embed.")
            return

        workers = 4
        logger.info("Starting embedding for %s RagSourceDocument(s) with %s workers…", total, workers)

        # Collect ids so we don't share ORM instances across threads.
        doc_ids = list(qs.values_list("id", flat=True))

        created_total = 0
        failed_total = 0

        def worker(doc_id: int) -> bool:
            close_old_connections()
            try:
                doc = RagSourceDocument.objects.get(id=doc_id)
                s3_client = boto3.client("s3")
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP,
                )
                self._process_document(doc, s3_client, bucket, text_splitter, batch_size)
                return True
            except Exception as exc:
                logger.error("Failed to embed doc id=%s: %s", doc_id, exc)
                return False

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_id = {executor.submit(worker, doc_id): doc_id for doc_id in doc_ids}
            for future in as_completed(future_to_id):
                ok = future.result()
                if ok:
                    created_total += 1
                else:
                    failed_total += 1

        logger.info(
            "Done. embedded=%s, failed=%s, total=%s.",
            created_total, failed_total, total,
        )

    # ------------------------------------------------------------------
    def _process_document(
        self,
        doc: RagSourceDocument,
        s3_client,
        bucket: str,
        text_splitter: RecursiveCharacterTextSplitter,
        batch_size: int,
    ):
        s3_bucket = doc.s3_bucket or bucket
        s3_key = doc.s3_key

        if not s3_key:
            raise ValueError("s3_key is empty")

        body = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)["Body"].read()
        payload = json.loads(body)

        clean_text = payload.get("clean_text")
        if not isinstance(clean_text, str) or not clean_text.strip():
            raise ValueError("missing or empty clean_text")

        # ---- Delete old chunks if force-re-embedding ----
        RagSourceDocumentChunk.objects.filter(rag_source_document=doc).delete()

        # ---- Chunk ----
        chunks: List[str] = text_splitter.split_text(clean_text)
        if not chunks:
            raise ValueError("text_splitter produced zero chunks")

        # ---- Embed chunks in batches ----
        all_embeddings: List[List[float]] = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_embs = embeddings.embed_documents(batch)
            all_embeddings.extend(batch_embs)

        # ---- Bulk-create chunk rows ----
        chunk_objects = [
            RagSourceDocumentChunk(
                id=uuid.uuid4(),
                rag_source_document=doc,
                content=text,
                embedding=emb,
                chunk_index=idx,
            )
            for idx, (text, emb) in enumerate(zip(chunks, all_embeddings))
        ]
        RagSourceDocumentChunk.objects.bulk_create(chunk_objects, batch_size=100)

        # ---- Generate description & embed it (same as ReferenceDocument) ----
        if not doc.description:
            doc.description = generate_description_for_text(clean_text, "ar")

        doc.description_embedding = embeddings.embed_query(doc.description)
        doc.is_embedded = True
        doc.save(update_fields=[
            "description", "description_embedding", "is_embedded", "updated_at",
        ])

        logger.info(
            "Embedded doc id=%s  chunks=%s  title=%r",
            doc.id, len(chunk_objects), doc.title,
        )
