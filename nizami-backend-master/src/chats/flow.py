import json
import re
import time
import uuid

from django.db import connection
from django.db.models import Q
from langchain.retrievers import MultiQueryRetriever
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Any

from src.chats.domain import rephrase_user_input_using_history, find_ref_document_ids_by_description, translate_question
from src.chats.models import Message, MessageLog, MessageStepLog
from src.chats.utils import create_legal_advice_llm, detect_language, create_llm
from src.prompts.enums import PromptType
from src.prompts.utils import get_prompt_value_by_name
from src.settings import vectorstore


class State(TypedDict):
    input: str
    query: str
    uuid: str
    input_translation: str
    message: Message
    chat_id: int
    history: list
    decision: str
    system_message: Message
    response: Any
    rag_response: Any
    used_languages: Any
    show_translation_disclaimer: str
    answer_language: str
    output: str


# Schema for structured output to use as routing logic
class Route(BaseModel):
    step: Literal["legal_question", "translation", "other"] = Field(
        None, description="The next step in the routing process"
    )


def router(state: State):
    t1 = time.time()

    llm = create_llm('gpt-5-nano', reasoning_effort="minimal")

    router_llm = llm.with_structured_output(Route)

    template = get_prompt_value_by_name(PromptType.ROUTER)

    decision = router_llm.invoke([
        SystemMessage(
            content=template,
        ),
        HumanMessage(
            content=state['input'],
        ),
    ])

    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='router',
        message_id=state['message'].id,
        time_sec=t2 - t1,
        input=None,
        output={
            'decision': decision.step,
        }
    )

    return {
        'decision': decision.step,
    }


def has_answer(state: State):
    child = state['message'].children.first()
    return {
        'decision': 'yes' if child is not None else 'no',
    }


def first_or_create_message(state: State):
    t1 = time.time()
    
    user_message = Message.objects.filter(uuid=state['uuid']).first()

    if user_message is None:
        question_language = detect_language(state['input'])
        user_message = Message.objects.create(
            role='user',
            language=question_language,
            used_query=state['input'],
            chat_id=state['chat_id'],
            text=state['input'],
            uuid=state['uuid'],
        )
        
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='first_or_create_message',
        message=user_message,
        time_sec=t2 - t1,
        input={
            'uuid': state['uuid'],
            'input': state['input'],
        },
        output=None
    )

    return {
        'message': user_message,
    }


def retrieve_history(state: State):
    t1 = time.time()
    
    history = list(
        reversed(
            Message.objects.filter(Q(chat_id=state['chat_id']) & ~Q(id=state['message'].id)).order_by('-created_at')[
            :10]))
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='retrieve_history',
        message_id=state['message'].id,
        time_sec=t2 - t1,
        input=None,
        output={
            'history_count': len(history),
        }
    )

    return {
        'history': history,
    }


def rephrase_user_input(state: State):
    t1 = time.time()

    user_message = state['message']

    query = state['message'].text
    history = state['history']

    if len(history) > 0:
        used_queries = list(filter(None, [msg.used_query if msg.role != 'ai' else None for msg in history]))
        if len(used_queries) > 0:
            query = rephrase_user_input_using_history(query, used_queries)
            user_message.used_query = query
            user_message.save()

    t2 = time.time()

    MessageStepLog.objects.create(
        step_name='rephrase_user_input',
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'query': query,
        }
    )

    return {
        'query': query,
    }


def translate_user_input(state: State):
    user_message = state['message']

    t1 = time.time()

    input_translation = translate_question(user_message.text, user_message.language)

    t2 = time.time()

    MessageStepLog.objects.create(
        step_name='translate_user_input',
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'input_translation': input_translation,
        }
    )

    return {
        'input_translation': input_translation,
    }


