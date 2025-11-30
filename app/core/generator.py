"""
Question generator using OpenAI for creating exam questions from educational content.
"""
import random
import uuid
from typing import List
from app.core.parser import ParsedDocument, ParsedSection
from app.models.schemas import (
    Question, Exam, ExamConfig, SourceReference, QuestionMeta
)
from app.services.openai_client import OpenAIClient


class QuestionGenerator:
    """Generates exam questions from parsed educational content."""

    def __init__(self):
        """Initialize generator with OpenAI client."""
        self.openai_client = OpenAIClient()

    def generate(
        self,
        document: ParsedDocument,
        config: ExamConfig,
        exam_id: str
    ) -> Exam:
        """
        Generate an exam from parsed document.

        Args:
            document: Parsed educational content
            config: Configuration for exam generation
            exam_id: Unique identifier for the exam

        Returns:
            Generated Exam with questions

        Raises:
            ValueError: If document has no content
        """
        if not document.sections or len(document.sections) == 0:
            raise ValueError("Document must have at least one section to generate questions")

        # Set random seed if provided
        if config.seed is not None:
            random.seed(config.seed)

        # Calculate number of each question type
        num_single = int(config.total_questions * config.single_choice_ratio)
        num_multiple = int(config.total_questions * config.multiple_choice_ratio)
        num_open_ended = config.total_questions - num_single - num_multiple

        # Generate questions
        questions: List[Question] = []
        question_counter = 0

        # Generate single choice questions
        for i in range(num_single):
            question = self._generate_single_question(
                document=document,
                question_type="single_choice",
                question_num=question_counter,
                difficulty=config.difficulty
            )
            questions.append(question)
            question_counter += 1

        # Generate multiple choice questions
        for i in range(num_multiple):
            question = self._generate_single_question(
                document=document,
                question_type="multiple_choice",
                question_num=question_counter,
                difficulty=config.difficulty
            )
            questions.append(question)
            question_counter += 1

        # Generate open-ended questions
        for i in range(num_open_ended):
            question = self._generate_single_question(
                document=document,
                question_type="open_ended",
                question_num=question_counter,
                difficulty=config.difficulty
            )
            questions.append(question)
            question_counter += 1

        # Shuffle questions if seed is set (for determinism testing)
        if config.seed is not None:
            random.shuffle(questions)

        return Exam(
            exam_id=exam_id,
            questions=questions,
            config_used=config
        )

    def _generate_single_question(
        self,
        document: ParsedDocument,
        question_type: str,
        question_num: int,
        difficulty: str
    ) -> Question:
        """
        Generate a single question.

        Args:
            document: Source document
            question_type: "single_choice", "multiple_choice", or "open_ended"
            question_num: Question number for ID
            difficulty: Difficulty level or "mixed"

        Returns:
            Generated Question
        """
        # Select a random section for this question
        section = random.choice(document.sections)

        # Determine difficulty
        if difficulty == "mixed":
            actual_difficulty = random.choice(["easy", "medium", "hard"])
        else:
            actual_difficulty = difficulty

        # Generate question using OpenAI
        try:
            result = self.openai_client.generate_question(
                content=section.content,
                question_type=question_type,
                difficulty=actual_difficulty
            )

            # Create source reference
            source_ref = SourceReference(
                file=document.title or "unknown",
                heading=section.heading,
                start=section.start_pos,
                end=section.end_pos
            )

            # Create question based on type
            if question_type == "open_ended":
                question = Question(
                    id=f"q-{question_num + 1:03d}",
                    type=question_type,
                    stem=result["stem"],
                    options=None,
                    correct=None,
                    reference_answer=result["reference_answer"],
                    rubric=result["rubric"],
                    source_refs=[source_ref],
                    meta=QuestionMeta(
                        difficulty=actual_difficulty,
                        tags=[section.heading] if section.heading else []
                    )
                )
            else:
                # Single or multiple choice
                question = Question(
                    id=f"q-{question_num + 1:03d}",
                    type=question_type,
                    stem=result["stem"],
                    options=result["options"],
                    correct=result["correct"],
                    reference_answer=None,
                    rubric=None,
                    source_refs=[source_ref],
                    meta=QuestionMeta(
                        difficulty=actual_difficulty,
                        tags=[section.heading] if section.heading else []
                    )
                )

            return question

        except Exception as e:
            # Fallback to simple question if OpenAI fails
            raise RuntimeError(f"Failed to generate question {question_num}: {str(e)}")

    def _create_fallback_question(
        self,
        section: ParsedSection,
        question_type: str,
        question_num: int,
        difficulty: str
    ) -> Question:
        """
        Create a simple fallback question if OpenAI fails.

        This is used as a safety mechanism during development.
        """
        if question_type == "single_choice":
            correct = [0]
        else:
            correct = [0, 1]

        source_ref = SourceReference(
            file="fallback",
            heading=section.heading,
            start=section.start_pos,
            end=section.end_pos
        )

        return Question(
            id=f"q-{question_num + 1:03d}",
            type=question_type,
            stem=f"Question about: {section.heading}",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct=correct,
            source_refs=[source_ref],
            meta=QuestionMeta(difficulty=difficulty, tags=[section.heading])
        )
