import pytest

from app.prompts import prompts_en
from app.prompts.registry import get_prompt_template


def test_default_variant_returns_base_template():
    template = get_prompt_template(
        language="en",
        question_type="single_choice",
        variant="default",
    )
    assert prompts_en.CHOICE_QUESTION_PROMPT_EN.strip() in template


def test_grounded_variant_adds_grounding_instruction():
    template = get_prompt_template(
        language="en",
        question_type="open_ended",
        variant="grounded",
    )
    assert "Grounding" in template or "grounded" in template.lower()
