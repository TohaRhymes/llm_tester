"""
Unit tests for count-based question configuration.

Tests the new count-based input system where users specify exact numbers
of each question type instead of ratios.
"""
import pytest
from pydantic import ValidationError
from app.models.schemas import ExamConfig


class TestCountBasedExamConfig:
    """Test ExamConfig with count-based inputs."""

    def test_config_with_counts_only(self):
        """Test that counts can be specified instead of ratios."""
        config = ExamConfig(
            single_choice_count=5,
            multiple_choice_count=3,
            open_ended_count=2
        )
        assert config.single_choice_count == 5
        assert config.multiple_choice_count == 3
        assert config.open_ended_count == 2
        # Total should be auto-calculated
        assert config.total_questions == 10
        # Ratios should be auto-calculated
        assert config.single_choice_ratio == 0.5
        assert config.multiple_choice_ratio == 0.3
        assert config.open_ended_ratio == 0.2

    def test_config_with_zero_counts(self):
        """Test that some counts can be zero."""
        config = ExamConfig(
            single_choice_count=10,
            multiple_choice_count=0,
            open_ended_count=0
        )
        assert config.single_choice_count == 10
        assert config.multiple_choice_count == 0
        assert config.open_ended_count == 0
        assert config.total_questions == 10
        assert config.single_choice_ratio == 1.0
        assert config.multiple_choice_ratio == 0.0
        assert config.open_ended_ratio == 0.0

    def test_all_counts_zero_raises_error(self):
        """Test that at least one count must be non-zero."""
        with pytest.raises(ValidationError) as exc_info:
            ExamConfig(
                single_choice_count=0,
                multiple_choice_count=0,
                open_ended_count=0
            )
        assert "at least one count must be positive" in str(exc_info.value).lower()

    def test_negative_count_raises_error(self):
        """Test that negative counts are rejected."""
        with pytest.raises(ValidationError):
            ExamConfig(
                single_choice_count=-5,
                multiple_choice_count=3,
                open_ended_count=2
            )

    def test_counts_exceed_maximum(self):
        """Test that total count cannot exceed maximum."""
        with pytest.raises(ValidationError) as exc_info:
            ExamConfig(
                single_choice_count=50,
                multiple_choice_count=50,
                open_ended_count=50  # Total = 150, exceeds max of 100
            )
        assert "total_questions" in str(exc_info.value).lower() or "maximum" in str(exc_info.value).lower()

    def test_backward_compatibility_with_ratios(self):
        """Test that old ratio-based configs still work."""
        config = ExamConfig(
            total_questions=20,
            single_choice_ratio=0.5,
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2
        )
        assert config.total_questions == 20
        assert config.single_choice_ratio == 0.5
        # Counts should be auto-calculated
        assert config.single_choice_count == 10
        assert config.multiple_choice_count == 6
        assert config.open_ended_count == 4

    def test_counts_override_ratios(self):
        """Test that if both counts and ratios are provided, counts take precedence."""
        config = ExamConfig(
            total_questions=20,  # Will be ignored
            single_choice_ratio=0.5,  # Will be recalculated
            multiple_choice_ratio=0.3,
            open_ended_ratio=0.2,
            single_choice_count=7,
            multiple_choice_count=2,
            open_ended_count=1
        )
        # Counts should win
        assert config.single_choice_count == 7
        assert config.multiple_choice_count == 2
        assert config.open_ended_count == 1
        assert config.total_questions == 10
        # Ratios recalculated from counts
        assert config.single_choice_ratio == 0.7
        assert config.multiple_choice_ratio == 0.2
        assert config.open_ended_ratio == 0.1


class TestCountBasedValidation:
    """Test validation logic for count-based inputs."""

    def test_integer_counts_accepted(self):
        """Test that integer counts work correctly."""
        config = ExamConfig(
            single_choice_count=5,
            multiple_choice_count=3,
            open_ended_count=2
        )
        assert config.single_choice_count == 5
        assert config.multiple_choice_count == 3
        assert config.open_ended_count == 2
        assert config.total_questions == 10

    def test_config_defaults_with_counts(self):
        """Test default values when using count-based system."""
        config = ExamConfig(
            single_choice_count=10
        )
        # Other counts default to 0
        assert config.single_choice_count == 10
        assert config.multiple_choice_count == 0
        assert config.open_ended_count == 0
        assert config.total_questions == 10

    def test_partial_count_specification(self):
        """Test that you can specify only some counts."""
        config = ExamConfig(
            single_choice_count=5,
            open_ended_count=3
            # multiple_choice_count not specified, should default to 0
        )
        assert config.single_choice_count == 5
        assert config.multiple_choice_count == 0
        assert config.open_ended_count == 3
        assert config.total_questions == 8


class TestCountToRatioConversion:
    """Test automatic conversion between counts and ratios."""

    def test_counts_to_ratios_exact(self):
        """Test conversion from counts to ratios (exact division)."""
        config = ExamConfig(
            single_choice_count=5,
            multiple_choice_count=3,
            open_ended_count=2
        )
        assert config.single_choice_ratio == 0.5
        assert config.multiple_choice_ratio == 0.3
        assert config.open_ended_ratio == 0.2

    def test_counts_to_ratios_rounding(self):
        """Test conversion handles rounding properly."""
        config = ExamConfig(
            single_choice_count=1,
            multiple_choice_count=1,
            open_ended_count=1
        )
        # Each should be ~0.333...
        assert abs(config.single_choice_ratio - 0.3333) < 0.01
        assert abs(config.multiple_choice_ratio - 0.3333) < 0.01
        assert abs(config.open_ended_ratio - 0.3333) < 0.01
        # Sum should still be 1.0 (within tolerance)
        total_ratio = config.single_choice_ratio + config.multiple_choice_ratio + config.open_ended_ratio
        assert abs(total_ratio - 1.0) < 0.01

    def test_ratios_to_counts_truncation(self):
        """Test conversion from ratios to counts handles truncation."""
        config = ExamConfig(
            total_questions=10,
            single_choice_ratio=0.33,
            multiple_choice_ratio=0.34,
            open_ended_ratio=0.33
        )
        # Should calculate counts: 3.3 -> 3, 3.4 -> 3, 3.3 -> 4 (remainder)
        assert config.single_choice_count == 3
        assert config.multiple_choice_count == 3
        assert config.open_ended_count == 4
        assert config.single_choice_count + config.multiple_choice_count + config.open_ended_count == 10
