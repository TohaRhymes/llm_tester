"""
Jupyter-friendly manual for model evaluation.

This script demonstrates how to test models using
app.services.model_answer_tester.

Run in Jupyter:
    %run examples/notebooks/02_model_evaluation.py

Or import functions:
    from app.services.model_answer_tester import ModelAnswerTester
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.model_answer_tester import ModelAnswerTester
from app.core.exam_builder import load_exam


# Convenience wrappers
tester = ModelAnswerTester()


def test_model(exam_file: str, model_name: str, provider: str, **kwargs):
    """Test single model on exam."""
    exam = load_exam(exam_file)
    return tester.test_model_on_exam(exam, model_name, provider, **kwargs)


def compare_models(exam_file: str, models: list, **kwargs):
    """Compare multiple models on exam."""
    exam = load_exam(exam_file)
    return tester.batch_test_models(exam, models, **kwargs)


def analyze_result(result):
    """Print detailed analysis."""
    print("=" * 70)
    print(f"Model: {result.model_name} ({result.provider})")
    print(f"Accuracy: {result.accuracy:.2%}")
    print(f"Correct: {result.correct_count}/{result.total_questions}")


def print_comparison(comparison):
    """Print comparison table."""
    print("\nModel Comparison:")
    for model in comparison["models"]:
        print(f"  {model['model_name']}: {model['accuracy']:.2%}")


# Example usage
if __name__ == "__main__":
    print("Model Evaluation Examples")
    print("=" * 70)

    # Find exams
    exam_files = list(Path("data/out").glob("exam_*.json"))
    if not exam_files:
        print("\nNo exams found. Generate one first!")
        sys.exit(0)

    exam_file = str(exam_files[0])
    print(f"\nUsing: {exam_file}")

    # Test single model
    print("\n1. Testing GPT-4o-mini...")
    try:
        result = test_model(exam_file, "gpt-4o-mini", "openai")
        analyze_result(result)
    except Exception as e:
        print(f"   Error: {e}")

    # Compare models
    print("\n2. Comparing models...")
    try:
        comparison = compare_models(
            exam_file,
            models=[{"model_name": "gpt-4o-mini", "provider": "openai"}]
        )
        print_comparison(comparison)
    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 70)
    print("Import: from app.services.model_answer_tester import ModelAnswerTester")
