"""
High-level API for exam generation and manipulation.

This module provides a convenient interface for:
- Generating exams from Markdown files or text
- Generating individual questions
- Saving and loading exams
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Literal

from app.core.parser import MarkdownParser
from app.core.generator import QuestionGenerator
from app.models.schemas import Exam, ExamConfig
from app.services.openai_client import OpenAIClient
from app.services.yandex_client import YandexGPTClient
from app.config import settings


class ExamBuilder:
    """High-level interface for exam generation."""

    def __init__(self):
        """Initialize exam builder."""
        self.parser = MarkdownParser()
        self.generator = QuestionGenerator()

    def from_file(
        self,
        file_path: str,
        total_questions: int = 10,
        single_choice_ratio: float = 0.5,
        multiple_choice_ratio: float = 0.3,
        open_ended_ratio: float = 0.2,
        difficulty: str = "mixed",
        language: str = "en",
        seed: Optional[int] = None,
        exam_id: Optional[str] = None
    ) -> Exam:
        """
        Generate exam from Markdown file.

        Args:
            file_path: Path to Markdown file
            total_questions: Total number of questions
            single_choice_ratio: Ratio of single-choice questions
            multiple_choice_ratio: Ratio of multiple-choice questions
            open_ended_ratio: Ratio of open-ended questions
            difficulty: "easy", "medium", "hard", or "mixed"
            language: "en" or "ru"
            seed: Optional seed for deterministic generation
            exam_id: Optional exam ID (auto-generated if None)

        Returns:
            Exam object

        Example:
            >>> builder = ExamBuilder()
            >>> exam = builder.from_file("content.md", total_questions=20)
            >>> print(f"Generated {len(exam.questions)} questions")
        """
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.from_text(
            markdown_content=content,
            total_questions=total_questions,
            single_choice_ratio=single_choice_ratio,
            multiple_choice_ratio=multiple_choice_ratio,
            open_ended_ratio=open_ended_ratio,
            difficulty=difficulty,
            language=language,
            seed=seed,
            exam_id=exam_id
        )

    def from_text(
        self,
        markdown_content: str,
        total_questions: int = 10,
        single_choice_ratio: float = 0.5,
        multiple_choice_ratio: float = 0.3,
        open_ended_ratio: float = 0.2,
        difficulty: str = "mixed",
        language: str = "en",
        seed: Optional[int] = None,
        exam_id: Optional[str] = None
    ) -> Exam:
        """
        Generate exam from Markdown text content.

        Args:
            markdown_content: Markdown content as string
            total_questions: Total number of questions
            single_choice_ratio: Ratio of single-choice questions
            multiple_choice_ratio: Ratio of multiple-choice questions
            open_ended_ratio: Ratio of open-ended questions
            difficulty: "easy", "medium", "hard", or "mixed"
            language: "en" or "ru"
            seed: Optional seed for deterministic generation
            exam_id: Optional exam ID (auto-generated if None)

        Returns:
            Exam object

        Example:
            >>> builder = ExamBuilder()
            >>> content = "# Topic\\n## Section\\nContent here..."
            >>> exam = builder.from_text(content, total_questions=5)
        """
        # Parse markdown
        document = self.parser.parse(markdown_content)

        # Create config
        config = ExamConfig(
            total_questions=total_questions,
            single_choice_ratio=single_choice_ratio,
            multiple_choice_ratio=multiple_choice_ratio,
            open_ended_ratio=open_ended_ratio,
            difficulty=difficulty,
            language=language,
            seed=seed
        )

        # Generate exam
        if exam_id is None:
            import hashlib
            exam_id = "ex-" + hashlib.md5(
                f"{markdown_content[:100]}{total_questions}".encode()
            ).hexdigest()[:8]

        exam = self.generator.generate(document, config, exam_id)
        return exam

    def save(self, exam: Exam, output_file: Optional[str] = None) -> str:
        """
        Save exam to JSON file.

        Args:
            exam: Exam object to save
            output_file: Path to save file (default: data/out/exam_{exam_id}.json)

        Returns:
            Path to saved file

        Example:
            >>> builder = ExamBuilder()
            >>> exam = builder.from_text("# Topic\\nContent")
            >>> filepath = builder.save(exam)
            >>> print(f"Saved to {filepath}")
        """
        if output_file is None:
            output_dir = Path(settings.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"exam_{exam.exam_id}.json"
        else:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(exam.model_dump(), f, indent=2, ensure_ascii=False)

        return str(output_file)

    def load(self, exam_path: str) -> Exam:
        """
        Load exam from JSON file.

        Args:
            exam_path: Path to exam JSON file

        Returns:
            Exam object

        Example:
            >>> builder = ExamBuilder()
            >>> exam = builder.load("data/out/exam_ex-123.json")
            >>> print(f"Loaded {len(exam.questions)} questions")
        """
        with open(exam_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Exam(**data)


class QuestionFactory:
    """Factory for generating individual questions."""

    @staticmethod
    def generate(
        content: str,
        question_type: Literal["single_choice", "multiple_choice", "open_ended"],
        difficulty: str = "medium",
        provider: Literal["openai", "yandex"] = "openai",
        model_name: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a single question from content.

        Args:
            content: Text content to generate question from
            question_type: "single_choice", "multiple_choice", or "open_ended"
            difficulty: "easy", "medium", or "hard"
            provider: "openai" or "yandex"
            model_name: Optional model name override
            language: "en" or "ru"

        Returns:
            Dictionary with question data

        Example:
            >>> question = QuestionFactory.generate(
            ...     "Machine learning is...",
            ...     question_type="single_choice",
            ...     provider="openai"
            ... )
            >>> print(question["stem"])
        """
        # Get client
        if provider == "openai":
            client = OpenAIClient()
            if model_name:
                client.model = model_name
        elif provider == "yandex":
            client = YandexGPTClient()
            if model_name:
                client.model = model_name
        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Generate question
        return client.generate_question(
            content=content,
            question_type=question_type,
            difficulty=difficulty,
            language=language
        )


# Convenience functions for backward compatibility and ease of use

def generate_exam_from_file(file_path: str, **kwargs) -> Exam:
    """
    Convenience function to generate exam from file.

    Args:
        file_path: Path to Markdown file
        **kwargs: Additional arguments for ExamBuilder.from_file()

    Returns:
        Exam object
    """
    builder = ExamBuilder()
    return builder.from_file(file_path, **kwargs)


def generate_exam_from_text(markdown_content: str, **kwargs) -> Exam:
    """
    Convenience function to generate exam from text.

    Args:
        markdown_content: Markdown content as string
        **kwargs: Additional arguments for ExamBuilder.from_text()

    Returns:
        Exam object
    """
    builder = ExamBuilder()
    return builder.from_text(markdown_content, **kwargs)


def generate_question(content: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to generate a single question.

    Args:
        content: Text content
        **kwargs: Additional arguments for QuestionFactory.generate()

    Returns:
        Question dictionary
    """
    return QuestionFactory.generate(content, **kwargs)


def save_exam(exam: Exam, output_file: Optional[str] = None) -> str:
    """
    Convenience function to save exam.

    Args:
        exam: Exam object
        output_file: Optional output file path

    Returns:
        Path to saved file
    """
    builder = ExamBuilder()
    return builder.save(exam, output_file)


def load_exam(exam_path: str) -> Exam:
    """
    Convenience function to load exam.

    Args:
        exam_path: Path to exam JSON file

    Returns:
        Exam object
    """
    builder = ExamBuilder()
    return builder.load(exam_path)
