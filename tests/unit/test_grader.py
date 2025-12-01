"""
Unit tests for answer grading module (TDD - RED phase).

Tests written BEFORE implementation.
"""
import pytest
from app.core.grader import Grader
from app.models.schemas import (
    Question, Exam, ExamConfig, GradeRequest,
    StudentAnswer, GradeResponse
)


class TestGrader:
    """Tests for grading functionality."""

    @pytest.fixture
    def grader(self):
        return Grader()

    @pytest.fixture
    def sample_exam(self):
        """Create a sample exam with mixed question types."""
        q1 = Question(
            id="q1",
            type="single_choice",
            stem="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct=[1]
        )
        q2 = Question(
            id="q2",
            type="single_choice",
            stem="Capital of France?",
            options=["London", "Paris", "Berlin"],
            correct=[1]
        )
        q3 = Question(
            id="q3",
            type="multiple_choice",
            stem="Select all even numbers:",
            options=["1", "2", "3", "4", "5", "6"],
            correct=[1, 3, 5]  # 2, 4, 6
        )
        q4 = Question(
            id="q4",
            type="multiple_choice",
            stem="Select all vowels:",
            options=["A", "B", "C", "E", "I"],
            correct=[0, 3, 4]  # A, E, I
        )

        return Exam(
            exam_id="exam1",
            questions=[q1, q2, q3, q4],
            config_used=ExamConfig()
        )

    def test_grader_initialization(self, grader):
        """Test that grader can be initialized."""
        assert grader is not None

    def test_grade_single_choice_correct(self, grader, sample_exam):
        """Test grading correct single choice answer."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q1", choice=[1])]
        )
        response = grader.grade(sample_exam, request)

        assert response.exam_id == "exam1"
        assert len(response.per_question) == 1
        result = response.per_question[0]
        assert result.is_correct is True
        assert result.question_id == "q1"
        assert result.partial_credit == 1.0

    def test_grade_single_choice_incorrect(self, grader, sample_exam):
        """Test grading incorrect single choice answer."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q1", choice=[0])]  # Wrong answer
        )
        response = grader.grade(sample_exam, request)

        result = response.per_question[0]
        assert result.is_correct is False
        assert result.partial_credit == 0.0
        assert result.expected == [1]
        assert result.given == [0]

    def test_grade_multiple_choice_all_correct(self, grader, sample_exam):
        """Test grading fully correct multiple choice answer."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q3", choice=[1, 3, 5])]
        )
        response = grader.grade(sample_exam, request)

        result = response.per_question[0]
        assert result.is_correct is True
        assert result.partial_credit == 1.0

    def test_grade_multiple_choice_partial_correct(self, grader, sample_exam):
        """Test partial credit for multiple choice (some correct answers)."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q3", choice=[1, 3])]  # 2/3 correct
        )
        response = grader.grade(sample_exam, request, partial_credit=True)

        result = response.per_question[0]
        # Partial credit calculation: correct answers / total correct expected
        # But should also penalize wrong selections
        assert result.partial_credit > 0.0
        assert result.partial_credit < 1.0

    def test_grade_multiple_choice_with_wrong_selections(self, grader, sample_exam):
        """Test partial credit when student selects some wrong options."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q3", choice=[0, 1, 3])]  # 2 correct, 1 wrong
        )
        response = grader.grade(sample_exam, request, partial_credit=True)

        result = response.per_question[0]
        # Should have reduced credit due to wrong selection
        assert result.partial_credit > 0.0
        assert result.partial_credit < 1.0

    def test_grade_multiple_choice_no_partial_credit(self, grader, sample_exam):
        """Test multiple choice without partial credit (all-or-nothing)."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="q3", choice=[1, 3])]  # Incomplete
        )
        response = grader.grade(sample_exam, request, partial_credit=False)

        result = response.per_question[0]
        assert result.is_correct is False
        assert result.partial_credit == 0.0

    def test_grade_summary_all_correct(self, grader, sample_exam):
        """Test summary when all answers are correct."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[
                StudentAnswer(question_id="q1", choice=[1]),
                StudentAnswer(question_id="q2", choice=[1]),
                StudentAnswer(question_id="q3", choice=[1, 3, 5]),
                StudentAnswer(question_id="q4", choice=[0, 3, 4]),
            ]
        )
        response = grader.grade(sample_exam, request)

        assert response.summary.total == 4
        assert response.summary.correct == 4
        assert response.summary.score_percent == 100.0

    def test_grade_summary_mixed_results(self, grader, sample_exam):
        """Test summary with mixed correct/incorrect answers."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[
                StudentAnswer(question_id="q1", choice=[1]),  # Correct - 1.0
                StudentAnswer(question_id="q2", choice=[0]),  # Wrong - 0.0
                StudentAnswer(question_id="q3", choice=[1, 3, 5]),  # Correct - 1.0
                StudentAnswer(question_id="q4", choice=[0]),  # Incomplete - partial credit ~0.33
            ]
        )
        response = grader.grade(sample_exam, request)

        assert response.summary.total == 4
        assert response.summary.correct == 2
        # With partial credit: (1.0 + 0.0 + 1.0 + ~0.33) / 4 * 100 ≈ 58.33%
        assert 55.0 <= response.summary.score_percent <= 60.0

    def test_grade_partial_answers_only(self, grader, sample_exam):
        """Test grading when not all questions are answered."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[
                StudentAnswer(question_id="q1", choice=[1]),
                StudentAnswer(question_id="q3", choice=[1, 3, 5]),
            ]
        )
        response = grader.grade(sample_exam, request)

        # Should only grade answered questions
        assert len(response.per_question) == 2
        assert response.summary.total == 2

    def test_grade_with_partial_credit_in_summary(self, grader, sample_exam):
        """Test that partial credit is reflected in summary score."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[
                StudentAnswer(question_id="q1", choice=[1]),  # 1.0 credit
                StudentAnswer(question_id="q3", choice=[1, 3]),  # Partial credit
            ]
        )
        response = grader.grade(sample_exam, request, partial_credit=True)

        # Total score should be between 50% and 100%
        assert 50.0 < response.summary.score_percent < 100.0

    def test_grade_invalid_question_id_raises_error(self, grader, sample_exam):
        """Test that grading with invalid question ID raises error."""
        request = GradeRequest(
            exam_id="exam1",
            answers=[StudentAnswer(question_id="invalid_id", choice=[0])]
        )

        with pytest.raises((ValueError, KeyError)):
            grader.grade(sample_exam, request)

    def test_grade_empty_answers(self, grader, sample_exam):
        """Test grading with no answers."""
        # Pydantic validates that answers list is not empty
        with pytest.raises(ValueError):
            GradeRequest(exam_id="exam1", answers=[])


