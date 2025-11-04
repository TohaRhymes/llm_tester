"""
Grading endpoint for automated answer checking.
"""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.schemas import GradeRequest, GradeResponse, Exam
from app.core.grader import Grader
from app.config import settings

router = APIRouter()
grader = Grader()


@router.post("/api/grade", response_model=GradeResponse, tags=["grading"])
async def grade_exam(request: GradeRequest):
    """
    Grade student answers against exam answer keys.

    Args:
        request: GradeRequest with exam_id and student answers

    Returns:
        GradeResponse with summary and per-question results

    Raises:
        HTTPException: If exam not found or grading fails
    """
    # Load exam from file
    exam_file = Path(settings.output_dir) / f"exam_{request.exam_id}.json"

    if not exam_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Exam '{request.exam_id}' not found"
        )

    try:
        with open(exam_file, 'r', encoding='utf-8') as f:
            exam_data = json.load(f)
            exam = Exam(**exam_data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load exam: {str(e)}"
        )

    # Grade the answers
    try:
        response = grader.grade(exam, request, partial_credit=True)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Grading error: {str(e)}"
        )

    # Save grading results
    try:
        result_file = Path(settings.output_dir) / f"grade_{request.exam_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Failed to save grading results: {e}")

    return response
