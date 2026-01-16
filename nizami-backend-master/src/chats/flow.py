import json
import re
import time
import uuid
import logging


from django.db import connection, transaction
from django.db.models import Q
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict, Literal, Any


from src.chats.domain import (
    rephrase_user_input_using_history,
    rephrase_user_input_using_summary,
    find_ref_document_ids_by_description,
    translate_question,
    create_initial_summary,
    update_conversation_summary,
)
from src.chats.models import Message, MessageLog, MessageStepLog, Chat
from src.chats.utils import create_legal_advice_llm, detect_language, create_llm
from src.prompts.enums import PromptType
from src.prompts.utils import get_prompt_value_by_name
from src.common.retrievers import FilteredRetriever
from src.gibberish import GibberishConfig, classify_input, InputVerdict


def determine_response_language(user_input: str) -> str:
    """
    Determine the response language based on user input.
    
    Rules:
    - 100% English (no Arabic characters) → English
    - 100% Arabic (no English letters) → Arabic
    - Mixed (both Arabic and English) → Arabic
    
    Args:
        user_input: The user's input text
        
    Returns:
        'en' for English, 'ar' for Arabic
    """
    arabic_chars = sum(1 for char in user_input if '\u0600' <= char <= '\u06FF')
    english_chars = sum(1 for char in user_input if ('A' <= char <= 'Z') or ('a' <= char <= 'z'))
    
    # If there are any Arabic characters, respond in Arabic (handles 100% Arabic and mixed)
    if arabic_chars > 0:
        return "ar"
    # If only English characters (or no letters), respond in English
    elif english_chars > 0:
        return "en"
    # Default to Arabic if no letters detected
    else:
        return "ar"


class State(TypedDict):
    input: str
    query: str
    uuid: str
    input_translation: str
    message: Message
    chat_id: int
    history: list
    summary: str
    unsummarized_messages: list
    decision: str
    system_message: Message
    response: Any
    rag_response: Any
    used_languages: Any
    show_translation_disclaimer: str
    answer_language: str
    output: str
    is_gibberish: bool
    is_related_to_history: bool


# Schema for structured output to use as routing logic
class Route(BaseModel):
    step: Literal["legal_question", "translation", "other"] = Field(
        None, description="The next step in the routing process"
    )


# Schema for input relevance to chat history
class InputRelevance(BaseModel):
    is_related_to_history: bool = Field(
        description="True if the current input is related to or asking about topics already discussed in the chat history. False if it's a completely new question or topic."
    )


def router(state: State):
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        message = state.get('message')
        input_text = state.get('input')
        
        if message is None:
            logger.error("router: message is None in state")
            raise ValueError("Message is None in state")
        
        if input_text is None:
            logger.error("router: input is None in state")
            raise ValueError("Input is None in state")
        
        llm = create_llm('gpt-5-nano', reasoning_effort="minimal")
        router_llm = llm.with_structured_output(Route)
        template = get_prompt_value_by_name(PromptType.ROUTER)

        decision = router_llm.invoke([
            SystemMessage(content=template),
            HumanMessage(content=input_text),
        ])

        t2 = time.time()
        MessageStepLog.objects.create(
            step_name='router',
            message_id=message.id,
            time_sec=t2 - t1,
            input=None,
            output={
                'decision': decision.step,
            }
        )

        return {
            'decision': decision.step,
        }
    except Exception as e:
        logger.error(f"Error in router: {str(e)}", exc_info=True)
        t2 = time.time()
        message = state.get('message')
        if message:
            try:
                MessageStepLog.objects.create(
                    step_name='router',
                    message_id=message.id,
                    time_sec=t2 - t1,
                    input={'error': str(e)},
                    output={
                        'decision': 'legal_question',
                        'error': True,
                    }
                )
            except:
                pass
        # Default to legal_question to continue processing
        return {
            'decision': 'legal_question',
        }


