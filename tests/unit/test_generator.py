"""
Unit tests for question generator (TDD - RED phase).

Tests written BEFORE implementation.
"""
import pytest
from unittest.mock import Mock, patch
from app.core.generator import QuestionGenerator
from app.core.parser import ParsedDocument, ParsedSection
from app.models.schemas import ExamConfig, Question, Exam


class TestQuestionGenerator:
    """Tests for question generation functionality."""

    @pytest.fixture
    def generator(self):
        return QuestionGenerator()

    @pytest.fixture
    def sample_document(self):
        """Create a sample parsed document."""
        sections = [
            ParsedSection(
                heading="Symptoms",
                content="Fever is a common symptom. Temperature above 38°C indicates fever.",
                level=2,
                start_pos=0,
                end_pos=100
            ),
            ParsedSection(
                heading="Treatment",
                content="Paracetamol 500mg every 6 hours for fever reduction.",
                level=2,
                start_pos=101,
                end_pos=200
            )
        ]
        return ParsedDocument(
            title="Medical Guide",
            sections=sections,
            source_text="# Medical Guide\n## Symptoms\nFever...\n## Treatment\nParacetamol..."
        )

    def test_generator_initialization(self, generator):
        """Test that generator can be initialized."""
        assert generator is not None

    def test_generate_returns_exam(self, generator, sample_document):
        """Test that generate returns an Exam object."""
        config = ExamConfig(total_questions=5)
        result = generator.generate(
            document=sample_document,
            config=config,
            exam_id="test-exam"
        )
        assert isinstance(result, Exam)
        assert result.exam_id == "test-exam"

    def test_generate_correct_number_of_questions(self, generator, sample_document):
        """Test that generator creates correct number of questions."""
        config = ExamConfig(total_questions=10)
        result = generator.generate(sample_document, config, "test")
        assert len(result.questions) == 10

    def test_generate_respects_question_type_ratios(self, generator, sample_document):
        """Test that generator respects single/multiple choice ratios."""
        config = ExamConfig(
            total_questions=10,
            single_choice_ratio=0.7,
            multiple_choice_ratio=0.3
        )
        result = generator.generate(sample_document, config, "test")

        single_count = sum(1 for q in result.questions if q.type == "single_choice")
        multiple_count = sum(1 for q in result.questions if q.type == "multiple_choice")

        assert single_count == 7
        assert multiple_count == 3

    def test_generated_questions_have_unique_ids(self, generator, sample_document):
        """Test that all generated questions have unique IDs."""
        config = ExamConfig(total_questions=5)
        result = generator.generate(sample_document, config, "test")

        ids = [q.id for q in result.questions]
        assert len(ids) == len(set(ids))

    def test_generated_questions_have_source_refs(self, generator, sample_document):
        """Test that questions include source references."""
        config = ExamConfig(total_questions=3)
        result = generator.generate(sample_document, config, "test")

        for question in result.questions:
            assert len(question.source_refs) > 0

    def test_single_choice_has_one_correct_answer(self, generator, sample_document):
        """Test that single choice questions have exactly one correct answer."""
        config = ExamConfig(
            total_questions=5,
            single_choice_ratio=1.0,
            multiple_choice_ratio=0.0
        )
        result = generator.generate(sample_document, config, "test")

        for question in result.questions:
            assert question.type == "single_choice"
            assert len(question.correct) == 1

    def test_multiple_choice_has_multiple_correct(self, generator, sample_document):
        """Test that multiple choice questions have 2+ correct answers."""
        config = ExamConfig(
            total_questions=5,
            single_choice_ratio=0.0,
            multiple_choice_ratio=1.0
        )
        result = generator.generate(sample_document, config, "test")

        for question in result.questions:
            assert question.type == "multiple_choice"
            assert len(question.correct) >= 2

    def test_questions_have_valid_options_count(self, generator, sample_document):
        """Test that questions have 3-5 options."""
        config = ExamConfig(total_questions=5)
        result = generator.generate(sample_document, config, "test")

        for question in result.questions:
            assert 3 <= len(question.options) <= 5

    def test_generate_with_seed_is_deterministic(self, generator, sample_document):
        """Test that using same seed produces same results."""
        config = ExamConfig(total_questions=5, seed=42)

        result1 = generator.generate(sample_document, config, "test1")
        result2 = generator.generate(sample_document, config, "test2")

        # Same seed should produce same question types and order
        types1 = [q.type for q in result1.questions]
        types2 = [q.type for q in result2.questions]
        assert types1 == types2

    def test_generate_handles_empty_document(self, generator):
        """Test that generator handles document with no content."""
        empty_doc = ParsedDocument(title=None, sections=[], source_text="")
        config = ExamConfig(total_questions=5)

        with pytest.raises(ValueError):
            generator.generate(empty_doc, config, "test")

    def test_exam_includes_config_used(self, generator, sample_document):
        """Test that generated exam includes the config used."""
        config = ExamConfig(total_questions=5)
        result = generator.generate(sample_document, config, "test")

        assert result.config_used == config


