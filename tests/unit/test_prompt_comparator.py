from app.core.parser import ParsedDocument, ParsedSection
from app.core.prompt_comparator import PromptComparator
from app.models.schemas import ExamConfig


def test_prompt_comparator_returns_report():
    document = ParsedDocument(
        title="Doc",
        sections=[
            ParsedSection(
                heading="Alpha",
                content="Alpha content about hypertension and diagnosis.",
                level=2,
                start_pos=0,
                end_pos=50,
            ),
            ParsedSection(
                heading="Beta",
                content="Beta content about treatment and management.",
                level=2,
                start_pos=51,
                end_pos=120,
            ),
        ],
        source_text="Alpha content about hypertension and diagnosis. "
                    "Beta content about treatment and management.",
    )

    comparator = PromptComparator()
    config = ExamConfig(
        total_questions=4,
        single_choice_ratio=0.5,
        multiple_choice_ratio=0.5,
        open_ended_ratio=0.0,
        provider="local",
    )

    report = comparator.compare_variants(
        document=document,
        config=config,
        variants=["default", "grounded"],
    )

    assert "variants" in report
    assert set(report["variants"].keys()) == {"default", "grounded"}
    for variant_report in report["variants"].values():
        assert "quality" in variant_report
        assert "grounding" in variant_report
