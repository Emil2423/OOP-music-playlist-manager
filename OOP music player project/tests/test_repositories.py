"""
Unit Tests for Repository Layer
Tests CRUD operations, error handling, and transaction management.
"""

import pytest
import os
import tempfile
from src.database.connection import DatabaseConnection
from src.database.schema import DatabaseSchema
from src.repositories.song_repository import SongRepository
from src.repositories.user_repository import UserRepository
from src.repositories.playlist_repository import PlaylistRepository
from src.models.song import Song
from src.models.user import User
from src.models.playlist import Playlist
from src.services.track_factory import TrackFactory


@pytest.fixture(scope="function")
def temp_db():
    """Create temporary database for testing."""
    # Create temporary database file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Reset singleton and initialize with temp database
    DatabaseConnection._instance = None
    db = DatabaseConnection(db_path)
    db.connect()
    
    # Initialize schema
    DatabaseSchema.initialize_database()
    
    yield db
    
    # Cleanup
    db.disconnect()
    try:
        os.remove(db_path)
    except:
        pass
    
    # Reset singleton
    DatabaseConnection._instance = None


@pytest.fixture
def song_repo(temp_db):
    """Create SongRepository instance."""
    return SongRepository(temp_db)


@pytest.fixture
def user_repo(temp_db):
    """Create UserRepository instance."""
    return UserRepository(temp_db)


@pytest.fixture
def playlist_repo(temp_db):
    """Create PlaylistRepository instance."""
    return PlaylistRepository(temp_db)


class TestSongRepository:
    """Test cases for SongRepository."""
    
    def test_create_song_success(self, song_repo):
        """Test creating a song successfully."""
        song = TrackFactory.create_song("Imagine", 183, "John Lennon", "Rock")
        song_id = song_repo.create(song)
        
        assert song_id is not None
        assert song_id == song.id
    
    def test_create_song_invalid_duration(self, song_repo):
        """Test creating song with invalid duration fails."""
        with pytest.raises(ValueError):
            song = TrackFactory.create_song("Bad Song", -50, "Artist", "Pop")
    
    def test_create_song_not_song_instance(self, song_repo):
        """Test creating with non-Song object fails."""
        with pytest.raises(ValueError):
            song_repo.create("not a song")
    
    def test_read_song_success(self, song_repo):
        """Test reading an existing song."""
        song = TrackFactory.create_song("Let It Be", 243, "The Beatles", "Rock")
        song_id = song_repo.create(song)
        
        result = song_repo.read(song_id)
        assert result is not None
        assert result['title'] == "Let It Be"
        assert result['artist'] == "The Beatles"
        assert result['duration'] == 243
    
    def test_read_song_not_found(self, song_repo):
        """Test reading non-existent song returns None."""
        result = song_repo.read("nonexistent-id")
        assert result is None
    
    def test_read_all_songs(self, song_repo):
        """Test reading all songs."""
        song1 = TrackFactory.create_song("Song 1", 200, "Artist 1", "Genre1")
        song2 = TrackFactory.create_song("Song 2", 250, "Artist 2", "Genre2")
        
        song_repo.create(song1)
        song_repo.create(song2)
        
        all_songs = song_repo.read_all()
        assert len(all_songs) == 2
    
    def test_read_by_artist(self, song_repo):
        """Test reading songs by artist."""
        song1 = TrackFactory.create_song("Song 1", 200, "Queen", "Rock")
        song2 = TrackFactory.create_song("Song 2", 250, "Queen", "Rock")
        song3 = TrackFactory.create_song("Song 3", 300, "Beatles", "Rock")
        
        song_repo.create(song1)
        song_repo.create(song2)
        song_repo.create(song3)
        
        queen_songs = song_repo.read_by_artist("Queen")
        assert len(queen_songs) == 2
        assert all(s['artist'] == "Queen" for s in queen_songs)
    
    def test_read_by_genre(self, song_repo):
        """Test reading songs by genre."""
        song1 = TrackFactory.create_song("Song 1", 200, "Artist 1", "Rock")
        song2 = TrackFactory.create_song("Song 2", 250, "Artist 2", "Jazz")
        song3 = TrackFactory.create_song("Song 3", 300, "Artist 3", "Rock")
        
        song_repo.create(song1)
        song_repo.create(song2)
        song_repo.create(song3)
        
        rock_songs = song_repo.read_by_genre("Rock")
        assert len(rock_songs) == 2
        assert all(s['genre'] == "Rock" for s in rock_songs)
    
    def test_song_exists(self, song_repo):
        """Test checking if song exists."""
        song = TrackFactory.create_song("Stairway to Heaven", 482, "Led Zeppelin", "Rock")
        song_id = song_repo.create(song)
        
        assert song_repo.exists(song_id) is True
        assert song_repo.exists("nonexistent") is False
    
    def test_delete_song(self, song_repo):
        """Test deleting a song."""
        song = TrackFactory.create_song("Song to Delete", 200, "Artist", "Genre")
        song_id = song_repo.create(song)
        
        assert song_repo.exists(song_id) is True
        success = song_repo.delete(song_id)
        assert success is True
        assert song_repo.exists(song_id) is False
    
    def test_delete_nonexistent_song(self, song_repo):
        """Test deleting non-existent song returns False."""
        success = song_repo.delete("nonexistent-id")
        assert success is False


