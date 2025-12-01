"""
Pydantic models for API contracts and data structures.
"""
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceReference(BaseModel):
    """Reference to source material in Markdown file."""
    file: str = Field(..., description="Source Markdown file path")
    heading: Optional[str] = Field(None, description="Section heading")
    start: int = Field(..., description="Start character position", ge=0)
    end: int = Field(..., description="End character position", ge=0)

    @field_validator('end')
    @classmethod
    def validate_end_after_start(cls, v: int, info) -> int:
        if 'start' in info.data and v < info.data['start']:
            raise ValueError('end must be >= start')
        return v


class QuestionMeta(BaseModel):
    """Metadata for a question."""
    difficulty: Literal["easy", "medium", "hard"] = Field("medium", description="Question difficulty")
    tags: List[str] = Field(default_factory=list, description="Content tags")


class Question(BaseModel):
    """
    Represents a single test question.

    For single_choice: correct contains exactly one index.
    For multiple_choice: correct contains one or more indices.
    For open_ended: options/correct are None, reference_answer and rubric are used.
    """
    id: str = Field(..., description="Unique question identifier")
    type: Literal["single_choice", "multiple_choice", "open_ended"] = Field(..., description="Question type")
    stem: str = Field(..., min_length=1, description="Question text")
    options: Optional[List[str]] = Field(None, description="Answer options (not used for open_ended)")
    correct: Optional[List[int]] = Field(None, description="Indices of correct answers (not used for open_ended)")
    reference_answer: Optional[str] = Field(None, description="Reference answer for open_ended questions")
    rubric: Optional[List[str]] = Field(None, description="Grading criteria for open_ended questions")
    source_refs: List[SourceReference] = Field(default_factory=list, description="Source material references")
    meta: QuestionMeta = Field(default_factory=QuestionMeta, description="Question metadata")

    @field_validator('options')
    @classmethod
    def validate_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        if 'type' in info.data and info.data['type'] == 'open_ended':
            return None  # open_ended doesn't use options

        if v is None:
            raise ValueError('options required for single_choice and multiple_choice')

        if any(not opt.strip() for opt in v):
            raise ValueError('All options must be non-empty')
        if len(v) < 2:
            raise ValueError('Must have at least 2 options')
        if len(v) > 10:
            raise ValueError('Cannot have more than 10 options')
        return v

    @field_validator('correct')
    @classmethod
    def validate_correct_indices(cls, v: Optional[List[int]], info) -> Optional[List[int]]:
        if 'type' in info.data and info.data['type'] == 'open_ended':
            return None  # open_ended doesn't use correct indices

        if v is None or not v:
            raise ValueError('Must have at least one correct answer for single/multiple choice')

        if 'type' in info.data:
            question_type = info.data['type']
            if question_type == 'single_choice' and len(v) != 1:
                raise ValueError('single_choice must have exactly one correct answer')
            if question_type == 'multiple_choice' and len(v) < 1:
                raise ValueError('multiple_choice must have at least one correct answer')

        if 'options' in info.data and info.data['options'] is not None:
            options = info.data['options']
            for idx in v:
                if idx < 0 or idx >= len(options):
                    raise ValueError(f'Correct index {idx} out of range for {len(options)} options')

        return v

    @field_validator('reference_answer')
    @classmethod
    def validate_reference_answer(cls, v: Optional[str], info) -> Optional[str]:
        if 'type' in info.data and info.data['type'] == 'open_ended':
            if not v or not v.strip():
                raise ValueError('reference_answer required for open_ended questions')
        return v


