"""Duration format strategy implementations using the Strategy pattern.

This module provides various duration formatting strategies that can be
selected and applied at runtime to display playlist/song durations.

Design Principles:
- Strategy Pattern: Defines a family of interchangeable duration formats
- Open/Closed: New format strategies can be added without modifying existing code
- Liskov Substitution: All strategies are interchangeable
- Single Responsibility: Each strategy handles one specific format

Example Usage:
    >>> from strategies.duration_format_strategies import (
    ...     SecondsFormat, MinutesFormat, HoursFormat
    ... )
    >>> 
    >>> duration = 3661  # 1 hour, 1 minute, 1 second
    >>> 
    >>> seconds_fmt = SecondsFormat()
    >>> print(seconds_fmt.format_duration(duration))  # "3661s"
    >>> 
    >>> minutes_fmt = MinutesFormat()
    >>> print(minutes_fmt.format_duration(duration))  # "61m 1s"
    >>> 
    >>> hours_fmt = HoursFormat()
    >>> print(hours_fmt.format_duration(duration))  # "1h 1m 1s"
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DurationFormatStrategy(ABC):
    """Abstract base class for duration formatting strategies.
    
    Defines the interface for all duration format algorithms.
    Each concrete strategy implements a different format representation.
    
    This demonstrates the Strategy Pattern, allowing runtime selection
    of duration display format without modifying client code.
    
    Attributes:
        name (str): Human-readable name of the strategy
    """
    
    def __init__(self):
        """Initialize duration format strategy."""
        self.name = self.__class__.__name__
        logger.debug(f"Created duration format strategy: {self.name}")
    
    @abstractmethod
    def format_duration(self, total_seconds: int) -> str:
        """Format the given duration according to this strategy.
        
        Args:
            total_seconds (int): Duration in seconds to format
            
        Returns:
            str: Formatted duration string
            
        Raises:
            ValueError: If total_seconds is negative
        """
        pass
    
    def _validate_seconds(self, total_seconds: int) -> None:
        """Validate that seconds value is non-negative.
        
        Args:
            total_seconds (int): Value to validate
            
        Raises:
            ValueError: If total_seconds is negative
        """
        if total_seconds < 0:
            raise ValueError("Duration cannot be negative")
    
    def __str__(self) -> str:
        """Return string representation of the strategy."""
        return self.name


class SecondsFormat(DurationFormatStrategy):
    """Format duration as total seconds.
    
    Simply displays the raw seconds value with 's' suffix.
    Most compact representation, useful for short durations.
    
    Example:
        >>> fmt = SecondsFormat()
        >>> fmt.format_duration(354)
        '354s'
        >>> fmt.format_duration(3661)
        '3661s'
    """
    
    def format_duration(self, total_seconds: int) -> str:
        """Format duration as total seconds.
        
        Args:
            total_seconds (int): Duration in seconds
            
        Returns:
            str: Duration formatted as "Xs" (e.g., "354s")
            
        Raises:
            ValueError: If total_seconds is negative
        """
        self._validate_seconds(total_seconds)
        logger.debug(f"Formatting {total_seconds}s using SecondsFormat")
        return f"{total_seconds}s"


class MinutesFormat(DurationFormatStrategy):
    """Format duration as minutes and seconds.
    
    Displays duration in "Xm Ys" format, suitable for most music tracks.
    
    Example:
        >>> fmt = MinutesFormat()
        >>> fmt.format_duration(354)
        '5m 54s'
        >>> fmt.format_duration(60)
        '1m 0s'
        >>> fmt.format_duration(45)
        '0m 45s'
    """
    
    def format_duration(self, total_seconds: int) -> str:
        """Format duration as minutes and seconds.
        
        Args:
            total_seconds (int): Duration in seconds
            
        Returns:
            str: Duration formatted as "Xm Ys" (e.g., "5m 54s")
            
        Raises:
            ValueError: If total_seconds is negative
        """
        self._validate_seconds(total_seconds)
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        logger.debug(f"Formatting {total_seconds}s as {minutes}m {seconds}s")
        return f"{minutes}m {seconds}s"


class HoursFormat(DurationFormatStrategy):
    """Format duration as hours, minutes, and seconds.
    
    Displays duration in "Xh Ym Zs" format, suitable for long playlists.
    
    Example:
        >>> fmt = HoursFormat()
        >>> fmt.format_duration(3661)
        '1h 1m 1s'
        >>> fmt.format_duration(7265)
        '2h 1m 5s'
        >>> fmt.format_duration(354)
        '0h 5m 54s'
    """
    
    def format_duration(self, total_seconds: int) -> str:
        """Format duration as hours, minutes, and seconds.
        
        Args:
            total_seconds (int): Duration in seconds
            
        Returns:
            str: Duration formatted as "Xh Ym Zs" (e.g., "1h 1m 1s")
            
        Raises:
            ValueError: If total_seconds is negative
        """
        self._validate_seconds(total_seconds)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        logger.debug(f"Formatting {total_seconds}s as {hours}h {minutes}m {seconds}s")
        return f"{hours}h {minutes}m {seconds}s"


class CompactFormat(DurationFormatStrategy):
    """Format duration in compact MM:SS or HH:MM:SS format.
    
    Uses colon-separated format common in media players.
    Automatically switches to hours format when duration exceeds 59 minutes.
    
    Example:
        >>> fmt = CompactFormat()
        >>> fmt.format_duration(354)
        '5:54'
        >>> fmt.format_duration(3661)
        '1:01:01'
        >>> fmt.format_duration(45)
        '0:45'
    """
    
    def format_duration(self, total_seconds: int) -> str:
        """Format duration in compact MM:SS or HH:MM:SS format.
        
        Args:
            total_seconds (int): Duration in seconds
            
        Returns:
            str: Duration formatted as "M:SS" or "H:MM:SS"
            
        Raises:
            ValueError: If total_seconds is negative
        """
        self._validate_seconds(total_seconds)
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            result = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            result = f"{minutes}:{seconds:02d}"
        
        logger.debug(f"Formatting {total_seconds}s as {result}")
        return result


# Duration Format Factory for easy selection
class DurationFormatFactory:
    """Factory class for creating duration format strategies.
    
    Provides convenient methods to get format strategies by name
    or to list all available formats.
    
    Example:
        >>> factory = DurationFormatFactory()
        >>> fmt = factory.get_format("hours")
        >>> fmt.format_duration(3661)
        '1h 1m 1s'
    """
    
    _formats = {
        "seconds": SecondsFormat,
        "minutes": MinutesFormat,
        "hours": HoursFormat,
        "compact": CompactFormat
    }
    
    @classmethod
    def get_format(cls, format_name: str) -> DurationFormatStrategy:
        """Get a format strategy by name.
        
        Args:
            format_name (str): Name of the format ('seconds', 'minutes', 
                             'hours', or 'compact')
            
        Returns:
            DurationFormatStrategy: Instance of the requested format
            
        Raises:
            ValueError: If format_name is not recognized
        """
        format_name = format_name.lower().strip()
        
        if format_name not in cls._formats:
            valid_formats = ", ".join(cls._formats.keys())
            raise ValueError(
                f"Unknown format '{format_name}'. Valid formats: {valid_formats}"
            )
        
        return cls._formats[format_name]()
    
    @classmethod
    def list_formats(cls) -> list:
        """List all available format names.
        
        Returns:
            list: List of available format name strings
        """
        return list(cls._formats.keys())
