"""Unit tests for playlist repository module.

Tests CRUD operations for Playlist entities, relationships, and repository inheritance.
"""

import unittest
import os
import tempfile

from database.connection import DatabaseConnection
from database.schema import initialize_database
from models.song import Song
from models.user import User
from models.playlist import Playlist
from repositories.playlist_repository import PlaylistRepository
from repositories.song_repository import SongRepository
from repositories.user_repository import UserRepository
from repositories.base_repository import BaseRepository


class TestPlaylistRepository(unittest.TestCase):
    """Test suite for PlaylistRepository class."""
    
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
        
        self.playlist_repo = PlaylistRepository(self.db)
        self.song_repo = SongRepository(self.db)
        self.user_repo = UserRepository(self.db)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.execute_update("DELETE FROM playlist_songs")
        self.db.execute_update("DELETE FROM playlists")
        self.db.execute_update("DELETE FROM songs")
        self.db.execute_update("DELETE FROM users")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_repository_inheritance(self):
        """Test that PlaylistRepository inherits from BaseRepository."""
        self.assertIsInstance(self.playlist_repo, BaseRepository)
    
    def test_create_playlist_returns_id(self):
        """Test that create_playlist persists and returns ID."""
        user = User(username="user1", email="user1@example.com")
        user_id = self.user_repo.create(user)
        
        playlist = Playlist(name="My Playlist", owner_id=user_id)
        
        playlist_id = self.playlist_repo.create(playlist)
        
        self.assertIsNotNone(playlist_id)
    
    def test_create_playlist_with_invalid_entity_raises_error(self):
        """Test that create raises ValueError for non-Playlist object."""
        with self.assertRaises(ValueError):
            self.playlist_repo.create("not a playlist")
    
    def test_read_by_id_returns_playlist(self):
        """Test that read_by_id retrieves created playlist."""
        user = User(username="user2", email="user2@example.com")
        user_id = self.user_repo.create(user)
        
        original_playlist = Playlist(name="Favorites", owner_id=user_id)
        playlist_id = self.playlist_repo.create(original_playlist)
        
        retrieved_playlist = self.playlist_repo.read_by_id(playlist_id)
        
        self.assertIsNotNone(retrieved_playlist)
        self.assertEqual(retrieved_playlist.name, "Favorites")
        self.assertEqual(retrieved_playlist.owner_id, user_id)
    
    def test_read_by_id_returns_none_for_nonexistent_id(self):
        """Test that read_by_id returns None for non-existent ID."""
        result = self.playlist_repo.read_by_id("nonexistent-id")
        self.assertIsNone(result)
    
    def test_read_all_returns_all_playlists(self):
        """Test that read_all returns all created playlists."""
        user = User(username="user3", email="user3@example.com")
        user_id = self.user_repo.create(user)
        
        for i in range(3):
            playlist = Playlist(name=f"Playlist {i}", owner_id=user_id)
            self.playlist_repo.create(playlist)
        
        all_playlists = self.playlist_repo.read_all()
        
        self.assertEqual(len(all_playlists), 3)
    
    def test_read_all_returns_empty_list_when_no_playlists(self):
        """Test that read_all returns empty list when database is empty."""
        all_playlists = self.playlist_repo.read_all()
        self.assertEqual(len(all_playlists), 0)
    
    def test_exists_returns_true_for_existing_playlist(self):
        """Test that exists returns True for created playlist."""
        user = User(username="user4", email="user4@example.com")
        user_id = self.user_repo.create(user)
        
        playlist = Playlist(name="Test", owner_id=user_id)
        playlist_id = self.playlist_repo.create(playlist)
        
        self.assertTrue(self.playlist_repo.exists(playlist_id))
    
    def test_exists_returns_false_for_nonexistent_playlist(self):
        """Test that exists returns False for non-existent ID."""
        self.assertFalse(self.playlist_repo.exists("nonexistent-id"))
    
    def test_read_by_owner_id_returns_user_playlists(self):
        """Test that read_by_owner_id returns only playlists for user."""
        user1 = User(username="alice", email="alice@example.com")
        user2 = User(username="bob", email="bob@example.com")
        
        user1_id = self.user_repo.create(user1)
        user2_id = self.user_repo.create(user2)
        
        # Create playlists for both users
        for i in range(2):
            playlist1 = Playlist(name=f"Alice's Playlist {i}", owner_id=user1_id)
            self.playlist_repo.create(playlist1)
        
        for i in range(3):
            playlist2 = Playlist(name=f"Bob's Playlist {i}", owner_id=user2_id)
            self.playlist_repo.create(playlist2)
        
        alice_playlists = self.playlist_repo.read_by_owner_id(user1_id)
        bob_playlists = self.playlist_repo.read_by_owner_id(user2_id)
        
        self.assertEqual(len(alice_playlists), 2)
        self.assertEqual(len(bob_playlists), 3)
        
        for playlist in alice_playlists:
            self.assertEqual(playlist.owner_id, user1_id)
    
    def test_read_by_owner_id_returns_empty_for_user_with_no_playlists(self):
        """Test that read_by_owner_id returns empty list for user without playlists."""
        user = User(username="charlie", email="charlie@example.com")
        user_id = self.user_repo.create(user)
        
        playlists = self.playlist_repo.read_by_owner_id(user_id)
        
        self.assertEqual(len(playlists), 0)
    
    def test_add_song_to_playlist_creates_junction_entry(self):
        """Test that add_song_to_playlist creates relationship."""
        user = User(username="user5", email="user5@example.com")
        user_id = self.user_repo.create(user)
        
        song = Song(title="Song", artist="Artist", genre="Genre", duration=180)
        song_id = self.song_repo.create(song)
        
        playlist = Playlist(name="Playlist", owner_id=user_id)
        playlist_id = self.playlist_repo.create(playlist)
        
        success = self.playlist_repo.add_song_to_playlist(playlist_id, song_id)
        
        self.assertTrue(success)
    
    def test_get_playlist_songs_returns_song_ids(self):
        """Test that get_playlist_songs returns all songs in playlist."""
        user = User(username="user6", email="user6@example.com")
        user_id = self.user_repo.create(user)
        
        # Create songs
        song_ids = []
        for i in range(3):
            song = Song(
                title=f"Song {i}",
                artist=f"Artist {i}",
                genre="Genre",
                duration=180 + i * 10
            )
            song_id = self.song_repo.create(song)
            song_ids.append(song_id)
        
        # Create playlist and add songs
        playlist = Playlist(name="Playlist", owner_id=user_id)
        playlist_id = self.playlist_repo.create(playlist)
        
        for song_id in song_ids:
            self.playlist_repo.add_song_to_playlist(playlist_id, song_id)
        
        # Retrieve songs
        retrieved_song_ids = self.playlist_repo.get_playlist_songs(playlist_id)
        
        self.assertEqual(len(retrieved_song_ids), 3)
        for song_id in song_ids:
            self.assertIn(song_id, retrieved_song_ids)
    
    def test_get_playlist_songs_returns_empty_for_empty_playlist(self):
        """Test that get_playlist_songs returns empty list for new playlist."""
        user = User(username="user7", email="user7@example.com")
        user_id = self.user_repo.create(user)
        
        playlist = Playlist(name="Empty", owner_id=user_id)
        playlist_id = self.playlist_repo.create(playlist)
        
        songs = self.playlist_repo.get_playlist_songs(playlist_id)
        
        self.assertEqual(len(songs), 0)
    
    def test_multiple_playlists_have_separate_songs(self):
        """Test that songs in one playlist don't affect another."""
        user = User(username="user8", email="user8@example.com")
        user_id = self.user_repo.create(user)
        
        # Create songs
        song1 = Song(title="Song 1", artist="Artist 1", genre="Genre", duration=180)
        song2 = Song(title="Song 2", artist="Artist 2", genre="Genre", duration=200)
        song1_id = self.song_repo.create(song1)
        song2_id = self.song_repo.create(song2)
        
        # Create playlists
        playlist1 = Playlist(name="Playlist 1", owner_id=user_id)
        playlist2 = Playlist(name="Playlist 2", owner_id=user_id)
        playlist1_id = self.playlist_repo.create(playlist1)
        playlist2_id = self.playlist_repo.create(playlist2)
        
        # Add different songs to each
        self.playlist_repo.add_song_to_playlist(playlist1_id, song1_id)
        self.playlist_repo.add_song_to_playlist(playlist2_id, song2_id)
        
        # Verify separation
        playlist1_songs = self.playlist_repo.get_playlist_songs(playlist1_id)
        playlist2_songs = self.playlist_repo.get_playlist_songs(playlist2_id)
        
        self.assertEqual(len(playlist1_songs), 1)
        self.assertEqual(len(playlist2_songs), 1)
        self.assertEqual(playlist1_songs[0], song1_id)
        self.assertEqual(playlist2_songs[0], song2_id)


if __name__ == '__main__':
    unittest.main()
