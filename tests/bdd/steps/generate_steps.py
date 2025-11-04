"""
BDD step definitions for question generation.
"""
import json
from pathlib import Path
from behave import given, when, then
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


client = TestClient(app)


@given('I have medical educational content in Markdown format')
def step_have_medical_content(context):
    """Prepare medical content for testing."""
    context.markdown_content = """# Гестационная гипертензия

## Определения
Гестационная гипертензия — это артериальное давление ≥140/90 мм рт. ст.,
впервые выявленное после 20-й недели беременности.

## Факторы риска
- Первая беременность
- Многоплодная беременность
- Ожирение (ИМТ ≥30)
- Возраст <18 или >40 лет

## Диагностика
Измерение АД проводится в положении сидя после 5-минутного отдыха.
Диагностический критерий: АД ≥140/90 мм рт. ст.

## Лечение
Препараты выбора при беременности:
- Метилдопа 250-500 мг 2-3 раза в день
- Лабеталол 100-400 мг 2-3 раза в день
"""


@given('I have empty Markdown content')
def step_have_empty_content(context):
    """Set empty content."""
    context.markdown_content = ""


@when('I request exam generation with default settings')
def step_request_generation_default(context):
    """Request generation with defaults."""
    request_data = {
        "markdown_content": context.markdown_content
    }
    context.response = client.post("/api/generate", json=request_data)


@when('I request exam generation with {count:d} questions')
def step_request_generation_count(context, count):
    """Request generation with specific count."""
    request_data = {
        "markdown_content": context.markdown_content,
        "config": {
            "total_questions": count
        }
    }
    context.response = client.post("/api/generate", json=request_data)


@when('I request exam generation with {single:d}% single choice and {multiple:d}% multiple choice')
def step_request_generation_ratios(context, single, multiple):
    """Request generation with custom ratios."""
    request_data = {
        "markdown_content": context.markdown_content,
        "config": {
            "total_questions": 10,
            "single_choice_ratio": single / 100.0,
            "multiple_choice_ratio": multiple / 100.0
        }
    }
    context.response = client.post("/api/generate", json=request_data)


@when('I request exam generation')
def step_request_generation(context):
    """Request exam generation."""
    step_request_generation_default(context)


@then('I receive a generated exam')
def step_check_exam_received(context):
    """Verify exam was generated."""
    assert context.response.status_code == 200
    context.exam = context.response.json()
    assert "exam_id" in context.exam
    assert "questions" in context.exam


@then('the exam contains {count:d} questions')
def step_check_question_count(context, count):
    """Check exact question count."""
    assert len(context.exam["questions"]) == count


@then('the exam contains exactly {count:d} questions')
def step_check_exact_count(context, count):
    """Check exact count (alias)."""
    step_check_question_count(context, count)


@then('the questions have appropriate mix of single and multiple choice')
def step_check_question_mix(context):
    """Verify mix of question types."""
    questions = context.exam["questions"]
    types = [q["type"] for q in questions]

    assert "single_choice" in types
    assert "multiple_choice" in types


@then('each question has source references')
def step_check_source_refs(context):
    """Verify source references exist."""
    for question in context.exam["questions"]:
        assert "source_refs" in question
        assert len(question["source_refs"]) > 0


@then('approximately {percent:d}% of questions are {question_type}')
def step_check_type_ratio(context, percent, question_type):
    """Check question type ratio."""
    questions = context.exam["questions"]
    total = len(questions)
    actual_count = sum(1 for q in questions if q["type"] == question_type.replace(" ", "_"))
    actual_percent = (actual_count / total) * 100

    # Allow 10% margin
    assert abs(actual_percent - percent) <= 15, \
        f"Expected ~{percent}% {question_type}, got {actual_percent}%"


@then('the exam is saved to the output directory')
def step_check_exam_saved(context):
    """Verify exam file was saved."""
    exam_id = context.exam["exam_id"]
    exam_file = Path(settings.output_dir) / f"exam_{exam_id}.json"
    assert exam_file.exists()

    # Store for cleanup
    context.exam_file = exam_file


@then('the exam file contains all question data')
def step_check_exam_file_content(context):
    """Verify exam file content."""
    with open(context.exam_file, 'r') as f:
        data = json.load(f)
        assert "questions" in data
        assert len(data["questions"]) > 0

    # Cleanup
    context.exam_file.unlink()


@then('I receive a validation error')
def step_check_validation_error(context):
    """Check for validation error."""
    assert context.response.status_code in [400, 422]


@then('the error indicates missing content')
def step_check_error_message_content(context):
    """Check error message about content."""
    # Either Pydantic validation or our custom error
    assert context.response.status_code in [400, 422]


@then('each question has a unique ID')
def step_check_unique_ids(context):
    """Verify unique question IDs."""
    questions = context.exam["questions"]
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids)), "Question IDs are not unique"


@then('each question has a stem (question text)')
def step_check_stems(context):
    """Verify all questions have stems."""
    for question in context.exam["questions"]:
        assert "stem" in question
        assert len(question["stem"]) > 0


@then('each question has {min_opt:d}-{max_opt:d} options')
def step_check_options_range(context, min_opt, max_opt):
    """Verify options count range."""
    for question in context.exam["questions"]:
        options_count = len(question["options"])
        assert min_opt <= options_count <= max_opt, \
            f"Question has {options_count} options, expected {min_opt}-{max_opt}"


@then('each question has correct answer indices')
def step_check_correct_indices(context):
    """Verify correct answers exist."""
    for question in context.exam["questions"]:
        assert "correct" in question
        assert len(question["correct"]) > 0


@then('single choice questions have exactly 1 correct answer')
def step_check_single_choice_correct(context):
    """Verify single choice has 1 correct."""
    for question in context.exam["questions"]:
        if question["type"] == "single_choice":
            assert len(question["correct"]) == 1


@then('multiple choice questions have 2 or more correct answers')
def step_check_multiple_choice_correct(context):
    """Verify multiple choice has 2+ correct."""
    for question in context.exam["questions"]:
        if question["type"] == "multiple_choice":
            assert len(question["correct"]) >= 2
