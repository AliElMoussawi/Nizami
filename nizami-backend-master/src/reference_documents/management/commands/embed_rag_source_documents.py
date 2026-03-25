import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
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
        parser.add_argument(
            "--created-after",
            type=str,
            help="Only process documents with created_at date strictly after this date (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--created-on",
            type=str,
            help="Only process documents with created_at on this date (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--offset",
            type=int,
            default=0,
            help="Skip the first N documents after filtering (for partitioned execution).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of documents to process after applying offset.",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=4,
            help="Number of worker threads to process documents.",
        )
        parser.add_argument(
            "--document-id",
            type=int,
            action="append",
            dest="document_ids",
            default=None,
            help=(
                "Only process RagSourceDocument row(s) with this primary key. "
                "Repeat the flag for multiple ids. Combine with --force to re-embed already embedded docs."
            ),
        )

    def handle(self, *args, **options):
        bucket: Optional[str] = options.get("bucket")
        batch_size: int = options["batch_size"]
        force: bool = options["force"]
        created_after_str: Optional[str] = options.get("created_after")
        created_on_str: Optional[str] = options.get("created_on")
        offset: int = options["offset"]
        limit: Optional[int] = options.get("limit")
        workers: int = options["workers"]
        document_ids: Optional[List[int]] = options.get("document_ids")

        if not bucket:
            logger.error("Bucket name is required (use --bucket or RAG_S3_BUCKET env var).")
            return

        if embeddings is None:
            logger.error("OpenAI embeddings not initialised (check OPENAI_API_KEY).")
            return

        qs = RagSourceDocument.objects.all()

        if document_ids:
            qs = qs.filter(id__in=document_ids)

        # Date filtering
        if created_on_str and created_after_str:
            logger.error("Use only one of --created-on or --created-after, not both.")
            return

        if created_on_str:
            try:
                created_on: date = datetime.strptime(created_on_str, "%Y-%m-%d").date()
            except ValueError:
                logger.error("Invalid --created-on date format. Use YYYY-MM-DD.")
                return
            qs = qs.filter(created_at__date=created_on)
        elif created_after_str:
            try:
                created_after: date = datetime.strptime(created_after_str, "%Y-%m-%d").date()
            except ValueError:
                logger.error("Invalid --created-after date format. Use YYYY-MM-DD.")
                return
            qs = qs.filter(created_at__date__gt=created_after)

        if not force:
            qs = qs.filter(is_embedded=False)

        # Partitioning: apply deterministic ordering, then offset/limit
        qs = qs.order_by("id")
        if offset:
            qs = qs[offset:]
        if limit is not None:
            qs = qs[:limit]

        total = qs.count()
        if total == 0:
            logger.info("No documents to embed.")
            return

        logger.info("Starting embedding for %s RagSourceDocument(s) with %s workers…", total, workers)

        # Collect ids so we don't share ORM instances across threads.
        doc_ids = list(qs.values_list("id", flat=True))

        created_total = 0
        failed_total = 0

        def worker(doc_id: int) -> bool:
            print(f"worker for doc_id {doc_id}")
            close_old_connections()
            try:
                doc = RagSourceDocument.objects.get(id=doc_id)
                s3_client = boto3.client("s3")
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP,
                )
                self._process_document(doc, s3_client, bucket, text_splitter, batch_size)
                print(f"execution done for doc_id {doc_id}")

                return True
            except Exception as exc:
                logger.error("Failed to embed doc id=%s: %s", doc_id, exc)
                print(f"execution failed for doc_id {doc_id}")

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
