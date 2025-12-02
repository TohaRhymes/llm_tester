"""
Jupyter-friendly manual for question generation.

This script demonstrates how to generate exam questions using the
high-level API from app.core.exam_builder.

Run in Jupyter:
    %run examples/notebooks/01_question_generation.py

Or import functions:
    from app.core.exam_builder import generate_exam_from_file, generate_question
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import high-level API from app.core
from app.core.exam_builder import (
    generate_exam_from_file,
    generate_exam_from_text,
    generate_question,
    save_exam,
    load_exam
)


# Re-export with simpler names for convenience
generate_exam = generate_exam_from_file
generate_single_question = generate_question


# Example usage (for Jupyter)
if __name__ == "__main__":
    print("Question Generation Examples")
    print("=" * 60)

    # Example 1: Generate full exam from file
    print("\n1. Generating full exam from file...")
    try:
        content_files = list(Path("data/uploads").glob("*.md"))
        if content_files:
            exam = generate_exam_from_file(
                str(content_files[0]),
                total_questions=5,
                language="en"
            )
            print(f"   ✓ Generated {len(exam.questions)} questions")
            print(f"   Exam ID: {exam.exam_id}")

            # Show first question
            if exam.questions:
                q = exam.questions[0]
                print(f"\n   Sample question:")
                print(f"   Type: {q.type}")
                print(f"   Stem: {q.stem[:100]}...")
        else:
            print("   No Markdown files found in data/uploads/")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Example 2: Generate single question from text
    print("\n2. Generating single question from text...")
    try:
        content = """
        The Force is an energy field created by all living things.
        It surrounds us, penetrates us, and binds the galaxy together.
        """

        question = generate_question(
            content,
            question_type="single_choice",
            difficulty="medium",
            provider="openai"
        )

        print(f"   ✓ Generated question")
        print(f"   Stem: {question['stem']}")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Example 3: Generate exam from text (no file)
    print("\n3. Generating exam from text content...")
    try:
        content_text = """
# Machine Learning
Machine learning is AI that learns from data automatically.
"""

        exam = generate_exam_from_text(
            content_text,
            total_questions=3
        )

        print(f"   ✓ Generated {len(exam.questions)} questions from text")
        exam_file = save_exam(exam)
        print(f"   ✓ Saved to: {exam_file}")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Import for use: from app.core.exam_builder import *")
