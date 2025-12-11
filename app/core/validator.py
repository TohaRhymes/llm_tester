"""
Validation utilities for generated exams and questions.
"""
from dataclasses import dataclass
from typing import List

from app.core.parser import ParsedDocument
from app.models.schemas import Exam, Question


@dataclass
class ValidationResult:
    valid: bool
    issues: List[str]


class QuestionValidator:
    """Validates generated exams for basic quality and grounding."""

    def validate_exam(self, exam: Exam, document: ParsedDocument) -> ValidationResult:
        issues: List[str] = []

        stems = set()
        doc_len = len(document.source_text) if document and document.source_text else 0

        for q in exam.questions:
            # Duplicate stems
            if q.stem in stems:
                issues.append(f"Duplicate stem detected: {q.stem[:50]}")
            stems.add(q.stem)

            # Source references
            if not q.source_refs:
                issues.append(f"Question {q.id} missing source_refs")
            else:
                for ref in q.source_refs:
                    if ref.start < 0 or ref.end < 0 or ref.start > ref.end:
                        issues.append(f"Question {q.id} has invalid source span ({ref.start}, {ref.end})")
                    if doc_len and ref.end > doc_len:
                        issues.append(f"Question {q.id} source_refs out of source bounds")

            # Type-specific checks
            if q.type in ("single_choice", "multiple_choice"):
                if not q.options or len(q.options) < 3:
                    issues.append(f"Question {q.id} has insufficient options")
                if not q.correct or any(idx >= len(q.options) or idx < 0 for idx in q.correct):
                    issues.append(f"Question {q.id} has invalid correct indices")
            elif q.type == "open_ended":
                if not q.reference_answer or not q.reference_answer.strip():
                    issues.append(f"Question {q.id} missing reference answer")
                if not q.rubric or len(q.rubric) < 2:
                    issues.append(f"Question {q.id} missing rubric items")

        return ValidationResult(valid=len(issues) == 0, issues=issues)
