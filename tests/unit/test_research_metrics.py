from app.core.parser import ParsedDocument, ParsedSection
from app.core.research_metrics import compute_generation_metrics, compute_ragas_metrics
from app.core.generator import QuestionGenerator
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
            )
        ],
        source_text="Hypertension is elevated blood pressure.",
    )


def test_compute_generation_metrics_returns_expected_keys():
    document = build_document()
    config = ExamConfig(
        total_questions=2,
        single_choice_ratio=0.5,
        multiple_choice_ratio=0.5,
        open_ended_ratio=0.0,
        provider="local",
    )
    exam = QuestionGenerator().generate(document, config, "metrics")

    metrics = compute_generation_metrics(exam, document)
    assert "quality" in metrics
    assert "grounding" in metrics
    assert "counts" in metrics


def test_compute_ragas_metrics_disabled_without_dependency():
    metrics = compute_ragas_metrics([])
    assert metrics["enabled"] is False