def has_answer(state: State):
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        message = state.get('message')
        if message is None:
            logger.error("has_answer: message is None in state")
            raise ValueError("Message is None in state")
        
        child = message.children.first()
        decision = 'yes' if child is not None else 'no'
        
        t2 = time.time()
        MessageStepLog.objects.create(
            step_name='has_answer',
            message_id=message.id,
            time_sec=t2 - t1,
            input=None,
            output={
                'decision': decision,
                'has_child': child is not None,
            }
        )
        
        return {
            'decision': decision,
        }
    except Exception as e:
        logger.error(f"Error in has_answer: {str(e)}", exc_info=True)
        # Default to 'no' to continue processing
        return {
            'decision': 'no',
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
    logger = logging.getLogger(__name__)
    
    try:
        # Get the chat object to access summary
        chat_id = state.get('chat_id')
        message = state.get('message')
        
        if chat_id is None:
            logger.error("retrieve_history: chat_id is None in state")
            raise ValueError("chat_id is None in state")
        
        if message is None:
            logger.error("retrieve_history: message is None in state")
            raise ValueError("message is None in state")
        
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            logger.error(f"retrieve_history: Chat with id {chat_id} does not exist")
            raise
        
        # Get recent messages (last 5 for immediate context, summary handles the rest)
        recent_messages = list(
            reversed(
                Message.objects.filter(Q(chat_id=chat_id) & ~Q(id=message.id)).order_by('-created_at')[
                :5]))
        
        # Get or create summary
        summary = chat.summary
        summary_last_message_id = chat.summary_last_message_id
        
        # Get messages that might not be in summary yet (created after last summarized message)
        unsummarized_messages = []
        if summary_last_message_id:
            # Get messages created after the last summarized message
            unsummarized_messages = list(
                Message.objects.filter(
                    Q(chat_id=chat_id) & 
                    Q(id__gt=summary_last_message_id) & 
                    ~Q(id=message.id)
                ).order_by('created_at')
            )
        
        if not summary and recent_messages:
            # Create initial summary if it doesn't exist
            all_messages = list(
                Message.objects.filter(
                    Q(chat_id=chat_id) & 
                    ~Q(id=message.id) &
                    ~Q(text__isnull=True) &
                    ~Q(text='')
                ).order_by('created_at')
            )
            if all_messages:
                summary = create_initial_summary(all_messages)
                chat.summary = summary
                # Track the last message ID included in summary
                chat.summary_last_message_id = all_messages[-1].id
                chat.save(update_fields=['summary', 'summary_last_message_id'])
        
        t2 = time.time()
        MessageStepLog.objects.create(
            step_name='retrieve_history',
            message_id=message.id,
            time_sec=t2 - t1,
            input=None,
            output={
                'history_count': len(recent_messages),
                'has_summary': bool(summary),
                'summary_length': len(summary) if summary else 0,
                'unsummarized_count': len(unsummarized_messages),
            }
        )

        return {
            'history': recent_messages,
            'summary': summary or '',
            'unsummarized_messages': unsummarized_messages,  # Messages not yet in summary
        }
    except Exception as e:
        logger.error(f"Error in retrieve_history: {str(e)}", exc_info=True)
        # Return empty history to allow processing to continue
        return {
            'history': [],
            'summary': '',
            'unsummarized_messages': [],
        }


def rephrase_user_input(state: State):
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        user_message = state.get('message')
        if user_message is None:
            logger.error("rephrase_user_input: message is None in state")
            raise ValueError("Message is None in state")
        
        query = user_message.text or state.get('input', '')
        if not query:
            logger.warning("rephrase_user_input: query is empty, using input")
            query = state.get('input', '')
        
        summary = state.get('summary', '')

        # Use summary for rephrasing if available, otherwise fall back to history
        if summary:
            query = rephrase_user_input_using_summary(query, summary)
            user_message.used_query = query
            user_message.save()
        else:
            # Fallback to old method if no summary exists
            history = state.get('history', [])
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
                'used_summary': bool(summary),
            }
        )

        return {
            'query': query,
        }
    except Exception as e:
        logger.error(f"Error in rephrase_user_input: {str(e)}", exc_info=True)
        t2 = time.time()
        user_message = state.get('message')
        # Use original input as fallback
        fallback_query = state.get('input', state.get('query', ''))
        
        if user_message:
            try:
                MessageStepLog.objects.create(
                    step_name='rephrase_user_input',
                    message=user_message,
                    time_sec=t2 - t1,
                    input={'error': str(e)},
                    output={
                        'query': fallback_query,
                        'used_summary': False,
                        'error': True,
                    }
                )
            except:
                pass
        
        return {
            'query': fallback_query,
        }