class TestPartialCreditCalculation:
    """Tests for partial credit calculation logic."""

    @pytest.fixture
    def grader(self):
        return Grader()

    def test_calculate_partial_credit_all_correct(self, grader):
        """Test partial credit when all answers correct."""
        expected = [0, 2, 4]
        given = [0, 2, 4]

        credit = grader.calculate_partial_credit(expected, given)
        assert credit == 1.0

    def test_calculate_partial_credit_subset(self, grader):
        """Test partial credit when student selects subset of correct."""
        expected = [0, 2, 4]
        given = [0, 2]  # 2/3 correct

        credit = grader.calculate_partial_credit(expected, given)
        assert 0.6 <= credit <= 0.7  # Should be around 2/3

    def test_calculate_partial_credit_with_wrong(self, grader):
        """Test partial credit with wrong selections."""
        expected = [0, 2, 4]
        given = [0, 1, 2]  # 2 correct, 1 wrong

        credit = grader.calculate_partial_credit(expected, given)
        # Should penalize for wrong selection
        assert 0.0 < credit < 0.7

    def test_calculate_partial_credit_all_wrong(self, grader):
        """Test partial credit when all selections wrong."""
        expected = [0, 2, 4]
        given = [1, 3, 5]

        credit = grader.calculate_partial_credit(expected, given)
        assert credit == 0.0


