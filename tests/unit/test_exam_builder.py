"""
Unit tests for app/core/exam_builder.py.

Tests for high-level exam generation API.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from app.core.exam_builder import (
    ExamBuilder,
    QuestionFactory,
    generate_exam_from_file,
    generate_exam_from_text,
    generate_question,
    save_exam,
    load_exam
)
from app.models.schemas import Exam, Question, ExamConfig


class TestExamBuilder:
    """Tests for ExamBuilder class."""

    def test_init(self):
        """Test ExamBuilder initialization."""
        builder = ExamBuilder()
        assert builder.parser is not None
        assert builder.generator is not None

    @patch("builtins.open", new_callable=mock_open, read_data="# Test\nContent here")
    @patch("app.core.exam_builder.MarkdownParser")
    @patch("app.core.exam_builder.QuestionGenerator")
    def test_from_file(self, mock_generator_class, mock_parser_class, mock_file):
        """Test generating exam from file."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_document = Mock()
        mock_parser.parse.return_value = mock_document

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        # Create mock exam
        mock_exam = Exam(
            exam_id="test-123",
            questions=[
                Question(
                    id="q-1",
                    type="single_choice",
                    stem="Test question",
                    options=["A", "B", "C"],
                    correct=[0],
                    source_refs=[],
                    meta={}
                )
            ],
            config_used=ExamConfig(
                total_questions=5,
                single_choice_ratio=0.5,
                multiple_choice_ratio=0.5,
                open_ended_ratio=0.0
            )
        )
        mock_generator.generate.return_value = mock_exam

        # Test
        builder = ExamBuilder()
        result = builder.from_file(
            "test.md",
            total_questions=5,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.5,
            open_ended_ratio=0.0
        )

        # Assertions
        mock_file.assert_called_once()
        mock_parser.parse.assert_called_once()
        mock_generator.generate.assert_called_once()
        assert result.exam_id == "test-123"
        assert isinstance(result, Exam)

    @patch("app.core.exam_builder.MarkdownParser")
    @patch("app.core.exam_builder.QuestionGenerator")
    def test_from_text(self, mock_generator_class, mock_parser_class):
        """Test generating exam from text."""
        # Setup mocks
        mock_parser = Mock()
        mock_parser_class.return_value = mock_parser
        mock_document = Mock()
        mock_parser.parse.return_value = mock_document

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator

        mock_exam = Exam(
            exam_id="test-456",
            questions=[
                Question(
                    id="q-2",
                    type="single_choice",
                    stem="Another question",
                    options=["X", "Y"],
                    correct=[1],
                    source_refs=[],
                    meta={}
                )
            ],
            config_used=ExamConfig(
                total_questions=3,
                single_choice_ratio=1.0,
                multiple_choice_ratio=0.0,
                open_ended_ratio=0.0
            )
        )
        mock_generator.generate.return_value = mock_exam

        # Test
        builder = ExamBuilder()
        result = builder.from_text(
            "# Content\nText here",
            total_questions=3,
            single_choice_ratio=1.0,
            multiple_choice_ratio=0.0,
            open_ended_ratio=0.0
        )

        # Assertions
        mock_parser.parse.assert_called_once_with("# Content\nText here")
        mock_generator.generate.assert_called_once()
        assert result.exam_id == "test-456"

    def test_from_text_generates_exam_id(self):
        """Test that from_text generates exam_id when not provided."""
        with patch("app.core.exam_builder.MarkdownParser") as mock_parser_class, \
             patch("app.core.exam_builder.QuestionGenerator") as mock_generator_class:

            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse.return_value = Mock()

            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.return_value = Exam(
                exam_id="ex-abc123",
                questions=[
                    Question(
                        id="q-3",
                        type="single_choice",
                        stem="Generated question",
                        options=["A", "B"],
                        correct=[0],
                        source_refs=[],
                        meta={}
                    )
                ],
                config_used=ExamConfig(
                    total_questions=1,
                    single_choice_ratio=1.0,
                    multiple_choice_ratio=0.0,
                    open_ended_ratio=0.0
                )
            )

            builder = ExamBuilder()
            result = builder.from_text("Test content")

            # Exam ID should be generated
            assert result.exam_id is not None
            assert len(result.exam_id) > 0

    @patch("builtins.open", new_callable=mock_open)
    @patch("app.core.exam_builder.settings")
    def test_save_default_path(self, mock_settings, mock_file):
        """Test saving exam with default path."""
        mock_settings.output_dir = "data/out"

        exam = Exam(
            exam_id="test-789",
            questions=[
                Question(
                    id="q-4",
                    type="single_choice",
                    stem="Save test",
                    options=["A", "B"],
                    correct=[0],
                    source_refs=[],
                    meta={}
                )
            ],
            config_used=ExamConfig(
                total_questions=1,
                single_choice_ratio=1.0,
                multiple_choice_ratio=0.0,
                open_ended_ratio=0.0
            )
        )

        builder = ExamBuilder()

        with patch("pathlib.Path.mkdir"):
            result = builder.save(exam)

        assert "exam_test-789.json" in result
        mock_file.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_save_custom_path(self, mock_file):
        """Test saving exam with custom path."""
        exam = Exam(
            exam_id="test-999",
            questions=[
                Question(
                    id="q-5",
                    type="single_choice",
                    stem="Custom path test",
                    options=["A", "B"],
                    correct=[0],
                    source_refs=[],
                    meta={}
                )
            ],
            config_used=ExamConfig(
                total_questions=1,
                single_choice_ratio=1.0,
                multiple_choice_ratio=0.0,
                open_ended_ratio=0.0
            )
        )

        builder = ExamBuilder()

        with patch("pathlib.Path.mkdir"):
            result = builder.save(exam, "/custom/path/exam.json")

        assert result == "/custom/path/exam.json"
        mock_file.assert_called_once()

    def test_load(self):
        """Test loading exam from file."""
        exam_data = {
            "exam_id": "loaded-123",
            "questions": [
                {
                    "id": "q-6",
                    "type": "single_choice",
                    "stem": "Loaded question",
                    "options": ["A", "B"],
                    "correct": [0],
                    "source_refs": [],
                    "meta": {}
                }
            ],
            "config_used": {
                "total_questions": 5,
                "single_choice_ratio": 0.6,
                "multiple_choice_ratio": 0.4,
                "open_ended_ratio": 0.0,
                "difficulty": "medium",
                "language": "en",
                "seed": None
            }
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(exam_data))):
            builder = ExamBuilder()
            result = builder.load("test_exam.json")

        assert isinstance(result, Exam)
        assert result.exam_id == "loaded-123"


