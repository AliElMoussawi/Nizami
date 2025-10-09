from src.prompts.enums import PromptType
from src.prompts.models import Prompt


def get_prompt_value_by_name(name: PromptType) -> str:
    return Prompt.objects.get(name=name.value).value
