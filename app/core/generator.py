"""
Question generator using LLM provider for creating exam questions from educational content.
"""
import logging
import random
from typing import List, Optional
from app.config import settings
from app.core.parser import ParsedDocument, ParsedSection
from app.models.schemas import (
    Question, Exam, ExamConfig, SourceReference, QuestionMeta
)
from app.services.llm_provider import get_llm_client, LLMProvider, ProviderName
from app.core.validator import QuestionValidator


logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates exam questions from parsed educational content."""

    def __init__(
        self,
        provider: Optional[ProviderName] = None,
        model_name: Optional[str] = None,
        llm_client: Optional[LLMProvider] = None,
        validator: Optional[QuestionValidator] = None,
        max_validation_attempts: int = 3,
        strict_validation: bool = False
    ):
        """Initialize generator with configurable LLM provider."""
        self.provider_name = provider or settings.default_provider
        self.model_name = model_name
        self.llm_client = llm_client
        self.validator = validator or QuestionValidator()
        self.max_validation_attempts = max_validation_attempts
        self.strict_validation = strict_validation

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

        # Calculate number of each question type using resolved counts
        num_single = config.single_choice_count or 0
        num_multiple = config.multiple_choice_count or 0
        num_open_ended = config.open_ended_count or 0

        logger.info(
            "Generating exam %s with provider=%s model=%s counts(single=%s,multi=%s,open=%s) language=%s difficulty=%s",
            exam_id,
            getattr(config, "provider", self.provider_name),
            getattr(config, "model_name", self.model_name),
            num_single,
            num_multiple,
            num_open_ended,
            getattr(config, "language", "en"),
            getattr(config, "difficulty", "mixed"),
        )

        validation = None
        questions: List[Question] = []
        llm_client = self._get_llm_client(config)

        use_rag = getattr(config, "rag_enabled", False)
        sections_pool = None
        if use_rag:
            from app.core.retriever import RAGRetriever

            retriever = RAGRetriever()
            query = getattr(config, "rag_query", None) or document.title or ""
            top_k = getattr(config, "rag_top_k", 3)
            sections_pool = retriever.retrieve_relevant_sections(
                document=document,
                query=query,
                top_k=top_k,
            )

        for attempt in range(self.max_validation_attempts):
            questions = []
            question_counter = 0

            # Generate single choice questions
            for i in range(num_single):
                question = self._generate_single_question(
                    document=document,
                    question_type="single_choice",
                    question_num=question_counter,
                    difficulty=config.difficulty,
                    config=config,
                    llm_client=llm_client,
                    sections_pool=sections_pool
                )
                questions.append(question)
                question_counter += 1

            # Generate multiple choice questions
            for i in range(num_multiple):
                question = self._generate_single_question(
                    document=document,
                    question_type="multiple_choice",
                    question_num=question_counter,
                    difficulty=config.difficulty,
                    config=config,
                    llm_client=llm_client,
                    sections_pool=sections_pool
                )
                questions.append(question)
                question_counter += 1

            # Generate open-ended questions
            for i in range(num_open_ended):
                question = self._generate_single_question(
                    document=document,
                    question_type="open_ended",
                    question_num=question_counter,
                    difficulty=config.difficulty,
                    config=config,
                    llm_client=llm_client,
                    sections_pool=sections_pool
                )
                questions.append(question)
                question_counter += 1

            # Validate generated questions
            validation = self.validator.validate_exam(
                Exam(exam_id=exam_id, questions=questions, config_used=config),
                document
            )
            if validation.valid or not self.strict_validation:
                logger.info(
                    "Validation passed for exam %s (grounded_ratio=%.2f, section_coverage=%.2f, attempt=%d)",
                    exam_id,
                    getattr(validation, "grounded_ratio", 0.0),
                    getattr(validation, "section_coverage", 0.0),
                    attempt + 1,
                )
                break

            # Retry with new seed when not provided
            if config.seed is None and attempt < self.max_validation_attempts - 1:
                logger.warning(
                    "Validation failed for exam %s on attempt %d: %s. Retrying with a new seed.",
                    exam_id,
                    attempt + 1,
                    validation.issues,
                )
                random.seed()
                continue
            break

        if validation and not validation.valid and self.strict_validation:
            logger.error("Validation failed after %d attempts for exam %s: %s", self.max_validation_attempts, exam_id, validation.issues)
            raise RuntimeError("Validation failed after retries")

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
        difficulty: str,
        config: ExamConfig,
        llm_client: LLMProvider,
        sections_pool: Optional[List[ParsedSection]] = None
    ) -> Question:
        """
        Generate a single question.

        Args:
            document: Source document
            question_type: "single_choice", "multiple_choice", or "open_ended"
            question_num: Question number for ID
            difficulty: Difficulty level or "mixed"
            config: Exam configuration for language and other settings

        Returns:
            Generated Question
        """
        # Select a random section for this question
        candidate_sections = sections_pool or document.sections
        section = random.choice(candidate_sections)

        # Determine difficulty
        if difficulty == "mixed":
            actual_difficulty = random.choice(["easy", "medium", "hard"])
        else:
            actual_difficulty = difficulty

        # Get language from config (defaulting to English)
        language = getattr(config, 'language', 'en')

        # Generate question using configured LLM
        try:
            prompt_variant = getattr(config, "prompt_variant", "default")
            result = llm_client.generate_question(
                content=section.content,
                question_type=question_type,
                difficulty=actual_difficulty,
                language=language,
                prompt_variant=prompt_variant
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
                # Single or multiple choice - now includes rubric
                question = Question(
                    id=f"q-{question_num + 1:03d}",
                    type=question_type,
                    stem=result["stem"],
                    options=result["options"],
                    correct=result["correct"],
                    reference_answer=None,
                    rubric=result.get("rubric"),  # Include rubric if provided
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

    def _get_llm_client(self, config: ExamConfig) -> LLMProvider:
        """Return the LLM client for this generation run."""
        provider = getattr(config, "provider", None) or self.provider_name
        model = getattr(config, "model_name", None) or self.model_name

        if self.llm_client:
            return self.llm_client

        return get_llm_client(provider=provider, model_name=model)

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
