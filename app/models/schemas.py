"""
Pydantic models for API contracts and data structures.
"""
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


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
    """Configuration used to generate an exam."""
    total_questions: int = Field(20, ge=1, le=100, description="Number of questions to generate")
    single_choice_ratio: float = Field(0.5, ge=0.0, le=1.0, description="Ratio of single choice questions")
    multiple_choice_ratio: float = Field(0.3, ge=0.0, le=1.0, description="Ratio of multiple choice questions")
    open_ended_ratio: float = Field(0.2, ge=0.0, le=1.0, description="Ratio of open-ended questions")
    difficulty: Literal["easy", "medium", "hard", "mixed"] = Field("mixed", description="Question difficulty")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")

    @field_validator('open_ended_ratio')
    @classmethod
    def validate_ratios_sum(cls, v: float, info) -> float:
        if 'single_choice_ratio' in info.data and 'multiple_choice_ratio' in info.data:
            total = info.data['single_choice_ratio'] + info.data['multiple_choice_ratio'] + v
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError(f'Ratios must sum to 1.0, got {total}')
        return v


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
