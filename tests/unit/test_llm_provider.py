import pytest

from app.models.schemas import ExamConfig, Exam, Question, QuestionMeta, SourceReference
from app.services.llm_provider import get_llm_client, LocalLLMClient
from app.core.generator import QuestionGenerator
from app.core.grader import Grader
from app.utils.path import safe_join
from app.core.parser import ParsedDocument, ParsedSection
from app.models.schemas import StudentAnswer, GradeRequest


def make_sample_doc():
    sections = [
        ParsedSection(
            heading="Section A",
            content="Alpha beta gamma.",
            level=2,
            start_pos=0,
            end_pos=20,
        )
    ]
    return ParsedDocument(title="Doc", sections=sections, source_text="Alpha beta gamma.")


def make_open_question():
    return Question(
        id="q-001",
        type="open_ended",
        stem="Explain the key fact?",
        options=None,
        correct=None,
        reference_answer="Alpha fact",
        rubric=["Mentions alpha", "Is concise"],
        source_refs=[SourceReference(file="Doc", heading="Section A", start=0, end=10)],
        meta=QuestionMeta(),
    )


def test_safe_join_blocks_traversal(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    with pytest.raises(ValueError):
        safe_join(base, "../secrets.txt")


def test_safe_join_returns_child(tmp_path):
    base = tmp_path / "uploads"
    base.mkdir()
    result = safe_join(base, "file.md")
    assert result == base / "file.md"


def test_llm_factory_returns_stub_when_local():
    client = get_llm_client(provider="local")
    assert isinstance(client, LocalLLMClient)
    q = client.generate_question("content", question_type="single_choice")
    assert "stem" in q and "options" in q and "correct" in q


def test_generator_respects_count_mode_with_local_stub(monkeypatch):
    # Force stub provider to avoid network
    gen = QuestionGenerator(provider="local")
    doc = make_sample_doc()
    config = ExamConfig(
        single_choice_count=2,
        multiple_choice_count=1,
        open_ended_count=1,
        language="en",
        provider="local",
    )

    exam = gen.generate(doc, config, exam_id="ex-123")

    types = [q.type for q in exam.questions]
    assert types.count("single_choice") == 2
    assert types.count("multiple_choice") == 1
    assert types.count("open_ended") == 1


def test_grader_uses_provider_from_exam_config(monkeypatch):
    # Use local stub for grading open-ended
    grader = Grader(provider="local")
    question = make_open_question()
    exam = Exam(
        exam_id="ex-1",
        questions=[question],
        config_used=ExamConfig(
            open_ended_count=1,
            single_choice_count=0,
            multiple_choice_count=0,
            provider="local",
        ),
    )

    request = GradeRequest(
        exam_id="ex-1",
        answers=[StudentAnswer(question_id="q-001", text_answer="Alpha fact is stated")]
    )

    result = grader.grade(exam, request)
    assert result.summary.total == 1
    assert result.summary.correct == 1
    assert result.per_question[0].partial_credit == 1.0