def calculate_disclaimer(state: State):
    t1 = time.time()

    response = state['response']
    answer = response['answer']
    used_languages = state['used_languages']
    user_message = state['message']
    question_language = user_message.language

    is_context_used = response.get('is_context_used', False)
    is_answer = response.get('is_answer', False)

    answer_language = detect_language(answer)

    context_multi_language = len(used_languages) > 1
    context_different_lang_from_question = len(used_languages) == 1 and list(used_languages)[0] != question_language
    answer_different_lang_from_question = answer_language != question_language
    is_different_language = (
            context_multi_language or context_different_lang_from_question or answer_different_lang_from_question)

    show_translation_disclaimer = is_different_language and is_context_used and is_answer

    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='calculate_disclaimer',
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'answer_language': answer_language,
            'context_different_lang_from_question': context_different_lang_from_question,
            'answer_different_lang_from_question': answer_different_lang_from_question,
            'is_different_language': is_different_language,
            'show_translation_disclaimer': show_translation_disclaimer,
        }
    )

    return {
        'answer_language': answer_language,
        'show_translation_disclaimer': show_translation_disclaimer,
    }


def store_system_message(state: State):
    response = state['response']
    answer = response['answer']
    user_message = state['message']
    answer_language = state['answer_language']
    show_translation_disclaimer = state['show_translation_disclaimer']
    question_language = user_message.language
    chat_id = user_message.chat_id

    system_message = Message.objects.create(
        chat_id=chat_id,
        parent=user_message,
        language=answer_language,
        text=answer,
        show_translation_disclaimer=show_translation_disclaimer,
        translation_disclaimer_language=question_language,
        role='ai',
        uuid=uuid.uuid4(),
    )

    return {
        'system_message': system_message,
    }