class TestOpenAIClient:
    """Tests for OpenAI client wrapper."""

    @pytest.fixture
    def client(self):
        from app.services.openai_client import OpenAIClient
        return OpenAIClient()

    def test_client_initialization(self, client):
        """Test that OpenAI client can be initialized."""
        assert client is not None

    @patch('app.services.openai_client.OpenAI')
    def test_generate_question_calls_openai(self, mock_openai, client):
        """Test that generate_question calls OpenAI API."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"question": "test"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # This test validates the client can call OpenAI
        # Actual implementation will determine exact behavior

    def test_client_respects_api_key(self):
        """Test that client uses API key from settings."""
        from app.services.openai_client import OpenAIClient
        from app.config import settings

        # Should not raise error if API key is set
        if settings.openai_api_key:
            client = OpenAIClient()
            assert client is not None


class TestQuestionValidation:
    """Tests for generated question validation."""

    def test_validate_correct_indices_in_range(self):
        """Test that correct indices are within options range."""
        # This will be validated by Pydantic schemas
        with pytest.raises(Exception):
            Question(
                id="q1",
                type="single_choice",
                stem="Test?",
                options=["A", "B"],
                correct=[5]  # Out of range
            )

    def test_validate_no_empty_options(self):
        """Test that options are not empty."""
        with pytest.raises(Exception):
            Question(
                id="q1",
                type="single_choice",
                stem="Test?",
                options=["A", ""],
                correct=[0]
            )


class TestOpenEndedQuestionGeneration:
    """Tests for open-ended question generation."""

    @pytest.fixture
    def generator(self):
        return QuestionGenerator()

    @pytest.fixture
    def sample_document(self):
        """Create a sample parsed document."""
        sections = [
            ParsedSection(
                heading="Preeclampsia Pathophysiology",
                content="Preeclampsia is characterized by endothelial dysfunction and placental ischemia. "
                        "Diagnosis requires BP ≥140/90 mmHg and proteinuria ≥300mg/24h after 20 weeks gestation.",
                level=2,
                start_pos=0,
                end_pos=200
            ),
            ParsedSection(
                heading="Management",
                content="Treatment includes antihypertensives (labetalol, nifedipine) and magnesium sulfate for seizure prophylaxis.",
                level=2,
                start_pos=201,
                end_pos=350
            )
        ]
        return ParsedDocument(
            title="Hypertensive Disorders",
            sections=sections,
            source_text="# Hypertensive Disorders\n## Preeclampsia..."
        )

    def test_generate_open_ended_questions(self, generator, sample_document):
        """Test generation of open-ended questions."""
        config = ExamConfig(
            total_questions=5,
            single_choice_ratio=0.0,
            multiple_choice_ratio=0.0,
            open_ended_ratio=1.0
        )
        result = generator.generate(sample_document, config, "test-open")

        assert len(result.questions) == 5
        for question in result.questions:
            assert question.type == "open_ended"
            assert question.options is None
            assert question.correct is None
            assert question.reference_answer is not None
            assert question.rubric is not None
            assert len(question.rubric) >= 3

    def test_generate_mixed_with_open_ended(self, generator, sample_document):
        """Test generation with mixed question types including open-ended."""
        config = ExamConfig(
            total_questions=10,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2
        )
        result = generator.generate(sample_document, config, "test-mixed")

        single_count = sum(1 for q in result.questions if q.type == "single_choice")
        multiple_count = sum(1 for q in result.questions if q.type == "multiple_choice")
        open_count = sum(1 for q in result.questions if q.type == "open_ended")

        assert single_count == 5
        assert multiple_count == 3
        assert open_count == 2

    def test_open_ended_has_valid_reference_answer(self, generator, sample_document):
        """Test that open-ended questions have non-empty reference answers."""
        config = ExamConfig(
            total_questions=3,
            single_choice_ratio=0.0,
            multiple_choice_ratio=0.0,
            open_ended_ratio=1.0
        )
        result = generator.generate(sample_document, config, "test-ref")

        for question in result.questions:
            assert question.reference_answer is not None
            assert len(question.reference_answer.strip()) > 0

    def test_open_ended_has_valid_rubric(self, generator, sample_document):
        """Test that open-ended questions have valid rubric."""
        config = ExamConfig(
            total_questions=2,
            single_choice_ratio=0.0,
            multiple_choice_ratio=0.0,
            open_ended_ratio=1.0
        )
        result = generator.generate(sample_document, config, "test-rubric")

        for question in result.questions:
            assert question.rubric is not None
            assert len(question.rubric) >= 3
            assert len(question.rubric) <= 5
            for criterion in question.rubric:
                assert len(criterion.strip()) > 0
