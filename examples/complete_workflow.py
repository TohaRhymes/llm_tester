#!/usr/bin/env python3
"""
Complete Workflow Example: Question Generation & Model Evaluation

This script demonstrates the complete workflow:
1. Generate questions from Markdown file
2. Generate questions from text content
3. Test models on generated questions
4. Compare model performance

Usage:
    python examples/complete_workflow.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import functions by loading the modules
import importlib.util

def load_module_from_file(filepath):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location("temp_module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load question generation functions
qgen_module = load_module_from_file(project_root / "examples/notebooks/01_question_generation.py")
generate_exam = qgen_module.generate_exam
generate_single_question = qgen_module.generate_single_question
save_exam = qgen_module.save_exam

# Load model evaluation functions
eval_module = load_module_from_file(project_root / "examples/notebooks/02_model_evaluation.py")
test_model = eval_module.test_model
compare_models = eval_module.compare_models
analyze_result = eval_module.analyze_result
print_comparison = eval_module.print_comparison


def example_1_from_file():
    """Example 1: Generate exam from Markdown file."""
    print("=" * 70)
    print("Example 1: Generate Exam from Markdown File")
    print("=" * 70)

    # Check if we have content files
    content_files = list(Path("data/uploads").glob("*.md"))
    if not content_files:
        print("No Markdown files found in data/uploads/")
        print("Creating example content...")

        # Create example content
        example_content = Path("data/uploads") / "example_content.md"
        example_content.parent.mkdir(parents=True, exist_ok=True)

        with open(example_content, 'w', encoding='utf-8') as f:
            f.write("""# Machine Learning Basics

## What is Machine Learning?

Machine learning is a subset of artificial intelligence that focuses on
algorithms that learn from data. Unlike traditional programming where rules
are explicitly coded, machine learning algorithms discover patterns in data.

## Types of Machine Learning

### Supervised Learning
In supervised learning, the algorithm learns from labeled training data.
Examples include:
- Classification: predicting categories (e.g., spam detection)
- Regression: predicting continuous values (e.g., house prices)

### Unsupervised Learning
Unsupervised learning works with unlabeled data to discover hidden patterns.
Examples include:
- Clustering: grouping similar data points
- Dimensionality reduction: simplifying data while retaining important features

