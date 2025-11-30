"""Filter strategy implementations using the Strategy pattern.

This module provides various filtering algorithms for songs
that can be selected and applied at runtime.

Design Principles:
- Strategy Pattern: Defines a family of interchangeable filtering algorithms
- Open/Closed: New filter strategies can be added without modifying existing code
- Composite Pattern: CompositeFilterStrategy allows combining multiple filters

Example Usage:
    >>> songs = song_service.get_all_songs()
    >>> 
    >>> # Single filter
    >>> rock_filter = FilterByGenreStrategy("Rock")
    >>> rock_songs = rock_filter.filter(songs)
    >>> 
    >>> # Combined filters (AND logic)
    >>> combined = CompositeFilterStrategy([
    ...     FilterByGenreStrategy("Rock"),
    ...     FilterByDurationRangeStrategy(180, 300)
    ... ])
    >>> filtered = combined.filter(songs)
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class FilterStrategy(ABC):
    """Abstract base class for filter strategies.
    
    Defines the interface for all filtering algorithms.
    Each concrete strategy implements a different filtering criterion.
    
    Attributes:
        name (str): Human-readable name of the strategy
    """
    
    def __init__(self):
        """Initialize filter strategy."""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def filter(self, items):
        """Filter the given items according to this strategy.
        
        Args:
            items (list): List of items to filter
            
        Returns:
            list: New list with items that match the filter
        """
        pass
    
    @abstractmethod
    def matches(self, item):
        """Check if a single item matches this filter.
        
        Args:
            item: Item to check
            
        Returns:
            bool: True if item matches the filter criteria
        """
        pass
    
    def __str__(self):
        return self.name


class FilterByGenreStrategy(FilterStrategy):
    """Filter songs by genre.
    
    Case-insensitive matching. Can match exact genre or partial match.
    
    Example:
        >>> filter_rock = FilterByGenreStrategy("Rock")
        >>> rock_songs = filter_rock.filter(all_songs)
        >>> 
        >>> # Partial match
        >>> filter_rock = FilterByGenreStrategy("rock", exact=False)
    """
    
    def __init__(self, genre, exact=True):
        """Initialize genre filter.
        
        Args:
            genre (str): Genre to filter by
            exact (bool): If True, exact match (case-insensitive).
                If False, checks if genre contains the string.
        """
        super().__init__()
        self.genre = genre.lower() if genre else ""
        self.exact = exact
        logger.debug(f"Created {self} filter: genre='{genre}', exact={exact}")
    
    def matches(self, item):
        """Check if item matches the genre filter.
        
        Args:
            item: Song to check (must have genre attribute)
            
        Returns:
            bool: True if genre matches
        """
        if not hasattr(item, 'genre') or not item.genre:
            return False
        
        item_genre = item.genre.lower()
        
        if self.exact:
            return item_genre == self.genre
        return self.genre in item_genre
    
    def filter(self, items):
        """Filter items by genre.
        
        Args:
            items (list): List of songs
            
        Returns:
            list: Songs matching the genre
        """
        if not items:
            return []
        
        result = [item for item in items if self.matches(item)]
        logger.debug(f"Genre filter '{self.genre}' matched {len(result)}/{len(items)} items")
        return result
    
    def __str__(self):
        match_type = "exact" if self.exact else "contains"
        return f"FilterByGenre('{self.genre}', {match_type})"


class FilterByArtistStrategy(FilterStrategy):
    """Filter songs by artist name.
    
    Case-insensitive matching. Can match exact artist or partial match.
    
    Example:
        >>> filter_beatles = FilterByArtistStrategy("The Beatles")
        >>> beatles_songs = filter_beatles.filter(all_songs)
    """
    
    def __init__(self, artist, exact=True):
        """Initialize artist filter.
        
        Args:
            artist (str): Artist name to filter by
            exact (bool): If True, exact match. If False, partial match.
        """
        super().__init__()
        self.artist = artist.lower() if artist else ""
        self.exact = exact
        logger.debug(f"Created {self} filter: artist='{artist}', exact={exact}")
    
    def matches(self, item):
        """Check if item matches the artist filter.
        
        Args:
            item: Song to check (must have artist attribute)
            
        Returns:
            bool: True if artist matches
        """
        if not hasattr(item, 'artist') or not item.artist:
            return False
        
        item_artist = item.artist.lower()
        
        if self.exact:
            return item_artist == self.artist
        return self.artist in item_artist
    
    def filter(self, items):
        """Filter items by artist.
        
        Args:
            items (list): List of songs
            
        Returns:
            list: Songs matching the artist
        """
        if not items:
            return []
        
        result = [item for item in items if self.matches(item)]
        logger.debug(f"Artist filter '{self.artist}' matched {len(result)}/{len(items)} items")
        return result
    
    def __str__(self):
        match_type = "exact" if self.exact else "contains"
        return f"FilterByArtist('{self.artist}', {match_type})"


class FilterByDurationRangeStrategy(FilterStrategy):
    """Filter songs by duration range.
    
    Inclusive range matching (min_duration <= duration <= max_duration).
    
    Example:
        >>> # Songs between 3 and 5 minutes
        >>> filter_medium = FilterByDurationRangeStrategy(180, 300)
        >>> medium_songs = filter_medium.filter(all_songs)
        >>> 
        >>> # Songs longer than 5 minutes
        >>> filter_long = FilterByDurationRangeStrategy(min_duration=300)
    """
    
    def __init__(self, min_duration=None, max_duration=None):
        """Initialize duration range filter.
        
        Args:
            min_duration (int, optional): Minimum duration in seconds (inclusive)
            max_duration (int, optional): Maximum duration in seconds (inclusive)
        """
        super().__init__()
        self.min_duration = min_duration
        self.max_duration = max_duration
        logger.debug(f"Created {self} filter: min={min_duration}, max={max_duration}")
    
    def matches(self, item):
        """Check if item's duration is within range.
        
        Args:
            item: Song to check (must have duration attribute)
            
        Returns:
            bool: True if duration is within range
        """
        if not hasattr(item, 'duration'):
            return False
        
        duration = item.duration
        
        if self.min_duration is not None and duration < self.min_duration:
            return False
        if self.max_duration is not None and duration > self.max_duration:
            return False
        
        return True
    
    def filter(self, items):
        """Filter items by duration range.
        
        Args:
            items (list): List of songs
            
        Returns:
            list: Songs within duration range
        """
        if not items:
            return []
        
        result = [item for item in items if self.matches(item)]
        logger.debug(f"Duration filter [{self.min_duration}-{self.max_duration}s] matched {len(result)}/{len(items)} items")
        return result
    
    def __str__(self):
        min_str = str(self.min_duration) if self.min_duration else "0"
        max_str = str(self.max_duration) if self.max_duration else "∞"
        return f"FilterByDuration({min_str}s - {max_str}s)"


class FilterByTitleContainsStrategy(FilterStrategy):
    """Filter songs by title containing a search string.
    
    Case-insensitive partial matching.
    
    Example:
        >>> filter_love = FilterByTitleContainsStrategy("love")
        >>> love_songs = filter_love.filter(all_songs)
    """
    
    def __init__(self, search_string):
        """Initialize title search filter.
        
        Args:
            search_string (str): String to search for in titles
        """
        super().__init__()
        self.search_string = search_string.lower() if search_string else ""
        logger.debug(f"Created {self} filter: search='{search_string}'")
    
    def matches(self, item):
        """Check if item's title contains the search string.
        
        Args:
            item: Song to check (must have title attribute)
            
        Returns:
            bool: True if title contains search string
        """
        if not hasattr(item, 'title') or not item.title:
            return False
        
        return self.search_string in item.title.lower()
    
    def filter(self, items):
        """Filter items by title.
        
        Args:
            items (list): List of songs
            
        Returns:
            list: Songs with matching titles
        """
        if not items:
            return []
        
        result = [item for item in items if self.matches(item)]
        logger.debug(f"Title filter '{self.search_string}' matched {len(result)}/{len(items)} items")
        return result
    
    def __str__(self):
        return f"FilterByTitle(contains '{self.search_string}')"


class CompositeFilterStrategy(FilterStrategy):
    """Composite filter that combines multiple filter strategies.
    
    Applies all filters with AND logic - items must match ALL filters.
    Implements the Composite pattern combined with Strategy pattern.
    
    Example:
        >>> # Rock songs between 3-5 minutes by artists containing "Beatles"
        >>> combined = CompositeFilterStrategy([
        ...     FilterByGenreStrategy("Rock"),
        ...     FilterByDurationRangeStrategy(180, 300),
        ...     FilterByArtistStrategy("Beatles", exact=False)
        ... ])
        >>> results = combined.filter(all_songs)
    """
    
    def __init__(self, filters=None):
        """Initialize composite filter.
        
        Args:
            filters (list, optional): List of FilterStrategy instances
        """
        super().__init__()
        self.filters = filters or []
        logger.debug(f"Created CompositeFilter with {len(self.filters)} filters")
    
    def add_filter(self, filter_strategy):
        """Add a filter to the composite.
        
        Args:
            filter_strategy (FilterStrategy): Filter to add
        """
        self.filters.append(filter_strategy)
        logger.debug(f"Added filter to composite: {filter_strategy}")
    
    def remove_filter(self, filter_strategy):
        """Remove a filter from the composite.
        
        Args:
            filter_strategy (FilterStrategy): Filter to remove
        """
        if filter_strategy in self.filters:
            self.filters.remove(filter_strategy)
            logger.debug(f"Removed filter from composite: {filter_strategy}")
    
    def clear_filters(self):
        """Remove all filters."""
        self.filters = []
        logger.debug("Cleared all filters from composite")
    
    def matches(self, item):
        """Check if item matches ALL filters.
        
        Args:
            item: Item to check
            
        Returns:
            bool: True if item matches all filters
        """
        if not self.filters:
            return True  # No filters = match everything
        
        return all(f.matches(item) for f in self.filters)
    
    def filter(self, items):
        """Filter items through all filters (AND logic).
        
        Args:
            items (list): List of items to filter
            
        Returns:
            list: Items matching all filters
        """
        if not items:
            return []
        
        if not self.filters:
            return list(items)  # No filters = return all
        
        result = [item for item in items if self.matches(item)]
        logger.debug(f"CompositeFilter matched {len(result)}/{len(items)} items")
        return result
    
    def __str__(self):
        if not self.filters:
            return "CompositeFilter(empty)"
        filter_strs = [str(f) for f in self.filters]
        return f"CompositeFilter({' AND '.join(filter_strs)})"


class SongFilter:
    """Context class for applying filter strategies to song lists.
    
    Demonstrates the Strategy pattern by allowing the filtering
    algorithm to be changed at runtime.
    
    Example:
        >>> filter_ctx = SongFilter(FilterByGenreStrategy("Rock"))
        >>> rock_songs = filter_ctx.apply(all_songs)
        >>> 
        >>> # Change strategy at runtime
        >>> filter_ctx.set_strategy(FilterByArtistStrategy("Beatles"))
        >>> beatles_songs = filter_ctx.apply(all_songs)
    """
    
    def __init__(self, strategy=None):
        """Initialize with optional strategy.
        
        Args:
            strategy (FilterStrategy, optional): Initial filtering strategy
        """
        self._strategy = strategy
        logger.debug(f"SongFilter initialized with {self._strategy}")
    
    def set_strategy(self, strategy):
        """Change the filtering strategy.
        
        Args:
            strategy (FilterStrategy): New filtering strategy
        """
        self._strategy = strategy
        logger.debug(f"SongFilter strategy changed to {strategy}")
    
    def apply(self, items):
        """Apply the current filter strategy.
        
        Args:
            items (list): Items to filter
            
        Returns:
            list: Filtered items (all items if no strategy set)
        """
        if not self._strategy:
            return list(items) if items else []
        return self._strategy.filter(items)
    
    @property
    def strategy_name(self):
        """Get the current strategy name."""
        return str(self._strategy) if self._strategy else "None"
