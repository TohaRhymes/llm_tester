import asyncio
import json
from pathlib import Path

import pytest

from app.api.import_exam import import_exam
from app.config import settings
from app.models.schemas import Exam


@pytest.mark.asyncio
async def test_import_exam_round_trip(tmp_path):
    # Point outputs to temp dir
    original_output_dir = settings.output_dir
    settings.output_dir = str(tmp_path)
    payload = {
        "exam_id": "imported-1",
        "config_used": {"total_questions": 1},
        "questions": [
            {
                "id": "q-001",
                "type": "single_choice",
                "stem": "What is alpha?",
                "options": ["A", "B", "C"],
                "correct": [0],
                "reference_answer": None,
                "rubric": ["Select alpha"],
                "source_refs": [
                    {"file": "Doc", "heading": "Topic", "start": 0, "end": 5}
                ],
                "meta": {"difficulty": "medium", "tags": []},
            }
        ],
    }

    try:
        exam = Exam(**payload)
        saved = await import_exam(exam)
        assert saved.exam_id == exam.exam_id

        exam_file = Path(settings.output_dir) / f"exam_{payload['exam_id']}.json"
        assert exam_file.exists()

        with open(exam_file, "r", encoding="utf-8") as f:
            stored = json.load(f)
        assert stored["exam_id"] == exam.exam_id
    finally:
        settings.output_dir = original_output_dir
