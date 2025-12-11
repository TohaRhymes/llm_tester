"""
Validation utilities for generated exams and questions.
"""
from dataclasses import dataclass
from typing import List, Set, Tuple

from app.core.parser import ParsedDocument
from app.models.schemas import Exam


@dataclass
class ValidationResult:
    valid: bool
    issues: List[str]
    grounded_ratio: float
    section_coverage: float


class QuestionValidator:
    """Validates generated exams for basic quality and grounding."""

    def validate_exam(self, exam: Exam, document: ParsedDocument) -> ValidationResult:
        issues: List[str] = []

        stems = set()
        doc_text = document.source_text or ""
        doc_len = len(doc_text)
        section_headings: Set[str] = {s.heading for s in document.sections if s.heading}
        referenced_headings: Set[str] = set()
        grounded_count = 0

        doc_terms = self._extract_terms(doc_text)

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
                    if ref.heading:
                        referenced_headings.add(ref.heading)
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

            # Grounding heuristic: stem/reference contains source terms
            question_text = f"{q.stem} {q.reference_answer or ''}"
            overlap = self._overlap_terms(question_text, doc_terms)
            if overlap < 1:
                issues.append(f"Question {q.id} may be ungrounded (no source term overlap)")
            else:
                grounded_count += 1

        grounded_ratio = grounded_count / len(exam.questions) if exam.questions else 0.0
        section_coverage = (
            len(referenced_headings & section_headings) / len(section_headings)
            if section_headings else 0.0
        )

        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            grounded_ratio=round(grounded_ratio, 3),
            section_coverage=round(section_coverage, 3),
        )

    def _extract_terms(self, text: str) -> Set[str]:
        """Return lowercase keywords >=4 chars."""
        import re

        return {t for t in re.findall(r"[A-Za-zА-Яа-я0-9]{4,}", text.lower())}

    def _overlap_terms(self, text: str, doc_terms: Set[str]) -> int:
        terms = self._extract_terms(text)
        return len(terms & doc_terms)
