"""
Integration tests for FastAPI endpoints.
"""
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import Exam, ExamConfig, Question
from app.config import settings

client = TestClient(app)


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

    def test_generate_returns_not_implemented(self):
        """Test that generate endpoint returns 501 (not implemented yet)."""
        request_data = {
            "markdown_content": "# Test\nSome content"
        }

        response = client.post("/api/generate", json=request_data)
        # Should return 501 until generator is implemented
        assert response.status_code == 501


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
