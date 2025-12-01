"""
LLM evaluation framework for comparing question generation and grading quality.
"""
from typing import List, Dict, Any
import statistics
from app.models.schemas import Question, QuestionResult


class QuestionQualityEvaluator:
    """Evaluates quality metrics for generated questions."""

    def __init__(self):
        """Initialize quality evaluator."""
        pass

    def evaluate_answerability(self, questions: List[Question]) -> float:
        """
        Evaluate if questions are answerable from source material.

        Args:
            questions: List of questions to evaluate

        Returns:
            Answerability score between 0.0 and 1.0
        """
        if not questions:
            return 0.0

        # Simple heuristic: questions with proper structure are answerable
        answerable_count = 0
        for q in questions:
            if q.type == "open_ended":
                # Open-ended should have reference answer and rubric
                if q.reference_answer and q.rubric and len(q.rubric) >= 3:
                    answerable_count += 1
            else:
                # Choice questions should have options and correct answers
                if q.options and len(q.options) >= 3 and q.correct:
                    answerable_count += 1

        return answerable_count / len(questions)

    def evaluate_difficulty_distribution(self, questions: List[Question]) -> Dict[str, int]:
        """
        Analyze difficulty distribution of questions.

        Args:
            questions: List of questions to analyze

        Returns:
            Dictionary with counts per difficulty level
        """
        distribution = {"easy": 0, "medium": 0, "hard": 0}

        for q in questions:
            difficulty = q.meta.difficulty if q.meta else "medium"
            distribution[difficulty] = distribution.get(difficulty, 0) + 1

        return distribution

    def evaluate_coherence(self, questions: List[Question]) -> float:
        """
        Evaluate coherence of question stems.

        Args:
            questions: List of questions to evaluate

        Returns:
            Coherence score between 0.0 and 1.0
        """
        if not questions:
            return 0.0

        # Simple heuristic: questions with proper length and ending
        coherent_count = 0
        for q in questions:
            stem = q.stem.strip()
            # Check if stem is reasonable length and ends with question mark
            if 20 <= len(stem) <= 500 and stem.endswith("?"):
                coherent_count += 1

        return coherent_count / len(questions)

    def evaluate_overall_quality(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Calculate overall quality score from multiple metrics.

        Args:
            questions: List of questions to evaluate

        Returns:
            Dictionary with individual and overall quality scores
        """
        answerability = self.evaluate_answerability(questions)
        difficulty_distribution = self.evaluate_difficulty_distribution(questions)
        coherence = self.evaluate_coherence(questions)

        # Calculate balance score for difficulty distribution
        total = sum(difficulty_distribution.values())
        if total > 0:
            # Ideal is 33% each, calculate deviation
            ideal = total / 3
            deviations = [abs(count - ideal) / ideal for count in difficulty_distribution.values()]
            balance_score = 1.0 - (sum(deviations) / (3 * len(deviations)))
        else:
            balance_score = 0.0

        # Overall is weighted average
        overall = (
            answerability * 0.4 +
            coherence * 0.3 +
            balance_score * 0.3
        )

        return {
            "answerability": round(answerability, 4),
            "difficulty_distribution": difficulty_distribution,
            "coherence": round(coherence, 4),
            "balance_score": round(balance_score, 4),
            "overall": round(overall, 4)
        }


class GradingConsistencyEvaluator:
    """Evaluates consistency of grading across multiple runs."""

    def __init__(self):
        """Initialize consistency evaluator."""
        pass

    def calculate_inter_rater_reliability(
        self,
        results1: List[QuestionResult],
        results2: List[QuestionResult]
    ) -> float:
        """
        Calculate inter-rater reliability between two grading runs.

        Args:
            results1: First grading run results
            results2: Second grading run results

        Returns:
            Reliability score between 0.0 and 1.0
        """
        if not results1 or not results2:
            return 0.0

        # Match results by question_id
        score_pairs = []
        results2_map = {r.question_id: r for r in results2}

        for r1 in results1:
            if r1.question_id in results2_map:
                r2 = results2_map[r1.question_id]
                score_pairs.append((r1.partial_credit, r2.partial_credit))

        if not score_pairs:
            return 0.0

        # Calculate correlation (simple difference-based metric)
        differences = [abs(s1 - s2) for s1, s2 in score_pairs]
        avg_difference = sum(differences) / len(differences)

        # Convert to reliability score (0 difference = 1.0 reliability)
        reliability = max(0.0, 1.0 - avg_difference)
        return round(reliability, 4)

    def analyze_score_distribution(self, results: List[QuestionResult]) -> Dict[str, float]:
        """
        Analyze distribution of scores.

        Args:
            results: Grading results to analyze

        Returns:
            Dictionary with distribution statistics
        """
        if not results:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        scores = [r.partial_credit for r in results]

        return {
            "mean": round(statistics.mean(scores), 4),
            "std": round(statistics.stdev(scores), 4) if len(scores) > 1 else 0.0,
            "min": round(min(scores), 4),
            "max": round(max(scores), 4)
        }

    def calculate_consistency_score(
        self,
        results1: List[QuestionResult],
        results2: List[QuestionResult]
    ) -> float:
        """
        Calculate overall consistency score.

        Args:
            results1: First grading run
            results2: Second grading run

        Returns:
            Consistency score between 0.0 and 1.0
        """
        reliability = self.calculate_inter_rater_reliability(results1, results2)
        return reliability


class ModelComparator:
    """Compares performance of different LLM models."""

    def __init__(self):
        """Initialize model comparator."""
        pass

    def compare_models(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple models on various metrics.

        Args:
            model_results: Dictionary mapping model names to their results

        Returns:
            Comparison report with rankings and best models
        """
        if not model_results:
            return {"rankings": {}, "best_overall": None, "best_value": None}

        # Rank models by quality score
        quality_rankings = sorted(
            model_results.items(),
            key=lambda x: x[1].get("quality_score", 0),
            reverse=True
        )

        # Calculate value score (quality / cost)
        value_scores = {}
        for model, results in model_results.items():
            quality = results.get("quality_score", 0)
            cost = results.get("cost_per_question", 1)
            value_scores[model] = quality / cost if cost > 0 else 0

        best_value = max(value_scores.items(), key=lambda x: x[1])[0] if value_scores else None

        return {
            "rankings": {
                "quality": [model for model, _ in quality_rankings]
            },
            "best_overall": quality_rankings[0][0] if quality_rankings else None,
            "best_value": best_value,
            "value_scores": value_scores
        }

    def calculate_cost_performance_ratio(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate cost-performance ratio for each model.

        Args:
            model_results: Dictionary mapping model names to their results

        Returns:
            Dictionary mapping model names to cost-performance ratios
        """
        ratios = {}
        for model, results in model_results.items():
            quality = results.get("quality_score", 0)
            cost = results.get("cost_per_question", 1)
            ratios[model] = round(quality / cost if cost > 0 else 0, 4)

        return ratios

    def generate_recommendation(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate recommendation based on model comparison.

        Args:
            model_results: Dictionary mapping model names to their results

        Returns:
            Recommendation with model choice and reasoning
        """
        comparison = self.compare_models(model_results)
        best_overall = comparison["best_overall"]
        best_value = comparison["best_value"]

        if best_overall == best_value:
            reasoning = f"{best_overall} offers the best quality and value"
        else:
            reasoning = (
                f"{best_overall} has highest quality, but {best_value} "
                f"offers better value for cost"
            )

        return {
            "recommended_model": best_value,  # Prefer value by default
            "alternative": best_overall if best_overall != best_value else None,
            "reasoning": reasoning
        }


class EvaluationReport:
    """Generates evaluation reports with visualizations."""

    def generate(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.

        Args:
            evaluation_data: Complete evaluation results

        Returns:
            Formatted report structure
        """
        model_results = evaluation_data.get("model_results", {})
        comparison = evaluation_data.get("comparison", {})

        summary = {
            "models_evaluated": list(model_results.keys()),
            "best_model": comparison.get("best_overall"),
            "total_questions": sum(
                results.get("num_questions", 0)
                for results in model_results.values()
            )
        }

        return {
            "summary": summary,
            "model_details": model_results,
            "comparison": comparison,
            "recommendations": evaluation_data.get("recommendations", {}),
            "timestamp": evaluation_data.get("timestamp", "")
        }

    def get_visualization_data(self, model_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare data for visualization.

        Args:
            model_results: Results from each model

        Returns:
            Dictionary with visualization-ready data
        """
        quality_comparison = {
            model: results.get("quality_score", 0)
            for model, results in model_results.items()
        }

        return {
            "quality_comparison": quality_comparison,
            "cost_comparison": {
                model: results.get("cost_per_question", 0)
                for model, results in model_results.items()
            }
        }