def translate_user_input(state: State):
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        user_message = state.get('message')
        if user_message is None:
            logger.error("translate_user_input: message is None in state")
            raise ValueError("Message is None in state")
        
        if not user_message.text:
            logger.warning("translate_user_input: message text is empty")
            # Return empty translation if no text
            t2 = time.time()
            MessageStepLog.objects.create(
                step_name='translate_user_input',
                message=user_message,
                time_sec=t2 - t1,
                input=None,
                output={
                    'input_translation': '',
                }
            )
            return {
                'input_translation': '',
            }
        
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
    except Exception as e:
        logger.error(f"Error in translate_user_input: {str(e)}", exc_info=True)
        t2 = time.time()
        user_message = state.get('message')
        
        if user_message:
            try:
                MessageStepLog.objects.create(
                    step_name='translate_user_input',
                    message=user_message,
                    time_sec=t2 - t1,
                    input={'error': str(e)},
                    output={
                        'input_translation': '',
                        'error': True,
                    }
                )
            except:
                pass
        
        # Return empty translation as fallback
        return {
            'input_translation': '',
        }


def calculate_disclaimer(state: State):
    t1 = time.time()

    response = state['response']
    used_languages = state['used_languages']
    user_message = state['message']
    question_language = user_message.language

    is_context_used = response.get('is_context_used', False)
    is_answer = response.get('is_answer', False)

    # Determine response language based on user's input (not detected from answer)
    # Rules: 100% English → English, 100% Arabic → Arabic, Mixed → Arabic
    answer_language = determine_response_language(user_message.text)

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


