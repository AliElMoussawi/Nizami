import json
import re
import uuid

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
from src.chats.models import Message, MessageLog
from src.chats.utils import create_legal_advice_llm, detect_language
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
    llm = create_legal_advice_llm()

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

    return {
        'decision': decision.step,
    }


def has_answer(state: State):
    child = state['message'].children.first()
    return {
        'decision': 'yes' if child is not None else 'no',
    }


def first_or_create_message(state: State):
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

    return {
        'message': user_message,
    }


def retrieve_history(state: State):
    history = list(
        reversed(
            Message.objects.filter(Q(chat_id=state['chat_id']) & ~Q(id=state['message'].id)).order_by('-created_at')[
            :10]))

    return {
        'history': history,
    }


def rephrase_user_input(state: State):
    user_message = state['message']

    query = state['message'].text
    history = state['history']

    if len(history) > 0:
        used_queries = list(filter(None, [msg.used_query if msg.role != 'ai' else None for msg in history]))
        if len(used_queries) > 0:
            query = rephrase_user_input_using_history(query, used_queries)
            user_message.used_query = query
            user_message.save()

    return {
        'query': query,
    }


def translate_user_input(state: State):
    user_message = state['message']

    input_translation = translate_question(user_message.text, user_message.language)

    return {
        'input_translation': input_translation,
    }


def calculate_disclaimer(state: State):
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
    user_message = state['message']
    translation = state['input_translation']
    query = state['query']

    ids = find_ref_document_ids_by_description(query)

    llm = create_legal_advice_llm()
    template = get_prompt_value_by_name(PromptType.LEGAL_ADVICE)

    search_kwargs = {
        'k': 20,
        'fetch_k': 50,
        "filter": {
            "reference_document_id": {
                "$in": ids,
            },
        },
    }

    retriever = vectorstore.as_retriever(
        search_kwargs=search_kwargs,
    )

    retriever = MultiQueryRetriever.from_llm(retriever, llm, include_original=False)

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
        return "\n\n".join(doc.page_content for doc in docs)

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

    return {
        'rag_response': response,
    }


def extract_used_languages(state: State):
    response = state['rag_response']
    source_documents = response['source_documents']

    used_languages = set()
    for source_document in source_documents:
        d: Document = source_document
        used_languages.add(d.metadata['language'])

    return {
        'used_languages': used_languages,
    }


def decode_response_json(state: State):
    response = state['rag_response']['response'].content

    if response.startswith('```json') and response.endswith('```'):
        response = response[7:-3].strip()
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        response = {
            'answer': response,
        }

    return {
        'response': response,
    }


def translate_previous_message(state: State):
    """Translate previous message"""
    history = state['history']

    llm = create_legal_advice_llm()
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
    return {"output": result.content}


def store_translation_message(state: State):
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

    return {
        'system_message': system_message,
    }


def legal_question_flow(state: State):
    return state


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