class TestUserRepository:
    """Test cases for UserRepository."""
    
    def test_create_user_success(self, user_repo):
        """Test creating a user successfully."""
        user = User("testuser", "test@example.com")
        user_id = user_repo.create(user)
        
        assert user_id is not None
        assert user_id == user.id
    
    def test_create_user_not_user_instance(self, user_repo):
        """Test creating with non-User object fails."""
        with pytest.raises(ValueError):
            user_repo.create("not a user")
    
    def test_read_user_success(self, user_repo):
        """Test reading an existing user."""
        user = User("johndoe", "john@example.com")
        user_id = user_repo.create(user)
        
        result = user_repo.read(user_id)
        assert result is not None
        assert result['username'] == "johndoe"
        assert result['email'] == "john@example.com"
    
    def test_read_user_not_found(self, user_repo):
        """Test reading non-existent user returns None."""
        result = user_repo.read("nonexistent-id")
        assert result is None
    
    def test_read_all_users(self, user_repo):
        """Test reading all users."""
        user1 = User("user1", "user1@example.com")
        user2 = User("user2", "user2@example.com")
        
        user_repo.create(user1)
        user_repo.create(user2)
        
        all_users = user_repo.read_all()
        assert len(all_users) == 2
    
    def test_read_by_username(self, user_repo):
        """Test reading user by username."""
        user = User("uniqueuser", "unique@example.com")
        user_repo.create(user)
        
        result = user_repo.read_by_username("uniqueuser")
        assert result is not None
        assert result['username'] == "uniqueuser"
    
    def test_read_by_email(self, user_repo):
        """Test reading user by email."""
        user = User("emailtest", "email@test.com")
        user_repo.create(user)
        
        result = user_repo.read_by_email("email@test.com")
        assert result is not None
        assert result['email'] == "email@test.com"
    
    def test_user_exists(self, user_repo):
        """Test checking if user exists."""
        user = User("existstest", "exists@example.com")
        user_id = user_repo.create(user)
        
        assert user_repo.exists(user_id) is True
        assert user_repo.exists("nonexistent") is False
    
    def test_delete_user(self, user_repo):
        """Test deleting a user."""
        user = User("deletetest", "delete@example.com")
        user_id = user_repo.create(user)
        
        assert user_repo.exists(user_id) is True
        success = user_repo.delete(user_id)
        assert success is True
        assert user_repo.exists(user_id) is False


