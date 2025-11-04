"""
Exam generation endpoint.
"""
import json
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.schemas import GenerateRequest, Exam, ExamConfig
from app.config import settings

router = APIRouter()

# TODO: Will be implemented with question generator
# from app.core.generator import QuestionGenerator
# generator = QuestionGenerator()


@router.post("/api/generate", response_model=Exam, tags=["generation"])
async def generate_exam(request: GenerateRequest):
    """
    Generate an exam from Markdown content.

    Args:
        request: GenerateRequest with markdown content and optional config

    Returns:
        Generated Exam with questions

    Raises:
        HTTPException: If generation fails
    """
    # Use provided config or defaults
    config = request.config or ExamConfig()

    # Generate unique exam ID
    exam_id = f"ex-{uuid.uuid4().hex[:8]}"

    # TODO: Replace with actual question generator
    # For now, return placeholder to make API functional
    raise HTTPException(
        status_code=501,
        detail="Question generator not yet implemented. Coming soon!"
    )

    # Future implementation:
    # try:
    #     exam = generator.generate(
    #         markdown_content=request.markdown_content,
    #         config=config,
    #         exam_id=exam_id
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"Generation failed: {str(e)}"
    #     )
    #
    # # Save exam to file
    # try:
    #     exam_file = Path(settings.output_dir) / f"exam_{exam_id}.json"
    #     with open(exam_file, 'w', encoding='utf-8') as f:
    #         json.dump(exam.model_dump(), f, ensure_ascii=False, indent=2)
    # except Exception as e:
    #     print(f"Warning: Failed to save exam: {e}")
    #
    # return exam