### Reinforcement Learning
Reinforcement learning involves an agent learning through trial and error,
receiving rewards or penalties for actions. Used in robotics, game AI,
and autonomous systems.
""")
        content_files = [example_content]

    # Use first available file
    content_file = str(content_files[0])
    print(f"\nGenerating exam from: {content_file}")

    try:
        exam = generate_exam(
            content_file,
            total_questions=10,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2,
            language="en"
        )

        print(f"✓ Generated {len(exam.questions)} questions")
        print(f"  Exam ID: {exam.exam_id}")

        # Show first question
        if exam.questions:
            q = exam.questions[0]
            print(f"\n  Sample question:")
            print(f"  Type: {q.type}")
            print(f"  Stem: {q.stem}")
            if q.options:
                print(f"  Options: {len(q.options)}")

        # Save exam
        exam_file = save_exam(exam)
        print(f"\n✓ Exam saved to: {exam_file}")

        return exam_file

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def example_2_from_text():
    """Example 2: Generate questions from text content (no file)."""
    print("\n" + "=" * 70)
    print("Example 2: Generate Questions from Text Content")
    print("=" * 70)

    # Direct text content (no file required)
    content = """
    Neural networks are computing systems inspired by biological neural networks.
    They consist of interconnected nodes (neurons) organized in layers:
    the input layer, hidden layers, and output layer. Each connection has
    a weight that adjusts during training through backpropagation.

    Deep learning uses neural networks with multiple hidden layers, allowing
    the model to learn hierarchical representations of data. This has led to
    breakthroughs in computer vision, natural language processing, and speech recognition.
    """

    print("\nGenerating questions from text...")

    try:
        # Generate different types of questions
        questions = []

        # Single choice question
        print("\n1. Generating single-choice question...")
        q1 = generate_single_question(
            content,
            question_type="single_choice",
            difficulty="medium",
            provider="openai"
        )
        questions.append(q1)
        print(f"   ✓ {q1['stem']}")

        # Multiple choice question
        print("\n2. Generating multiple-choice question...")
        q2 = generate_single_question(
            content,
            question_type="multiple_choice",
            difficulty="hard",
            provider="openai"
        )
        questions.append(q2)
        print(f"   ✓ {q2['stem']}")

        # Open-ended question
        print("\n3. Generating open-ended question...")
        q3 = generate_single_question(
            content,
            question_type="open_ended",
            difficulty="medium",
            provider="openai"
        )
        questions.append(q3)
        print(f"   ✓ {q3['stem']}")

        print(f"\n✓ Generated {len(questions)} questions from text")

        return questions

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def example_3_test_models(exam_file):
    """Example 3: Test models on generated exam."""
    if not exam_file or not Path(exam_file).exists():
        print("\n✗ No exam file available for testing")
        return

    print("\n" + "=" * 70)
    print("Example 3: Test Models on Generated Exam")
    print("=" * 70)

    print(f"\nTesting models on: {exam_file}")

    try:
        # Test single model
        print("\n1. Testing GPT-4o-mini...")
        result = test_model(
            exam_file,
            model_name="gpt-4o-mini",
            provider="openai",
            save_results=True
        )

        print(f"   ✓ Accuracy: {result.accuracy:.2%}")
        print(f"   ✓ Correct: {result.correct_count}/{result.total_questions}")

        # Detailed analysis
        print("\n2. Detailed Analysis:")
        analyze_result(result)

    except Exception as e:
        print(f"✗ Error: {e}")


def example_4_compare_models(exam_file):
    """Example 4: Compare multiple models."""
    if not exam_file or not Path(exam_file).exists():
        print("\n✗ No exam file available for comparison")
        return

    print("\n" + "=" * 70)
    print("Example 4: Compare Multiple Models")
    print("=" * 70)

    print(f"\nComparing models on: {exam_file}")

    try:
        # Prepare models list
        models = [
            {"model_name": "gpt-4o-mini", "provider": "openai"},
        ]

        # Add Yandex if available
        from app.config import settings
        if settings.yandex_cloud_api_key and settings.yandex_folder_id:
            models.append({"model_name": "yandexgpt-lite", "provider": "yandex"})
            print(f"\n✓ Testing {len(models)} models (OpenAI + Yandex)")
        else:
            print(f"\n✓ Testing {len(models)} model (OpenAI only)")
            print("   Note: Add Yandex credentials to test YandexGPT")

        # Compare models
        comparison = compare_models(
            exam_file,
            models=models,
            save_results=True
        )

        # Print comparison
        print_comparison(comparison)

        # Show insights
        if "per_question_breakdown" in comparison:
            breakdown = comparison["per_question_breakdown"]
            all_failed = [
                q_id for q_id, data in breakdown.items()
                if not data["models_correct"]
            ]

            if all_failed:
                print(f"\n⚠️  Questions where ALL models failed: {len(all_failed)}")
                print("   These might be good AI-resistant questions!")
            else:
                print("\n✓ All questions were answered correctly by at least one model")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_batch_processing():
    """Example 5: Batch process multiple content files."""
    print("\n" + "=" * 70)
    print("Example 5: Batch Process Multiple Files")
    print("=" * 70)

    # Get all markdown files
    content_files = list(Path("data/uploads").glob("*.md"))

    if len(content_files) <= 1:
        print("\nOnly one content file available. Skipping batch processing.")
        return

    print(f"\nFound {len(content_files)} Markdown files")

    try:
        results = []

        for i, content_file in enumerate(content_files[:3], 1):  # Process first 3
            print(f"\n{i}. Processing {content_file.name}...")

            # Generate exam
            exam = generate_exam(
                str(content_file),
                total_questions=5,
                language="en"
            )

            exam_file = save_exam(exam)

            # Test model
            result = test_model(
                exam_file,
                "gpt-4o-mini",
                "openai",
                save_results=False
            )

            results.append((content_file.name, result.accuracy))
            print(f"   ✓ Accuracy: {result.accuracy:.2%}")

        # Summary
        print("\n" + "-" * 70)
        print("Batch Processing Summary:")
        for name, accuracy in results:
            print(f"  {name}: {accuracy:.2%}")

        avg_accuracy = sum(acc for _, acc in results) / len(results)
        print(f"\n  Average Accuracy: {avg_accuracy:.2%}")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "🚀" * 35)
    print("Complete Workflow Example")
    print("Question Generation & Model Evaluation")
    print("🚀" * 35)

    # Example 1: Generate from file
    exam_file = example_1_from_file()

    # Example 2: Generate from text
    example_2_from_text()

    # Example 3: Test models
    example_3_test_models(exam_file)

    # Example 4: Compare models
    example_4_compare_models(exam_file)

    # Example 5: Batch processing
    example_5_batch_processing()

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("\n✓ All examples completed!")
    print("\nGenerated files:")
    print(f"  - Exams: data/out/exam_*.json")
    print(f"  - Results: data/results/model_*.json")

    print("\nNext steps:")
    print("  - Review generated exams in data/out/")
    print("  - Check evaluation results in data/results/")
    print("  - Try examples in Jupyter: %run examples/complete_workflow.py")
    print("  - Read docs/QUICK_START.md for more examples")


if __name__ == "__main__":
    main()