class TestPlaylistRepository:
    """Test cases for PlaylistRepository."""
    
    def test_create_playlist_success(self, user_repo, playlist_repo):
        """Test creating a playlist successfully."""
        user = User("playlistuser", "playlist@example.com")
        user_id = user_repo.create(user)
        
        playlist = Playlist("My Favorites", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        assert playlist_id is not None
    
    def test_create_playlist_invalid(self, playlist_repo):
        """Test creating playlist with invalid data fails."""
        playlist = Playlist("", "user-id")
        with pytest.raises(ValueError):
            playlist_repo.create(playlist)
    
    def test_read_playlist_success(self, user_repo, playlist_repo):
        """Test reading an existing playlist."""
        user = User("owner", "owner@example.com")
        user_id = user_repo.create(user)
        
        playlist = Playlist("Workout Mix", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        result = playlist_repo.read(playlist_id)
        assert result is not None
        assert result['name'] == "Workout Mix"
    
    def test_read_playlist_not_found(self, playlist_repo):
        """Test reading non-existent playlist returns None."""
        result = playlist_repo.read("nonexistent-id")
        assert result is None
    
    def test_read_by_owner(self, user_repo, playlist_repo):
        """Test reading playlists by owner."""
        user = User("ownertest", "ownertest@example.com")
        user_id = user_repo.create(user)
        
        pl1 = Playlist("Playlist 1", user_id)
        pl2 = Playlist("Playlist 2", user_id)
        
        playlist_repo.create(pl1)
        playlist_repo.create(pl2)
        
        owner_playlists = playlist_repo.read_by_owner(user_id)
        assert len(owner_playlists) == 2
    
    def test_add_track_to_playlist(self, user_repo, song_repo, playlist_repo):
        """Test adding a track to playlist."""
        user = User("trackowner", "track@example.com")
        user_id = user_repo.create(user)
        
        song = TrackFactory.create_song("Track 1", 200, "Artist", "Genre")
        song_id = song_repo.create(song)
        
        playlist = Playlist("Playlist with Track", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        ps_id = playlist_repo.add_track(playlist_id, song_id)
        assert ps_id is not None
    
    def test_remove_track_from_playlist(self, user_repo, song_repo, playlist_repo):
        """Test removing a track from playlist."""
        user = User("removeuser", "remove@example.com")
        user_id = user_repo.create(user)
        
        song = TrackFactory.create_song("Track to Remove", 200, "Artist", "Genre")
        song_id = song_repo.create(song)
        
        playlist = Playlist("Remove Test", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        playlist_repo.add_track(playlist_id, song_id)
        success = playlist_repo.remove_track(playlist_id, song_id)
        assert success is True
    
    def test_get_playlist_tracks(self, user_repo, song_repo, playlist_repo):
        """Test getting all tracks in playlist."""
        user = User("getuser", "get@example.com")
        user_id = user_repo.create(user)
        
        song1 = TrackFactory.create_song("Track 1", 200, "Artist", "Genre")
        song2 = TrackFactory.create_song("Track 2", 250, "Artist", "Genre")
        
        song_id1 = song_repo.create(song1)
        song_id2 = song_repo.create(song2)
        
        playlist = Playlist("Multiple Tracks", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        playlist_repo.add_track(playlist_id, song_id1)
        playlist_repo.add_track(playlist_id, song_id2)
        
        tracks = playlist_repo.get_tracks(playlist_id)
        assert len(tracks) == 2
    
    def test_get_playlist_total_duration(self, user_repo, song_repo, playlist_repo):
        """Test calculating playlist total duration."""
        user = User("durationuser", "duration@example.com")
        user_id = user_repo.create(user)
        
        song1 = TrackFactory.create_song("Song 1", 200, "Artist", "Genre")
        song2 = TrackFactory.create_song("Song 2", 300, "Artist", "Genre")
        
        song_id1 = song_repo.create(song1)
        song_id2 = song_repo.create(song2)
        
        playlist = Playlist("Duration Test", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        playlist_repo.add_track(playlist_id, song_id1)
        playlist_repo.add_track(playlist_id, song_id2)
        
        total_duration = playlist_repo.get_total_duration(playlist_id)
        assert total_duration == 500


class TestIntegration:
    """Integration tests across repositories."""
    
    def test_complete_workflow(self, user_repo, song_repo, playlist_repo):
        """Test complete workflow: create user, songs, playlist, add tracks."""
        # Create user
        user = User("integrationuser", "integration@example.com")
        user_id = user_repo.create(user)
        assert user_repo.exists(user_id)
        
        # Create songs
        song1 = TrackFactory.create_song("Song A", 180, "Artist A", "Pop")
        song2 = TrackFactory.create_song("Song B", 240, "Artist B", "Rock")
        song_id1 = song_repo.create(song1)
        song_id2 = song_repo.create(song2)
        
        # Create playlist
        playlist = Playlist("Integration Playlist", user_id)
        playlist_id = playlist_repo.create(playlist)
        
        # Add tracks
        playlist_repo.add_track(playlist_id, song_id1)
        playlist_repo.add_track(playlist_id, song_id2)
        
        # Verify
        tracks = playlist_repo.get_tracks(playlist_id)
        assert len(tracks) == 2
        
        total_duration = playlist_repo.get_total_duration(playlist_id)
        assert total_duration == 420
