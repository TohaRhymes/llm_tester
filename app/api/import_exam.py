"""
Endpoint to import externally prepared exams.
"""
import json
from pathlib import Path
import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import Exam
from app.config import settings
from app.utils.path import safe_join

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/exams/import", response_model=Exam, tags=["exams"])
async def import_exam(exam: Exam):
    """
    Import an existing exam JSON and persist it.

    Args:
        exam: Exam payload to store

    Returns:
        Stored exam
    """
    try:
        exam_file = safe_join(Path(settings.output_dir), f"exam_{exam.exam_id}.json")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid exam id")

    try:
        exam_file.parent.mkdir(parents=True, exist_ok=True)
        with open(exam_file, 'w', encoding='utf-8') as f:
            json.dump(exam.model_dump(), f, ensure_ascii=False, indent=2)
        logger.info("Imported exam %s to %s", exam.exam_id, exam_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save exam: {str(e)}")

    return exam
