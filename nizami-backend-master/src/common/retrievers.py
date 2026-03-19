"""
Vector similarity search retrievers with document filtering.

Strategy: filter by document ID in SQL first, then rank by vector distance
within that filtered set. This is the only correct approach — a global ANN
search followed by Python-side filtering (the old fallback) loads O(k×20)
vectors into memory and silently returns empty or irrelevant results whenever
the target documents are not globally prominent.

Performance prerequisite — this index must exist on langchain_pg_embedding:

    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_lpe_ref_doc_id
    ON langchain_pg_embedding
    (((cmetadata->>'reference_document_id')::bigint));

Without it, every retrieval does a full table scan of the embeddings table.
Add this index in a Django migration before deploying to production.
"""
import json
import logging

from django.db import connection
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def similarity_search_with_document_filter(
    query_text: str,
    document_ids,
    k: int = 8,
    embeddings=None,
    log: logging.Logger = None,
) -> list[Document]:
    """
    Similarity search pre-filtered by document IDs using a single SQL query.

    The query vector is declared once in a CTE to avoid serializing the
    1536-dimension embedding string twice as query parameters.

    Raises on any database or embedding error — callers decide how to handle
    failures; silent fallbacks that return wrong results are worse than an
    explicit error.
    """
    if log is None:
        log = logger

    if not document_ids:
        return []

    if embeddings is None:
        from src.settings import embeddings

    query_emb = embeddings.embed_query(query_text)
    embedding_str = "[" + ",".join(str(x) for x in query_emb) + "]"

    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH query_vec AS (
                SELECT %s::vector AS vec
            )
            SELECT
                e.id,
                e.document,
                e.cmetadata,
                1 - (e.embedding <=> q.vec) AS similarity
            FROM langchain_pg_embedding e, query_vec q
            WHERE (e.cmetadata->>'reference_document_id')::bigint = ANY(%s::bigint[])
            ORDER BY e.embedding <=> q.vec
            LIMIT %s
            """,
            [embedding_str, list(document_ids), k],
        )
        rows = cursor.fetchall()

    docs = []
    for chunk_id, document, metadata, _similarity in rows:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        elif metadata is None:
            metadata = {}
        metadata["id"] = str(chunk_id) if chunk_id else None
        docs.append(Document(page_content=document or "", metadata=metadata))

    log.info(
        "SQL similarity search: %d chunks from %d target documents",
        len(docs),
        len(list(document_ids)),
    )
    return docs


class FilteredRetriever:
    """
    Retriever that scopes similarity search to a specific set of document IDs.

    Uses a single SQL path (filter-first, then ANN). The previous global-search
    fallback has been removed: it loaded k×20 vectors into memory and returned
    silently incorrect results whenever target documents were not globally
    prominent — a correctness failure, not just a performance one.

    If the SQL query fails (DB down, missing table, etc.) the error is logged
    and an empty list is returned so the LLM answers without retrieval context
    rather than answering from irrelevant chunks.
    """

    def __init__(self, document_ids, k: int = 8, log: logging.Logger = None):
        self.document_ids = set(document_ids) if document_ids else set()
        self.k = k
        self.log = log or logging.getLogger(__name__)

    def invoke(self, query_text: str) -> list[Document]:
        if not self.document_ids:
            return []

        try:
            return similarity_search_with_document_filter(
                query_text=query_text,
                document_ids=self.document_ids,
                k=self.k,
                log=self.log,
            )
        except Exception:
            self.log.error(
                "FilteredRetriever SQL search failed — returning empty context. "
                "document_ids=%s",
                self.document_ids,
                exc_info=True,
            )
            return []
