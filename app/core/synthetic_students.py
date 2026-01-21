"""
Synthetic student answer generator.
"""
from __future__ import annotations

import random
from typing import Dict, List

from app.models.schemas import Exam


class SyntheticStudentGenerator:
    """Generate synthetic student answers for research evaluation."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def generate_students(self, exam: Exam, count: int = 48) -> List[Dict]:
        profiles = ["strong", "medium", "weak", "guessing"]
        per_profile = count // len(profiles)
        remainder = count % len(profiles)

        students = []
        idx = 0
        for profile in profiles:
            num = per_profile + (1 if remainder > 0 else 0)
            remainder = max(0, remainder - 1)
            for _ in range(num):
                students.append(
                    {
                        "student_id": f"student-{idx:03d}",
                        "profile": profile,
                        "answers": self._generate_answers(exam, profile),
                    }
                )
                idx += 1

        return students[:count]

    def _generate_answers(self, exam: Exam, profile: str) -> List[Dict]:
        accuracy = {
            "strong": 0.85,
            "medium": 0.65,
            "weak": 0.4,
            "guessing": 0.25,
        }[profile]

        answers = []
        for question in exam.questions:
            if question.type == "open_ended":
                answers.append(
                    {
                        "question_id": question.id,
                        "text_answer": self._open_ended_answer(question.reference_answer, accuracy),
                    }
                )
            else:
                answers.append(
                    {
                        "question_id": question.id,
                        "choice": self._choice_answer(question.correct, question.options, accuracy),
                    }
                )
        return answers

    def _choice_answer(self, correct: List[int], options: List[str], accuracy: float) -> List[int]:
        if self._rng.random() <= accuracy:
            return list(correct)

        option_indices = list(range(len(options)))
        incorrect = [i for i in option_indices if i not in correct]
        if not incorrect:
            return list(correct)
        return [self._rng.choice(incorrect)]

    def _open_ended_answer(self, reference: str | None, accuracy: float) -> str:
        if not reference:
            return "No reference provided."

        words = reference.split()
        if not words:
            return "No content."

        if self._rng.random() <= accuracy:
            cutoff = max(4, int(len(words) * 0.7))
            return " ".join(words[:cutoff])

        shuffled = words[:]
        self._rng.shuffle(shuffled)
        return " ".join(shuffled[: max(3, len(shuffled) // 3)])
