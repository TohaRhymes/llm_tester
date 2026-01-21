"""
Prompt variant comparison utilities.
"""
from __future__ import annotations

from typing import Dict, List, Any

from app.core.evaluator import QuestionQualityEvaluator
from app.core.generator import QuestionGenerator
from app.core.validator import QuestionValidator
from app.models.schemas import ExamConfig
from app.core.parser import ParsedDocument


class PromptComparator:
    """Compare prompt variants using quality and grounding metrics."""

    def __init__(
        self,
        generator: QuestionGenerator | None = None,
        evaluator: QuestionQualityEvaluator | None = None,
        validator: QuestionValidator | None = None,
    ):
        self.generator = generator or QuestionGenerator()
        self.evaluator = evaluator or QuestionQualityEvaluator()
        self.validator = validator or QuestionValidator()

    def compare_variants(
        self,
        document: ParsedDocument,
        config: ExamConfig,
        variants: List[str],
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {"variants": {}}

        for variant in variants:
            variant_config = config.model_copy(update={"prompt_variant": variant})
            exam = self.generator.generate(document, variant_config, f"prompt-{variant}")
            quality = self.evaluator.evaluate_overall_quality(exam.questions)
            grounding = self.validator.validate_exam(exam, document)

            results["variants"][variant] = {
                "quality": quality,
                "grounding": {
                    "grounded_ratio": grounding.grounded_ratio,
                    "section_coverage": grounding.section_coverage,
                    "issues": grounding.issues,
                },
            }

        return results
