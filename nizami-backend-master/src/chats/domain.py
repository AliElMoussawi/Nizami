from langchain_core.messages import HumanMessage, SystemMessage
from pgvector.django import CosineDistance

from src.chats.utils import create_llm
from src.reference_documents.models import ReferenceDocument
from src.settings import embeddings


def rephrase_user_input_using_history(message, old_messages):
    llm = create_llm('gpt-5-nano', reasoning_effort="low")

    message = message
    context = '\n'.join(filter(None, old_messages))

    prompt = f"""
You are an AI assistant that helps rephrase user input by incorporating relevant context provided in ##CONTEXT.
Given a user’s input and a list of ##CONTEXT sentences, identify the key themes and details from the ##CONTEXT that are relevant to the user’s input. 
Then, rephrase the user's input to include the most important parts of the ##CONTEXT while maintaining natural flow and clarity.

Instructions for output:
- Don't answer the user's query.
- Rephrase the user's query to include important parts of the context.
- If the context is not related to the user query, say the user query as is, don't make up answers.
- Use the context only if the user's query is vague, ambiguous, or lacks context and to rephrase the user query while maintaining the original structure and context of the query.
- If the user's query is clear, self-explanatory, and does not require further clarification, respond with the user's query without modifications.
- If the user is asking about more details or information but without specifying topic, the context must be used to rephrase the user's query and include topic.
- Don't answer by asking new questions but rephrase the user's query while maintaining the sentence structure (the question must remain question but rephrased).
- Don't change the jurisdiction of the user's query.

Context Instructions:
- The sentences are ordered by time i.e. the most relevant are first.
- Not all sentences are relevant.
- Score the sentences internally based on the relevance to the current query first then use most relevant parts.
- Use only the relevant parts of the context.

##CONTEXT
{context}
        """

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=message),
    ]

    response = llm.invoke(messages)

    return response.content


def translate_question(text, from_lang):
    translations = {
        'ar': 'English',
        'en': 'Arabic',
    }

    to_lang = translations[from_lang]
    llm = create_llm('gpt-5-nano', reasoning_effort="minimal")
    prompt = f"""
    You are a professional translator. Translate the following text provided by the user into {to_lang}, maintaining the original meaning, tone, and context. If the sentence contains idioms, cultural references, or technical terms, translate them appropriately for native speakers of the target language. Provide only the translation.
    
    {text}
    """

    messages = [
        SystemMessage(content=prompt),
    ]
    response = llm.invoke(messages)

    return response.content


def find_ref_document_ids_by_description(text):
    embedded_text = embeddings.embed_query(text)

    files = (ReferenceDocument
             .objects
             .order_by(CosineDistance('description_embedding', embedded_text))
             .values('id')[:10])

    return list(map(lambda file: file['id'], files))
