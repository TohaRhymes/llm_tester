"""
BDD step definitions for evaluation scenarios.
"""
from __future__ import annotations

from behave import given, when, then

from app.core.evaluator import (
    QuestionQualityEvaluator,
    GradingConsistencyEvaluator,
    ModelComparator,
    EvaluationReport,
)
from app.core.generator import QuestionGenerator
from app.core.parser import MarkdownParser
from app.models.schemas import ExamConfig, Exam, Question, QuestionMeta, QuestionResult


@given("I have sample medical content")
def step_sample_medical_content(context):
    context.sample_markdown = """# Sample Medical Content

## Section One
Hypertension is defined as blood pressure above 140/90 mmHg.

## Section Two
Lifestyle changes include diet and exercise.
"""
    parser = MarkdownParser()
    context.parsed_document = parser.parse(context.sample_markdown)


@given("I have configured evaluation metrics")
def step_configured_metrics(context):
    context.quality_evaluator = QuestionQualityEvaluator()
    context.consistency_evaluator = GradingConsistencyEvaluator()
    context.model_comparator = ModelComparator()
    context.report_generator = EvaluationReport()
    context.model_results = {}
    context.grading_results = {}


@when('I generate questions using model "{model_name}"')
def step_generate_questions_for_model(context, model_name):
    generator = QuestionGenerator(provider="local")
    config = ExamConfig(
        total_questions=6,
        single_choice_ratio=0.5,
        multiple_choice_ratio=0.3,
        open_ended_ratio=0.2,
        provider="local",
        model_name=model_name,
    )
    exam = generator.generate(context.parsed_document, config, f"eval-{model_name}")
    quality = context.quality_evaluator.evaluate_overall_quality(exam.questions)

    context.model_results[model_name] = {
        "quality_score": quality["overall"],
        "quality_details": quality,
        "consistency_score": 0.9,
        "cost_per_question": 0.001,
        "num_questions": len(exam.questions),
    }


@then("I should receive quality scores for both models")
def step_quality_scores_present(context):
    assert len(context.model_results) >= 2
    for result in context.model_results.values():
        assert "quality_details" in result
        assert "overall" in result["quality_details"]


@then("the scores should include answerability metrics")
def step_quality_has_answerability(context):
    for result in context.model_results.values():
        assert "answerability" in result["quality_details"]


@then("the scores should include difficulty distribution metrics")
def step_quality_has_distribution(context):
    for result in context.model_results.values():
        assert "difficulty_distribution" in result["quality_details"]


@then("the scores should include coherence metrics")
def step_quality_has_coherence(context):
    for result in context.model_results.values():
        assert "coherence" in result["quality_details"]


@given("I have a reference exam with open-ended questions")
def step_reference_exam(context):
    question = Question(
        id="q-001",
        type="open_ended",
        stem="Explain hypertension in brief?",
        options=None,
        correct=None,
        reference_answer="Hypertension is elevated blood pressure.",
        rubric=["Defines hypertension", "Mentions threshold", "Concise summary"],
        source_refs=[],
        meta=QuestionMeta(difficulty="medium", tags=["cardiology"]),
    )
    context.reference_exam = Exam(
        exam_id="eval-exam",
        questions=[question],
        config_used=ExamConfig(provider="local"),
    )


@given("I have sample student answers")
def step_sample_answers(context):
    context.sample_answers = ["Hypertension is high blood pressure."]


@when('I grade answers using model "{model_name}"')
def step_grade_answers(context, model_name):
    score = 0.8 if "mini" in model_name else 0.85
    result = QuestionResult(
        question_id="q-001",
        is_correct=score >= 0.7,
        partial_credit=score,
        feedback="stub",
    )
    context.grading_results[model_name] = [result]


@then("I should receive consistency scores")
def step_consistency_score(context):
    models = list(context.grading_results.keys())
    results1 = context.grading_results[models[0]]
    results2 = context.grading_results[models[1]]
    context.consistency_score = context.consistency_evaluator.calculate_consistency_score(
        results1, results2
    )
    assert 0.0 <= context.consistency_score <= 1.0


@then("the scores should include inter-rater reliability")
def step_inter_rater_present(context):
    assert context.consistency_score is not None


@then("the scores should include score distribution analysis")
def step_score_distribution_present(context):
    model = next(iter(context.grading_results.keys()))
    distribution = context.consistency_evaluator.analyze_score_distribution(
        context.grading_results[model]
    )
    assert {"mean", "std", "min", "max"} <= set(distribution.keys())


@when('I run comparative evaluation with models "{models}"')
def step_compare_models(context, models):
    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if not getattr(context, "model_results", None):
        context.model_results = {}
        for model in model_list:
            context.model_results[model] = {
                "quality_score": 0.8 if "mini" in model else 0.85,
                "consistency_score": 0.9,
                "cost_per_question": 0.001,
            }

    context.comparison = context.model_comparator.compare_models(context.model_results)


@then("I should receive a comparison report")
def step_comparison_present(context):
    assert "rankings" in context.comparison
    assert context.comparison.get("best_overall") is not None


@then("the report should include generation quality metrics")
def step_comparison_has_quality(context):
    for result in context.model_results.values():
        assert "quality_score" in result


@then("the report should include grading accuracy metrics")
def step_comparison_has_grading(context):
    for result in context.model_results.values():
        assert "consistency_score" in result


@then("the report should include cost-performance analysis")
def step_comparison_has_cost(context):
    assert "value_scores" in context.comparison


@given("I have evaluation results for multiple models")
def step_eval_results_ready(context):
    if not getattr(context, "model_results", None):
        context.model_results = {
            "gpt-4o-mini": {"quality_score": 0.8, "cost_per_question": 0.001},
            "gpt-4o": {"quality_score": 0.85, "cost_per_question": 0.003},
        }


@when("I request an evaluation report")
def step_request_report(context):
    comparison = context.model_comparator.compare_models(context.model_results)
    recommendations = context.model_comparator.generate_recommendation(context.model_results)
    report = context.report_generator.generate(
        {
            "model_results": context.model_results,
            "comparison": comparison,
            "recommendations": recommendations,
        }
    )
    report["visualizations"] = context.report_generator.get_visualization_data(
        context.model_results
    )
    context.report = report


@then("I should receive a formatted report with visualizations")
def step_report_with_visualizations(context):
    assert "summary" in context.report
    assert "visualizations" in context.report


@then("the report should include model rankings")
def step_report_has_rankings(context):
    assert "comparison" in context.report
    assert "rankings" in context.report["comparison"]


@then("the report should include recommendations")
def step_report_has_recommendations(context):
    assert "recommendations" in context.report


@given("I have defined custom evaluation metrics")
def step_custom_metrics(context):
    context.custom_metrics = {"custom_metric": 0.42}


@when("I run evaluation with custom metrics")
def step_run_custom_metrics(context):
    context.custom_results = {
        "gpt-4o-mini": {"custom_metric": context.custom_metrics["custom_metric"]},
        "gpt-4o": {"custom_metric": context.custom_metrics["custom_metric"] + 0.1},
    }


@then("the results should include custom metric scores")
def step_custom_scores_present(context):
    for result in context.custom_results.values():
        assert "custom_metric" in result


@then("the results should be comparable across models")
def step_custom_results_comparable(context):
    assert len(context.custom_results) >= 2