class TestOpenEndedGrading:
    """Tests for open-ended question grading."""

    @pytest.fixture
    def grader(self):
        return Grader()

    @pytest.fixture
    def open_ended_exam(self):
        """Create an exam with open-ended questions."""
        q1 = Question(
            id="oe1",
            type="open_ended",
            stem="Explain the pathophysiology of preeclampsia.",
            options=None,
            correct=None,
            reference_answer="Preeclampsia involves endothelial dysfunction caused by placental ischemia. "
                           "This leads to systemic vasoconstriction, increased vascular permeability, and organ damage.",
            rubric=[
                "Mentions endothelial dysfunction",
                "Explains placental ischemia as root cause",
                "Describes systemic effects (vasoconstriction, permeability)"
            ]
        )
        q2 = Question(
            id="oe2",
            type="open_ended",
            stem="Describe the diagnostic criteria for preeclampsia.",
            options=None,
            correct=None,
            reference_answer="Diagnosis requires BP ≥140/90 mmHg after 20 weeks gestation plus proteinuria ≥300mg/24h "
                           "or other organ dysfunction markers.",
            rubric=[
                "States BP threshold (≥140/90 mmHg)",
                "Mentions timing (after 20 weeks)",
                "Includes proteinuria criteria (≥300mg/24h)"
            ]
        )
        return Exam(
            exam_id="open-exam",
            questions=[q1, q2],
            config_used=ExamConfig(
                total_questions=2,
                single_choice_ratio=0.0,
                multiple_choice_ratio=0.0,
                open_ended_ratio=1.0
            )
        )

    def test_grade_open_ended_with_good_answer(self, grader, open_ended_exam):
        """Test grading a good open-ended answer."""
        request = GradeRequest(
            exam_id="open-exam",
            answers=[
                StudentAnswer(
                    question_id="oe1",
                    text_answer="Preeclampsia is caused by endothelial dysfunction from placental ischemia. "
                               "This results in widespread vasoconstriction and increased permeability."
                )
            ]
        )
        response = grader.grade(open_ended_exam, request)

        assert len(response.per_question) == 1
        result = response.per_question[0]
        assert result.question_id == "oe1"
        assert result.given_text is not None
        assert result.feedback is not None
        assert 0.0 <= result.partial_credit <= 1.0

    def test_grade_open_ended_uses_ai_scoring(self, grader, open_ended_exam):
        """Test that open-ended grading uses AI for scoring."""
        request = GradeRequest(
            exam_id="open-exam",
            answers=[
                StudentAnswer(
                    question_id="oe1",
                    text_answer="Preeclampsia involves endothelial problems and placental issues causing high blood pressure."
                )
            ]
        )
        response = grader.grade(open_ended_exam, request)

        result = response.per_question[0]
        # AI should provide feedback
        assert result.feedback is not None
        assert len(result.feedback) > 0
        # Score should be between 0 and 1
        assert 0.0 <= result.partial_credit <= 1.0

    def test_grade_open_ended_correctness_threshold(self, grader, open_ended_exam):
        """Test that score >= 0.7 is considered correct."""
        # This test verifies the threshold logic
        # We can't control AI output, so we test with mock or just verify the logic exists
        request = GradeRequest(
            exam_id="open-exam",
            answers=[
                StudentAnswer(
                    question_id="oe1",
                    text_answer="Complete answer with all key points."
                )
            ]
        )
        response = grader.grade(open_ended_exam, request)
        result = response.per_question[0]

        # If partial_credit >= 0.7, should be marked correct
        if result.partial_credit >= 0.7:
            assert result.is_correct is True
        else:
            assert result.is_correct is False

    def test_grade_mixed_exam_with_open_ended(self, grader):
        """Test grading exam with both choice and open-ended questions."""
        q_choice = Question(
            id="q1",
            type="single_choice",
            stem="Select correct answer",
            options=["A", "B", "C"],
            correct=[1]
        )
        q_open = Question(
            id="oe1",
            type="open_ended",
            stem="Explain the concept.",
            reference_answer="The concept involves multiple factors...",
            rubric=["Factor 1", "Factor 2", "Factor 3"]
        )
        mixed_exam = Exam(
            exam_id="mixed",
            questions=[q_choice, q_open],
            config_used=ExamConfig()
        )

        request = GradeRequest(
            exam_id="mixed",
            answers=[
                StudentAnswer(question_id="q1", choice=[1]),
                StudentAnswer(question_id="oe1", text_answer="This concept has several factors including...")
            ]
        )
        response = grader.grade(mixed_exam, request)

        assert len(response.per_question) == 2
        # First is choice question
        assert response.per_question[0].given is not None
        # Second is open-ended
        assert response.per_question[1].given_text is not None
        assert response.per_question[1].feedback is not None

    def test_grade_open_ended_summary_calculation(self, grader, open_ended_exam):
        """Test that open-ended scores are included in summary."""
        request = GradeRequest(
            exam_id="open-exam",
            answers=[
                StudentAnswer(question_id="oe1", text_answer="Good answer here."),
                StudentAnswer(question_id="oe2", text_answer="Another good answer.")
            ]
        )
        response = grader.grade(open_ended_exam, request)

        # Summary should include both questions
        assert response.summary.total == 2
        # Score percent should be calculated from partial credits
        assert 0.0 <= response.summary.score_percent <= 100.0