@transaction.atomic
def _update_chat_summary_sync(chat_id: int, message_ids: list):
    """
    Synchronous function to update chat summary (called in background).
    Updates summary and tracks the last message ID included.
    Uses database locking to prevent race conditions.
    
    Args:
        chat_id: The chat ID
        message_ids: List of message IDs to add to summary
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not message_ids:
            return
        
        # Use select_for_update to lock the row and prevent concurrent updates
        chat = Chat.objects.select_for_update().get(id=chat_id)
        existing_summary = chat.summary or ""
        
        # Ensure we're not processing messages already in summary
        if chat.summary_last_message_id:
            message_ids = [mid for mid in message_ids if mid > chat.summary_last_message_id]
        
        if not message_ids:
            logger.debug(f"No new messages to add to summary for chat {chat_id}")
            return
        
        # Get messages
        new_messages = list(Message.objects.filter(id__in=message_ids).order_by('created_at'))
        if not new_messages:
            return
        
        # Update summary with new messages
        updated_summary = update_conversation_summary(existing_summary, new_messages)
        chat.summary = updated_summary
        # Track the last message ID included in summary (the most recent one)
        chat.summary_last_message_id = max(message_ids)
        chat.save(update_fields=['summary', 'summary_last_message_id'])
        
        logger.info(f"Summary updated for chat {chat_id} with {len(new_messages)} messages (last message ID: {chat.summary_last_message_id})")
    except Exception as e:
        logger.error(f"Error updating summary for chat {chat_id}: {str(e)}", exc_info=True)


def update_chat_summary(chat_id: int, new_messages: list):
    """
    Update the chat summary with new messages synchronously.
    
    Args:
        chat_id: The chat ID
        new_messages: List of new Message objects to add to summary
    """
    if not new_messages:
        return
    
    # Extract message IDs for processing
    message_ids = [msg.id for msg in new_messages]
    
    # Update summary synchronously
    _update_chat_summary_sync(chat_id, message_ids)


def store_system_message(state: State):
    t1 = time.time()
    
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
    
    update_chat_summary(chat_id, [user_message, system_message])
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='store_system_message',
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'system_message_id': system_message.id,
            'summary_updated': True,
        }
    )

    return {
        'system_message': system_message,
    }


def answer_legal_question(state: State):
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    user_message = state['message']
    translation = state['input_translation']
    query = state['query']

    ids = find_ref_document_ids_by_description(query)

    llm = create_legal_advice_llm()
    template = get_prompt_value_by_name(PromptType.LEGAL_ADVICE)

    retriever = FilteredRetriever(ids, k=8, logger=logger)
    search_kwargs = {'k': 8, 'filter': {'reference_document_id': {'$in': ids}}}

    # Use summary for context, with recent messages for immediate context
    summary = state.get('summary', '')
    history = state.get('history', [])
    unsummarized_messages = state.get('unsummarized_messages', [])
    
    # Build history messages from summary and recent messages
    history_messages = []
    if summary:
        # Add summary as context
        history_messages.append(SystemMessage(
            content=f"Conversation Summary (for context):\n{summary}"
        ))
    
    # Add messages that aren't in summary yet (from async update race condition)
    # These are messages created after the last summarized message
    for msg in unsummarized_messages:
        if msg.role == 'user':
            history_messages.append(HumanMessage(content=msg.text))
        elif msg.role == 'ai':
            history_messages.append(AIMessage(content=msg.text))
    
    # Add recent messages (last 3 for immediate context)
    recent_messages = history[-3:] if len(history) > 3 else history
    for msg in recent_messages:
        if msg.role == 'user':
            history_messages.append(HumanMessage(content=msg.text))
        elif msg.role == 'ai':
            history_messages.append(AIMessage(content=msg.text))

    # Determine the response language based on user's input
    response_language = determine_response_language(user_message.text)
    
    languages = {
        'ar': "Arabic",
        'en': "English",
    }
    
    # Update the template to explicitly instruct the LLM to respond in the determined language
    language_instruction = f"IMPORTANT: You must respond ONLY in {languages[response_language]}. Do not mix languages. "
    updated_template = language_instruction + template

    prompt = ChatPromptTemplate.from_messages([
        ("system", re.sub(r"\{language}", languages[response_language], updated_template)),
        *history_messages,
        ("human", "{input}"),
    ])

    def format_docs(docs):
        if len(docs) == 0:
            logger.warning('No documents retrieved! Context will be empty.')
        return "\n\n".join(doc.page_content for doc in docs)

    with connection.cursor() as cursor:
        try:
            cursor.execute("SET LOCAL hnsw.ef_search = 32;")
        except Exception as e:
            logger.error(f"Error setting hnsw.ef_search: {e}")
    
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
    
    update_chat_summary(chat_id, [user_message, system_message])
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name="store_translation_message",
        message=user_message,
        time_sec=t2 - t1,
        input=None,
        output={
            'system_message_id': system_message.id,
            'summary_updated': True,
        }
    )

    return {
        'system_message': system_message,
    }


def legal_question_flow(state: State):
    return state


def return_first_child(state: State):
    return {
        'system_message': state['message'].children.first(),
    }


def validate_input_quality(state: State):
    """Check if the user input is random characters or gibberish using deterministic detection"""
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        message = state.get('message')
        input_text = state.get('input')
        
        if message is None:
            logger.error("validate_input_quality: message is None in state")
            raise ValueError("Message is None in state")
        
        if input_text is None:
            logger.error("validate_input_quality: input is None in state")
            raise ValueError("Input is None in state")
        
        gibberishConfig = GibberishConfig()
        gibberishConfig.llm_enabled = True
        # Use our deterministic gibberish detection system
        result = classify_input(input_text, config=gibberishConfig)
        
        # Classify as gibberish if status is GIBBERISH
        is_gibberish = (result.status == InputVerdict.GIBBERISH)
        
        t2 = time.time()
        MessageStepLog.objects.create(
            step_name='validate_input_quality',
            message_id=message.id,
            time_sec=t2 - t1,
            input={
                'input': input_text,
            },
            output={
                'is_gibberish': is_gibberish,
                'classification_status': result.status.value,
                'score': result.score,
                'reasons': result.reasons[:3] if result.reasons else [],  # Store first 3 reasons
            }
        )
        
        return {
            'is_gibberish': is_gibberish,
        }
    except Exception as e:
        logger.error(f"Error in validate_input_quality: {str(e)}", exc_info=True)
        # Default to not gibberish to allow processing to continue
        return {
            'is_gibberish': False,
        }


def handle_gibberish_input(state: State):
    """Handle gibberish input by returning a message in the appropriate language"""
    t1 = time.time()
    
    user_message = state['message']
    chat_id = user_message.chat_id
    
    # Detect if input is purely English (no Arabic characters)
    input_text = state['input']
    has_arabic = any('\u0600' <= char <= '\u06FF' for char in input_text)
    
    if not has_arabic:
        # Pure English input - return English only
        response_message = "I couldn't understand your message. Could you please rephrase it? I'm here to help with legal inquiries."
        answer_language = "en"
    else:
        # Arabic or mixed input - return bilingual message
        response_message = """I couldn't understand your message. Could you please rephrase it? I'm here to help with legal inquiries.

