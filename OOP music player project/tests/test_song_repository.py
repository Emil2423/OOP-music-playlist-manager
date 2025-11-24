"""Unit tests for song repository module.

Tests CRUD operations for Song entities and repository inheritance.
"""

import unittest
import os
import tempfile

from database.connection import DatabaseConnection
from database.schema import initialize_database
from models.song import Song
from repositories.song_repository import SongRepository
from repositories.base_repository import BaseRepository


class TestSongRepository(unittest.TestCase):
    """Test suite for SongRepository class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
        # Use persistent test database for the class
        cls.test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.test_db_path = cls.test_db_file.name
        cls.test_db_file.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after entire test class."""
        if os.path.exists(cls.test_db_path):
            os.unlink(cls.test_db_path)
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Reset singleton for each test
        DatabaseConnection.reset_instance()
        
        # Create fresh database connection
        self.db = DatabaseConnection(self.test_db_path)
        self.db.connect()
        
        # Initialize schema
        initialize_database(self.db)
        
        # Create repository
        self.repo = SongRepository(self.db)
    
    def tearDown(self):
        """Clean up after each test."""
        # Clean up database
        self.db.execute_update("DELETE FROM playlist_songs")
        self.db.execute_update("DELETE FROM songs")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_repository_inheritance(self):
        """Test that SongRepository inherits from BaseRepository."""
        self.assertIsInstance(self.repo, BaseRepository)
    
    def test_create_song_returns_id(self):
        """Test that create_song persists and returns ID."""
        song = Song(
            title="Imagine",
            artist="John Lennon",
            genre="Rock",
            duration=183
        )
        
        song_id = self.repo.create(song)
        
        self.assertIsNotNone(song_id)
        self.assertEqual(song_id, song.id)
    
    def test_create_song_with_invalid_entity_raises_error(self):
        """Test that create raises ValueError for non-Song object."""
        with self.assertRaises(ValueError):
            self.repo.create("not a song")
    
    def test_read_by_id_returns_song(self):
        """Test that read_by_id retrieves created song."""
        original_song = Song(
            title="Test Song",
            artist="Test Artist",
            genre="Test Genre",
            duration=100
        )
        
        song_id = self.repo.create(original_song)
        retrieved_song = self.repo.read_by_id(song_id)
        
        self.assertIsNotNone(retrieved_song)
        self.assertEqual(retrieved_song.title, "Test Song")
        self.assertEqual(retrieved_song.artist, "Test Artist")
        self.assertEqual(retrieved_song.genre, "Test Genre")
        self.assertEqual(retrieved_song.duration, 100)
    
    def test_read_by_id_returns_none_for_nonexistent_id(self):
        """Test that read_by_id returns None for non-existent ID."""
        result = self.repo.read_by_id("nonexistent-id")
        self.assertIsNone(result)
    
    def test_read_all_returns_all_songs(self):
        """Test that read_all returns all created songs."""
        songs_data = [
            ("Song 1", "Artist 1", "Rock", 180),
            ("Song 2", "Artist 2", "Pop", 200),
            ("Song 3", "Artist 3", "Jazz", 220)
        ]
        
        for title, artist, genre, duration in songs_data:
            song = Song(title=title, artist=artist, genre=genre, duration=duration)
            self.repo.create(song)
        
        all_songs = self.repo.read_all()
        
        self.assertEqual(len(all_songs), 3)
    
    def test_read_all_returns_empty_list_when_no_songs(self):
        """Test that read_all returns empty list when database is empty."""
        all_songs = self.repo.read_all()
        self.assertEqual(len(all_songs), 0)
    
    def test_exists_returns_true_for_existing_song(self):
        """Test that exists returns True for created song."""
        song = Song(title="Test", artist="Test", genre="Test", duration=100)
        song_id = self.repo.create(song)
        
        self.assertTrue(self.repo.exists(song_id))
    
    def test_exists_returns_false_for_nonexistent_song(self):
        """Test that exists returns False for non-existent ID."""
        self.assertFalse(self.repo.exists("nonexistent-id"))
    
    def test_read_by_artist_filters_correctly(self):
        """Test that read_by_artist returns only songs by specified artist."""
        songs_data = [
            ("Song 1", "Beatles", "Rock", 180),
            ("Song 2", "Beatles", "Rock", 200),
            ("Song 3", "Lennon", "Rock", 220)
        ]
        
        for title, artist, genre, duration in songs_data:
            song = Song(title=title, artist=artist, genre=genre, duration=duration)
            self.repo.create(song)
        
        beatles_songs = self.repo.read_by_artist("Beatles")
        
        self.assertEqual(len(beatles_songs), 2)
        for song in beatles_songs:
            self.assertEqual(song.artist, "Beatles")
    
    def test_read_by_artist_returns_empty_for_nonexistent_artist(self):
        """Test that read_by_artist returns empty list for unknown artist."""
        result = self.repo.read_by_artist("Unknown Artist")
        self.assertEqual(len(result), 0)
    
    def test_read_by_genre_filters_correctly(self):
        """Test that read_by_genre returns only songs of specified genre."""
        songs_data = [
            ("Song 1", "Artist 1", "Rock", 180),
            ("Song 2", "Artist 2", "Rock", 200),
            ("Song 3", "Artist 3", "Jazz", 220)
        ]
        
        for title, artist, genre, duration in songs_data:
            song = Song(title=title, artist=artist, genre=genre, duration=duration)
            self.repo.create(song)
        
        rock_songs = self.repo.read_by_genre("Rock")
        
        self.assertEqual(len(rock_songs), 2)
        for song in rock_songs:
            self.assertEqual(song.genre, "Rock")
    
    def test_read_by_genre_returns_empty_for_nonexistent_genre(self):
        """Test that read_by_genre returns empty list for unknown genre."""
        result = self.repo.read_by_genre("Unknown Genre")
        self.assertEqual(len(result), 0)
    
    def test_create_multiple_songs_with_unique_ids(self):
        """Test that each created song has a unique ID."""
        songs = []
        for i in range(5):
            song = Song(
                title=f"Song {i}",
                artist=f"Artist {i}",
                genre=f"Genre {i}",
                duration=100 + i * 10
            )
            song_id = self.repo.create(song)
            songs.append(song_id)
        
        # Check all IDs are unique
        self.assertEqual(len(songs), len(set(songs)))
    
    def test_song_attributes_preserved_after_round_trip(self):
        """Test that song attributes are preserved through database round-trip."""
        original = Song(
            title="Test Title",
            artist="Test Artist",
            genre="Test Genre",
            duration=250
        )
        
        song_id = self.repo.create(original)
        retrieved = self.repo.read_by_id(song_id)
        
        self.assertEqual(retrieved.title, original.title)
        self.assertEqual(retrieved.artist, original.artist)
        self.assertEqual(retrieved.genre, original.genre)
        self.assertEqual(retrieved.duration, original.duration)
    
    def test_special_characters_in_song_title(self):
        """Test that special characters in titles are handled correctly."""
        song = Song(
            title="Bohemian Rhapsody (Rock Opera) - Remastered [2009]",
            artist="Queen & Freddie Mercury's 'True' Collection",
            genre="Rock/Opera",
            duration=354
        )
        
        song_id = self.repo.create(song)
        retrieved = self.repo.read_by_id(song_id)
        
        self.assertEqual(retrieved.title, song.title)
        self.assertEqual(retrieved.artist, song.artist)
        self.assertEqual(retrieved.genre, song.genre)


if __name__ == '__main__':
    unittest.main()
