"""
BDD step definitions for grading functionality.
"""
import json
from pathlib import Path
from behave import given, when, then
from app.models.schemas import Exam, ExamConfig, Question
from app.config import settings
from tests.utils import SyncASGIClient

client = SyncASGIClient()


@given('a test exam with {num:d} questions exists')
def step_create_test_exam(context, num):
    """Create a test exam with specified number of questions."""
    context.exam_id = "bdd-test-exam"

    # Create questions
    questions = [
        Question(
            id="q1",
            type="single_choice",
            stem="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct=[1]
        ),
        Question(
            id="q2",
            type="multiple_choice",
            stem="Select all even numbers:",
            options=["1", "2", "3", "4", "5", "6"],
            correct=[1, 3, 5]
        ),
        Question(
            id="q3",
            type="single_choice",
            stem="Capital of France?",
            options=["London", "Paris", "Berlin"],
            correct=[1]
        ),
    ][:num]

    exam = Exam(
        exam_id=context.exam_id,
        questions=questions,
        config_used=ExamConfig()
    )

    # Save exam to file
    exam_file = Path(settings.output_dir) / f"exam_{context.exam_id}.json"
    with open(exam_file, 'w', encoding='utf-8') as f:
        json.dump(exam.model_dump(), f)

    context.exam = exam


@given('the exam contains single choice and multiple choice questions')
def step_verify_question_types(context):
    """Verify exam has mixed question types."""
    types = [q.type for q in context.exam.questions]
    assert "single_choice" in types
    assert "multiple_choice" in types


@given('a student answers all questions correctly')
def step_create_all_correct_answers(context):
    """Create correct answers for all questions."""
    context.answers = [
        {"question_id": "q1", "choice": [1]},
        {"question_id": "q2", "choice": [1, 3, 5]},
        {"question_id": "q3", "choice": [1]},
    ]


@given('a student answers {correct:d} out of {total:d} questions correctly')
def step_create_partial_correct_answers(context, correct, total):
    """Create answers with some correct and some incorrect."""
    context.answers = [
        {"question_id": "q1", "choice": [1]},  # Correct
        {"question_id": "q2", "choice": [1, 3, 5]},  # Correct
        {"question_id": "q3", "choice": [0]},  # Wrong
    ]


@given('a student partially answers a multiple choice question')
def step_create_partial_multiple_choice_answer(context):
    """Create incomplete answer for multiple choice."""
    context.answers = [
        {"question_id": "q2", "choice": [1, 3]},  # Only 2 out of 3 correct
    ]


@given('no exam exists with ID "{exam_id}"')
def step_ensure_no_exam(context, exam_id):
    """Ensure exam file doesn't exist."""
    context.exam_id = exam_id
    exam_file = Path(settings.output_dir) / f"exam_{exam_id}.json"
    exam_file.unlink(missing_ok=True)


@given('a student answers only {answered:d} out of {total:d} questions')
def step_create_subset_answers(context, answered, total):
    """Create answers for only some questions."""
    context.answers = [
        {"question_id": "q1", "choice": [1]},
        {"question_id": "q2", "choice": [1, 3, 5]},
    ]


@when('I submit answers for grading')
def step_submit_answers_for_grading(context):
    """Submit answers to grading endpoint."""
    request_data = {
        "exam_id": context.exam_id,
        "answers": context.answers
    }
    context.response = client.post("/api/grade", json=request_data)


@when('I submit answers for grading with partial credit enabled')
def step_submit_with_partial_credit(context):
    """Submit answers for grading (partial credit is default)."""
    step_submit_answers_for_grading(context)


@when('I submit answers for the non-existent exam')
def step_submit_for_nonexistent_exam(context):
    """Submit answers for exam that doesn't exist."""
    request_data = {
        "exam_id": context.exam_id,
        "answers": [{"question_id": "q1", "choice": [0]}]
    }
    context.response = client.post("/api/grade", json=request_data)


@when('I submit the partial answers for grading')
def step_submit_partial_answers(context):
    """Submit partial set of answers."""
    step_submit_answers_for_grading(context)


@then('the grading summary shows {score:d}% score')
def step_check_exact_score(context, score):
    """Check that score matches exactly."""
    assert context.response.status_code == 200
    data = context.response.json()
    assert data["summary"]["score_percent"] == float(score)


@then('the grading summary shows approximately {score:d}% score')
def step_check_approximate_score(context, score):
    """Check that score is approximately the expected value."""
    assert context.response.status_code == 200
    data = context.response.json()
    # Allow 10% margin
    actual_score = data["summary"]["score_percent"]
    assert abs(actual_score - score) <= 10.0


@then('all questions are marked as correct')
def step_check_all_correct(context):
    """Verify all questions marked correct."""
    data = context.response.json()
    for result in data["per_question"]:
        assert result["is_correct"] is True


@then('the results are saved to file')
def step_check_results_saved(context):
    """Verify grading results were saved."""
    grade_file = Path(settings.output_dir) / f"grade_{context.exam_id}.json"
    assert grade_file.exists()

    # Cleanup
    grade_file.unlink()
    exam_file = Path(settings.output_dir) / f"exam_{context.exam_id}.json"
    exam_file.unlink(missing_ok=True)


@then('exactly {count:d} questions are marked as correct')
def step_check_correct_count(context, count):
    """Check exact number of correct answers."""
    data = context.response.json()
    assert data["summary"]["correct"] == count


@then('{count:d} question is marked as incorrect')
def step_check_incorrect_count(context, count):
    """Check number of incorrect answers."""
    data = context.response.json()
    total = data["summary"]["total"]
    correct = data["summary"]["correct"]
    incorrect = total - correct
    assert incorrect == count


@then('the question receives partial credit')
def step_check_partial_credit_awarded(context):
    """Verify partial credit was awarded."""
    data = context.response.json()
    result = data["per_question"][0]
    assert result["partial_credit"] > 0.0
    assert result["partial_credit"] < 1.0


@then('the score is between {low:d}% and {high:d}%')
def step_check_score_range(context, low, high):
    """Check score is in range."""
    data = context.response.json()
    score = data["summary"]["score_percent"]
    assert low <= score <= high


@then('I receive a {status_code:d} error')
def step_check_error_status(context, status_code):
    """Check error status code."""
    assert context.response.status_code == status_code


@then('the error message indicates exam not found')
def step_check_error_message(context):
    """Check error message."""
    data = context.response.json()
    assert "not found" in data["detail"].lower()


@then('only the answered questions are graded')
def step_check_only_answered_graded(context):
    """Verify only answered questions in results."""
    data = context.response.json()
    assert len(data["per_question"]) == len(context.answers)


@then('the summary reflects the number of answered questions')
def step_check_summary_count(context):
    """Check summary total matches answered count."""
    data = context.response.json()
    assert data["summary"]["total"] == len(context.answers)
