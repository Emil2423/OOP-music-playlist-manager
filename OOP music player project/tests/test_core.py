import pytest
from models.song import Song
from models.playlist import Playlist
from models.user import User
from services.track_factory import TrackFactory

@pytest.fixture
def sample_user():
    return User("emil", "emil@gmail.com")

@pytest.fixture
def sample_song():
    return TrackFactory.create_song("Bohemian Rhapsody", 354, "Queen", "Rock")

def test_song_attributes(sample_song):
    assert sample_song.title == "Bohemian Rhapsody"
    assert sample_song.artist == "Queen"
    assert sample_song.duration == 354
    assert len(sample_song.id) > 0 

def test_polymorphism_get_details(sample_song):
    details = sample_song.get_details()
    assert "Song:" in details
    assert "Queen" in details
    assert "[Rock]" in details

def test_factory_validation():
    with pytest.raises(ValueError):
        TrackFactory.create_song("Bad Song", -50, "Artist", "Pop")

def test_playlist_add_remove_tracks(sample_user, sample_song):
    playlist = Playlist("My Favorites", sample_user.id)
    
    playlist.add_track(sample_song)
    assert len(playlist.get_tracks()) == 1
    assert playlist.total_duration == 354
    
    playlist.remove_track(sample_song.id)
    assert len(playlist.get_tracks()) == 0
    assert playlist.total_duration == 0

def test_user_create_playlist_security(sample_user):
    valid_playlist = Playlist("Chill Vibes", sample_user.id)
    sample_user.create_playlist(valid_playlist)
    assert len(sample_user.playlists) == 1

    other_user_id = "fake-uuid-999"
    invalid_playlist = Playlist("Hacked List", other_user_id)
    
    with pytest.raises(ValueError) as excinfo:
        sample_user.create_playlist(invalid_playlist)
    
    assert "owner_id does not match" in str(excinfo.value)