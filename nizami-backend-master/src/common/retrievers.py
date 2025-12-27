"""
Vector similarity search retrievers with document filtering.

This module provides utilities for performing similarity searches with document ID filtering,
which is necessary because PGVector's filter syntax doesn't support filter-before-search.
"""
import json
import logging

from django.db import connection
from langchain_core.documents import Document


def similarity_search_with_document_filter(query_text, document_ids, k=8, embeddings=None, logger=None):
    """
    Perform similarity search filtered by document IDs using raw SQL.
    
    This is necessary because PGVector's filter syntax doesn't support 
    filter-before-search, which can result in zero results when target 
    documents don't appear in the top global results.
    
    Args:
        query_text: Text to search for
        document_ids: List of document IDs to filter by
        k: Number of results to return
        embeddings: Embeddings model (defaults to settings.embeddings)
        logger: Optional logger instance
    
    Returns:
        List of Document objects or None if search fails
    """
    if embeddings is None:
        from src.settings import embeddings
    
    if not document_ids:
        return []
    
    try:
        query_emb = embeddings.embed_query(query_text)
        
        with connection.cursor() as cursor:
            # Format embedding as vector string for pgvector
            embedding_str = '[' + ','.join(str(x) for x in query_emb) + ']'
            document_ids_list = list(document_ids)
            
            # Parameterized query: Filter FIRST, then search within filtered set
            cursor.execute("""
                SELECT 
                    id,
                    document,
                    cmetadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM langchain_pg_embedding 
                WHERE (cmetadata->>'reference_document_id')::bigint = ANY(%s::bigint[])
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, [embedding_str, document_ids_list, embedding_str, k])
            
            rows = cursor.fetchall()
            if rows:
                docs = []
                for row in rows:
                    chunk_id, document, metadata, similarity = row
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    elif metadata is None:
                        metadata = {}
                    
                    metadata['id'] = str(chunk_id) if chunk_id else None
                    docs.append(Document(
                        page_content=document or '',
                        metadata=metadata
                    ))
                
                if logger:
                    logger.info(f'Similarity search found {len(docs)} chunks from {len(document_ids)} target documents')
                return docs
    except Exception as e:
        if logger:
            logger.warning(f'Similarity search with document filter failed: {e}')
        return None
    
    return None


def fallback_similarity_search_with_filter(query_text, retriever, document_ids, k=8, logger=None):
    """
    Fallback strategy: Search globally and filter by document ID.
    
    This is less reliable than SQL-based search because it searches globally
    first, then filters. If target documents don't appear in the top global
    results, this will return zero results even if chunks exist.
    
    Args:
        query_text: Text to search for
        retriever: LangChain retriever instance (should search with larger k)
        document_ids: Set of document IDs to filter by
        k: Number of results to return
        logger: Optional logger instance
    
    Returns:
        List of Document objects filtered by document_ids
    """
    if logger:
        logger.info('Using FALLBACK strategy: searching globally then filtering')
    
    all_docs = retriever.invoke(query_text)
    
    # Filter by reference_document_id in metadata
    filtered_docs = []
    for doc in all_docs:
        ref_id = doc.metadata.get('reference_document_id')
        if ref_id is not None:
            try:
                ref_id_int = int(ref_id) if isinstance(ref_id, str) else ref_id
                if ref_id_int in document_ids:
                    filtered_docs.append(doc)
                    if len(filtered_docs) >= k:
                        break
            except (ValueError, TypeError):
                pass
    
    if len(filtered_docs) == 0:
        found_doc_ids = {int(doc.metadata.get('reference_document_id')) 
                        for doc in all_docs 
                        if doc.metadata.get('reference_document_id')}
        if logger:
            logger.warning(f'Fallback: Base search returned chunks from {found_doc_ids}, but looking for {document_ids}')
    else:
        if logger:
            logger.info(f'Fallback strategy found {len(filtered_docs)} chunks')
    
    return filtered_docs[:k]


class FilteredRetriever:
    """
    Custom retriever that filters similarity search by document IDs.
    
    Uses two strategies:
    1. SQL-based search: Filters FIRST, then searches within filtered set (preferred)
    2. Fallback search: Searches globally, then filters (less reliable)
    
    This is necessary because PGVector's filter syntax doesn't support
    filter-before-search, which can result in zero results when target
    documents don't appear in the top global results.
    """
    
    def __init__(self, document_ids, k=8, logger=None, vectorstore=None):
        """
        Initialize the filtered retriever.
        
        Args:
            document_ids: List of document IDs to filter by
            k: Number of results to return
            logger: Optional logger instance
            vectorstore: Vectorstore instance (defaults to settings.vectorstore)
        """
        from src.settings import vectorstore as default_vectorstore
        
        self.document_ids = set(document_ids) if document_ids else set()
        self.k = k
        self.logger = logger or logging.getLogger(__name__)
        self.vectorstore = vectorstore or default_vectorstore
        # Fallback: base retriever for when SQL approach doesn't work
        self.base_retriever = self.vectorstore.as_retriever(search_kwargs={'k': max(k * 20, 100)})
    
    def _sql_based_search(self, query_text):
        """
        Strategy 1: SQL-based similarity search within filtered chunks.
        This ensures we search only within chunks from target documents.
        Returns list of Document objects or None if search fails.
        """
        return similarity_search_with_document_filter(
            query_text=query_text,
            document_ids=self.document_ids,
            k=self.k,
            logger=self.logger
        )
    
    def _fallback_search(self, query_text):
        """
        Strategy 2: Fallback - search globally and filter by document ID.
        Less reliable but works when SQL-based search fails.
        Returns list of Document objects.
        """
        return fallback_similarity_search_with_filter(
            query_text=query_text,
            retriever=self.base_retriever,
            document_ids=self.document_ids,
            k=self.k,
            logger=self.logger
        )
    
    def invoke(self, query_text):
        """
        Invoke the retriever with the given query text.
        
        Tries SQL-based search first, falls back to global search if it fails.
        
        Args:
            query_text: Text to search for
        
        Returns:
            List of Document objects
        """
        if not self.document_ids:
            return []
        
        # Try Strategy 1: SQL-based search
        docs = self._sql_based_search(query_text)
        if docs is not None:
            return docs
        
        # Fallback to Strategy 2: Global search then filter
        return self._fallback_search(query_text)

