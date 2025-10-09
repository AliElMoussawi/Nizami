from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate

from src.chats.utils import create_description_llm
from src.common.document_loaders import TextLoader
from src.prompts.enums import PromptType
from src.prompts.utils import get_prompt_value_by_name
from src.reference_documents.models import ReferenceDocument


def generate_description_for_text(text: str, language: str = 'ar'):
    languages = {
        'ar': "Arabic",
        'en': "English",
    }

    llm = create_description_llm()

    template = get_prompt_value_by_name(PromptType.GENERATE_DESCRIPTION)

    prompt = PromptTemplate(
        template=template,
        input_variables=[],
        partial_variables={
            'text': text,
            'language': languages[language]
        }
    )

    response = llm.invoke([
        SystemMessage(prompt.format()),
    ])

    return response.content


def generate_description_for_ref_doc(doc: ReferenceDocument):
    text_loader = TextLoader(doc.file.path)
    documents = text_loader.load()

    return generate_description_for_text('\n'.join(doc.page_content for doc in documents), doc.language)
