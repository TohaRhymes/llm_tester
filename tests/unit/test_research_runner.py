from app.core.parser import ParsedDocument, ParsedSection
from app.core.research_runner import ResearchRunner
from app.models.schemas import ExamConfig


def build_document():
    return ParsedDocument(
        title="Doc",
        sections=[
            ParsedSection(
                heading="One",
                content="Hypertension is elevated blood pressure.",
                level=2,
                start_pos=0,
                end_pos=50,
            ),
            ParsedSection(
                heading="Two",
                content="Treatment includes diet and exercise.",
                level=2,
                start_pos=51,
                end_pos=100,
            ),
        ],
        source_text="Hypertension is elevated blood pressure. "
                    "Treatment includes diet and exercise.",
    )


def test_research_runner_returns_variant_and_rag_results():
    document = build_document()
    config = ExamConfig(
        total_questions=3,
        single_choice_ratio=0.7,
        multiple_choice_ratio=0.3,
        open_ended_ratio=0.0,
        provider="local",
    )
    runner = ResearchRunner()

    report = runner.run(
        document=document,
        config=config,
        prompt_variants=["default"],
        rag_settings=[
            {"rag_enabled": False},
            {"rag_enabled": True, "rag_top_k": 1},
        ],
        student_count=8,
        seed=7,
    )

    assert "experiments" in report
    assert len(report["experiments"]) == 2
    summary = report["experiments"][0]["grading_summary"]
    assert "open_ended_mean" in summary
    assert "choice_mean" in summary