class ExamConfig(BaseModel):
    """Configuration used to generate an exam.

    Supports two input modes:
    1. Count-based (preferred): Specify exact counts for each question type
    2. Ratio-based (legacy): Specify ratios that sum to 1.0

    If counts are provided, they take precedence and ratios are auto-calculated.
    If ratios are provided, counts are auto-calculated from total_questions.
    """
    # Count-based fields (preferred)
    single_choice_count: Optional[int] = Field(None, ge=0, description="Exact number of single choice questions")
    multiple_choice_count: Optional[int] = Field(None, ge=0, description="Exact number of multiple choice questions")
    open_ended_count: Optional[int] = Field(None, ge=0, description="Exact number of open-ended questions")

    # Ratio-based fields (legacy, for backward compatibility)
    total_questions: int = Field(20, ge=1, le=100, description="Number of questions to generate")
    single_choice_ratio: float = Field(0.5, ge=0.0, le=1.0, description="Ratio of single choice questions")
    multiple_choice_ratio: float = Field(0.3, ge=0.0, le=1.0, description="Ratio of multiple choice questions")
    open_ended_ratio: float = Field(0.2, ge=0.0, le=1.0, description="Ratio of open-ended questions")

    difficulty: Literal["easy", "medium", "hard", "mixed"] = Field("mixed", description="Question difficulty")
    language: Literal["en", "ru"] = Field("en", description="Language for questions and prompts (en=English, ru=Russian)")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")

    @model_validator(mode='after')
    def sync_counts_and_ratios(self) -> 'ExamConfig':
        """Synchronize counts and ratios, prioritizing counts if both are provided."""
        # Check if any counts are provided
        has_counts = any([
            self.single_choice_count is not None,
            self.multiple_choice_count is not None,
            self.open_ended_count is not None
        ])

        if has_counts:
            # Count-based mode: counts take precedence
            # Fill in missing counts with 0
            if self.single_choice_count is None:
                self.single_choice_count = 0
            if self.multiple_choice_count is None:
                self.multiple_choice_count = 0
            if self.open_ended_count is None:
                self.open_ended_count = 0

            # Round floats to integers if needed
            self.single_choice_count = round(self.single_choice_count)
            self.multiple_choice_count = round(self.multiple_choice_count)
            self.open_ended_count = round(self.open_ended_count)

            # Validate at least one count is positive
            total_count = self.single_choice_count + self.multiple_choice_count + self.open_ended_count
            if total_count == 0:
                raise ValueError('At least one count must be positive')

            # Validate total doesn't exceed maximum
            if total_count > 100:
                raise ValueError(f'Total questions ({total_count}) exceeds maximum of 100')

            # Calculate total_questions from counts
            self.total_questions = total_count

            # Calculate ratios from counts
            self.single_choice_ratio = self.single_choice_count / total_count
            self.multiple_choice_ratio = self.multiple_choice_count / total_count
            self.open_ended_ratio = self.open_ended_count / total_count
        else:
            # Ratio-based mode: validate ratios and calculate counts
            # Validate ratios sum to 1.0
            total_ratio = self.single_choice_ratio + self.multiple_choice_ratio + self.open_ended_ratio
            if abs(total_ratio - 1.0) > 0.01:
                raise ValueError(f'Ratios must sum to 1.0, got {total_ratio}')

            # Calculate counts from ratios
            # Use floor division and assign remainder to maintain total
            single_count = int(self.total_questions * self.single_choice_ratio)
            multiple_count = int(self.total_questions * self.multiple_choice_ratio)
            open_ended_count = self.total_questions - single_count - multiple_count

            self.single_choice_count = single_count
            self.multiple_choice_count = multiple_count
            self.open_ended_count = open_ended_count

        return self


class Exam(BaseModel):
    """Generated exam with questions."""
    exam_id: str = Field(..., description="Unique exam identifier")
    questions: List[Question] = Field(..., min_length=1, description="List of questions")
    config_used: ExamConfig = Field(..., description="Configuration used for generation")

    @field_validator('questions')
    @classmethod
    def validate_unique_question_ids(cls, v: List[Question]) -> List[Question]:
        ids = [q.id for q in v]
        if len(ids) != len(set(ids)):
            raise ValueError('All question IDs must be unique')
        return v


class StudentAnswer(BaseModel):
    """Student's answer to a question."""
    question_id: str = Field(..., description="Question identifier")
    choice: Optional[List[int]] = Field(None, description="Selected answer indices (for single/multiple choice)")
    text_answer: Optional[str] = Field(None, description="Text answer (for open_ended)")

    @field_validator('text_answer')
    @classmethod
    def validate_answer_present(cls, v: Optional[str], info) -> Optional[str]:
        # At least one of choice or text_answer must be present
        if 'choice' not in info.data or info.data['choice'] is None:
            if v is None or not v.strip():
                raise ValueError('Either choice or text_answer must be provided')
        return v


class GradeRequest(BaseModel):
    """Request to grade exam answers."""
    exam_id: str = Field(..., description="Exam identifier")
    answers: List[StudentAnswer] = Field(..., min_length=1, description="Student answers")


class QuestionResult(BaseModel):
    """Grading result for a single question."""
    question_id: str = Field(..., description="Question identifier")
    is_correct: bool = Field(..., description="Whether answer is correct")
    expected: Optional[List[int]] = Field(None, description="Expected correct indices (for choice questions)")
    given: Optional[List[int]] = Field(None, description="Student's answer indices (for choice questions)")
    given_text: Optional[str] = Field(None, description="Student's text answer (for open_ended)")
    partial_credit: float = Field(0.0, ge=0.0, le=1.0, description="Partial credit (0.0-1.0)")
    feedback: Optional[str] = Field(None, description="Detailed feedback (for open_ended)")


class GradeSummary(BaseModel):
    """Summary statistics for grading."""
    total: int = Field(..., ge=0, description="Total questions")
    correct: int = Field(..., ge=0, description="Number of correct answers")
    score_percent: float = Field(..., ge=0.0, le=100.0, description="Score percentage")

    @field_validator('correct')
    @classmethod
    def validate_correct_not_exceeds_total(cls, v: int, info) -> int:
        if 'total' in info.data and v > info.data['total']:
            raise ValueError('correct cannot exceed total')
        return v


class GradeResponse(BaseModel):
    """Response with grading results."""
    exam_id: str = Field(..., description="Exam identifier")
    summary: GradeSummary = Field(..., description="Summary statistics")
    per_question: List[QuestionResult] = Field(..., description="Per-question results")


class GenerateRequest(BaseModel):
    """Request to generate an exam."""
    config: Optional[ExamConfig] = Field(None, description="Exam generation configuration")
    markdown_content: str = Field(..., min_length=1, description="Markdown content for question generation")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field("0.1.0", description="API version")