class TestQuestionFactory:
    """Tests for QuestionFactory class."""

    @patch("app.core.exam_builder.OpenAIClient")
    def test_generate_with_openai(self, mock_client_class):
        """Test generating question with OpenAI."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.generate_question.return_value = {
            "stem": "Test question?",
            "options": ["A", "B", "C"],
            "correct": [0]
        }

        result = QuestionFactory.generate(
            "Test content",
            question_type="single_choice",
            difficulty="medium",
            provider="openai"
        )

        assert result["stem"] == "Test question?"
        mock_client.generate_question.assert_called_once()

    @patch("app.core.exam_builder.YandexGPTClient")
    def test_generate_with_yandex(self, mock_client_class):
        """Test generating question with YandexGPT."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.generate_question.return_value = {
            "stem": "Yandex question?",
            "options": ["X", "Y", "Z"],
            "correct": [1]
        }

        result = QuestionFactory.generate(
            "Test content",
            question_type="multiple_choice",
            difficulty="hard",
            provider="yandex"
        )

        assert result["stem"] == "Yandex question?"
        mock_client.generate_question.assert_called_once()

    @patch("app.core.exam_builder.OpenAIClient")
    def test_generate_with_custom_model(self, mock_client_class):
        """Test generating question with custom model name."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.generate_question.return_value = {"stem": "Test"}

        QuestionFactory.generate(
            "Content",
            question_type="single_choice",
            provider="openai",
            model_name="gpt-4o"
        )

        # Should set custom model
        assert mock_client.model == "gpt-4o"

    def test_generate_invalid_provider(self):
        """Test generating question with invalid provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            QuestionFactory.generate(
                "Content",
                question_type="single_choice",
                provider="invalid"
            )


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch("app.core.exam_builder.ExamBuilder")
    def test_generate_exam_from_file(self, mock_builder_class):
        """Test generate_exam_from_file convenience function."""
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_exam = Mock()
        mock_builder.from_file.return_value = mock_exam

        result = generate_exam_from_file("test.md", total_questions=10)

        mock_builder.from_file.assert_called_once_with("test.md", total_questions=10)
        assert result == mock_exam

    @patch("app.core.exam_builder.ExamBuilder")
    def test_generate_exam_from_text(self, mock_builder_class):
        """Test generate_exam_from_text convenience function."""
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_exam = Mock()
        mock_builder.from_text.return_value = mock_exam

        result = generate_exam_from_text("# Content", total_questions=5)

        mock_builder.from_text.assert_called_once_with("# Content", total_questions=5)
        assert result == mock_exam

    @patch("app.core.exam_builder.QuestionFactory")
    def test_generate_question(self, mock_factory_class):
        """Test generate_question convenience function."""
        mock_factory_class.generate.return_value = {"stem": "Test?"}

        result = generate_question("Content", question_type="single_choice")

        mock_factory_class.generate.assert_called_once_with(
            "Content",
            question_type="single_choice"
        )
        assert result == {"stem": "Test?"}

    @patch("app.core.exam_builder.ExamBuilder")
    def test_save_exam(self, mock_builder_class):
        """Test save_exam convenience function."""
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_builder.save.return_value = "/path/to/exam.json"

        mock_exam = Mock()
        result = save_exam(mock_exam, "/custom/path.json")

        mock_builder.save.assert_called_once_with(mock_exam, "/custom/path.json")
        assert result == "/path/to/exam.json"

    @patch("app.core.exam_builder.ExamBuilder")
    def test_load_exam(self, mock_builder_class):
        """Test load_exam convenience function."""
        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder
        mock_exam = Mock()
        mock_builder.load.return_value = mock_exam

        result = load_exam("/path/to/exam.json")

        mock_builder.load.assert_called_once_with("/path/to/exam.json")
        assert result == mock_exam
