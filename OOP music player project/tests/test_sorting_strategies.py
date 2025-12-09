"""Unit tests for sorting strategy implementations.

Tests all sorting strategies including edge cases and polymorphism.
"""

import pytest
from strategies.sorting_strategies import (
    SortStrategy,
    SortByNameStrategy,
    SortByDurationStrategy,
    SortByArtistStrategy,
    SortByGenreStrategy,
    PlaylistSorter
)
from services.track_factory import TrackFactory


class TestSortByNameStrategy:
    """Test suite for SortByNameStrategy."""
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Zebra", 180, "Artist1", "Rock"),
            TrackFactory.create_song("Apple", 200, "Artist2", "Pop"),
            TrackFactory.create_song("Mango", 150, "Artist3", "Jazz"),
        ]
    
    def test_sort_ascending(self, sample_songs):
        """Test sorting by name in ascending order."""
        sorter = SortByNameStrategy()
        result = sorter.sort(sample_songs)
        
        titles = [song.title for song in result]
        assert titles == ["Apple", "Mango", "Zebra"]
    
    def test_sort_descending(self, sample_songs):
        """Test sorting by name in descending order."""
        sorter = SortByNameStrategy(reverse=True)
        result = sorter.sort(sample_songs)
        
        titles = [song.title for song in result]
        assert titles == ["Zebra", "Mango", "Apple"]
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        sorter = SortByNameStrategy()
        result = sorter.sort([])
        assert result == []
    
    def test_sort_case_insensitive(self):
        """Test that sorting is case-insensitive."""
        songs = [
            TrackFactory.create_song("zebra", 180, "Artist1", "Rock"),
            TrackFactory.create_song("APPLE", 200, "Artist2", "Pop"),
            TrackFactory.create_song("Mango", 150, "Artist3", "Jazz"),
        ]
        sorter = SortByNameStrategy()
        result = sorter.sort(songs)
        
        titles = [song.title for song in result]
        assert titles[0] == "APPLE"
        assert titles[1] == "Mango"
        assert titles[2] == "zebra"
    
    def test_str_representation(self):
        """Test string representation."""
        sorter = SortByNameStrategy()
        assert "ascending" in str(sorter)
        
        sorter_desc = SortByNameStrategy(reverse=True)
        assert "descending" in str(sorter_desc)


class TestSortByDurationStrategy:
    """Test suite for SortByDurationStrategy."""
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Song1", 300, "Artist1", "Rock"),
            TrackFactory.create_song("Song2", 100, "Artist2", "Pop"),
            TrackFactory.create_song("Song3", 200, "Artist3", "Jazz"),
        ]
    
    def test_sort_ascending(self, sample_songs):
        """Test sorting by duration shortest first."""
        sorter = SortByDurationStrategy()
        result = sorter.sort(sample_songs)
        
        durations = [song.duration for song in result]
        assert durations == [100, 200, 300]
    
    def test_sort_descending(self, sample_songs):
        """Test sorting by duration longest first."""
        sorter = SortByDurationStrategy(reverse=True)
        result = sorter.sort(sample_songs)
        
        durations = [song.duration for song in result]
        assert durations == [300, 200, 100]
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        sorter = SortByDurationStrategy()
        result = sorter.sort([])
        assert result == []


class TestSortByArtistStrategy:
    """Test suite for SortByArtistStrategy."""
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Song1", 180, "Zeppelin", "Rock"),
            TrackFactory.create_song("Song2", 200, "ABBA", "Pop"),
            TrackFactory.create_song("Song3", 150, "Madonna", "Pop"),
        ]
    
    def test_sort_ascending(self, sample_songs):
        """Test sorting by artist in ascending order."""
        sorter = SortByArtistStrategy()
        result = sorter.sort(sample_songs)
        
        artists = [song.artist for song in result]
        assert artists[0] == "ABBA"
        assert artists[-1] == "Zeppelin"
    
    def test_sort_descending(self, sample_songs):
        """Test sorting by artist in descending order."""
        sorter = SortByArtistStrategy(reverse=True)
        result = sorter.sort(sample_songs)
        
        artists = [song.artist for song in result]
        assert artists[0] == "Zeppelin"
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        sorter = SortByArtistStrategy()
        result = sorter.sort([])
        assert result == []


