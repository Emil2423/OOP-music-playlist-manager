"""Song service module for business logic layer.

This service encapsulates all business logic related to Song management,
providing a clean API that orchestrates between the presentation layer (CLI)
and the data access layer (repositories).

Design Principles Applied:
- Single Responsibility: Only handles Song business logic
- Dependency Inversion: Depends on repository abstractions
- GRASP Controller: Coordinates use case operations
"""

import logging
from models.song import Song
from repositories.song_repository import SongRepository
from services.track_factory import TrackFactory
from exceptions.custom_exceptions import (
    EntityNotFoundError,
    ValidationError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class SongService:
    """Service class for Song business operations.
    
    Provides high-level operations for song management including
    validation, business rule enforcement, and coordination with repositories.
    
    Attributes:
        song_repo (SongRepository): Repository for song persistence
    
    Example:
        >>> service = SongService()
        >>> song = service.create_song("Imagine", "John Lennon", "Rock", 183)
        >>> all_songs = service.get_all_songs()
    """
    
    # Song constraints
    MIN_TITLE_LENGTH = 1
    MAX_TITLE_LENGTH = 200
    MIN_DURATION = 1  # Minimum 1 second
    MAX_DURATION = 36000  # Maximum 10 hours
    
    def __init__(self, song_repo=None):
        """Initialize SongService with repository.
        
        Args:
            song_repo (SongRepository, optional): Song repository instance.
                If None, creates a new instance.
        """
        self.song_repo = song_repo or SongRepository()
        logger.debug("SongService initialized")
    
    def _validate_title(self, title):
        """Validate song title.
        
        Args:
            title (str): Title to validate
            
        Raises:
            ValidationError: If title is invalid
        """
        if not title or not title.strip():
            raise ValidationError("title", title, "cannot be empty")
        
        if len(title.strip()) > self.MAX_TITLE_LENGTH:
            raise ValidationError(
                "title", title,
                f"must be at most {self.MAX_TITLE_LENGTH} characters"
            )
    
    def _validate_artist(self, artist):
        """Validate artist name.
        
        Args:
            artist (str): Artist name to validate
            
        Raises:
            ValidationError: If artist is invalid
        """
        if not artist or not artist.strip():
            raise ValidationError("artist", artist, "cannot be empty")
    
    def _validate_genre(self, genre):
        """Validate genre.
        
        Args:
            genre (str): Genre to validate
            
        Raises:
            ValidationError: If genre is invalid
        """
        if not genre or not genre.strip():
            raise ValidationError("genre", genre, "cannot be empty")
    
    def _validate_duration(self, duration):
        """Validate song duration.
        
        Args:
            duration (int): Duration in seconds
            
        Raises:
            ValidationError: If duration is invalid
        """
        if not isinstance(duration, int):
            raise ValidationError("duration", duration, "must be an integer")
        
        if duration < self.MIN_DURATION:
            raise ValidationError(
                "duration", duration,
                f"must be at least {self.MIN_DURATION} second"
            )
        
        if duration > self.MAX_DURATION:
            raise ValidationError(
                "duration", duration,
                f"must be at most {self.MAX_DURATION} seconds (10 hours)"
            )
    
    def create_song(self, title, artist, genre, duration):
        """Create a new song with validation.
        
        Uses TrackFactory pattern to create the song instance.
        
        Args:
            title (str): Song title
            artist (str): Artist name
            genre (str): Music genre
            duration (int): Duration in seconds
            
        Returns:
            Song: Created song instance with ID
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If persistence fails
            
        Example:
            >>> song = service.create_song("Imagine", "John Lennon", "Rock", 183)
            >>> print(f"Created song with ID: {song.id}")
        """
        logger.info(f"Creating song: title={title}, artist={artist}")
        
        # Validate inputs
        self._validate_title(title)
        self._validate_artist(artist)
        self._validate_genre(genre)
        self._validate_duration(duration)
        
        # Auto-capitalize names
        title = title.strip().title()
        artist = artist.strip().title()
        genre = genre.strip().title()
        
        # Create song using Factory pattern
        try:
            song = TrackFactory.create_song(title, duration, artist, genre)
            self.song_repo.create(song)
            logger.info(f"Song created successfully: ID={song.id}")
            return song
        except ValueError as e:
            raise ValidationError("song", str(e), str(e))
        except Exception as e:
            logger.error(f"Failed to create song: {e}")
            raise DatabaseError("CREATE", e, "songs")
    
    def get_song_by_id(self, song_id):
        """Get a song by ID.
        
        Args:
            song_id (str): Song's unique identifier
            
        Returns:
            Song: Song instance
            
        Raises:
            EntityNotFoundError: If song not found
        """
        logger.debug(f"Getting song by ID: {song_id}")
        
        song = self.song_repo.read_by_id(song_id)
        if not song:
            raise EntityNotFoundError("Song", song_id)
        
        return song
    
    def get_all_songs(self):
        """Get all songs.
        
        Returns:
            list: List of all Song instances
        """
        logger.debug("Getting all songs")
        return self.song_repo.read_all()
    
    def get_songs_by_artist(self, artist):
        """Get all songs by a specific artist.
        
        Args:
            artist (str): Artist name
            
        Returns:
            list: List of Song instances by the artist
            
        Raises:
            ValidationError: If artist is empty
        """
        if not artist or not artist.strip():
            raise ValidationError("artist", artist, "cannot be empty")
        
        logger.debug(f"Getting songs by artist: {artist}")
        return self.song_repo.read_by_artist(artist.strip())
    
    def get_songs_by_genre(self, genre):
        """Get all songs of a specific genre.
        
        Args:
            genre (str): Music genre
            
        Returns:
            list: List of Song instances in the genre
            
        Raises:
            ValidationError: If genre is empty
        """
        if not genre or not genre.strip():
            raise ValidationError("genre", genre, "cannot be empty")
        
        logger.debug(f"Getting songs by genre: {genre}")
        return self.song_repo.read_by_genre(genre.strip())
    
    def update_song(self, song_id, new_title=None, new_artist=None, 
                    new_genre=None, new_duration=None):
        """Update song information.
        
        Note: Since Song uses immutable properties, we create a new Song
        with updated values and the same ID.
        
        Args:
            song_id (str): ID of song to update
            new_title (str, optional): New title
            new_artist (str, optional): New artist
            new_genre (str, optional): New genre
            new_duration (int, optional): New duration
            
        Returns:
            Song: Updated song instance
            
        Raises:
            EntityNotFoundError: If song not found
            ValidationError: If new values are invalid
            DatabaseError: If update fails
        """
        logger.info(f"Updating song: ID={song_id}")
        
        # Get existing song
        existing = self.get_song_by_id(song_id)
        
        # Use existing values if not provided, auto-capitalize names
        title = new_title.strip().title() if new_title else existing.title
        artist = new_artist.strip().title() if new_artist else existing.artist
        genre = new_genre.strip().title() if new_genre else existing.genre
        duration = new_duration if new_duration is not None else existing.duration
        
        # Validate new values
        self._validate_title(title)
        self._validate_artist(artist)
        self._validate_genre(genre)
        self._validate_duration(duration)
        
        # Create new song with same ID (workaround for immutable properties)
        try:
            updated_song = Song(title=title, artist=artist, genre=genre, duration=duration)
            # Preserve the original ID
            updated_song._AudioTrack__id = song_id
            
            success = self.song_repo.update(updated_song)
            if not success:
                raise DatabaseError("UPDATE", Exception("Update returned False"), "songs")
            
            logger.info(f"Song updated successfully: ID={song_id}")
            return updated_song
        except Exception as e:
            logger.error(f"Failed to update song: {e}")
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError("UPDATE", e, "songs")
    
    def delete_song(self, song_id):
        """Delete a song by ID.
        
        Also removes the song from all playlists.
        
        Args:
            song_id (str): ID of song to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            EntityNotFoundError: If song not found
            DatabaseError: If deletion fails
        """
        logger.info(f"Deleting song: ID={song_id}")
        
        # Verify song exists
        self.get_song_by_id(song_id)
        
        try:
            success = self.song_repo.delete(song_id)
            if not success:
                raise DatabaseError("DELETE", Exception("Delete returned False"), "songs")
            logger.info(f"Song deleted successfully: ID={song_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete song: {e}")
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError("DELETE", e, "songs")
    
    def search_songs(self, query):
        """Search songs by title or artist.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching Song instances
        """
        if not query or not query.strip():
            return []
        
        query = query.strip().lower()
        all_songs = self.get_all_songs()
        
        matches = [
            song for song in all_songs
            if query in song.title.lower() or query in song.artist.lower()
        ]
        
        logger.debug(f"Search for '{query}' returned {len(matches)} results")
        return matches
