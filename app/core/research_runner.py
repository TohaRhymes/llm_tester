"""
Research runner for prompt and RAG experiments.
"""
from __future__ import annotations

from typing import Dict, Any, List

from app.core.generator import QuestionGenerator
from app.core.grader import Grader
from app.core.research_metrics import compute_generation_metrics, compute_ragas_metrics
from app.core.synthetic_students import SyntheticStudentGenerator
from app.models.schemas import ExamConfig, GradeRequest, StudentAnswer
from app.core.parser import ParsedDocument


class ResearchRunner:
    """Run prompt + RAG experiments with synthetic students."""

    def __init__(self):
        self.generator = QuestionGenerator()

    def run(
        self,
        document: ParsedDocument,
        config: ExamConfig,
        prompt_variants: List[str],
        rag_settings: List[Dict[str, Any]],
        student_count: int = 48,
        seed: int = 42,
    ) -> Dict[str, Any]:
        experiments = []
        student_generator = SyntheticStudentGenerator(seed=seed)

        for rag_config in rag_settings:
            for variant in prompt_variants:
                run_config = config.model_copy(update={"prompt_variant": variant, **rag_config})
                exam = self.generator.generate(document, run_config, f"exp-{variant}")

                metrics = compute_generation_metrics(exam, document)
                grading_summary = self._grade_students(exam, student_generator, student_count)
                ragas_metrics = self._ragas_for_exam(exam, grading_summary.get("sample_answers", []))

                experiments.append(
                    {
                        "prompt_variant": variant,
                        "rag": rag_config,
                        "metrics": metrics,
                        "grading_summary": grading_summary["summary"],
                        "ragas": ragas_metrics,
                    }
                )

        return {"experiments": experiments}

    def _grade_students(
        self,
        exam,
        student_generator: SyntheticStudentGenerator,
        student_count: int,
    ) -> Dict[str, Any]:
        grader = Grader(provider=exam.config_used.provider, model_name=exam.config_used.model_name)
        students = student_generator.generate_students(exam, count=student_count)
        scores = []
        open_ended_scores = []
        choice_scores = []
        question_type_map = {question.id: question.type for question in exam.questions}
        sample_answers = []

        for student in students:
            answers = [
                StudentAnswer(**answer)
                for answer in student["answers"]
            ]
            request = GradeRequest(exam_id=exam.exam_id, answers=answers)
            response = grader.grade(exam, request)
            scores.append(response.summary.score_percent)
            for result in response.per_question:
                question_type = question_type_map.get(result.question_id)
                if question_type == "open_ended":
                    open_ended_scores.append(result.partial_credit)
                elif question_type in {"single_choice", "multiple_choice"}:
                    choice_scores.append(result.partial_credit)

            if not sample_answers:
                sample_answers = student["answers"]

        mean_score = sum(scores) / len(scores) if scores else 0.0
        mean_open_ended = sum(open_ended_scores) / len(open_ended_scores) if open_ended_scores else 0.0
        mean_choice = sum(choice_scores) / len(choice_scores) if choice_scores else 0.0
        return {
            "summary": {
                "students": len(students),
                "mean_score": round(mean_score, 2),
                "min_score": round(min(scores), 2) if scores else 0.0,
                "max_score": round(max(scores), 2) if scores else 0.0,
                "open_ended_mean": round(mean_open_ended, 4),
                "choice_mean": round(mean_choice, 4),
            },
            "sample_answers": sample_answers,
        }

    def _ragas_for_exam(self, exam, sample_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        samples = []
        for question in exam.questions:
            if question.type != "open_ended":
                continue

            answer = None
            for sample in sample_answers:
                if sample["question_id"] == question.id:
                    answer = sample.get("text_answer")
                    break

            if not answer:
                continue

            contexts = [ref.heading or "" for ref in question.source_refs] or ["context"]
            samples.append(
                {
                    "question": question.stem,
                    "answer": answer,
                    "contexts": contexts,
                    "ground_truth": question.reference_answer or "",
                }
            )

        return compute_ragas_metrics(samples)
