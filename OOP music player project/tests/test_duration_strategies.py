"""Unit tests for duration format strategies.

Tests all duration formatting strategies including edge cases and error handling.
"""

import pytest
from strategies.duration_format_strategies import (
    DurationFormatStrategy,
    SecondsFormat,
    MinutesFormat,
    HoursFormat,
    CompactFormat,
    DurationFormatFactory
)


class TestSecondsFormat:
    """Test suite for SecondsFormat strategy."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds."""
        fmt = SecondsFormat()
        assert fmt.format_duration(0) == "0s"
    
    def test_format_small_duration(self):
        """Test formatting small duration."""
        fmt = SecondsFormat()
        assert fmt.format_duration(45) == "45s"
    
    def test_format_typical_song_duration(self):
        """Test formatting typical song duration (5:54)."""
        fmt = SecondsFormat()
        assert fmt.format_duration(354) == "354s"
    
    def test_format_large_duration(self):
        """Test formatting large duration (1 hour+)."""
        fmt = SecondsFormat()
        assert fmt.format_duration(3661) == "3661s"
    
    def test_format_negative_raises_error(self):
        """Test that negative duration raises ValueError."""
        fmt = SecondsFormat()
        with pytest.raises(ValueError):
            fmt.format_duration(-1)
    
    def test_str_representation(self):
        """Test string representation of strategy."""
        fmt = SecondsFormat()
        assert str(fmt) == "SecondsFormat"


class TestMinutesFormat:
    """Test suite for MinutesFormat strategy."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds."""
        fmt = MinutesFormat()
        assert fmt.format_duration(0) == "0m 0s"
    
    def test_format_less_than_minute(self):
        """Test formatting duration less than one minute."""
        fmt = MinutesFormat()
        assert fmt.format_duration(45) == "0m 45s"
    
    def test_format_exact_minute(self):
        """Test formatting exact minute."""
        fmt = MinutesFormat()
        assert fmt.format_duration(60) == "1m 0s"
    
    def test_format_typical_song_duration(self):
        """Test formatting typical song duration (5:54)."""
        fmt = MinutesFormat()
        assert fmt.format_duration(354) == "5m 54s"
    
    def test_format_over_hour(self):
        """Test formatting duration over one hour."""
        fmt = MinutesFormat()
        assert fmt.format_duration(3661) == "61m 1s"
    
    def test_format_negative_raises_error(self):
        """Test that negative duration raises ValueError."""
        fmt = MinutesFormat()
        with pytest.raises(ValueError):
            fmt.format_duration(-100)
    
    def test_str_representation(self):
        """Test string representation of strategy."""
        fmt = MinutesFormat()
        assert str(fmt) == "MinutesFormat"


class TestHoursFormat:
    """Test suite for HoursFormat strategy."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds."""
        fmt = HoursFormat()
        assert fmt.format_duration(0) == "0h 0m 0s"
    
    def test_format_less_than_minute(self):
        """Test formatting duration less than one minute."""
        fmt = HoursFormat()
        assert fmt.format_duration(45) == "0h 0m 45s"
    
    def test_format_less_than_hour(self):
        """Test formatting duration less than one hour."""
        fmt = HoursFormat()
        assert fmt.format_duration(354) == "0h 5m 54s"
    
    def test_format_exactly_one_hour(self):
        """Test formatting exactly one hour."""
        fmt = HoursFormat()
        assert fmt.format_duration(3600) == "1h 0m 0s"
    
    def test_format_over_one_hour(self):
        """Test formatting duration over one hour."""
        fmt = HoursFormat()
        assert fmt.format_duration(3661) == "1h 1m 1s"
    
    def test_format_multiple_hours(self):
        """Test formatting multiple hours."""
        fmt = HoursFormat()
        assert fmt.format_duration(7265) == "2h 1m 5s"
    
    def test_format_negative_raises_error(self):
        """Test that negative duration raises ValueError."""
        fmt = HoursFormat()
        with pytest.raises(ValueError):
            fmt.format_duration(-3600)
    
    def test_str_representation(self):
        """Test string representation of strategy."""
        fmt = HoursFormat()
        assert str(fmt) == "HoursFormat"


