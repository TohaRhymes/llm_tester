from app.prompts import prompts_en, prompts_ru


def test_prompt_variant_falls_back_to_default():
    assert prompts_en.get_choice_prompt_en("unknown") == prompts_en.CHOICE_PROMPT_VARIANTS_EN["default"]
    assert prompts_en.get_open_ended_prompt_en("unknown") == prompts_en.OPEN_ENDED_PROMPT_VARIANTS_EN["default"]
    assert prompts_ru.get_choice_prompt_ru("unknown") == prompts_ru.CHOICE_PROMPT_VARIANTS_RU["default"]
    assert prompts_ru.get_open_ended_prompt_ru("unknown") == prompts_ru.OPEN_ENDED_PROMPT_VARIANTS_RU["default"]
