"""
Unit tests for Pydantic schemas.
"""
import pytest
from pydantic import ValidationError
from app.models.schemas import (
    Question, Exam, ExamConfig, GradeRequest, GradeResponse,
    StudentAnswer, QuestionResult, GradeSummary, SourceReference,
    QuestionMeta, GenerateRequest, HealthResponse
)


class TestSourceReference:
    def test_valid_source_reference(self):
        ref = SourceReference(
            file="test.md",
            heading="Introduction",
            start=100,
            end=200
        )
        assert ref.file == "test.md"
        assert ref.heading == "Introduction"
        assert ref.start == 100
        assert ref.end == 200

    def test_end_before_start_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            SourceReference(file="test.md", start=200, end=100)
        assert "end must be >= start" in str(exc_info.value)


class TestQuestion:
    def test_valid_single_choice_question(self):
        q = Question(
            id="q1",
            type="single_choice",
            stem="What is 2+2?",
            options=["3", "4", "5"],
            correct=[1]
        )
        assert q.id == "q1"
        assert q.type == "single_choice"
        assert len(q.correct) == 1

    def test_valid_multiple_choice_question(self):
        q = Question(
            id="q2",
            type="multiple_choice",
            stem="Select all even numbers:",
            options=["1", "2", "3", "4"],
            correct=[1, 3]
        )
        assert q.type == "multiple_choice"
        assert len(q.correct) == 2

    def test_single_choice_with_multiple_correct_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="q3",
                type="single_choice",
                stem="Test",
                options=["A", "B", "C"],
                correct=[0, 1]
            )
        assert "single_choice must have exactly one correct answer" in str(exc_info.value)

    def test_empty_options_raises_error(self):
        with pytest.raises(ValidationError):
            Question(
                id="q4",
                type="single_choice",
                stem="Test",
                options=["A", ""],
                correct=[0]
            )

    def test_correct_index_out_of_range_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="q5",
                type="single_choice",
                stem="Test",
                options=["A", "B"],
                correct=[5]
            )
        assert "out of range" in str(exc_info.value)

    def test_too_few_options_raises_error(self):
        with pytest.raises(ValidationError):
            Question(
                id="q6",
                type="single_choice",
                stem="Test",
                options=["A"],
                correct=[0]
            )

    def test_question_with_source_refs(self):
        q = Question(
            id="q7",
            type="single_choice",
            stem="Test question",
            options=["A", "B", "C"],
            correct=[0],
            source_refs=[
                SourceReference(file="test.md", start=0, end=100)
            ]
        )
        assert len(q.source_refs) == 1
        assert q.source_refs[0].file == "test.md"


class TestExamConfig:
    def test_valid_config(self):
        config = ExamConfig(
            total_questions=20,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2,
            difficulty="mixed"
        )
        assert config.total_questions == 20
        assert config.difficulty == "mixed"

    def test_ratios_must_sum_to_one(self):
        with pytest.raises(ValidationError) as exc_info:
            ExamConfig(
                total_questions=10,
                single_choice_ratio=0.5,
                multiple_choice_ratio=0.6
            )
        assert "must sum to 1.0" in str(exc_info.value)

    def test_default_values(self):
        config = ExamConfig()
        assert config.total_questions == 20
        assert config.single_choice_ratio == 0.5
        assert config.multiple_choice_ratio == 0.3
        assert config.open_ended_ratio == 0.2


class TestExam:
    def test_valid_exam(self):
        q1 = Question(
            id="q1",
            type="single_choice",
            stem="Test 1",
            options=["A", "B"],
            correct=[0]
        )
        q2 = Question(
            id="q2",
            type="single_choice",
            stem="Test 2",
            options=["A", "B"],
            correct=[1]
        )
        exam = Exam(
            exam_id="exam1",
            questions=[q1, q2],
            config_used=ExamConfig()
        )
        assert exam.exam_id == "exam1"
        assert len(exam.questions) == 2

    def test_duplicate_question_ids_raise_error(self):
        q1 = Question(
            id="q1",
            type="single_choice",
            stem="Test 1",
            options=["A", "B"],
            correct=[0]
        )
        q2 = Question(
            id="q1",  # Duplicate ID
            type="single_choice",
            stem="Test 2",
            options=["A", "B"],
            correct=[1]
        )
        with pytest.raises(ValidationError) as exc_info:
            Exam(
                exam_id="exam1",
                questions=[q1, q2],
                config_used=ExamConfig()
            )
        assert "must be unique" in str(exc_info.value)