def answer_legal_question(state: State):
    t1 = time.time()
    
    user_message = state['message']
    translation = state['input_translation']
    query = state['query']

    ids = find_ref_document_ids_by_description(query)
    
    # Debug: Log document IDs found
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'[DEBUG] Found {len(ids)} document IDs: {ids}')

    llm = create_legal_advice_llm()
    template = get_prompt_value_by_name(PromptType.LEGAL_ADVICE)

    # Create a custom retriever that properly filters by document IDs
    # The issue: if we search globally and filter, we might not get chunks from target docs
    # Solution: Use SQL to do similarity search within the filtered chunk set
    class FilteredRetriever:
        def __init__(self, document_ids, k=8):
            self.document_ids = set(document_ids) if document_ids else set()
            self.k = k
            # Fallback: base retriever for when SQL approach doesn't work
            self.base_retriever = vectorstore.as_retriever(search_kwargs={'k': max(k * 20, 100)})  # Get many more candidates
        
        def invoke(self, query_text):
            if not self.document_ids:
                return []
            
            # Strategy 1: Try SQL-based similarity search within filtered chunks
            # This ensures we search only within chunks from target documents
            try:
                # Get query embedding for the current query text
                from src.settings import embeddings
                query_emb = embeddings.embed_query(query_text)
                
                # Build SQL query to do similarity search within filtered chunks
                with connection.cursor() as cursor:
                    # Use cosine distance for similarity (<=> operator)
                    # Format embedding as string for pgvector: '[1,2,3]'::vector
                    embedding_str = '[' + ','.join(str(x) for x in query_emb) + ']'
                    
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
                    
                    rows = cursor.fetchall()
                    if rows:
                        # Convert SQL results to Document objects
                        from langchain_core.documents import Document
                        docs = []
                        for row in rows:
                            chunk_id, document, metadata, similarity = row
                            # Parse metadata if it's a string
                            if isinstance(metadata, str):
                                import json
                                metadata = json.loads(metadata)
                            elif metadata is None:
                                metadata = {}
                            
                            # Add id to metadata for reference
                            metadata['id'] = str(chunk_id) if chunk_id else None
                            
                            doc = Document(
                                page_content=document or '',
                                metadata=metadata
                            )
                            docs.append(doc)
                        
                        print(f'[DEBUG] SQL-based search found {len(docs)} chunks from target documents', flush=True)
                        import logging
                        logging.getLogger(__name__).info(f'[DEBUG] SQL-based search found {len(docs)} chunks from target documents')
                        return docs
            except Exception as e:
                print(f'[DEBUG] SQL-based search failed: {e}, falling back to filter approach', flush=True)
                import logging
                logging.getLogger(__name__).warning(f'[DEBUG] SQL-based search failed: {e}, falling back to filter approach')
            
            # Strategy 2: Fallback - search globally and filter (less reliable)
            all_docs = self.base_retriever.invoke(query_text)
            
            # Debug: Check what document IDs we're getting
            found_doc_ids = set()
            for doc in all_docs:
                ref_id = doc.metadata.get('reference_document_id')
                if ref_id is not None:
                    try:
                        ref_id_int = int(ref_id) if isinstance(ref_id, str) else ref_id
                        found_doc_ids.add(ref_id_int)
                    except (ValueError, TypeError):
                        pass
            
            print(f'[DEBUG] Base search returned chunks from document IDs: {found_doc_ids}', flush=True)
            print(f'[DEBUG] Looking for document IDs: {self.document_ids}', flush=True)
            import logging
            logging.getLogger(__name__).info(f'[DEBUG] Base search returned chunks from document IDs: {found_doc_ids}')
            logging.getLogger(__name__).info(f'[DEBUG] Looking for document IDs: {self.document_ids}')
            
            # Filter by reference_document_id in metadata
            filtered_docs = []
            for doc in all_docs:
                # Check if reference_document_id matches (handle both int and string)
                ref_id = doc.metadata.get('reference_document_id')
                if ref_id is not None:
                    # Convert to int for comparison (metadata might be stored as string)
                    try:
                        ref_id_int = int(ref_id) if isinstance(ref_id, str) else ref_id
                        if ref_id_int in self.document_ids:
                            filtered_docs.append(doc)
                    except (ValueError, TypeError):
                        pass
                
                # Stop when we have enough results
                if len(filtered_docs) >= self.k:
                    break
            
            print(f'[DEBUG] After filtering, found {len(filtered_docs)} chunks', flush=True)
            import logging
            logging.getLogger(__name__).info(f'[DEBUG] After filtering, found {len(filtered_docs)} chunks')
            
            return filtered_docs[:self.k]
    
    # Debug: Log the query being used
    import logging
    logger = logging.getLogger(__name__)
    print(f'[DEBUG] Query being used for retrieval: "{query[:200]}"', flush=True)
    print(f'[DEBUG] Translation being used: "{translation[:200] if translation else "N/A"}"', flush=True)
    logger.info(f'[DEBUG] Query: "{query[:200]}"')
    logger.info(f'[DEBUG] Translation: "{translation[:200] if translation else "N/A"}"')
    
    # Use the custom filtered retriever
    # Note: query_embedding will be computed per-query in invoke() method
    retriever = FilteredRetriever(ids, k=8)
    search_kwargs = {'k': 8, 'filter': {'reference_document_id': {'$in': ids}}}

    # retriever = MultiQueryRetriever.from_llm(retriever, llm, include_original=False)

    history_messages = [
        HumanMessage(content=msg.text) if msg.role == 'user' else AIMessage(content=msg.text)
        for msg in state['history']
    ]

    languages = {
        'ar': "Arabic",
        'en': "English",
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", re.sub(r"\{language}", languages[user_message.language], template)),
        *history_messages,
        ("human", "{input}"),
    ])

    def format_docs(docs):
        logger.info(f'[DEBUG] format_docs called with {len(docs)} documents')
        if len(docs) == 0:
            logger.warning('[DEBUG] No documents retrieved! Context will be empty.')
        else:
            logger.info(f'[DEBUG] First doc preview: {docs[0].page_content[:200] if docs[0].page_content else "EMPTY"}...')
        return "\n\n".join(doc.page_content for doc in docs)

    with connection.cursor() as cursor:
        try:
            ef_search_value = 32
            # Set the desired ef_search value
            cursor.execute(f"SET LOCAL hnsw.ef_search = {ef_search_value};")
            # NOTE: We don't execute the search here, we just set the parameter.
            # The next query that uses the same connection will pick it up.

        except Exception as e:
            print(f"Error setting hnsw.ef_search: {e}")

    # Debug: Check if chunks exist in database
    
    try:
        # Check if chunks exist for these document IDs
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM langchain_pg_embedding 
                WHERE (cmetadata->>'reference_document_id')::bigint = ANY(%s)
            """, [ids])
            chunk_count = cursor.fetchone()[0]
            print(f'[DEBUG] Total chunks in DB for these {len(ids)} document IDs: {chunk_count}', flush=True)
            logger.info(f'[DEBUG] Total chunks in DB for these {len(ids)} document IDs: {chunk_count}')
            
            # Check each document ID individually
            for doc_id in ids[:3]:  # Check first 3
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM langchain_pg_embedding 
                    WHERE (cmetadata->>'reference_document_id')::bigint = %s
                """, [doc_id])
                count = cursor.fetchone()[0]
                print(f'[DEBUG] Document ID {doc_id} has {count} chunks', flush=True)
                logger.info(f'[DEBUG] Document ID {doc_id} has {count} chunks')
    except Exception as e:
        print(f'[DEBUG] Error checking chunks in DB: {e}', flush=True)
        logger.error(f'[DEBUG] Error checking chunks in DB: {e}')
    
    # Test the retriever
    try:
        test_docs = retriever.invoke(query)
        print(f'[DEBUG] Filtered retriever found {len(test_docs)} chunks for query: "{query[:100]}"', flush=True)
        logger.info(f'[DEBUG] Filtered retriever found {len(test_docs)} chunks for query: "{query[:100]}"')
        if len(test_docs) == 0:
            print(f'[DEBUG] No chunks found! Document IDs: {ids}', flush=True)
            logger.warning(f'[DEBUG] No chunks found! Document IDs: {ids}')
            logger.warning(f'[DEBUG] This means context will be empty even though {len(ids)} document IDs were found')
    except Exception as e:
        print(f'[DEBUG] Error testing retriever: {e}', flush=True)
        logger.error(f'[DEBUG] Error testing retriever: {e}')
    
    rag_chain = (
            RunnablePassthrough.assign(source_documents=RunnableLambda(
                lambda x: retriever.invoke(x['input']) + retriever.invoke(x['translated_input'])))
            | RunnablePassthrough.assign(context=lambda inputs: format_docs(inputs["source_documents"]))
            | RunnablePassthrough.assign(prompt=lambda inputs: prompt.format_messages(
        input=inputs["input"],
        context=inputs["context"]
    ))
            | RunnablePassthrough.assign(response=lambda inputs: llm.invoke(inputs["prompt"]))
    )

    response = rag_chain.invoke({
        'input': query,
        'translated_input': translation,
    })

    MessageLog.logs_objects.create(
        message=user_message,
        response=response,
    )
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='answer_legal_question',
        message=user_message,
        time_sec=t2 - t1,
        input={
            'input': query,
            'translated_input': translation,
            'filters': search_kwargs,
        },
        output={
            'rag_response': response,
        }
    )


    return {
        'rag_response': response,
    }


