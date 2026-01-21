"""
Unit tests for model answer evaluation service.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from app.services.model_answer_tester import ModelAnswerTester, ModelTestResult
from app.models.schemas import Question, Exam, QuestionMeta


class TestModelAnswerTester:
    """Test suite for ModelAnswerTester."""

    @pytest.fixture
    def sample_exam(self):
        """Create a sample exam for testing."""
        questions = [
            Question(
                id="q-001",
                type="single_choice",
                stem="What is 2+2?",
                options=["2", "3", "4", "5"],
                correct=[2],
                source_refs=[],
                meta=QuestionMeta(difficulty="easy", tags=["math"])
            ),
            Question(
                id="q-002",
                type="multiple_choice",
                stem="Select all even numbers:",
                options=["1", "2", "3", "4"],
                correct=[1, 3],
                source_refs=[],
                meta=QuestionMeta(difficulty="medium", tags=["math"])
            ),
            Question(
                id="q-003",
                type="open_ended",
                stem="Explain photosynthesis:",
                reference_answer="Photosynthesis is the process by which plants convert light energy into chemical energy.",
                rubric=["Mentions light energy", "Mentions chemical energy", "Mentions plants"],
                source_refs=[],
                meta=QuestionMeta(difficulty="hard", tags=["biology"])
            )
        ]
        return Exam(
            exam_id="test-exam",
            questions=questions,
            config_used={}
        )

    @pytest.fixture
    def tester(self):
        """Create ModelAnswerTester instance."""
        return ModelAnswerTester()

    def test_test_model_on_exam_openai(self, tester, sample_exam, tmp_path):
        """Test evaluating OpenAI model on exam."""
        with patch('app.services.model_answer_tester.get_llm_client') as mock_get_client:
            mock_instance = Mock()
            mock_get_client.return_value = mock_instance

            # Mock answer_question calls
            mock_instance.answer_question = Mock(side_effect=[
                {"choice": [2], "reasoning": "2+2=4"},  # Correct
                {"choice": [1, 3], "reasoning": "2 and 4 are even"},  # Correct
                {"text_answer": "Plants convert light to energy", "reasoning": ""}
            ])

            # Mock grade_open_ended call
            mock_instance.grade_open_ended = Mock(return_value={
                "score": 0.67,
                "rubric_scores": [1, 1, 0],
                "feedback": "Good answer"
            })

            result = tester.test_model_on_exam(
                exam=sample_exam,
                model_name="gpt-4o-mini",
                provider="openai",
                output_dir=str(tmp_path)
            )

            assert result.model_name == "gpt-4o-mini"
            assert result.provider == "openai"
            assert result.exam_id == "test-exam"
            assert result.total_questions == 3
            assert result.correct_count == 2  # 2 MCQ correct
            assert 0.5 <= result.accuracy <= 1.0

    def test_test_model_on_exam_yandex(self, tester, sample_exam, tmp_path):
        """Test evaluating YandexGPT model on exam."""
        with patch('app.services.model_answer_tester.get_llm_client') as mock_get_client:
            mock_instance = Mock()
            mock_get_client.return_value = mock_instance

            mock_instance.answer_question = Mock(side_effect=[
                {"choice": [2], "reasoning": "Answer is 4"},
                {"choice": [1, 2], "reasoning": "2 and 3"},  # Wrong
                {"text_answer": "Light energy conversion", "reasoning": ""}
            ])

            mock_instance.grade_open_ended = Mock(return_value={
                "score": 0.33,
                "rubric_scores": [1, 0, 0],
                "feedback": "Incomplete"
            })

            result = tester.test_model_on_exam(
                exam=sample_exam,
                model_name="yandexgpt-lite",
                provider="yandex",
                output_dir=str(tmp_path)
            )

            assert result.model_name == "yandexgpt-lite"
            assert result.provider == "yandex"
            assert result.correct_count == 1  # Only first MCQ correct

    def test_load_exam_from_file(self, tester, sample_exam, tmp_path):
        """Test loading exam from JSON file."""
        exam_file = tmp_path / "exam_test.json"
        with open(exam_file, 'w') as f:
            json.dump(sample_exam.model_dump(), f)

        loaded_exam = tester.load_exam(str(exam_file))
        assert loaded_exam.exam_id == "test-exam"
        assert len(loaded_exam.questions) == 3

    def test_check_single_choice_answer_correct(self, tester):
        """Test checking correct single-choice answer."""
        question = Question(
            id="q-001",
            type="single_choice",
            stem="Test?",
            options=["A", "B", "C"],
            correct=[1],
            source_refs=[]
        )
        model_answer = {"choice": [1]}

        is_correct = tester._check_answer(question, model_answer)
        assert is_correct is True

    def test_check_single_choice_answer_incorrect(self, tester):
        """Test checking incorrect single-choice answer."""
        question = Question(
            id="q-001",
            type="single_choice",
            stem="Test?",
            options=["A", "B", "C"],
            correct=[1],
            source_refs=[]
        )
        model_answer = {"choice": [0]}

        is_correct = tester._check_answer(question, model_answer)
        assert is_correct is False

    def test_check_multiple_choice_answer_correct(self, tester):
        """Test checking correct multiple-choice answer."""
        question = Question(
            id="q-002",
            type="multiple_choice",
            stem="Test?",
            options=["A", "B", "C", "D"],
            correct=[0, 2],
            source_refs=[]
        )
        model_answer = {"choice": [0, 2]}

        is_correct = tester._check_answer(question, model_answer)
        assert is_correct is True

    def test_check_multiple_choice_answer_partial(self, tester):
        """Test checking partial multiple-choice answer."""
        question = Question(
            id="q-002",
            type="multiple_choice",
            stem="Test?",
            options=["A", "B", "C", "D"],
            correct=[0, 2],
            source_refs=[]
        )
        model_answer = {"choice": [0, 1]}  # One correct, one incorrect

        is_correct = tester._check_answer(question, model_answer)
        assert is_correct is False  # Exact match required by default

    def test_compare_models(self, tester, tmp_path):
        """Test comparing multiple models."""
        results = [
            ModelTestResult(
                model_name="gpt-4o-mini",
                provider="openai",
                exam_id="test-exam",
                total_questions=10,
                correct_count=8,
                accuracy=0.8,
                per_question_results=[],
                metadata={}
            ),
            ModelTestResult(
                model_name="yandexgpt-lite",
                provider="yandex",
                exam_id="test-exam",
                total_questions=10,
                correct_count=6,
                accuracy=0.6,
                per_question_results=[],
                metadata={}
            )
        ]

        comparison = tester.compare_models(results, output_dir=str(tmp_path))

        assert "models" in comparison
        assert len(comparison["models"]) == 2
        assert comparison["best_model"] == "gpt-4o-mini"
        assert comparison["best_accuracy"] == 0.8

    def test_save_and_load_results(self, tester, tmp_path):
        """Test saving and loading test results."""
        result = ModelTestResult(
            model_name="test-model",
            provider="openai",
            exam_id="test-exam",
            total_questions=5,
            correct_count=3,
            accuracy=0.6,
            per_question_results=[
                {
                    "question_id": "q-001",
                    "correct": True,
                    "model_answer": {"choice": [0]},
                    "expected_answer": [0]
                }
            ],
            metadata={"test": "value"}
        )

        output_file = tester.save_result(result, output_dir=str(tmp_path))
        assert Path(output_file).exists()

        # Verify content
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["model_name"] == "test-model"
            assert saved_data["accuracy"] == 0.6

    def test_invalid_provider(self, tester, sample_exam):
        """Test fallback behavior for invalid provider."""
        with patch('app.services.model_answer_tester.get_llm_client') as mock_get_client:
            mock_instance = Mock()
            mock_instance.answer_question = Mock(return_value={"choice": [0]})
            mock_get_client.return_value = mock_instance

            result = tester.test_model_on_exam(
                exam=sample_exam,
                model_name="test-model",
                provider="invalid-provider"
            )

            assert result.provider == "invalid-provider"

    def test_batch_test_models(self, tester, sample_exam, tmp_path):
        """Test batch testing multiple models."""
        with patch('app.services.model_answer_tester.get_llm_client') as mock_get_client:
            mock_openai = Mock()
            mock_openai.answer_question = Mock(return_value={"choice": [0]})
            mock_yandex = Mock()
            mock_yandex.answer_question = Mock(return_value={"choice": [0]})
            mock_get_client.side_effect = [mock_openai, mock_yandex]

            models_config = [
                {"model_name": "gpt-4o-mini", "provider": "openai"},
                {"model_name": "yandexgpt-lite", "provider": "yandex"}
            ]

            results = tester.batch_test_models(
                exam=sample_exam,
                models=models_config,
                output_dir=str(tmp_path)
            )

            assert len(results) == 2
            assert results[0].provider == "openai"
            assert results[1].provider == "yandex"