class TestGradeRequest:
    def test_valid_grade_request(self):
        req = GradeRequest(
            exam_id="exam1",
            answers=[
                StudentAnswer(question_id="q1", choice=[0]),
                StudentAnswer(question_id="q2", choice=[1])
            ]
        )
        assert req.exam_id == "exam1"
        assert len(req.answers) == 2


class TestGradeResponse:
    def test_valid_grade_response(self):
        summary = GradeSummary(total=10, correct=8, score_percent=80.0)
        result = QuestionResult(
            question_id="q1",
            is_correct=True,
            expected=[0],
            given=[0],
            partial_credit=1.0
        )
        response = GradeResponse(
            exam_id="exam1",
            summary=summary,
            per_question=[result]
        )
        assert response.exam_id == "exam1"
        assert response.summary.score_percent == 80.0

    def test_correct_cannot_exceed_total(self):
        with pytest.raises(ValidationError) as exc_info:
            GradeSummary(total=10, correct=15, score_percent=150.0)
        assert "cannot exceed total" in str(exc_info.value)


class TestGenerateRequest:
    def test_valid_generate_request(self):
        req = GenerateRequest(
            markdown_content="# Test\nSome content",
            config=ExamConfig(total_questions=10)
        )
        assert req.markdown_content == "# Test\nSome content"
        assert req.config.total_questions == 10

    def test_generate_request_with_defaults(self):
        req = GenerateRequest(markdown_content="# Test")
        assert req.config is None


class TestHealthResponse:
    def test_valid_health_response(self):
        response = HealthResponse(status="ok")
        assert response.status == "ok"
        assert response.version == "0.1.0"

class TestOpenEndedQuestion:
    def test_valid_open_ended_question(self):
        """Test creating a valid open-ended question."""
        q = Question(
            id="q-oe1",
            type="open_ended",
            stem="Explain the pathophysiology of preeclampsia.",
            options=None,
            correct=None,
            reference_answer="Preeclampsia involves endothelial dysfunction and placental ischemia...",
            rubric=["Mentions endothelial dysfunction", "Explains placental ischemia"]
        )
        assert q.id == "q-oe1"
        assert q.type == "open_ended"
        assert q.options is None
        assert q.correct is None
        assert q.reference_answer is not None
        assert len(q.rubric) == 2

    def test_open_ended_requires_reference_answer(self):
        """Test that open_ended questions require reference_answer."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="q-oe2",
                type="open_ended",
                stem="Explain something.",
                options=None,
                correct=None,
                reference_answer=None  # Missing!
            )
        assert "reference_answer required" in str(exc_info.value)

    def test_choice_question_cannot_have_none_options(self):
        """Test that single/multiple choice require options."""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                id="q3",
                type="single_choice",
                stem="Question?",
                options=None,  # Should fail
                correct=[0]
            )
        assert "options required" in str(exc_info.value)


class TestExamConfigWithOpenEnded:
    def test_config_with_three_ratios(self):
        """Test ExamConfig with all three question types."""
        config = ExamConfig(
            total_questions=10,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2
        )
        assert config.single_choice_ratio == 0.5
        assert config.multiple_choice_ratio == 0.3
        assert config.open_ended_ratio == 0.2

    def test_ratios_must_sum_to_one(self):
        """Test that ratios must sum to 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            ExamConfig(
                single_choice_ratio=0.5,
                multiple_choice_ratio=0.4,
                open_ended_ratio=0.2  # Sum = 1.1, should fail
            )
        assert "must sum to 1.0" in str(exc_info.value)


class TestStudentAnswerWithText:
    def test_student_answer_with_choice(self):
        """Test answer with choice array."""
        answer = StudentAnswer(
            question_id="q1",
            choice=[1, 2],
            text_answer=None
        )
        assert answer.choice == [1, 2]
        assert answer.text_answer is None

    def test_student_answer_with_text(self):
        """Test answer with text response."""
        answer = StudentAnswer(
            question_id="q-oe1",
            choice=None,
            text_answer="Preeclampsia is caused by..."
        )
        assert answer.choice is None
        assert answer.text_answer is not None

    def test_must_have_either_choice_or_text(self):
        """Test that at least one answer type is required."""
        with pytest.raises(ValidationError) as exc_info:
            StudentAnswer(
                question_id="q1",
                choice=None,
                text_answer=None  # Both None should fail
            )
        assert "Either choice or text_answer must be provided" in str(exc_info.value)