def extract_used_languages(state: State):
    t1 = time.time()
    
    response = state['rag_response']
    source_documents = response['source_documents']

    used_languages = set()
    for source_document in source_documents:
        d: Document = source_document
        used_languages.add(d.metadata['language'])


    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='extract_used_languages',
        message=state['message'],
        time_sec=t2 - t1,
        input={
            'response': response,
            'source_documents': source_documents,
        },
        output={
            'used_languages': used_languages,
        }
    )


    return {
        'used_languages': used_languages,
    }


def decode_response_json(state: State):
    t1 = time.time()
    response = state['rag_response']['response'].content

    if response.startswith('```json') and response.endswith('```'):
        response = response[7:-3].strip()
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        response = {
            'answer': response,
        }
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='decode_response_json',
        message=state['message'],
        time_sec=t2 - t1,
        input=None,
        output={
            'response': response,
        }
    )

    return {
        'response': response,
    }


def translate_previous_message(state: State):
    """Translate previous message"""
    history = state['history']
    
    t1 = time.time()

    llm = create_llm('gpt-5-nano', reasoning_effort="low")
    to_langs = {
        'ar': 'English',
        'en': 'Arabic',
    }

    previous_message: Message = history[-1]
    to_lang = to_langs[previous_message.language]

    result = llm.invoke([
        SystemMessage(
            f"Translate the user query to {to_lang} without adding any context or so, just translate as requested"),
        HumanMessage(
            previous_message.text
        ),
    ])

    t2 = time.time()

    MessageStepLog.objects.create(
        step_name="translate_previous_message",
        message=state['message'],
        time_sec=t2 - t1,
        input=None,
        output={
            'output': result.content,
        }
    )
    
    return {"output": result.content}