class TestSortByGenreStrategy:
    """Test suite for SortByGenreStrategy."""
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Song1", 180, "Artist1", "Rock"),
            TrackFactory.create_song("Song2", 200, "Artist2", "Jazz"),
            TrackFactory.create_song("Song3", 150, "Artist3", "Pop"),
        ]
    
    def test_sort_ascending(self, sample_songs):
        """Test sorting by genre in ascending order."""
        sorter = SortByGenreStrategy()
        result = sorter.sort(sample_songs)
        
        genres = [song.genre for song in result]
        assert genres == ["Jazz", "Pop", "Rock"]
    
    def test_sort_descending(self, sample_songs):
        """Test sorting by genre in descending order."""
        sorter = SortByGenreStrategy(reverse=True)
        result = sorter.sort(sample_songs)
        
        genres = [song.genre for song in result]
        assert genres == ["Rock", "Pop", "Jazz"]
    
    def test_sort_empty_list(self):
        """Test sorting empty list."""
        sorter = SortByGenreStrategy()
        result = sorter.sort([])
        assert result == []


class TestPlaylistSorter:
    """Test suite for PlaylistSorter facade."""
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Zebra", 300, "Artist1", "Rock"),
            TrackFactory.create_song("Apple", 100, "Artist2", "Pop"),
            TrackFactory.create_song("Mango", 200, "Artist3", "Jazz"),
        ]
    
    def test_sort_with_default_strategy(self, sample_songs):
        """Test sorting with default strategy (by name)."""
        sorter = PlaylistSorter()
        result = sorter.sort(sample_songs)
        
        titles = [song.title for song in result]
        assert titles[0] == "Apple"
    
    def test_sort_with_duration_strategy(self, sample_songs):
        """Test sorting by duration using set_strategy."""
        sorter = PlaylistSorter()
        sorter.set_strategy(SortByDurationStrategy())
        result = sorter.sort(sample_songs)
        
        durations = [song.duration for song in result]
        assert durations == [100, 200, 300]
    
    def test_strategy_name_property(self):
        """Test strategy_name property."""
        sorter = PlaylistSorter()
        assert "SortByNameStrategy" in sorter.strategy_name
        
        sorter.set_strategy(SortByDurationStrategy())
        assert "SortByDurationStrategy" in sorter.strategy_name
    
    def test_change_strategy_at_runtime(self, sample_songs):
        """Test changing strategy at runtime."""
        sorter = PlaylistSorter(SortByNameStrategy())
        
        # Sort by name first
        by_name = sorter.sort(sample_songs)
        assert by_name[0].title == "Apple"
        
        # Change to duration strategy
        sorter.set_strategy(SortByDurationStrategy())
        by_duration = sorter.sort(sample_songs)
        assert by_duration[0].duration == 100


class TestSortStrategyPolymorphism:
    """Test that all strategies are polymorphic."""
    
    @pytest.fixture
    def all_strategies(self):
        """Fixture providing all strategy instances."""
        return [
            SortByNameStrategy(),
            SortByDurationStrategy(),
            SortByArtistStrategy(),
            SortByGenreStrategy()
        ]
    
    @pytest.fixture
    def sample_songs(self):
        """Create sample songs for testing."""
        return [
            TrackFactory.create_song("Song1", 180, "Artist1", "Rock"),
            TrackFactory.create_song("Song2", 200, "Artist2", "Pop"),
        ]
    
    def test_all_inherit_from_base(self, all_strategies):
        """Test that all strategies inherit from SortStrategy."""
        for strategy in all_strategies:
            assert isinstance(strategy, SortStrategy)
    
    def test_all_implement_sort(self, all_strategies, sample_songs):
        """Test that all strategies implement sort method."""
        for strategy in all_strategies:
            result = strategy.sort(sample_songs)
            assert isinstance(result, list)
    
    def test_all_have_reverse_option(self, all_strategies):
        """Test that all strategies support reverse option."""
        for strategy in all_strategies:
            assert hasattr(strategy, 'reverse')
