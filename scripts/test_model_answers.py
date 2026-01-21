#!/usr/bin/env python3
"""
CLI script to test how well different LLM models answer exam questions.

Usage:
    # Test a single model on an exam
    python scripts/test_model_answers.py --exam data/out/exam_ex-123.json --model gpt-4o-mini --provider openai

    # Test multiple models and compare
    python scripts/test_model_answers.py --exam data/out/exam_ex-123.json --compare

    # Test on all exams in a directory
    python scripts/test_model_answers.py --exam-dir data/out --model yandexgpt-lite --provider yandex
"""
import argparse
import json
from typing import List, Dict

from scripts._utils import ensure_repo_root_on_path, collect_exam_files

# Add parent directory to path for imports
ensure_repo_root_on_path(__file__)

from app.services.model_answer_tester import ModelAnswerTester, ModelTestResult
from app.config import settings


def print_result(result: ModelTestResult):
    """Print formatted test result."""
    print(f"\n{'='*60}")
    print(f"Model: {result.model_name} ({result.provider})")
    print(f"Exam: {result.exam_id}")
    print(f"{'='*60}")
    print(f"Total Questions: {result.total_questions}")
    print(f"Correct Answers: {result.correct_count}")
    print(f"Accuracy: {result.accuracy:.2%}")
    print(f"AI Pass Rate: {result.accuracy:.2%}")
    print(f"\nTimestamp: {result.timestamp}")

    # Per-question breakdown
    print(f"\n{'Question Breakdown':=^60}")
    for i, q_result in enumerate(result.per_question_results, 1):
        status = "✓" if q_result.get("correct", False) else "✗"
        q_type = q_result.get("question_type", "unknown")
        print(f"{i}. [{status}] {q_result['question_id']} ({q_type})")

        if "error" in q_result:
            print(f"   Error: {q_result['error']}")
        elif q_type == "open_ended":
            print(f"   Score: {q_result.get('grading_score', 0):.2%}")
            print(f"   Feedback: {q_result.get('feedback', 'N/A')}")
        else:
            print(f"   Model: {q_result.get('model_answer', 'N/A')}")
            print(f"   Expected: {q_result.get('expected_answer', 'N/A')}")


def print_comparison(comparison: Dict):
    """Print formatted comparison of models."""
    print(f"\n{'='*60}")
    print(f"Model Comparison - Exam: {comparison['exam_id']}")
    print(f"{'='*60}")
    print(f"Total Questions: {comparison['total_questions']}\n")

    # Models summary
    print(f"{'Model':<25} {'Provider':<12} {'Accuracy':<12} {'Correct'}")
    print("-" * 60)
    for model in comparison['models']:
        print(
            f"{model['model_name']:<25} "
            f"{model['provider']:<12} "
            f"{model['accuracy']:>10.2%}  "
            f"{model['correct_count']}/{comparison['total_questions']}"
        )

    print(f"\n{'Best Model:':<25} {comparison['best_model']}")
    print(f"{'Best Accuracy:':<25} {comparison['best_accuracy']:.2%}")

    # Per-question breakdown
    if "per_question_breakdown" in comparison:
        print(f"\n{'Per-Question Analysis':=^60}")
        breakdown = comparison["per_question_breakdown"]
        for q_id, q_data in list(breakdown.items())[:10]:  # Show first 10
            correct_models = ", ".join(q_data["models_correct"]) or "None"
            print(f"\n{q_id} ({q_data['question_type']})")
            print(f"  Correct: {correct_models}")

        if len(breakdown) > 10:
            print(f"\n... and {len(breakdown) - 10} more questions")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Test LLM models on exam questions and compare performance"
    )

    # Exam input
    exam_group = parser.add_mutually_exclusive_group(required=True)
    exam_group.add_argument(
        "--exam",
        type=str,
        help="Path to single exam JSON file"
    )
    exam_group.add_argument(
        "--exam-dir",
        type=str,
        help="Directory containing exam JSON files"
    )

    # Model selection
    parser.add_argument(
        "--model",
        type=str,
        help="Model name (e.g., gpt-4o-mini, yandexgpt-lite)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "yandex"],
        help="Model provider (openai or yandex)"
    )

    # Comparison mode
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple predefined models"
    )

    # Output
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save results (default: data/results)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        choices=["en", "ru"],
        help="Language for prompts (default: en)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.compare and (not args.model or not args.provider):
        parser.error("--model and --provider required unless --compare is used")

    # Initialize tester
    tester = ModelAnswerTester()

    # Get exam(s)
    exam_files = collect_exam_files(args.exam, args.exam_dir)
    if not exam_files and args.exam_dir:
        print(f"No exam files found in {args.exam_dir}")
        return

    # Process each exam
    for exam_file in exam_files:
        print(f"\nLoading exam: {exam_file}")
        try:
            exam = tester.load_exam(str(exam_file))
        except Exception as e:
            print(f"Error loading exam: {e}")
            continue

        if args.compare:
            # Compare predefined models
            models = [
                {"model_name": "gpt-4o-mini", "provider": "openai"},
                {"model_name": "gpt-4o", "provider": "openai"},
            ]

            # Add Yandex if credentials available
            if settings.yandex_cloud_api_key and settings.yandex_folder_id:
                models.append({"model_name": "yandexgpt-lite", "provider": "yandex"})
                models.append({"model_name": "yandexgpt", "provider": "yandex"})

            print(f"\nTesting {len(models)} models on {exam.exam_id}...")
            results = tester.batch_test_models(
                exam=exam,
                models=models,
                output_dir=args.output_dir,
                language=args.language
            )

            if results:
                comparison = tester.compare_models(results, output_dir=args.output_dir)
                print_comparison(comparison)

                if "comparison_file" in comparison:
                    print(f"\nComparison saved to: {comparison['comparison_file']}")

        else:
            # Test single model
            print(f"\nTesting {args.model} on {exam.exam_id}...")
            result = tester.test_model_on_exam(
                exam=exam,
                model_name=args.model,
                provider=args.provider,
                output_dir=args.output_dir,
                language=args.language
            )

            print_result(result)

            # Save result
            output_file = tester.save_result(result, output_dir=args.output_dir)
            print(f"\nResults saved to: {output_file}")

    print("\n" + "="*60)
    print("Testing complete!")


if __name__ == "__main__":
    main()
