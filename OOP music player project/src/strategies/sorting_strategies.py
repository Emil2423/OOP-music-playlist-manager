"""Sorting strategy implementations using the Strategy pattern.

This module provides various sorting algorithms for songs and playlists
that can be selected and applied at runtime.

Design Principles:
- Strategy Pattern: Defines a family of interchangeable sorting algorithms
- Open/Closed: New sorting strategies can be added without modifying existing code
- Liskov Substitution: All strategies are interchangeable

Example Usage:
    >>> songs = playlist.get_tracks()
    >>> sorter = SortByArtistStrategy()
    >>> sorted_songs = sorter.sort(songs)
    >>> 
    >>> # Or with reverse order
    >>> sorter = SortByDurationStrategy(reverse=True)
    >>> longest_first = sorter.sort(songs)
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class SortStrategy(ABC):
    """Abstract base class for sorting strategies.
    
    Defines the interface for all sorting algorithms.
    Each concrete strategy implements a different sorting criterion.
    
    Attributes:
        reverse (bool): If True, sort in descending order
        name (str): Human-readable name of the strategy
    """
    
    def __init__(self, reverse=False):
        """Initialize sort strategy.
        
        Args:
            reverse (bool): If True, reverse the sort order
        """
        self.reverse = reverse
        self.name = self.__class__.__name__
    
    @abstractmethod
    def sort(self, items):
        """Sort the given items according to this strategy.
        
        Args:
            items (list): List of items to sort (songs or playlists)
            
        Returns:
            list: New list with items sorted
        """
        pass
    
    def __str__(self):
        order = "descending" if self.reverse else "ascending"
        return f"{self.name} ({order})"


class SortByNameStrategy(SortStrategy):
    """Sort items alphabetically by name/title.
    
    For songs, sorts by title. For playlists, sorts by name.
    Case-insensitive sorting.
    
    Example:
        >>> sorter = SortByNameStrategy()
        >>> sorted_songs = sorter.sort(songs)  # A-Z by title
    """
    
    def sort(self, items):
        """Sort items by name/title alphabetically.
        
        Args:
            items (list): List of songs or playlists
            
        Returns:
            list: Sorted list
        """
        if not items:
            return []
        
        logger.debug(f"Sorting {len(items)} items by name ({self})")
        
        def get_name(item):
            # Support both Song (title) and Playlist (name)
            if hasattr(item, 'title'):
                return item.title.lower()
            elif hasattr(item, 'name'):
                return item.name.lower()
            return str(item).lower()
        
        return sorted(items, key=get_name, reverse=self.reverse)


class SortByDurationStrategy(SortStrategy):
    """Sort songs by duration.
    
    Default order is shortest first (ascending).
    Use reverse=True for longest first.
    
    Example:
        >>> sorter = SortByDurationStrategy(reverse=True)
        >>> longest_songs = sorter.sort(songs)  # Longest first
    """
    
    def sort(self, items):
        """Sort items by duration.
        
        Args:
            items (list): List of songs (must have duration attribute)
            
        Returns:
            list: Sorted list by duration
        """
        if not items:
            return []
        
        logger.debug(f"Sorting {len(items)} items by duration ({self})")
        
        # Filter to only items with duration
        items_with_duration = [i for i in items if hasattr(i, 'duration')]
        
        return sorted(items_with_duration, key=lambda x: x.duration, reverse=self.reverse)


class SortByArtistStrategy(SortStrategy):
    """Sort songs alphabetically by artist name.
    
    Case-insensitive sorting. Songs with the same artist
    are sorted by title as a secondary criterion.
    
    Example:
        >>> sorter = SortByArtistStrategy()
        >>> sorted_songs = sorter.sort(songs)  # A-Z by artist
    """
    
    def sort(self, items):
        """Sort items by artist name.
        
        Args:
            items (list): List of songs (must have artist attribute)
            
        Returns:
            list: Sorted list by artist, then by title
        """
        if not items:
            return []
        
        logger.debug(f"Sorting {len(items)} items by artist ({self})")
        
        # Filter to only items with artist attribute
        items_with_artist = [i for i in items if hasattr(i, 'artist')]
        
        def sort_key(item):
            artist = item.artist.lower() if item.artist else ""
            title = item.title.lower() if hasattr(item, 'title') else ""
            return (artist, title)
        
        return sorted(items_with_artist, key=sort_key, reverse=self.reverse)


class SortByDateAddedStrategy(SortStrategy):
    """Sort items by date added (most recent first by default).
    
    This strategy is particularly useful for playlists where
    you want to see recently added songs first.
    
    Note: Requires items to have a 'created_at' or 'added_at' attribute.
    If not present, maintains original order.
    
    Example:
        >>> sorter = SortByDateAddedStrategy()
        >>> recent_first = sorter.sort(songs)
    """
    
    def __init__(self, reverse=True):
        """Initialize with most recent first as default.
        
        Args:
            reverse (bool): If True (default), most recent first
        """
        super().__init__(reverse=reverse)
    
    def sort(self, items):
        """Sort items by date added.
        
        Args:
            items (list): List of items with created_at/added_at attribute
            
        Returns:
            list: Sorted list by date
        """
        if not items:
            return []
        
        logger.debug(f"Sorting {len(items)} items by date added ({self})")
        
        def get_date(item):
            # Try different date attributes
            if hasattr(item, 'added_at'):
                return item.added_at or ""
            elif hasattr(item, 'created_at'):
                return item.created_at or ""
            return ""
        
        # Only sort if items have date attributes
        if any(get_date(item) for item in items):
            return sorted(items, key=get_date, reverse=self.reverse)
        
        # Return in original order if no dates
        return list(items)


class SortByGenreStrategy(SortStrategy):
    """Sort songs alphabetically by genre.
    
    Songs with the same genre are sorted by artist as secondary,
    then by title as tertiary criterion.
    
    Example:
        >>> sorter = SortByGenreStrategy()
        >>> sorted_songs = sorter.sort(songs)  # Grouped by genre
    """
    
    def sort(self, items):
        """Sort items by genre.
        
        Args:
            items (list): List of songs (must have genre attribute)
            
        Returns:
            list: Sorted list by genre, artist, then title
        """
        if not items:
            return []
        
        logger.debug(f"Sorting {len(items)} items by genre ({self})")
        
        # Filter to only items with genre attribute
        items_with_genre = [i for i in items if hasattr(i, 'genre')]
        
        def sort_key(item):
            genre = item.genre.lower() if item.genre else ""
            artist = item.artist.lower() if hasattr(item, 'artist') and item.artist else ""
            title = item.title.lower() if hasattr(item, 'title') else ""
            return (genre, artist, title)
        
        return sorted(items_with_genre, key=sort_key, reverse=self.reverse)


class PlaylistSorter:
    """Context class for applying sort strategies to playlists.
    
    Demonstrates the Strategy pattern by allowing the sorting
    algorithm to be changed at runtime.
    
    Example:
        >>> sorter = PlaylistSorter(SortByArtistStrategy())
        >>> sorted_songs = sorter.sort(playlist.get_tracks())
        >>> 
        >>> # Change strategy at runtime
        >>> sorter.set_strategy(SortByDurationStrategy(reverse=True))
        >>> sorted_by_duration = sorter.sort(playlist.get_tracks())
    """
    
    def __init__(self, strategy=None):
        """Initialize with optional strategy.
        
        Args:
            strategy (SortStrategy, optional): Initial sorting strategy.
                Defaults to SortByNameStrategy.
        """
        self._strategy = strategy or SortByNameStrategy()
        logger.debug(f"PlaylistSorter initialized with {self._strategy}")
    
    def set_strategy(self, strategy):
        """Change the sorting strategy.
        
        Args:
            strategy (SortStrategy): New sorting strategy
        """
        self._strategy = strategy
        logger.debug(f"PlaylistSorter strategy changed to {strategy}")
    
    def sort(self, items):
        """Sort items using the current strategy.
        
        Args:
            items (list): Items to sort
            
        Returns:
            list: Sorted items
        """
        return self._strategy.sort(items)
    
    @property
    def strategy_name(self):
        """Get the current strategy name."""
        return str(self._strategy)
