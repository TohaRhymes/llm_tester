"""
Prompt template registry for generation variants.
"""
from __future__ import annotations

from app.prompts import prompts_en, prompts_ru


_GROUNDING_HINTS = {
    "en": "\n\nGrounding requirements:\n- Use exact terms from the provided content\n- Avoid introducing facts not present in the content\n- Keep the question tightly anchored to specific sentences\n",
    "ru": "\n\nТребования к привязке:\n- Используйте точные термины из предоставленного контента\n- Не добавляйте факты, отсутствующие в контенте\n- Привязывайте вопрос к конкретным формулировкам\n",
}


def get_prompt_template(language: str, question_type: str, variant: str) -> str:
    """
    Return a prompt template for the given variant.
    """
    prompts_module = prompts_ru if language == "ru" else prompts_en
    if question_type == "open_ended":
        base = prompts_module.OPEN_ENDED_PROMPT_RU if language == "ru" else prompts_module.OPEN_ENDED_PROMPT_EN
    else:
        base = prompts_module.CHOICE_QUESTION_PROMPT_RU if language == "ru" else prompts_module.CHOICE_QUESTION_PROMPT_EN

    if variant == "grounded":
        return base + _GROUNDING_HINTS["ru" if language == "ru" else "en"]

    return base
