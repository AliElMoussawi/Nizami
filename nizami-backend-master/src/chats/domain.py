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


def translate_question(text: str, from_lang: str) -> str:
    translations = {
        'ar': 'English',
        'en': 'Arabic',
    }

    to_lang = translations.get(from_lang)
    if not to_lang:
        raise ValueError(f"Unsupported source language: {from_lang}")

    llm = create_llm('gpt-4o')

    system_prompt = f"""
        You are a professional translator working for a legal-tech platform.

        Your task:
        - Translate all user text into {to_lang}.
        - Always keep a **clear, precise, professional** tone.

        Style rules:
        - If the text is a legal question or contains legal content 
        (e.g. contracts, clauses, terms & conditions, policies, laws, regulations, legal opinions, disclaimers):
            - Use a **formal legal register** appropriate for {to_lang}.
            - Preserve:
            - Sentence structure and paragraphing
            - Numbering, bullet points, headings
            - Dates, amounts, article numbers, references to laws/codes/contracts
            - Defined terms (e.g. "Client", "Party", "Service Provider") consistently
        - If the text is not legal, translate it in a **neutral, professional** tone, not slangy or overly casual.

        General rules:
        - Do **not** summarize, simplify, or explain.
        - Do **not** add comments, notes, or extra sentences.
        - Do **not** change or omit information.
        - Decide whether the text is legal or not based only on the user content and apply the right style.
        - Return **only** the translated text, with no extra explanation.
        """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=text),
    ]

    response = llm.invoke(messages)
    return response.content.strip()


def find_ref_document_ids_by_description(text):
    embedded_text = embeddings.embed_query(text)

    files = (ReferenceDocument
             .objects
             .order_by(CosineDistance('description_embedding', embedded_text))
             .values('id')[:10])

    return list(map(lambda file: file['id'], files))
