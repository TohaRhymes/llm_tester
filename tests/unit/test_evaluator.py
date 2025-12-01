"""
Unit tests for LLM evaluation framework (TDD approach).

Tests written BEFORE implementation.
"""
import pytest
from typing import List, Dict
from app.core.evaluator import (
    QuestionQualityEvaluator,
    GradingConsistencyEvaluator,
    ModelComparator
)
from app.models.schemas import Question, Exam, ExamConfig, QuestionResult


class TestQuestionQualityEvaluator:
    """Tests for question quality evaluation metrics."""

    @pytest.fixture
    def evaluator(self):
        return QuestionQualityEvaluator()

    @pytest.fixture
    def sample_questions(self):
        """Create sample questions for evaluation."""
        return [
            Question(
                id="q1",
                type="single_choice",
                stem="What is the primary pathophysiology of preeclampsia?",
                options=[
                    "Endothelial dysfunction",
                    "Cardiac failure",
                    "Renal stones",
                    "Liver disease"
                ],
                correct=[0]
            ),
            Question(
                id="q2",
                type="open_ended",
                stem="Explain the diagnostic criteria for preeclampsia.",
                reference_answer="Diagnosis requires BP ≥140/90 mmHg after 20 weeks plus proteinuria.",
                rubric=[
                    "Mentions BP threshold",
                    "States timing requirement",
                    "Includes proteinuria"
                ]
            )
        ]

    def test_evaluator_initialization(self, evaluator):
        """Test that evaluator can be initialized."""
        assert evaluator is not None

    def test_evaluate_answerability(self, evaluator, sample_questions):
        """Test answerability metric calculation."""
        score = evaluator.evaluate_answerability(sample_questions)
        assert 0.0 <= score <= 1.0

    def test_evaluate_difficulty_distribution(self, evaluator, sample_questions):
        """Test difficulty distribution analysis."""
        distribution = evaluator.evaluate_difficulty_distribution(sample_questions)
        assert "easy" in distribution
        assert "medium" in distribution
        assert "hard" in distribution
        assert sum(distribution.values()) == len(sample_questions)

    def test_evaluate_coherence(self, evaluator, sample_questions):
        """Test question coherence scoring."""
        score = evaluator.evaluate_coherence(sample_questions)
        assert 0.0 <= score <= 1.0

    def test_evaluate_overall_quality(self, evaluator, sample_questions):
        """Test overall quality score aggregation."""
        quality_score = evaluator.evaluate_overall_quality(sample_questions)

        assert "answerability" in quality_score
        assert "difficulty_distribution" in quality_score
        assert "coherence" in quality_score
        assert "overall" in quality_score
        assert 0.0 <= quality_score["overall"] <= 1.0


class TestGradingConsistencyEvaluator:
    """Tests for grading consistency evaluation."""

    @pytest.fixture
    def evaluator(self):
        return GradingConsistencyEvaluator()

    @pytest.fixture
    def sample_grading_results(self):
        """Create sample grading results from two runs."""
        run1 = [
            QuestionResult(
                question_id="q1",
                is_correct=True,
                expected=None,
                given=None,
                given_text="Good answer",
                partial_credit=0.8,
                feedback="Well done"
            ),
            QuestionResult(
                question_id="q2",
                is_correct=False,
                expected=None,
                given=None,
                given_text="Weak answer",
                partial_credit=0.4,
                feedback="Missing key points"
            )
        ]
        run2 = [
            QuestionResult(
                question_id="q1",
                is_correct=True,
                expected=None,
                given=None,
                given_text="Good answer",
                partial_credit=0.85,
                feedback="Excellent"
            ),
            QuestionResult(
                question_id="q2",
                is_correct=False,
                expected=None,
                given=None,
                given_text="Weak answer",
                partial_credit=0.35,
                feedback="Incomplete"
            )
        ]
        return {"run1": run1, "run2": run2}

    def test_evaluator_initialization(self, evaluator):
        """Test that consistency evaluator can be initialized."""
        assert evaluator is not None

    def test_calculate_inter_rater_reliability(self, evaluator, sample_grading_results):
        """Test inter-rater reliability calculation."""
        reliability = evaluator.calculate_inter_rater_reliability(
            sample_grading_results["run1"],
            sample_grading_results["run2"]
        )
        assert 0.0 <= reliability <= 1.0

    def test_analyze_score_distribution(self, evaluator, sample_grading_results):
        """Test score distribution analysis."""
        distribution = evaluator.analyze_score_distribution(
            sample_grading_results["run1"]
        )
        assert "mean" in distribution
        assert "std" in distribution
        assert "min" in distribution
        assert "max" in distribution

    def test_calculate_consistency_score(self, evaluator, sample_grading_results):
        """Test overall consistency score."""
        score = evaluator.calculate_consistency_score(
            sample_grading_results["run1"],
            sample_grading_results["run2"]
        )
        assert 0.0 <= score <= 1.0


class TestModelComparator:
    """Tests for model comparison functionality."""

    @pytest.fixture
    def comparator(self):
        return ModelComparator()

    @pytest.fixture
    def sample_model_results(self):
        """Create sample results from multiple models."""
        return {
            "gpt-4o-mini": {
                "quality_score": 0.75,
                "consistency_score": 0.80,
                "avg_generation_time": 2.5,
                "cost_per_question": 0.001
            },
            "gpt-4o": {
                "quality_score": 0.90,
                "consistency_score": 0.92,
                "avg_generation_time": 4.0,
                "cost_per_question": 0.005
            }
        }

    def test_comparator_initialization(self, comparator):
        """Test that comparator can be initialized."""
        assert comparator is not None

    def test_compare_models(self, comparator, sample_model_results):
        """Test model comparison."""
        comparison = comparator.compare_models(sample_model_results)

        assert "rankings" in comparison
        assert "best_overall" in comparison
        assert "best_value" in comparison

    def test_calculate_cost_performance_ratio(self, comparator, sample_model_results):
        """Test cost-performance analysis."""
        ratios = comparator.calculate_cost_performance_ratio(sample_model_results)

        for model, ratio in ratios.items():
            assert ratio >= 0.0

    def test_generate_recommendation(self, comparator, sample_model_results):
        """Test recommendation generation."""
        recommendation = comparator.generate_recommendation(sample_model_results)

        assert "recommended_model" in recommendation
        assert "reasoning" in recommendation
        assert isinstance(recommendation["reasoning"], str)


class TestEvaluationReport:
    """Tests for evaluation report generation."""

    def test_generate_report_structure(self):
        """Test that report has correct structure."""
        from app.core.evaluator import EvaluationReport

        report = EvaluationReport()
        report_data = report.generate({
            "model_results": {},
            "comparison": {},
            "timestamp": "2024-01-01T00:00:00"
        })

        assert "summary" in report_data
        assert "model_details" in report_data
        assert "recommendations" in report_data
        assert "timestamp" in report_data

    def test_report_includes_visualizations(self):
        """Test that report includes visualization data."""
        from app.core.evaluator import EvaluationReport

        report = EvaluationReport()
        viz_data = report.get_visualization_data({
            "gpt-4o-mini": {"quality_score": 0.75},
            "gpt-4o": {"quality_score": 0.90}
        })

        assert "quality_comparison" in viz_data
        assert isinstance(viz_data["quality_comparison"], dict)
