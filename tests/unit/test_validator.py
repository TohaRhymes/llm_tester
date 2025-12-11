import pytest

from app.core.validator import QuestionValidator
from app.models.schemas import Exam, ExamConfig, Question, QuestionMeta, SourceReference
from app.core.parser import ParsedDocument, ParsedSection


def make_doc():
    section = ParsedSection(
        heading="Topic",
        content="Important fact about alpha beta.",
        level=2,
        start_pos=0,
        end_pos=50,
    )
    return ParsedDocument(title="Doc", sections=[section], source_text=section.content)


def make_choice_question(stem="What is alpha?", qid="q-001"):
    return Question(
        id=qid,
        type="single_choice",
        stem=stem,
        options=["A", "B", "C"],
        correct=[0],
        reference_answer=None,
        rubric=["Select alpha"],
        source_refs=[SourceReference(file="Doc", heading="Topic", start=0, end=10)],
        meta=QuestionMeta(),
    )


def make_open_question(qid="q-002"):
    return Question(
        id=qid,
        type="open_ended",
        stem="Explain beta?",
        options=None,
        correct=None,
        reference_answer="Beta is explained.",
        rubric=["Mentions beta", "Is concise"],
        source_refs=[SourceReference(file="Doc", heading="Topic", start=0, end=20)],
        meta=QuestionMeta(),
    )


def test_validator_accepts_well_formed_exam():
    validator = QuestionValidator()
    exam = Exam(
        exam_id="ex-1",
        questions=[make_choice_question(), make_open_question()],
        config_used=ExamConfig(total_questions=2),
    )
    doc = make_doc()

    result = validator.validate_exam(exam, doc)
    assert result.valid
    assert result.issues == []


def test_validator_detects_duplicate_stems():
    validator = QuestionValidator()
    q1 = make_choice_question(stem="Same?", qid="q-001")
    q2 = make_choice_question(stem="Same?", qid="q-002")
    exam = Exam(
        exam_id="ex-dup",
        questions=[q1, q2],
        config_used=ExamConfig(total_questions=2),
    )
    doc = make_doc()

    result = validator.validate_exam(exam, doc)
    assert not result.valid
    assert any("Duplicate stem" in issue for issue in result.issues)


def test_validator_flags_missing_source_refs():
    validator = QuestionValidator()
    q = make_choice_question()
    q.source_refs = []
    exam = Exam(exam_id="ex-missing", questions=[q], config_used=ExamConfig(total_questions=1))
    doc = make_doc()

    result = validator.validate_exam(exam, doc)
    assert not result.valid
    assert any("source_refs" in issue for issue in result.issues)


def test_validator_flags_out_of_bounds_refs():
    validator = QuestionValidator()
    q = make_choice_question()
    q.source_refs = [SourceReference(file="Doc", heading="Topic", start=1000, end=1010)]
    exam = Exam(exam_id="ex-bounds", questions=[q], config_used=ExamConfig(total_questions=1))
    doc = make_doc()

    result = validator.validate_exam(exam, doc)
    assert not result.valid
    assert any("out of source bounds" in issue for issue in result.issues)