لم أتمكن من فهم رسالتك. هل يمكنك إعادة صياغتها؟ أنا هنا للمساعدة في الاستفسارات القانونية."""
        answer_language = detect_language(response_message)
    
    system_message = Message.objects.create(
        chat_id=chat_id,
        parent=user_message,
        language=answer_language,
        text=response_message,
        role='ai',
        uuid=uuid.uuid4(),
    )
    
    update_chat_summary(chat_id, [user_message, system_message])
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='handle_gibberish_input',
        message=user_message,
        time_sec=t2 - t1,
        input={
            'input': state['input'],
        },
        output={
            'system_message_id': system_message.id,
            'response_language': answer_language,
            'summary_updated': True,
        }
    )
    
    return {
        'system_message': system_message,
    }


def check_input_relevance(state: State):
    """Check if the current input is related to the chat history"""
    t1 = time.time()
    logger = logging.getLogger(__name__)
    
    try:
        message = state.get('message')
        input_text = state.get('input')
        
        if message is None:
            logger.error("check_input_relevance: message is None in state")
            raise ValueError("Message is None in state")
        
        if input_text is None:
            logger.error("check_input_relevance: input is None in state")
            raise ValueError("Input is None in state")
        
        summary = state.get('summary', '')
        history = state.get('history', [])
        unsummarized_messages = state.get('unsummarized_messages', [])
        
        # If no summary and no history, it's definitely a new question
        if not summary and (not history or len(history) == 0) and not unsummarized_messages:
            t2 = time.time()
            MessageStepLog.objects.create(
                step_name='check_input_relevance',
                message_id=message.id,
                time_sec=t2 - t1,
                input={
                    'input': input_text,
                    'history_count': 0,
                },
                output={
                    'is_related_to_history': False,
                    'reason': 'no_history',
                }
            )
            return {
                'is_related_to_history': False,
            }
        
        llm = create_llm('gpt-5-nano', reasoning_effort="minimal")
        relevance_llm = llm.with_structured_output(InputRelevance)
        
        # Build conversation context from summary and recent messages
        history_context = ""
        last_ai_message = None
        
        if summary:
            # Use summary as primary context
            history_context = f"\n\nConversation Summary:\n{summary}"
        
        # Add messages that aren't in summary yet (from async update race condition)
        if unsummarized_messages:
            unsummarized_context = "\n\nRecent Messages (not yet in summary):\n"
            for msg in unsummarized_messages:
                role = "User" if msg.role == 'user' else "Assistant"
                unsummarized_context += f"{role}: {msg.text}\n"
            history_context += unsummarized_context
        
        # Add recent messages for immediate context (last 3 messages)
        recent_messages = history[-3:] if len(history) > 3 else history
        if recent_messages:
            recent_context = "\n\nMost Recent Messages:\n"
            for msg in recent_messages:
                role = "User" if msg.role == 'user' else "Assistant"
                recent_context += f"{role}: {msg.text}\n"
            history_context += recent_context
        
        # Find the most recent AI message
        for msg in reversed(recent_messages if recent_messages else history):
            if msg.role == 'ai':
                last_ai_message = msg.text
                break
        
        # Highlight the last AI message if it exists
        last_ai_context = ""
        if last_ai_message:
            last_ai_context = f"\n\nIMPORTANT: The Assistant's last message was:\n{last_ai_message}\n\nIf the user is answering this question (e.g., 'yes', 'no', 'ok', 'sure', etc.), it is RELATED."
        
        prompt = f"""You are analyzing whether the current user input is related to the previous conversation history.

