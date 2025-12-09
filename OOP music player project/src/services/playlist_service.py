"""Playlist service module for business logic layer.

This service encapsulates all business logic related to Playlist management,
providing a clean API that orchestrates between the presentation layer (CLI)
and the data access layer (repositories).

Design Principles Applied:
- Single Responsibility: Only handles Playlist business logic
- Dependency Inversion: Depends on repository abstractions
- GRASP Controller: Coordinates use case operations
"""

import logging
from models.playlist import Playlist
from repositories.playlist_repository import PlaylistRepository
from repositories.song_repository import SongRepository
from repositories.user_repository import UserRepository
from exceptions.custom_exceptions import (
    EntityNotFoundError,
    ValidationError,
    DatabaseError,
    AuthorizationError
)

logger = logging.getLogger(__name__)


class PlaylistService:
    """Service class for Playlist business operations.
    
    Provides high-level operations for playlist management including
    validation, business rule enforcement, and coordination with repositories.
    
    Attributes:
        playlist_repo (PlaylistRepository): Repository for playlist persistence
        song_repo (SongRepository): Repository for song access
        user_repo (UserRepository): Repository for user access
    
    Example:
        >>> service = PlaylistService()
        >>> playlist = service.create_playlist("My Favorites", user_id)
        >>> service.add_song_to_playlist(playlist.id, song_id)
    """
    
    # Playlist constraints
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 100
    
    def __init__(self, playlist_repo=None, song_repo=None, user_repo=None):
        """Initialize PlaylistService with repositories.
        
        Args:
            playlist_repo (PlaylistRepository, optional): Playlist repository.
            song_repo (SongRepository, optional): Song repository.
            user_repo (UserRepository, optional): User repository.
        """
        self.playlist_repo = playlist_repo or PlaylistRepository()
        self.song_repo = song_repo or SongRepository()
        self.user_repo = user_repo or UserRepository()
        logger.debug("PlaylistService initialized")
    
    def _validate_name(self, name):
        """Validate playlist name.
        
        Args:
            name (str): Name to validate
            
        Raises:
            ValidationError: If name is invalid
        """
        if not name or not name.strip():
            raise ValidationError("name", name, "cannot be empty")
        
        if len(name.strip()) > self.MAX_NAME_LENGTH:
            raise ValidationError(
                "name", name,
                f"must be at most {self.MAX_NAME_LENGTH} characters"
            )
    
    def _validate_owner_exists(self, owner_id):
        """Validate that the owner exists.
        
        Args:
            owner_id (str): User ID to validate
            
        Raises:
            EntityNotFoundError: If user not found
        """
        if not self.user_repo.exists(owner_id):
            raise EntityNotFoundError("User", owner_id)
    
    def _validate_song_exists(self, song_id):
        """Validate that a song exists.
        
        Args:
            song_id (str): Song ID to validate
            
        Raises:
            EntityNotFoundError: If song not found
        """
        if not self.song_repo.exists(song_id):
            raise EntityNotFoundError("Song", song_id)
    
    def create_playlist(self, name, owner_id):
        """Create a new playlist with validation.
        
        Args:
            name (str): Playlist name
            owner_id (str): ID of the user who owns this playlist
            
        Returns:
            Playlist: Created playlist instance with ID
            
        Raises:
            ValidationError: If input validation fails
            EntityNotFoundError: If owner user not found
            DatabaseError: If persistence fails
            
        Example:
            >>> playlist = service.create_playlist("My Favorites", user_id)
            >>> print(f"Created playlist: {playlist.name}")
        """
        logger.info(f"Creating playlist: name={name}, owner_id={owner_id}")
        
        # Validate inputs
        self._validate_name(name)
        self._validate_owner_exists(owner_id)
        
        # Auto-capitalize playlist name
        name = name.strip().title()
        
        # Create and persist playlist
        try:
            playlist = Playlist(name=name, owner_id=owner_id)
            playlist_id = self.playlist_repo.create(playlist)
            # Override the auto-generated ID with the database ID
            playlist._Playlist__id = playlist_id
            logger.info(f"Playlist created successfully: ID={playlist_id}")
            return playlist
        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            raise DatabaseError("CREATE", e, "playlists")
    
    def get_playlist_by_id(self, playlist_id):
        """Get a playlist by ID.
        
        Args:
            playlist_id (str): Playlist's unique identifier
            
        Returns:
            Playlist: Playlist instance
            
        Raises:
            EntityNotFoundError: If playlist not found
        """
        logger.debug(f"Getting playlist by ID: {playlist_id}")
        
        playlist = self.playlist_repo.read_by_id(playlist_id)
        if not playlist:
            raise EntityNotFoundError("Playlist", playlist_id)
        
        return playlist
    
    def get_all_playlists(self):
        """Get all playlists.
        
        Returns:
            list: List of all Playlist instances
        """
        logger.debug("Getting all playlists")
        return self.playlist_repo.read_all()
    
    def get_playlists_by_owner(self, owner_id):
        """Get all playlists owned by a user.
        
        Args:
            owner_id (str): User ID
            
        Returns:
            list: List of Playlist instances
            
        Raises:
            EntityNotFoundError: If user not found
        """
        self._validate_owner_exists(owner_id)
        logger.debug(f"Getting playlists by owner: {owner_id}")
        return self.playlist_repo.read_by_owner_id(owner_id)
    
    def update_playlist(self, playlist_id, new_name=None, requesting_user_id=None):
        """Update playlist information.
        
        Args:
            playlist_id (str): ID of playlist to update
            new_name (str, optional): New playlist name
            requesting_user_id (str, optional): ID of user making the request
                (for authorization check)
            
        Returns:
            Playlist: Updated playlist instance
            
        Raises:
            EntityNotFoundError: If playlist not found
            ValidationError: If new values are invalid
            AuthorizationError: If user is not the owner
            DatabaseError: If update fails
        """
        logger.info(f"Updating playlist: ID={playlist_id}")
        
        # Get existing playlist
        playlist = self.get_playlist_by_id(playlist_id)
        
        # Authorization check (if requesting user provided)
        if requesting_user_id and playlist.owner_id != requesting_user_id:
            raise AuthorizationError(
                requesting_user_id, "update", "playlist",
                "Only the playlist owner can update it"
            )
        
        # Update name if provided, auto-capitalize
        if new_name:
            self._validate_name(new_name)
            playlist.name = new_name.strip().title()
        
        # Persist changes
        try:
            success = self.playlist_repo.update(playlist)
            if not success:
                raise DatabaseError("UPDATE", Exception("Update returned False"), "playlists")
            logger.info(f"Playlist updated successfully: ID={playlist_id}")
            return playlist
        except Exception as e:
            logger.error(f"Failed to update playlist: {e}")
            if isinstance(e, (DatabaseError, AuthorizationError)):
                raise
            raise DatabaseError("UPDATE", e, "playlists")
    
    def delete_playlist(self, playlist_id, requesting_user_id=None):
        """Delete a playlist by ID.
        
        Also removes all song associations.
        
        Args:
            playlist_id (str): ID of playlist to delete
            requesting_user_id (str, optional): ID of user making the request
                (for authorization check)
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            EntityNotFoundError: If playlist not found
            AuthorizationError: If user is not the owner
            DatabaseError: If deletion fails
        """
        logger.info(f"Deleting playlist: ID={playlist_id}")
        
        # Get existing playlist (also verifies existence)
        playlist = self.get_playlist_by_id(playlist_id)
        
        # Authorization check (if requesting user provided)
        if requesting_user_id and playlist.owner_id != requesting_user_id:
            raise AuthorizationError(
                requesting_user_id, "delete", "playlist",
                "Only the playlist owner can delete it"
            )
        
        try:
            success = self.playlist_repo.delete(playlist_id)
            if not success:
                raise DatabaseError("DELETE", Exception("Delete returned False"), "playlists")
            logger.info(f"Playlist deleted successfully: ID={playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete playlist: {e}")
            if isinstance(e, (DatabaseError, AuthorizationError)):
                raise
            raise DatabaseError("DELETE", e, "playlists")
    
    def add_song_to_playlist(self, playlist_id, song_id, requesting_user_id=None):
        """Add a song to a playlist.
        
        Args:
            playlist_id (str): ID of the playlist
            song_id (str): ID of the song to add
            requesting_user_id (str, optional): ID of user making the request
            
        Returns:
            bool: True if successful
            
        Raises:
            EntityNotFoundError: If playlist or song not found
            AuthorizationError: If user is not the owner
            DatabaseError: If operation fails
        """
        logger.info(f"Adding song {song_id} to playlist {playlist_id}")
        
        # Verify playlist exists
        playlist = self.get_playlist_by_id(playlist_id)
        
        # Authorization check
        if requesting_user_id and playlist.owner_id != requesting_user_id:
            raise AuthorizationError(
                requesting_user_id, "modify", "playlist",
                "Only the playlist owner can add songs"
            )
        
        # Verify song exists
        self._validate_song_exists(song_id)
        
        try:
            self.playlist_repo.add_song_to_playlist(playlist_id, song_id)
            logger.info(f"Song added to playlist successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add song to playlist: {e}")
            raise DatabaseError("CREATE", e, "playlist_songs")
    
    def remove_song_from_playlist(self, playlist_id, song_id, requesting_user_id=None):
        """Remove a song from a playlist.
        
        Args:
            playlist_id (str): ID of the playlist
            song_id (str): ID of the song to remove
            requesting_user_id (str, optional): ID of user making the request
            
        Returns:
            bool: True if successful
            
        Raises:
            EntityNotFoundError: If playlist not found
            AuthorizationError: If user is not the owner
            DatabaseError: If operation fails
        """
        logger.info(f"Removing song {song_id} from playlist {playlist_id}")
        
        # Verify playlist exists
        playlist = self.get_playlist_by_id(playlist_id)
        
        # Authorization check
        if requesting_user_id and playlist.owner_id != requesting_user_id:
            raise AuthorizationError(
                requesting_user_id, "modify", "playlist",
                "Only the playlist owner can remove songs"
            )
        
        try:
            success = self.playlist_repo.remove_song_from_playlist(playlist_id, song_id)
            if not success:
                logger.warning(f"Song {song_id} was not in playlist {playlist_id}")
            else:
                logger.info(f"Song removed from playlist successfully")
            return success
        except Exception as e:
            logger.error(f"Failed to remove song from playlist: {e}")
            raise DatabaseError("DELETE", e, "playlist_songs")
    
    def get_playlist_songs(self, playlist_id):
        """Get all songs in a playlist.
        
        Args:
            playlist_id (str): ID of the playlist
            
        Returns:
            list: List of Song instances in the playlist
            
        Raises:
            EntityNotFoundError: If playlist not found
        """
        logger.debug(f"Getting songs for playlist: {playlist_id}")
        
        # Verify playlist exists
        self.get_playlist_by_id(playlist_id)
        
        # Get song IDs and fetch full song objects
        song_ids = self.playlist_repo.get_playlist_songs(playlist_id)
        songs = []
        
        for song_id in song_ids:
            song = self.song_repo.read_by_id(song_id)
            if song:
                songs.append(song)
        
        return songs
    
    def get_playlist_with_songs(self, playlist_id):
        """Get a playlist with all its songs loaded.
        
        Args:
            playlist_id (str): ID of the playlist
            
        Returns:
            Playlist: Playlist instance with tracks populated
            
        Raises:
            EntityNotFoundError: If playlist not found
        """
        playlist = self.get_playlist_by_id(playlist_id)
        songs = self.get_playlist_songs(playlist_id)
        
        # Add songs to the playlist's track list
        for song in songs:
            playlist.add_track(song)
        
        return playlist
