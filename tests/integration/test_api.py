"""
Integration tests for FastAPI endpoints.
"""
import json
from pathlib import Path

import pytest

from app.api import files as files_api
from app.config import settings
from app.models.schemas import Exam, ExamConfig, Question
from tests.utils import SyncASGIClient

client = SyncASGIClient()


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Test health endpoint returns OK."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestGradeEndpoint:
    """Tests for grading endpoint."""

    @pytest.fixture(autouse=True)
    def setup_test_exam(self):
        """Create a test exam file before each test."""
        # Create test exam
        q1 = Question(
            id="q1",
            type="single_choice",
            stem="What is 2+2?",
            options=["3", "4", "5"],
            correct=[1]
        )
        q2 = Question(
            id="q2",
            type="multiple_choice",
            stem="Select even numbers:",
            options=["1", "2", "3", "4"],
            correct=[1, 3]
        )

        exam = Exam(
            exam_id="test-exam-123",
            questions=[q1, q2],
            config_used=ExamConfig()
        )

        # Save to file
        exam_file = Path(settings.output_dir) / "exam_test-exam-123.json"
        with open(exam_file, 'w', encoding='utf-8') as f:
            json.dump(exam.model_dump(), f)

        yield

        # Cleanup
        exam_file.unlink(missing_ok=True)
        grade_file = Path(settings.output_dir) / "grade_test-exam-123.json"
        grade_file.unlink(missing_ok=True)

    def test_grade_all_correct(self):
        """Test grading with all correct answers."""
        request_data = {
            "exam_id": "test-exam-123",
            "answers": [
                {"question_id": "q1", "choice": [1]},
                {"question_id": "q2", "choice": [1, 3]}
            ]
        }

        response = client.post("/api/grade", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["exam_id"] == "test-exam-123"
        assert data["summary"]["total"] == 2
        assert data["summary"]["correct"] == 2
        assert data["summary"]["score_percent"] == 100.0

    def test_grade_partial_correct(self):
        """Test grading with some incorrect answers."""
        request_data = {
            "exam_id": "test-exam-123",
            "answers": [
                {"question_id": "q1", "choice": [0]},  # Wrong
                {"question_id": "q2", "choice": [1, 3]}  # Correct
            ]
        }

        response = client.post("/api/grade", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["correct"] == 1
        assert data["summary"]["score_percent"] == 50.0

    def test_grade_nonexistent_exam(self):
        """Test grading with non-existent exam ID."""
        request_data = {
            "exam_id": "nonexistent",
            "answers": [
                {"question_id": "q1", "choice": [1]}
            ]
        }

        response = client.post("/api/grade", json=request_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_grade_invalid_question_id(self):
        """Test grading with invalid question ID."""
        request_data = {
            "exam_id": "test-exam-123",
            "answers": [
                {"question_id": "invalid", "choice": [0]}
            ]
        }

        response = client.post("/api/grade", json=request_data)
        assert response.status_code == 400

    def test_grade_saves_results_to_file(self):
        """Test that grading results are saved to file."""
        request_data = {
            "exam_id": "test-exam-123",
            "answers": [
                {"question_id": "q1", "choice": [1]},
                {"question_id": "q2", "choice": [1, 3]}
            ]
        }

        response = client.post("/api/grade", json=request_data)
        assert response.status_code == 200

        # Check that grade file was created
        grade_file = Path(settings.output_dir) / "grade_test-exam-123.json"
        assert grade_file.exists()

        # Verify content
        with open(grade_file, 'r') as f:
            data = json.load(f)
            assert data["exam_id"] == "test-exam-123"
            assert data["summary"]["score_percent"] == 100.0


class TestGenerateEndpoint:
    """Tests for generate endpoint."""

    def test_generate_returns_exam(self):
        """Test that generate endpoint creates an exam."""
        request_data = {
            "markdown_content": """# Medical Topic

## Symptoms
Fever is a common symptom. Temperature above 38°C indicates fever.
Cough can be dry or productive. Headache may accompany fever.

## Treatment
Paracetamol 500mg every 6 hours for fever reduction.
Rest and hydration are important for recovery.
""",
            "config": {
                "single_choice_count": 2,
                "multiple_choice_count": 1,
                "open_ended_count": 0,
                "provider": "local"
            }
        }

        response = client.post("/api/generate", json=request_data)

        # Should succeed with 200
        assert response.status_code == 200

        data = response.json()
        assert "exam_id" in data
        assert "questions" in data
        assert len(data["questions"]) == 3

        # Verify question structure
        for question in data["questions"]:
            assert "id" in question
            assert "type" in question
            assert "stem" in question
            assert "options" in question
            assert "correct" in question
            assert len(question["options"]) >= 3

    def test_generate_with_empty_content(self):
        """Test that generate rejects empty markdown."""
        request_data = {
            "markdown_content": ""
        }

        response = client.post("/api/generate", json=request_data)
        # Pydantic validation returns 422 for empty string
        assert response.status_code == 422


class TestFilesEndpoints:
    """Tests for file upload and listing endpoints."""

    def test_upload_list_and_read_file(self, tmp_path, monkeypatch):
        """Upload a file and then list and read it back."""
        monkeypatch.setattr(files_api, "UPLOAD_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)

        content = b"# Title\n\nBody"
        response = client.post(
            "/api/upload",
            files={"file": ("example.md", content, "text/markdown")}
        )
        assert response.status_code == 200
        assert response.json()["filename"] == "example.md"

        response = client.get("/api/files")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["files"][0]["filename"] == "example.md"

        response = client.get("/api/files/example.md")
        assert response.status_code == 200
        assert response.json()["content"] == content.decode("utf-8")

    def test_upload_rejects_non_markdown(self, tmp_path, monkeypatch):
        """Reject non-markdown uploads."""
        monkeypatch.setattr(files_api, "UPLOAD_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)

        response = client.post(
            "/api/upload",
            files={"file": ("example.txt", b"plain", "text/plain")}
        )
        assert response.status_code == 400

    def test_upload_accepts_pdf_and_creates_markdown(self, tmp_path, monkeypatch):
        """Accept PDF uploads and create a markdown conversion."""
        monkeypatch.setattr(files_api, "UPLOAD_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)

        def fake_convert(pdf_path, output_dir):
            markdown_path = output_dir / "example.md"
            markdown_path.write_text("# example\n\nPDF extracted text\n", encoding="utf-8")
            return markdown_path

        monkeypatch.setattr(files_api, "convert_pdf_to_markdown", fake_convert)

        response = client.post(
            "/api/upload",
            files={"file": ("example.pdf", b"%PDF-1.4 fake", "application/pdf")}
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["filename"] == "example.pdf"
        assert payload["markdown_filename"].endswith(".md")

        response = client.get("/api/files")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        filenames = [item["filename"] for item in data["files"]]
        assert filenames == sorted(filenames, key=str.lower)
        assert "example.pdf" in filenames
        assert "example.md" in filenames

        response = client.get(f"/api/files/{payload['markdown_filename']}")
        assert response.status_code == 200
        assert "PDF extracted text" in response.json()["content"]

        response = client.get("/api/files/example.pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_upload_with_custom_name(self, tmp_path, monkeypatch):
        """Store uploaded file using a custom name."""
        monkeypatch.setattr(files_api, "UPLOAD_DIR", tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)

        response = client.post(
            "/api/upload?name=custom-doc",
            files={"file": ("example.md", b"# Title", "text/markdown")}
        )
        assert response.status_code == 200
        assert response.json()["filename"] == "custom-doc.md"


class TestExamsEndpoints:
    """Tests for exam listing endpoints."""

    def test_list_and_get_exam(self, tmp_path, monkeypatch):
        """List exams and fetch a specific exam by ID."""
        monkeypatch.setattr(settings, "output_dir", str(tmp_path))
        exam_path = tmp_path / "exam_abc.json"
        with open(exam_path, "w", encoding="utf-8") as f:
            json.dump(
                {"exam_id": "abc", "questions": [], "config_used": {}},
                f
            )

        response = client.get("/api/exams")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["exams"][0]["exam_id"] == "abc"

        response = client.get("/api/exams/abc")
        assert response.status_code == 200
        assert response.json()["exam_id"] == "abc"


class TestOpenAPISchema:
    """Tests for OpenAPI documentation."""

    def test_openapi_schema_available(self):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_docs_ui_available(self):
        """Test that Swagger UI is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_ui_available(self):
        """Test that ReDoc UI is available."""
        response = client.get("/redoc")
        assert response.status_code == 200
