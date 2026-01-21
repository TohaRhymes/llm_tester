"""
Research metrics for prompt and RAG experiments.
"""
from __future__ import annotations

from typing import Dict, Any, List

from app.core.evaluator import QuestionQualityEvaluator
from app.core.validator import QuestionValidator
from app.models.schemas import Exam
from app.core.parser import ParsedDocument


def compute_generation_metrics(exam: Exam, document: ParsedDocument) -> Dict[str, Any]:
    evaluator = QuestionQualityEvaluator()
    validator = QuestionValidator()

    quality = evaluator.evaluate_overall_quality(exam.questions)
    grounding = validator.validate_exam(exam, document)

    counts = {
        "total": len(exam.questions),
        "single_choice": sum(1 for q in exam.questions if q.type == "single_choice"),
        "multiple_choice": sum(1 for q in exam.questions if q.type == "multiple_choice"),
        "open_ended": sum(1 for q in exam.questions if q.type == "open_ended"),
    }

    return {
        "quality": quality,
        "grounding": {
            "grounded_ratio": grounding.grounded_ratio,
            "section_coverage": grounding.section_coverage,
            "issues": grounding.issues,
        },
        "counts": counts,
    }


def compute_ragas_metrics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute RAGAS metrics if available. Returns disabled metadata otherwise.
    """
    try:
        from ragas import evaluate  # type: ignore
        from ragas.metrics import (  # type: ignore
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        )
        from datasets import Dataset  # type: ignore
        import os
    except Exception as exc:  # pragma: no cover - optional dependency
        return {"enabled": False, "reason": f"ragas unavailable: {exc}"}

    if not samples:
        return {"enabled": False, "reason": "no samples provided"}

    if not os.getenv("OPENAI_API_KEY"):
        return {"enabled": False, "reason": "OPENAI_API_KEY not set"}

    dataset = Dataset.from_list(samples)
    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )

    return {
        "enabled": True,
        "scores": results.to_pandas().mean(numeric_only=True).to_dict(),
    }
