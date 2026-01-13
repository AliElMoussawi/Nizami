from langchain_core.messages import HumanMessage, SystemMessage
from pgvector.django import CosineDistance

from src.chats.utils import create_llm
from src.reference_documents.models import ReferenceDocument
from src.settings import embeddings


def create_initial_summary(messages: list) -> str:
    """
    Create an initial conversation summary from a list of messages.
    
    Args:
        messages: List of Message objects (user and AI messages)
        
    Returns:
        Summary string of the conversation
    """
    if not messages:
        return ""
    
    llm = create_llm('gpt-4o-mini', reasoning_effort="low")
    
    # Format messages for summarization
    conversation_text = ""
    for msg in messages:
        role = "User" if msg.role == 'user' else "Assistant"
        conversation_text += f"{role}: {msg.text}\n\n"
    
    prompt = f"""You are a Legal Conversation Summarizer AI.

Your task is to analyze the full transcript of a conversation between a User and a Legal Assistant and generate a structured, professional summary. Focus on clarity, legal relevance, and actionable insights.

Carefully extract and organize the following elements:

🧑‍⚖️ Main Legal Topics & Subtopics

Identify the primary legal domains (e.g., contracts, family law, IP) and any sub-issues raised.

📌 Key Facts & Context

Extract all relevant user-provided facts: names, dates, jurisdictions, legal terms, case types, timelines, or other case details.

💬 Conversation Flow

Outline the progression of the conversation in a clear step-by-step format:

User questions or issues raised

Assistant responses or clarifications

Any follow-up interactions or new concerns

📚 Legal Advice or Clarifications Given

Summarize the most important legal explanations, definitions, or guidance provided by the assistant.

❓ Unresolved Questions or Next Steps

Note anything the assistant could not answer, or any recommendations for follow-up, further action, or legal consultation.

⚖️ User Intent & Assistant Guidance Direction

Summarize the user's underlying goal (e.g., "understand custody rights") and how the assistant directed or reframed the issue.

✴️ Exclude small talk, confirmations, or repetition. Only summarize content that has legal or contextual significance.

Transcript to summarize:
{conversation_text}

Now generate the structured summary."""

    messages_list = [
        SystemMessage(content=prompt),
        HumanMessage(content="Please create the summary now."),
    ]
    
    response = llm.invoke(messages_list)
    return response.content.strip()


def update_conversation_summary(existing_summary: str, new_messages: list) -> str:
    """
    Update an existing conversation summary with new messages.
    This uses an incremental approach to maintain a comprehensive summary.
    
    Args:
        existing_summary: The current summary of the conversation
        new_messages: List of new Message objects to add to the summary
        
    Returns:
        Updated summary string
    """
    if not new_messages:
        return existing_summary
    
    llm = create_llm('gpt-4o-mini', reasoning_effort="low")
    
    # Format new messages
    new_conversation_text = ""
    for msg in new_messages:
        role = "User" if msg.role == 'user' else "Assistant"
        new_conversation_text += f"{role}: {msg.text}\n\n"
    
    if not existing_summary:
        # If no existing summary, create initial summary
        return create_initial_summary(new_messages)
    
    prompt = f"""You are a Legal Conversation Summarizer AI maintaining a structured summary of a legal consultation conversation.

You have an existing structured summary of the conversation so far, and new messages have been added.

Your task is to update the summary while maintaining the same structured format and ensuring all information is preserved and organized:

Main Legal Topics & Subtopics
- Preserve all existing topics
- Add any new legal domains or sub-issues from new messages

Key Facts & Context
- Keep all existing facts (names, dates, jurisdictions, legal terms, case types, timelines)
- Add any new relevant facts from the new messages

Conversation Flow
- Maintain the existing step-by-step progression
- Add new user questions, assistant responses, and follow-up interactions chronologically

Legal Advice or Clarifications Given
- Preserve all existing legal explanations and guidance
- Add new legal advice or clarifications from the new messages

Unresolved Questions or Next Steps
- Keep existing unresolved questions
- Add any new unresolved questions or updated recommendations

User Intent & Assistant Guidance Direction
- Update to reflect any evolution in user's underlying goal
- Note any new direction or reframing by the assistant

Exclude small talk, confirmations, or repetition. Only summarize content that has legal or contextual significance.

Guidelines for updating:
- Preserve ALL important information from the existing summary
- Integrate new information seamlessly
- Maintain the structured format
- Ensure chronological flow
- Remove redundancy if necessary
- The updated summary should be a complete, standalone summary of the entire conversation

Existing Summary:
{existing_summary}

New Messages:
{new_conversation_text}

Now generate the updated structured summary:"""

    messages_list = [
        SystemMessage(content=prompt),
        HumanMessage(content="Please update the summary now."),
    ]
    
    response = llm.invoke(messages_list)
    return response.content.strip()


def rephrase_user_input_using_summary(message: str, summary: str) -> str:
    """
    Rephrase user input by incorporating relevant context from conversation summary.
    
    Args:
        message: The user's current input message
        summary: The conversation summary
        
    Returns:
        Rephrased query with context incorporated
    """
    if not summary:
        return message
    
    llm = create_llm('gpt-5-nano', reasoning_effort="low")
    
    prompt = f"""You are an AI assistant that helps rephrase user input by incorporating relevant context provided in ##CONTEXT.
Given a user's input and a conversation summary in ##CONTEXT, identify the key themes and details from the ##CONTEXT that are relevant to the user's input. 
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
- The context is a comprehensive summary of the conversation so far.
- Not all parts of the context may be relevant to the current query.
- Score the relevance internally and use only the most relevant parts.
- Use only the relevant parts of the context.

##CONTEXT
{summary}
        """

    messages_list = [
        SystemMessage(content=prompt),
        HumanMessage(content=message),
    ]

    response = llm.invoke(messages_list)
    return response.content


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
