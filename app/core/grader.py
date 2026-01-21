"""
Answer grading module for automated exam checking.
"""
from typing import List, Dict, Optional
from app.models.schemas import (
    Exam, GradeRequest, GradeResponse,
    QuestionResult, GradeSummary, Question, StudentAnswer
)
from app.config import settings
from app.services.llm_provider import get_llm_client, LLMProvider, ProviderName


class Grader:
    """Handles grading of student answers against exam answer keys."""

    def __init__(
        self,
        provider: Optional[ProviderName] = None,
        model_name: Optional[str] = None,
        llm_client: Optional[LLMProvider] = None
    ):
        """Initialize grader with LLM provider for open-ended grading."""
        self.provider_name = provider or settings.default_provider
        self.model_name = model_name
        self.llm_client = llm_client

    def grade(
        self,
        exam: Exam,
        request: GradeRequest,
        partial_credit: bool = True
    ) -> GradeResponse:
        """
        Grade student answers against exam answer keys.

        Args:
            exam: The exam with questions and correct answers
            request: Student answers to grade
            partial_credit: Whether to award partial credit for multiple choice

        Returns:
            GradeResponse with summary and per-question results

        Raises:
            ValueError: If request has no answers or invalid question IDs
        """
        if not request.answers:
            raise ValueError("GradeRequest must contain at least one answer")

        # Build question lookup
        questions_map: Dict[str, Question] = {q.id: q for q in exam.questions}

        # Validate all question IDs exist
        for answer in request.answers:
            if answer.question_id not in questions_map:
                raise ValueError(f"Question ID '{answer.question_id}' not found in exam")

        # Grade each answer
        results: List[QuestionResult] = []
        total_credit = 0.0
        llm_client = self._get_llm_client(getattr(exam, "config_used", None))
        language = getattr(exam.config_used, "language", "en") if exam else "en"

        for student_answer in request.answers:
            question = questions_map[student_answer.question_id]

            # Grade based on question type
            if question.type == "open_ended":
                result = self._grade_open_ended_question(question, student_answer, llm_client, language)
            else:
                result = self._grade_choice_question(
                    question,
                    student_answer.choice,
                    partial_credit
                )

            results.append(result)
            total_credit += result.partial_credit

        # Calculate summary
        total_questions = len(results)
        correct_count = sum(1 for r in results if r.is_correct)
        score_percent = (total_credit / total_questions * 100.0) if total_questions > 0 else 0.0

        summary = GradeSummary(
            total=total_questions,
            correct=correct_count,
            score_percent=round(score_percent, 2)
        )

        return GradeResponse(
            exam_id=request.exam_id,
            summary=summary,
            per_question=results
        )

    def _grade_choice_question(
        self,
        question: Question,
        given: List[int],
        partial_credit: bool
    ) -> QuestionResult:
        """
        Grade a single choice or multiple choice question.

        Args:
            question: The question being graded
            given: Student's answer choices (indices)
            partial_credit: Whether to calculate partial credit

        Returns:
            QuestionResult with grading details
        """
        expected = question.correct

        # For single_choice, simple exact match
        if question.type == "single_choice":
            is_correct = given == expected
            credit = 1.0 if is_correct else 0.0

        # For multiple_choice
        else:
            # Sort for comparison
            expected_sorted = sorted(expected)
            given_sorted = sorted(given)

            # Check if fully correct
            is_correct = expected_sorted == given_sorted

            # Calculate credit
            if is_correct:
                credit = 1.0
            elif partial_credit:
                credit = self.calculate_partial_credit(expected, given)
            else:
                credit = 0.0

        return QuestionResult(
            question_id=question.id,
            is_correct=is_correct,
            expected=expected,
            given=given,
            given_text=None,
            partial_credit=round(credit, 4),
            feedback=None
        )

    def _grade_open_ended_question(
        self,
        question: Question,
        student_answer: StudentAnswer,
        llm_client: LLMProvider,
        language: str
    ) -> QuestionResult:
        """
        Grade an open-ended question using AI.

        Args:
            question: The open-ended question
            student_answer: Student's text response

        Returns:
            QuestionResult with AI grading and feedback
        """
        if not student_answer.text_answer:
            # No answer provided
            return QuestionResult(
                question_id=question.id,
                is_correct=False,
                expected=None,
                given=None,
                given_text="",
                partial_credit=0.0,
                feedback="No answer provided.",
                rubric_scores=[0 for _ in (question.rubric or [])],
                metrics={
                    "rubric_coverage": 0.0,
                    "reference_overlap": 0.0,
                    "answer_length": 0.0,
                }
            )

        try:
            # Use OpenAI to grade the answer
            grading_result = llm_client.grade_open_ended(
                question_stem=question.stem,
                reference_answer=question.reference_answer,
                rubric=question.rubric,
                student_answer=student_answer.text_answer,
                language=language
            )

            # Determine if "correct" (>= 0.7 score)
            is_correct = grading_result["score"] >= 0.7
            metrics = self._compute_open_ended_metrics(
                grading_result["rubric_scores"],
                question.rubric,
                student_answer.text_answer,
                question.reference_answer,
            )

            return QuestionResult(
                question_id=question.id,
                is_correct=is_correct,
                expected=None,
                given=None,
                given_text=student_answer.text_answer,
                partial_credit=round(grading_result["score"], 4),
                feedback=grading_result["feedback"],
                rubric_scores=grading_result["rubric_scores"],
                metrics=metrics
            )

        except Exception as e:
            # Fallback if AI grading fails
            return QuestionResult(
                question_id=question.id,
                is_correct=False,
                expected=None,
                given=None,
                given_text=student_answer.text_answer,
                partial_credit=0.0,
                feedback=f"Grading failed: {str(e)}",
                rubric_scores=[0 for _ in (question.rubric or [])],
                metrics={
                    "rubric_coverage": 0.0,
                    "reference_overlap": 0.0,
                    "answer_length": float(len(student_answer.text_answer.split())) if student_answer.text_answer else 0.0,
                }
            )

    def _compute_open_ended_metrics(
        self,
        rubric_scores: List[int],
        rubric: Optional[List[str]],
        student_answer: str,
        reference_answer: Optional[str],
    ) -> Dict[str, float]:
        """Compute open-ended grading metrics."""
        rubric_len = len(rubric_scores) if rubric_scores else 0
        rubric_coverage = sum(rubric_scores) / rubric_len if rubric_len else 0.0
        answer_length = float(len(student_answer.split())) if student_answer else 0.0

        reference_overlap = 0.0
        if reference_answer:
            ref_terms = self._extract_terms(reference_answer)
            student_terms = self._extract_terms(student_answer)
            if ref_terms:
                reference_overlap = len(ref_terms & student_terms) / len(ref_terms)

        return {
            "rubric_coverage": round(rubric_coverage, 4),
            "reference_overlap": round(reference_overlap, 4),
            "answer_length": answer_length,
        }

    def _extract_terms(self, text: str) -> set[str]:
        """Extract lowercase terms for overlap scoring."""
        import re

        stopwords = {"about", "question", "answer", "what", "which", "explain", "select", "choose"}
        return {
            term
            for term in re.findall(r"[A-Za-zА-Яа-я0-9]{4,}", text.lower())
            if term not in stopwords
        }

    def calculate_partial_credit(
        self,
        expected: List[int],
        given: List[int]
    ) -> float:
        """
        Calculate partial credit for multiple choice questions.

        Formula: (correct_selected - wrong_selected) / total_expected
        Credit is clamped to [0.0, 1.0]

        Args:
            expected: List of correct answer indices
            given: List of student's answer indices

        Returns:
            Partial credit score between 0.0 and 1.0
        """
        expected_set = set(expected)
        given_set = set(given)

        # Count correct selections (intersection)
        correct_selected = len(expected_set & given_set)

        # Count wrong selections (given but not expected)
        wrong_selected = len(given_set - expected_set)

        # Total correct answers expected
        total_expected = len(expected_set)

        if total_expected == 0:
            return 0.0

        # Calculate credit: reward correct, penalize wrong
        credit = (correct_selected - wrong_selected) / total_expected

        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, credit))

    def _get_llm_client(self, exam_config) -> LLMProvider:
        """Return configured LLM client for grading."""
        provider = getattr(exam_config, "provider", None) or self.provider_name
        model = getattr(exam_config, "model_name", None) or self.model_name

        if self.llm_client:
            return self.llm_client

        return get_llm_client(provider=provider, model_name=model)