def store_translation_message(state: State):
    t1 = time.time()

    answer = state['output']
    user_message = state['message']
    answer_language = detect_language(answer)
    chat_id = user_message.chat_id

    system_message = Message.objects.create(
        chat_id=chat_id,
        parent=user_message,
        language=answer_language,
        text=answer,
        role='ai',
        uuid=uuid.uuid4(),
    )
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name="store_translation_message",
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'system_message_id': system_message.id,
        }
    )

    return {
        'system_message': system_message,
    }


def legal_question_flow(state: State):
    # Set query and input_translation directly from input (bypassing rephrase and translate)
    # This allows testing without rephrase/translation steps
    return {
        'query': state['input'],  # Use input directly as query (no rephrasing)
        'input_translation': state['input'],  # Use input directly as translation (no translation)
    }


def return_first_child(state: State):
    return {
        'system_message': state['message'].children.first(),
    }


def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node('first_or_create_message', first_or_create_message)
    graph_builder.add_node('retrieve_history', retrieve_history)
    graph_builder.add_node('router', router)
    graph_builder.add_node('legal_question_flow', legal_question_flow)
    graph_builder.add_node('translate_user_input', translate_user_input)
    graph_builder.add_node('translate_previous_message', translate_previous_message)
    graph_builder.add_node('store_translation_message', store_translation_message)
    graph_builder.add_node('rephrase_user_input', rephrase_user_input)
    graph_builder.add_node('answer_legal_question', answer_legal_question)
    graph_builder.add_node('extract_used_languages', extract_used_languages)
    graph_builder.add_node('decode_response_json', decode_response_json)
    graph_builder.add_node('calculate_disclaimer', calculate_disclaimer)
    graph_builder.add_node('store_system_message', store_system_message)
    graph_builder.add_node('has_answer', has_answer)
    graph_builder.add_node('return_first_child', return_first_child)

    graph_builder.add_edge(START, "first_or_create_message")
    graph_builder.add_edge('first_or_create_message', 'has_answer')

    graph_builder.add_conditional_edges(
        "has_answer",
        lambda state: state['decision'],
        {
            "yes": 'return_first_child',
            "no": 'retrieve_history',
        },
    )

    graph_builder.add_edge("retrieve_history", "router")

    graph_builder.add_conditional_edges(
        "router",
        lambda state: state['decision'],
        {
            "legal_question": 'legal_question_flow',
            "other": 'legal_question_flow',
            "translation": 'legal_question_flow',  # Route translation to legal_question_flow (bypassing translation)
            "translation": "translate_previous_message",  # Original translation flow (commented out)
        },
    )

    graph_builder.add_edge('legal_question_flow', 'translate_user_input')
    graph_builder.add_edge('legal_question_flow', 'rephrase_user_input')

    graph_builder.add_edge('translate_user_input', 'answer_legal_question')
    graph_builder.add_edge('rephrase_user_input', 'answer_legal_question')
    
    # Connect legal_question_flow directly to answer_legal_question (bypassing translate/rephrase)
    graph_builder.add_edge('legal_question_flow', 'answer_legal_question')

    graph_builder.add_edge('answer_legal_question', 'extract_used_languages')
    graph_builder.add_edge('answer_legal_question', 'decode_response_json')

    graph_builder.add_edge('extract_used_languages', 'calculate_disclaimer')
    graph_builder.add_edge('decode_response_json', 'calculate_disclaimer')

    graph_builder.add_edge('calculate_disclaimer', 'store_system_message')

    graph_builder.add_edge("store_system_message", END)

    graph_builder.add_edge("translate_previous_message", 'store_translation_message')
    graph_builder.add_edge("store_translation_message", END)

    return graph_builder.compile()
