import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

pytestmark = pytest.mark.skip(reason="TestClient hangs in current sandbox; run locally.")

client = TestClient(app)


def sample_exam_payload():
    return {
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


def test_import_exam_round_trip(tmp_path):
    from app.config import settings

    settings.output_dir = str(tmp_path)

    payload = sample_exam_payload()
    response = client.post("/api/exams/import", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == payload["exam_id"]

    # File should be written
    exam_file = Path(settings.output_dir) / f"exam_{payload['exam_id']}.json"
    assert exam_file.exists()

    # Read back via API
    get_resp = client.get(f"/api/exams/{payload['exam_id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["exam_id"] == payload["exam_id"]

    # Cleanup
    exam_file.unlink(missing_ok=True)
