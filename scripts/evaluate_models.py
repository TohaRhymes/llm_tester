#!/usr/bin/env python3
"""
Script to evaluate and compare different LLM models for question generation and grading.

Usage:
    python scripts/evaluate_models.py --models gpt-4o-mini,gpt-4o --content examples/medical_content.md
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from app.core.parser import MarkdownParser
from app.core.generator import QuestionGenerator
from app.core.grader import Grader
from app.core.evaluator import (
    QuestionQualityEvaluator,
    GradingConsistencyEvaluator,
    ModelComparator,
    EvaluationReport
)
from app.models.schemas import ExamConfig, GradeRequest, StudentAnswer
from app.services.openai_client import OpenAIClient


class ModelEvaluator:
    """Orchestrates evaluation of multiple models."""

    def __init__(self, models: List[str], content_path: str, output_dir: str = "out/evaluations"):
        """
        Initialize model evaluator.

        Args:
            models: List of model names to evaluate
            content_path: Path to markdown content file
            output_dir: Directory for evaluation outputs
        """
        self.models = models
        self.content_path = content_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize evaluators
        self.quality_evaluator = QuestionQualityEvaluator()
        self.consistency_evaluator = GradingConsistencyEvaluator()
        self.comparator = ModelComparator()
        self.report_generator = EvaluationReport()

    def run_evaluation(self, num_questions: int = 10) -> Dict[str, Any]:
        """
        Run complete evaluation for all models.

        Args:
            num_questions: Number of questions to generate per model

        Returns:
            Complete evaluation results
        """
        print(f"Starting evaluation of {len(self.models)} models...")
        print(f"Content: {self.content_path}")
        print(f"Questions per model: {num_questions}\n")

        # Parse content
        parser = MarkdownParser()
        with open(self.content_path, 'r') as f:
            content = f.read()
        document = parser.parse(content)

        model_results = {}

        for model in self.models:
            print(f"\nEvaluating {model}...")
            result = self._evaluate_single_model(model, document, num_questions)
            model_results[model] = result
            print(f"  Quality Score: {result['quality_score']:.4f}")
            print(f"  Consistency Score: {result['consistency_score']:.4f}")
            print(f"  Avg Generation Time: {result['avg_generation_time']:.2f}s")

        # Compare models
        print("\n\nComparing models...")
        comparison = self.comparator.compare_models(model_results)
        recommendations = self.comparator.generate_recommendation(model_results)

        # Generate report
        evaluation_data = {
            "model_results": model_results,
            "comparison": comparison,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

        report = self.report_generator.generate(evaluation_data)

        # Save results
        output_file = self.output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n\nEvaluation complete!")
        print(f"Results saved to: {output_file}")
        print(f"\nRecommended model: {recommendations['recommended_model']}")
        print(f"Reasoning: {recommendations['reasoning']}")

        return report

    def _evaluate_single_model(
        self,
        model: str,
        document,
        num_questions: int
    ) -> Dict[str, Any]:
        """
        Evaluate a single model.

        Args:
            model: Model name
            document: Parsed document
            num_questions: Number of questions to generate

        Returns:
            Evaluation results for this model
        """
        # Update OpenAI client to use this model
        import app.config
        original_model = app.config.settings.openai_model
        app.config.settings.openai_model = model

        try:
            # Generate questions
            generator = QuestionGenerator()
            config = ExamConfig(
                total_questions=num_questions,
                single_choice_ratio=0.4,
                multiple_choice_ratio=0.3,
                open_ended_ratio=0.3
            )

            start_time = time.time()
            exam = generator.generate(document, config, f"eval-{model}")
            generation_time = time.time() - start_time

            # Evaluate question quality
            quality_metrics = self.quality_evaluator.evaluate_overall_quality(exam.questions)

            # Test grading consistency (generate twice and compare)
            grader = Grader()

            # Create sample answers
            sample_answers = []
            for q in exam.questions[:3]:  # Test on first 3 questions
                if q.type == "open_ended":
                    sample_answers.append(
                        StudentAnswer(
                            question_id=q.id,
                            text_answer="Sample answer for consistency testing"
                        )
                    )
                else:
                    sample_answers.append(
                        StudentAnswer(
                            question_id=q.id,
                            choice=[0]
                        )
                    )

            # Grade twice
            request = GradeRequest(exam_id=exam.exam_id, answers=sample_answers)
            results1 = grader.grade(exam, request).per_question
            results2 = grader.grade(exam, request).per_question

            consistency_score = self.consistency_evaluator.calculate_consistency_score(
                results1, results2
            )

            # Estimate costs (approximate)
            cost_per_question = self._estimate_cost(model, num_questions)

            return {
                "quality_score": quality_metrics["overall"],
                "quality_details": quality_metrics,
                "consistency_score": consistency_score,
                "avg_generation_time": round(generation_time / num_questions, 2),
                "total_generation_time": round(generation_time, 2),
                "cost_per_question": cost_per_question,
                "num_questions": num_questions
            }

        finally:
            # Restore original model
            app.config.settings.openai_model = original_model

    def _estimate_cost(self, model: str, num_questions: int) -> float:
        """
        Estimate cost per question for a model.

        Args:
            model: Model name
            num_questions: Number of questions generated

        Returns:
            Estimated cost per question
        """
        # Approximate costs (as of 2024)
        cost_per_1k_tokens = {
            "gpt-4o-mini": 0.00015,  # $0.15/1M input
            "gpt-4o": 0.0025,        # $2.50/1M input
            "gpt-3.5-turbo": 0.0005,
            "gpt-4": 0.03
        }

        # Rough estimate: ~500 tokens per question
        tokens_per_question = 500
        base_cost = cost_per_1k_tokens.get(model, 0.001)
        return round((tokens_per_question / 1000) * base_cost, 6)


def main():
    """Main entry point for evaluation script."""
    parser = argparse.ArgumentParser(
        description="Evaluate and compare LLM models for question generation"
    )
    parser.add_argument(
        "--models",
        type=str,
        default="gpt-4o-mini,gpt-4o",
        help="Comma-separated list of models to evaluate"
    )
    parser.add_argument(
        "--content",
        type=str,
        default="examples/medical_content.md",
        help="Path to markdown content file"
    )
    parser.add_argument(
        "--num-questions",
        type=int,
        default=10,
        help="Number of questions to generate per model"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="out/evaluations",
        help="Output directory for evaluation results"
    )

    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",")]

    evaluator = ModelEvaluator(
        models=models,
        content_path=args.content,
        output_dir=args.output_dir
    )

    evaluator.run_evaluation(num_questions=args.num_questions)


if __name__ == "__main__":
    main()