class TestCompactFormat:
    """Test suite for CompactFormat strategy."""
    
    def test_format_zero_seconds(self):
        """Test formatting zero seconds."""
        fmt = CompactFormat()
        assert fmt.format_duration(0) == "0:00"
    
    def test_format_less_than_minute(self):
        """Test formatting duration less than one minute."""
        fmt = CompactFormat()
        assert fmt.format_duration(45) == "0:45"
    
    def test_format_single_digit_seconds(self):
        """Test formatting with single digit seconds."""
        fmt = CompactFormat()
        assert fmt.format_duration(65) == "1:05"
    
    def test_format_typical_song_duration(self):
        """Test formatting typical song duration."""
        fmt = CompactFormat()
        assert fmt.format_duration(354) == "5:54"
    
    def test_format_over_one_hour(self):
        """Test formatting duration over one hour."""
        fmt = CompactFormat()
        assert fmt.format_duration(3661) == "1:01:01"
    
    def test_format_multiple_hours(self):
        """Test formatting multiple hours."""
        fmt = CompactFormat()
        assert fmt.format_duration(7265) == "2:01:05"
    
    def test_format_negative_raises_error(self):
        """Test that negative duration raises ValueError."""
        fmt = CompactFormat()
        with pytest.raises(ValueError):
            fmt.format_duration(-1)
    
    def test_str_representation(self):
        """Test string representation of strategy."""
        fmt = CompactFormat()
        assert str(fmt) == "CompactFormat"


class TestDurationFormatFactory:
    """Test suite for DurationFormatFactory."""
    
    def test_get_seconds_format(self):
        """Test getting seconds format by name."""
        fmt = DurationFormatFactory.get_format("seconds")
        assert isinstance(fmt, SecondsFormat)
    
    def test_get_minutes_format(self):
        """Test getting minutes format by name."""
        fmt = DurationFormatFactory.get_format("minutes")
        assert isinstance(fmt, MinutesFormat)
    
    def test_get_hours_format(self):
        """Test getting hours format by name."""
        fmt = DurationFormatFactory.get_format("hours")
        assert isinstance(fmt, HoursFormat)
    
    def test_get_compact_format(self):
        """Test getting compact format by name."""
        fmt = DurationFormatFactory.get_format("compact")
        assert isinstance(fmt, CompactFormat)
    
    def test_get_format_case_insensitive(self):
        """Test that format name is case insensitive."""
        fmt = DurationFormatFactory.get_format("SECONDS")
        assert isinstance(fmt, SecondsFormat)
        
        fmt = DurationFormatFactory.get_format("Hours")
        assert isinstance(fmt, HoursFormat)
    
    def test_get_format_with_whitespace(self):
        """Test that format name handles whitespace."""
        fmt = DurationFormatFactory.get_format("  seconds  ")
        assert isinstance(fmt, SecondsFormat)
    
    def test_get_unknown_format_raises_error(self):
        """Test that unknown format raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            DurationFormatFactory.get_format("unknown")
        assert "Unknown format" in str(excinfo.value)
    
    def test_list_formats(self):
        """Test listing all available formats."""
        formats = DurationFormatFactory.list_formats()
        assert "seconds" in formats
        assert "minutes" in formats
        assert "hours" in formats
        assert "compact" in formats
        assert len(formats) == 4


class TestStrategyPolymorphism:
    """Test that all strategies are polymorphic and interchangeable."""
    
    @pytest.fixture
    def all_strategies(self):
        """Fixture providing all strategy instances."""
        return [
            SecondsFormat(),
            MinutesFormat(),
            HoursFormat(),
            CompactFormat()
        ]
    
    def test_all_inherit_from_base(self, all_strategies):
        """Test that all strategies inherit from DurationFormatStrategy."""
        for strategy in all_strategies:
            assert isinstance(strategy, DurationFormatStrategy)
    
    def test_all_implement_format_duration(self, all_strategies):
        """Test that all strategies implement format_duration method."""
        duration = 354
        for strategy in all_strategies:
            result = strategy.format_duration(duration)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_all_validate_negative_input(self, all_strategies):
        """Test that all strategies validate negative input."""
        for strategy in all_strategies:
            with pytest.raises(ValueError):
                strategy.format_duration(-1)
    
    def test_all_have_name_attribute(self, all_strategies):
        """Test that all strategies have name attribute."""
        for strategy in all_strategies:
            assert hasattr(strategy, 'name')
            assert isinstance(strategy.name, str)


class TestEdgeCases:
    """Test edge cases for duration formatting."""
    
    def test_large_duration(self):
        """Test formatting very large duration (100 hours)."""
        fmt = HoursFormat()
        result = fmt.format_duration(360000)  # 100 hours
        assert result == "100h 0m 0s"
    
    def test_exact_minute_boundary(self):
        """Test formatting at exact minute boundary."""
        fmt = MinutesFormat()
        assert fmt.format_duration(120) == "2m 0s"
    
    def test_exact_hour_boundary(self):
        """Test formatting at exact hour boundary."""
        fmt = HoursFormat()
        assert fmt.format_duration(7200) == "2h 0m 0s"
    
    def test_one_second(self):
        """Test formatting one second."""
        fmt = SecondsFormat()
        assert fmt.format_duration(1) == "1s"
        
        fmt = MinutesFormat()
        assert fmt.format_duration(1) == "0m 1s"
        
        fmt = HoursFormat()
        assert fmt.format_duration(1) == "0h 0m 1s"
        
        fmt = CompactFormat()
        assert fmt.format_duration(1) == "0:01"
