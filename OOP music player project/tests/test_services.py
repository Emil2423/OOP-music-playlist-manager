"""Unit tests for service layer modules.

Tests business logic in SongService, PlaylistService, and UserService.
"""

import unittest
import os
import tempfile

from database.connection import DatabaseConnection
from database.schema import initialize_database
from models.song import Song
from models.user import User
from models.playlist import Playlist
from services.song_service import SongService
from services.playlist_service import PlaylistService
from services.user_service import UserService
from repositories.song_repository import SongRepository
from repositories.user_repository import UserRepository
from repositories.playlist_repository import PlaylistRepository
from services.track_factory import TrackFactory
from exceptions.custom_exceptions import (
    ValidationError,
    EntityNotFoundError,
    DatabaseError
)


class TestSongService(unittest.TestCase):
    """Test suite for SongService class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
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
        DatabaseConnection.reset_instance()
        self.db = DatabaseConnection(self.test_db_path)
        self.db.connect()
        initialize_database(self.db)
        
        self.song_repo = SongRepository(self.db)
        self.service = SongService(self.song_repo)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.execute_update("DELETE FROM playlist_songs")
        self.db.execute_update("DELETE FROM songs")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_create_song_success(self):
        """Test successful song creation."""
        song = self.service.create_song(
            title="Imagine",
            artist="John Lennon",
            genre="Rock",
            duration=183
        )
        
        self.assertIsNotNone(song)
        self.assertIsNotNone(song.id)
        self.assertEqual(song.title, "Imagine")
        self.assertEqual(song.artist, "John Lennon")
    
    def test_create_song_empty_title_raises_error(self):
        """Test that empty title raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_song("", "Artist", "Rock", 180)
    
    def test_create_song_empty_artist_raises_error(self):
        """Test that empty artist raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_song("Title", "", "Rock", 180)
    
    def test_create_song_empty_genre_raises_error(self):
        """Test that empty genre raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_song("Title", "Artist", "", 180)
    
    def test_create_song_negative_duration_raises_error(self):
        """Test that negative duration raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_song("Title", "Artist", "Rock", -10)
    
    def test_create_song_zero_duration_raises_error(self):
        """Test that zero duration raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_song("Title", "Artist", "Rock", 0)
    
    def test_get_song_by_id_success(self):
        """Test retrieving a song by ID."""
        created = self.service.create_song("Test", "Artist", "Rock", 180)
        retrieved = self.service.get_song_by_id(created.id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Test")
    
    def test_get_song_by_id_not_found_raises_error(self):
        """Test that non-existent song ID raises EntityNotFoundError."""
        with self.assertRaises(EntityNotFoundError):
            self.service.get_song_by_id("nonexistent-id")
    
    def test_get_all_songs_returns_list(self):
        """Test retrieving all songs."""
        self.service.create_song("Song1", "Artist1", "Rock", 180)
        self.service.create_song("Song2", "Artist2", "Pop", 200)
        
        songs = self.service.get_all_songs()
        
        self.assertEqual(len(songs), 2)
    
    def test_get_all_songs_empty_database(self):
        """Test retrieving all songs when database is empty."""
        songs = self.service.get_all_songs()
        self.assertEqual(len(songs), 0)
    
    def test_update_song_success(self):
        """Test successful song update."""
        song = self.service.create_song("Original", "Artist", "Rock", 180)
        
        updated = self.service.update_song(
            song.id,
            new_title="Updated Title"
        )
        
        self.assertEqual(updated.title, "Updated Title")
    
    def test_delete_song_success(self):
        """Test successful song deletion."""
        song = self.service.create_song("To Delete", "Artist", "Rock", 180)
        
        self.service.delete_song(song.id)
        
        with self.assertRaises(EntityNotFoundError):
            self.service.get_song_by_id(song.id)


class TestUserService(unittest.TestCase):
    """Test suite for UserService class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
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
        DatabaseConnection.reset_instance()
        self.db = DatabaseConnection(self.test_db_path)
        self.db.connect()
        initialize_database(self.db)
        
        self.user_repo = UserRepository(self.db)
        self.service = UserService(self.user_repo)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.execute_update("DELETE FROM playlist_songs")
        self.db.execute_update("DELETE FROM playlists")
        self.db.execute_update("DELETE FROM users")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user = self.service.create_user(
            username="john_doe",
            email="john@example.com"
        )
        
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.id)
        # Note: UserService may title-case usernames
        self.assertIn("john", user.username.lower())
        self.assertEqual(user.email, "john@example.com")
    
    def test_create_user_empty_username_raises_error(self):
        """Test that empty username raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_user("", "email@example.com")
    
    def test_create_user_empty_email_raises_error(self):
        """Test that empty email raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_user("username", "")
    
    def test_get_user_by_id_success(self):
        """Test retrieving a user by ID."""
        created = self.service.create_user("testuser", "test@example.com")
        retrieved = self.service.get_user_by_id(created.id)
        
        self.assertIsNotNone(retrieved)
        # Note: UserService may title-case usernames
        self.assertIn("testuser", retrieved.username.lower())
    
    def test_get_user_by_id_not_found_raises_error(self):
        """Test that non-existent user ID raises EntityNotFoundError."""
        with self.assertRaises(EntityNotFoundError):
            self.service.get_user_by_id("nonexistent-id")
    
    def test_get_all_users_returns_list(self):
        """Test retrieving all users."""
        self.service.create_user("user1", "user1@example.com")
        self.service.create_user("user2", "user2@example.com")
        
        users = self.service.get_all_users()
        
        self.assertEqual(len(users), 2)
    
    def test_update_user_success(self):
        """Test successful user update."""
        user = self.service.create_user("original", "original@example.com")
        
        updated = self.service.update_user(
            user.id,
            new_username="updated_user"
        )
        
        # Note: UserService may title-case usernames
        self.assertIn("updated", updated.username.lower())
    
    def test_delete_user_success(self):
        """Test successful user deletion."""
        user = self.service.create_user("todelete", "delete@example.com")
        
        self.service.delete_user(user.id)
        
        with self.assertRaises(EntityNotFoundError):
            self.service.get_user_by_id(user.id)


class TestPlaylistService(unittest.TestCase):
    """Test suite for PlaylistService class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
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
        DatabaseConnection.reset_instance()
        self.db = DatabaseConnection(self.test_db_path)
        self.db.connect()
        initialize_database(self.db)
        
        self.user_repo = UserRepository(self.db)
        self.song_repo = SongRepository(self.db)
        self.playlist_repo = PlaylistRepository(self.db)
        self.service = PlaylistService(self.playlist_repo, self.song_repo, self.user_repo)
        
        # Create test user for playlists
        self.test_user = User(username="testuser", email="test@example.com")
        self.user_repo.create(self.test_user)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.execute_update("DELETE FROM playlist_songs")
        self.db.execute_update("DELETE FROM playlists")
        self.db.execute_update("DELETE FROM songs")
        self.db.execute_update("DELETE FROM users")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_create_playlist_success(self):
        """Test successful playlist creation."""
        playlist = self.service.create_playlist(
            name="My Favorites",
            owner_id=self.test_user.id
        )
        
        self.assertIsNotNone(playlist)
        self.assertIsNotNone(playlist.id)
        # Note: playlist name gets title-cased
        self.assertIn("Favorites", playlist.name)
    
    def test_create_playlist_empty_name_raises_error(self):
        """Test that empty name raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.service.create_playlist("", self.test_user.id)
    
    def test_create_playlist_invalid_owner_raises_error(self):
        """Test that invalid owner_id raises EntityNotFoundError."""
        with self.assertRaises(EntityNotFoundError):
            self.service.create_playlist("Test Playlist", "invalid-user-id")
    
    def test_get_playlist_by_id_success(self):
        """Test retrieving a playlist by ID."""
        created = self.service.create_playlist("Test", self.test_user.id)
        retrieved = self.service.get_playlist_by_id(created.id)
        
        self.assertIsNotNone(retrieved)
    
    def test_get_playlist_by_id_not_found_raises_error(self):
        """Test that non-existent playlist ID raises EntityNotFoundError."""
        with self.assertRaises(EntityNotFoundError):
            self.service.get_playlist_by_id("nonexistent-id")
    
    def test_get_all_playlists_returns_list(self):
        """Test retrieving all playlists."""
        self.service.create_playlist("Playlist1", self.test_user.id)
        self.service.create_playlist("Playlist2", self.test_user.id)
        
        playlists = self.service.get_all_playlists()
        
        self.assertEqual(len(playlists), 2)
    
    def test_add_song_to_playlist_success(self):
        """Test adding a song to a playlist."""
        playlist = self.service.create_playlist("Test", self.test_user.id)
        song = TrackFactory.create_song("Test Song", 180, "Artist", "Rock")
        self.song_repo.create(song)
        
        self.service.add_song_to_playlist(playlist.id, song.id)
        
        songs = self.service.get_playlist_songs(playlist.id)
        self.assertEqual(len(songs), 1)
    
    def test_remove_song_from_playlist_success(self):
        """Test removing a song from a playlist."""
        playlist = self.service.create_playlist("Test", self.test_user.id)
        song = TrackFactory.create_song("Test Song", 180, "Artist", "Rock")
        self.song_repo.create(song)
        
        self.service.add_song_to_playlist(playlist.id, song.id)
        self.service.remove_song_from_playlist(playlist.id, song.id)
        
        songs = self.service.get_playlist_songs(playlist.id)
        self.assertEqual(len(songs), 0)
    
    def test_get_playlist_song_count(self):
        """Test getting playlist song count."""
        playlist = self.service.create_playlist("Test", self.test_user.id)
        
        song1 = TrackFactory.create_song("Song1", 180, "Artist1", "Rock")
        song2 = TrackFactory.create_song("Song2", 200, "Artist2", "Pop")
        self.song_repo.create(song1)
        self.song_repo.create(song2)
        
        self.service.add_song_to_playlist(playlist.id, song1.id)
        self.service.add_song_to_playlist(playlist.id, song2.id)
        
        songs = self.service.get_playlist_songs(playlist.id)
        self.assertEqual(len(songs), 2)


class TestTrackFactory(unittest.TestCase):
    """Test suite for TrackFactory."""
    
    def test_create_song_success(self):
        """Test successful song creation via factory."""
        song = TrackFactory.create_song(
            title="Test Song",
            duration=180,
            artist="Test Artist",
            genre="Rock"
        )
        
        self.assertIsNotNone(song)
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.artist, "Test Artist")
        self.assertEqual(song.duration, 180)
    
    def test_create_song_negative_duration_raises_error(self):
        """Test that negative duration raises ValueError."""
        with self.assertRaises(ValueError):
            TrackFactory.create_song("Test", -10, "Artist", "Rock")
    
    def test_create_song_generates_unique_ids(self):
        """Test that each created song has a unique ID."""
        song1 = TrackFactory.create_song("Song1", 100, "Artist", "Rock")
        song2 = TrackFactory.create_song("Song2", 100, "Artist", "Rock")
        
        self.assertNotEqual(song1.id, song2.id)


if __name__ == '__main__':
    unittest.main()