Determine if the current input is:
- RELATED to the chat history: The user is asking about, referring to, or continuing a topic already discussed in the conversation, OR answering a question that the Assistant asked
- NOT RELATED to the chat history: The user is asking a completely new question about a different topic that is unrelated to the conversation

Examples of RELATED (return True):
- User answers "yes" or "no" to a question the Assistant asked
- User responds with short answers like "ok", "sure", "correct", "that's right" to the Assistant's question
- User asks "Can you tell me more about that?" after discussing contracts
- User asks "What about the second point?" referring to a previous answer
- User asks "How does this apply to my case?" after discussing a legal concept
- User asks follow-up questions about the same topic
- User asks for clarification on something mentioned earlier
- User provides additional information related to a previous discussion
- User confirms or denies something the Assistant mentioned

Examples of NOT RELATED (return False):
- User asks "What is a contract?" when previous conversation was about employment law (completely different topic)
- User asks a completely new legal question on a different topic
- User starts a new conversation thread on an unrelated subject
- User asks about something that has no connection to the conversation history

Current user input to check:
{input_text}
{history_context}{last_ai_context}
"""
        
        decision = relevance_llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=input_text),
        ])
        
        t2 = time.time()
        MessageStepLog.objects.create(
            step_name='check_input_relevance',
            message_id=message.id,
            time_sec=t2 - t1,
            input={
                'input': input_text,
                'history_count': len(history),
                'has_summary': bool(summary),
            },
            output={
                'is_related_to_history': decision.is_related_to_history,
            }
        )
        
        return {
            'is_related_to_history': decision.is_related_to_history,
        }
    except Exception as e:
        logger.error(f"Error in check_input_relevance: {str(e)}", exc_info=True)
        # Default to not related to allow processing to continue
        t2 = time.time()
        message = state.get('message')
        input_text = state.get('input', '')
        if message:
            try:
                MessageStepLog.objects.create(
                    step_name='check_input_relevance',
                    message_id=message.id,
                    time_sec=t2 - t1,
                    input={
                        'input': input_text,
                        'error': str(e),
                    },
                    output={
                        'is_related_to_history': False,
                        'error': True,
                    }
                )
            except:
                pass
        return {
            'is_related_to_history': False,
        }


def handle_related_input(state: State):
    """Handle input that is related to chat history - ask user to be more specific"""
    t1 = time.time()
    
    user_message = state['message']
    chat_id = user_message.chat_id
    question_language = user_message.language
    
    # Bilingual response message
    if question_language == 'ar':
        bilingual_message = """يرجى أن تكون أكثر تحديداً في سؤالك. يرجى إعادة صياغة سؤالك بشكل أوضح وأكثر تفصيلاً.

