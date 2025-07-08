"""Tests for threshold calculation logic."""

import pytest

from git_hooks.core import ThresholdCalculator


class TestThresholdCalculator:
    """Test the threshold calculator."""

    def test_calculate_warn_threshold_default(self) -> None:
        """Test warn threshold calculation with default multiplier."""
        calculator = ThresholdCalculator()
        assert calculator.calculate_warn_threshold(100) == 90
        assert calculator.calculate_warn_threshold(1000) == 900

    def test_calculate_urgent_threshold_default(self) -> None:
        """Test urgent threshold calculation with default multiplier."""
        calculator = ThresholdCalculator()
        assert calculator.calculate_urgent_threshold(100) == 80
        assert calculator.calculate_urgent_threshold(1000) == 800

    def test_calculate_warn_threshold_custom_multiplier(self) -> None:
        """Test warn threshold with custom multiplier."""
        calculator = ThresholdCalculator(warn_multiplier=0.95)
        assert calculator.calculate_warn_threshold(100) == 95

    def test_calculate_urgent_threshold_custom_multiplier(self) -> None:
        """Test urgent threshold with custom multiplier."""
        calculator = ThresholdCalculator(urgent_multiplier=0.75)
        assert calculator.calculate_urgent_threshold(100) == 75

    def test_both_custom_multipliers(self) -> None:
        """Test with both custom multipliers."""
        calculator = ThresholdCalculator(warn_multiplier=0.85, urgent_multiplier=0.70)
        assert calculator.calculate_warn_threshold(100) == 85
        assert calculator.calculate_urgent_threshold(100) == 70

    def test_thresholds_rounded_correctly(self) -> None:
        """Test that thresholds are rounded to integers."""
        calculator = ThresholdCalculator()
        # 87 * 0.9 = 78.3, should round to 78
        assert calculator.calculate_warn_threshold(87) == 78
        # 87 * 0.8 = 69.6, should round to 70
        assert calculator.calculate_urgent_threshold(87) == 70

    def test_zero_limit(self) -> None:
        """Test with zero limit."""
        calculator = ThresholdCalculator()
        assert calculator.calculate_warn_threshold(0) == 0
        assert calculator.calculate_urgent_threshold(0) == 0

    def test_negative_limit_raises(self) -> None:
        """Test that negative limits raise an error."""
        calculator = ThresholdCalculator()
        with pytest.raises(ValueError, match="Limit must be non-negative"):
            calculator.calculate_warn_threshold(-10)
        with pytest.raises(ValueError, match="Limit must be non-negative"):
            calculator.calculate_urgent_threshold(-10)

    def test_invalid_multipliers_raise(self) -> None:
        """Test that invalid multipliers raise errors."""
        with pytest.raises(ValueError, match="Multipliers must be between 0 and 1"):
            ThresholdCalculator(warn_multiplier=1.5)
        with pytest.raises(ValueError, match="Multipliers must be between 0 and 1"):
            ThresholdCalculator(urgent_multiplier=-0.1)
        with pytest.raises(ValueError, match="Multipliers must be between 0 and 1"):
            ThresholdCalculator(warn_multiplier=0, urgent_multiplier=0.8)
