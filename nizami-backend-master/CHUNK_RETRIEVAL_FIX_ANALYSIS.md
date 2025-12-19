# Chunk Retrieval Issue - Root Cause Analysis & Fix

## Problem Summary

The system was finding 10 document IDs with 88 total chunks in the database, but the vectorstore retriever was returning **0 chunks** when filtering by those document IDs. This resulted in empty context being passed to the LLM, leading to poor or incomplete responses.

## Root Cause Analysis

### Primary Issue: Search-Then-Filter Approach Failure

The original implementation used a **search-then-filter** strategy:

1. **Step 1**: Search globally across ALL documents → Get top 50 most similar chunks
2. **Step 2**: Filter results by document ID → Return only chunks from target documents

**Why This Failed:**

When an Arabic query like `"ما هي احكام تصفية شركة ذات مسؤولية محدودة..."` was executed:

- The global similarity search returned chunks from documents: `[6407, 15369, 8969, 4108, 9743, ...]`
- Target documents were: `[12025, 15783, 16372, 20879, 13978, 14522, 22131, 26810, 20421, 26738]`
- **Intersection**: ∅ (empty set)
- **Result**: 0 chunks returned, even though 88 chunks existed for the target documents

The problem: **If the query doesn't semantically match chunks from target documents in the top 50 global results, filtering produces zero results.**

### Secondary Issues

1. **PGVector Filter Syntax Incompatibility**
   - The code attempted to use `$in` and `$or` filter operators
   - PGVector/LangChain's filter syntax may not reliably support these operators
   - Metadata is stored as JSONB in PostgreSQL, requiring specific handling

2. **Metadata Type Mismatch**
   - Metadata stored as JSONB strings vs. integer comparisons
   - Filter didn't properly handle type conversion (string → int)

3. **Column Name Error**
   - SQL query used `uuid` column which doesn't exist
   - Correct column name is `id`

## Solution Implemented

### Strategy 1: SQL-Based Similarity Search (Primary)

**Approach: Filter FIRST, then Search**

Instead of searching globally and filtering, we now:

1. **Filter by document ID FIRST** → Only consider chunks from target documents
2. **Search within filtered set** → Find most similar chunks from those documents
3. **Return top k results** → Guaranteed to find chunks if they exist

**Implementation:**

```python
class FilteredRetriever:
    def invoke(self, query_text):
        # Get query embedding
        query_emb = embeddings.embed_query(query_text)
        
        # Format embedding for pgvector
        embedding_str = '[' + ','.join(str(x) for x in query_emb) + ']'
        
        # SQL query: Filter FIRST, then search
        cursor.execute("""
            SELECT 
                id,
                document,
                cmetadata,
                1 - (embedding <=> %s::vector) as similarity
            FROM langchain_pg_embedding 
            WHERE (cmetadata->>'reference_document_id')::bigint = ANY(%s)
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, [embedding_str, list(self.document_ids), embedding_str, self.k])
```

**Why This Works:**

- ✅ **Guarantees results**: If chunks exist for target document IDs, they WILL be found
- ✅ **Better performance**: Uses HNSW index on embedding column efficiently
- ✅ **Direct control**: Bypasses PGVector filter syntax issues
- ✅ **Type-safe**: Properly handles JSONB metadata extraction

### Strategy 2: Enhanced Fallback

If SQL-based search fails, fallback to:

- Search globally with larger k (k * 20 = 160 candidates)
- Filter results by document ID
- Comprehensive debugging to show what document IDs were found vs. expected

### Key Fixes

1. **Fixed SQL Column Name**
   - Changed: `uuid` → `id`
   - The `langchain_pg_embedding` table uses `id` as primary key

2. **Proper Embedding Format**
   - Converts embedding list to string: `'[0.123, 0.456, ...]'`
   - Casts to `::vector` type in PostgreSQL for pgvector operations

3. **Metadata Handling**
   - Handles both string and dict JSONB metadata
   - Converts `reference_document_id` from string to int for comparison

4. **Enhanced Debugging**
   - Logs query and translation being used
   - Shows document IDs found vs. expected
   - Tracks which strategy succeeded

## Technical Details

### Database Schema

The `langchain_pg_embedding` table structure:
- `id` (primary key) - NOT `uuid`
- `document` (text content)
- `embedding` (vector(1536))
- `cmetadata` (JSONB) - contains `reference_document_id`

### Vector Similarity Search

Uses PostgreSQL's pgvector extension:
- `<=>` operator: Cosine distance
- `1 - (embedding <=> query_vector)`: Cosine similarity
- HNSW index for efficient approximate nearest neighbor search

### Query Flow Comparison

**Before (Failed):**
```
1. Embed query → [0.123, 0.456, ...]
2. Search globally → Top 50 chunks from ANY documents
3. Filter by document ID → 0 matches (chunks from wrong documents)
4. Return: [] (empty)
```

**After (Works):**
```
1. Embed query → [0.123, 0.456, ...]
2. Filter by document ID FIRST → Only chunks from target documents
3. Search within filtered set → Top 8 most similar chunks
4. Return: [chunk1, chunk2, ..., chunk8] (guaranteed if chunks exist)
```

## Expected Results

### Before Fix
- ✅ Found 10 document IDs with 88 chunks
- ❌ Returned 0 chunks (filter failed)
- ❌ Empty context passed to LLM

### After Fix
- ✅ Finds chunks from target documents using SQL-based search
- ✅ Returns up to 8 most relevant chunks from those documents
- ✅ Falls back to global search if SQL fails
- ✅ Comprehensive debugging for troubleshooting

## Potential Remaining Considerations

1. **Translation/Rephrasing Quality**
   - If query is poorly translated/rephrased, similarity scores may be lower
   - Chunks will still be found, but may be less semantically relevant
   - Consider improving translation/rephrasing logic if needed

2. **SQL Connection Context**
   - SQL approach uses Django's database connection
   - Ensure it's in the same transaction context as the main query
   - May need connection pooling considerations for high traffic

3. **Performance at Scale**
   - SQL approach should be faster (uses index efficiently)
   - Monitor performance with large document sets
   - Consider caching query embeddings if needed

4. **Edge Cases**
   - What if no chunks exist for target document IDs? (Returns empty, which is correct)
   - What if SQL query fails? (Falls back to global search)
   - What if embedding generation fails? (Exception handling in place)

## Code Changes Summary

### Files Modified
- `src/chats/flow.py` - `answer_legal_question()` function

### Key Changes
1. Created `FilteredRetriever` class with SQL-based search
2. Fixed SQL column name from `uuid` to `id`
3. Added proper embedding string formatting for pgvector
4. Enhanced debugging and logging
5. Added fallback strategy for robustness

### Testing Recommendations

1. **Test with Arabic queries** - Verify chunks are retrieved correctly
2. **Test with English queries** - Ensure no regression
3. **Test with edge cases**:
   - No matching document IDs
   - SQL query failure
   - Empty query
   - Very long queries

4. **Monitor logs** for:
   - SQL-based search success rate
   - Fallback usage frequency
   - Document ID matching accuracy

## Conclusion

The root cause was a **fundamental flaw in the search strategy**: searching globally then filtering meant that if target documents weren't in the top global results, filtering would produce zero results.

The fix implements a **filter-first approach** using direct SQL queries, which:
- Guarantees results when chunks exist for target documents
- Bypasses PGVector filter syntax limitations
- Provides better performance through proper index usage
- Includes robust error handling and fallback mechanisms

This ensures that when document IDs are found, their chunks will be retrieved and used as context for the LLM, significantly improving response quality.