Please be more specific in your question. Please rephrase your question more clearly and in more detail."""
    else:
        bilingual_message = """Please be more specific in your question. Please rephrase your question more clearly and in more detail.

يرجى أن تكون أكثر تحديداً في سؤالك. يرجى إعادة صياغة سؤالك بشكل أوضح وأكثر تفصيلاً."""
    
    # Detect language for the response
    answer_language = detect_language(bilingual_message)
    
    system_message = Message.objects.create(
        chat_id=chat_id,
        parent=user_message,
        language=answer_language,
        text=bilingual_message,
        role='ai',
        uuid=uuid.uuid4(),
    )
    
    update_chat_summary(chat_id, [user_message, system_message])
    
    t2 = time.time()
    MessageStepLog.objects.create(
        step_name='handle_related_input',
        message=user_message,
        time_sec=t2 - t1,
        input={
            'input': state['input'],
        },
        output={
            'system_message_id': system_message.id,
            'summary_updated': True,
        }
    )
    
    return {
        'system_message': system_message,
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
    graph_builder.add_node('validate_input_quality', validate_input_quality)
    graph_builder.add_node('handle_gibberish_input', handle_gibberish_input)
    graph_builder.add_node('check_input_relevance', check_input_relevance)
    graph_builder.add_node('handle_related_input', handle_related_input)

    graph_builder.add_edge(START, "first_or_create_message")
    graph_builder.add_edge('first_or_create_message', 'validate_input_quality')
    
    graph_builder.add_conditional_edges(
        "validate_input_quality",
        lambda state: "gibberish" if state.get('is_gibberish', False) else "valid",
        {
            "gibberish": 'handle_gibberish_input',
            "valid": 'has_answer',
        },
    )
    
    graph_builder.add_edge("handle_gibberish_input", END)

    graph_builder.add_conditional_edges(
        "has_answer",
        lambda state: state['decision'],
        {
            "yes": 'return_first_child',
            "no": 'retrieve_history',
        },
    )

    graph_builder.add_edge("retrieve_history", "check_input_relevance")
    
    graph_builder.add_conditional_edges(
        "check_input_relevance",
        lambda state: "related" if state.get('is_related_to_history', False) else "new_question",
        {
            "related": 'handle_related_input',
            "new_question": 'router',
        },
    )
    
    graph_builder.add_edge("handle_related_input", END)

    graph_builder.add_conditional_edges(
        "router",
        lambda state: state['decision'],
        {
            "legal_question": 'legal_question_flow',
            "other": 'legal_question_flow',
            "translation": "translate_previous_message",
        },
    )

    graph_builder.add_edge('legal_question_flow', 'translate_user_input')
    graph_builder.add_edge('legal_question_flow', 'rephrase_user_input')

    graph_builder.add_edge('translate_user_input', 'answer_legal_question')
    graph_builder.add_edge('rephrase_user_input', 'answer_legal_question')
    
    graph_builder.add_edge('answer_legal_question', 'extract_used_languages')
    graph_builder.add_edge('answer_legal_question', 'decode_response_json')

    graph_builder.add_edge('extract_used_languages', 'calculate_disclaimer')
    graph_builder.add_edge('decode_response_json', 'calculate_disclaimer')

    graph_builder.add_edge('calculate_disclaimer', 'store_system_message')

    graph_builder.add_edge("store_system_message", END)

    graph_builder.add_edge("translate_previous_message", 'store_translation_message')
    graph_builder.add_edge("store_translation_message", END)

    return graph_builder.compile()
