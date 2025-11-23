"""Playlist repository for data access layer.

Implements CRUD operations for Playlist entities imported from Student A's models.
Demonstrates Repository pattern, polymorphism, and handling of relationships.
"""

from typing import Optional, List
import logging
from uuid import uuid4
from src.database.connection import DatabaseConnection
from src.models.playlist import Playlist
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class PlaylistRepository(BaseRepository):
    """Repository for Playlist entity persistence and retrieval.
    
    Implements CRUD operations for Playlist objects by translating between
    domain models (from Student A's Playlist class) and database records.
    
    Note: Student A's Playlist class stores tracks in memory as a list.
    This repository persists playlist metadata. Track associations are managed
    through the playlist_songs junction table.
    
    Inheritance demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Liskov Substitution: Can substitute BaseRepository where needed
    - Single Responsibility: Focuses only on Playlist persistence
    
    Database Table Schema:
        playlists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Initialize PlaylistRepository with database connection.
        
        Args:
            db_connection (Optional[DatabaseConnection]): Database connection instance.
                If None, uses singleton instance.
        """
        super().__init__()
        self.db = db_connection or DatabaseConnection()
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def create(self, playlist: Playlist) -> str:
        """Create (persist) a new Playlist in the database.
        
        Converts Playlist domain model to database record and inserts it.
        Note: Playlist class in Student A doesn't use UUID, so we generate one.
        
        Args:
            playlist (Playlist): Playlist instance to persist (from Student A's models)
            
        Returns:
            str: ID of the created playlist
            
        Raises:
            ValueError: If playlist is invalid or not a Playlist instance
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> playlist = Playlist(name="My Favorite Songs", owner_id=user_id)
            >>> repo = PlaylistRepository()
            >>> playlist_id = repo.create(playlist)
        """
        try:
            if not isinstance(playlist, Playlist):
                raise ValueError("Entity must be a Playlist instance")
            
            # Generate UUID for playlist if not present
            playlist_id = str(uuid4()) if not hasattr(playlist, 'id') else playlist.id
            
            query = """
            INSERT INTO playlists (id, name, owner_id)
            VALUES (?, ?, ?)
            """
            
            params = (
                playlist_id,
                playlist.name,
                playlist.owner_id
            )
            
            self.db.execute_update(query, params)
            self._log_operation("CREATE", playlist_id)
            logger.debug(f"Playlist created with ID: {playlist_id}, Name: {playlist.name}")
            return playlist_id
            
        except ValueError as e:
            logger.error(f"Invalid playlist entity: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create playlist: {e}")
            raise
    
    def read_by_id(self, playlist_id: str) -> Optional[Playlist]:
        """Read (retrieve) a Playlist by ID from the database.
        
        Queries database and converts record to Playlist domain model instance.
        Note: Only retrieves playlist metadata, not associated tracks.
        
        Args:
            playlist_id (str): Unique identifier (UUID) of playlist
            
        Returns:
            Optional[Playlist]: Playlist instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = PlaylistRepository()
            >>> playlist = repo.read_by_id("550e8400-e29b-41d4-a716-446655440000")
            >>> if playlist:
            ...     print(f"Playlist: {playlist.name}")
        """
        try:
            query = "SELECT id, name, owner_id FROM playlists WHERE id = ?"
            results = self.db.execute_query(query, (playlist_id,))
            
            if not results:
                logger.debug(f"No playlist found with ID: {playlist_id}")
                return None
            
            row = results[0]
            # Create Playlist instance from database record
            playlist = Playlist(
                name=row[1],
                owner_id=row[2]
            )
            # Store ID for reference
            playlist.id = row[0]
            
            self._log_operation("READ", playlist_id)
            return playlist
            
        except Exception as e:
            logger.error(f"Failed to read playlist by ID {playlist_id}: {e}")
            raise
    
    def read_all(self) -> List[Playlist]:
        """Read (retrieve) all Playlists from the database.
        
        Returns:
            List[Playlist]: List of Playlist instances (empty if none exist)
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = PlaylistRepository()
            >>> all_playlists = repo.read_all()
            >>> print(f"Found {len(all_playlists)} playlists")
        """
        try:
            query = "SELECT id, name, owner_id FROM playlists ORDER BY created_at DESC"
            results = self.db.execute_query(query)
            
            playlists = []
            for row in results:
                playlist = Playlist(
                    name=row[1],
                    owner_id=row[2]
                )
                playlist.id = row[0]
                playlists.append(playlist)
            
            logger.info(f"Retrieved {len(playlists)} playlists from database")
            return playlists
            
        except Exception as e:
            logger.error(f"Failed to read all playlists: {e}")
            raise
    
    def exists(self, playlist_id: str) -> bool:
        """Check if a Playlist with the given ID exists.
        
        Args:
            playlist_id (str): Playlist ID to check
            
        Returns:
            bool: True if playlist exists, False otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT COUNT(*) FROM playlists WHERE id = ?"
            result = self.db.execute_query(query, (playlist_id,))
            exists = result[0][0] > 0
            
            if exists:
                logger.debug(f"Playlist with ID {playlist_id} exists")
            
            return exists
            
        except Exception as e:
            logger.error(f"Failed to check if playlist exists: {e}")
            raise
    
    def read_by_owner_id(self, owner_id: str) -> List[Playlist]:
        """Read all Playlists owned by a specific user.
        
        Args:
            owner_id (str): User ID (owner)
            
        Returns:
            List[Playlist]: List of playlists owned by the user
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT id, name, owner_id FROM playlists WHERE owner_id = ? ORDER BY created_at DESC"
            results = self.db.execute_query(query, (owner_id,))
            
            playlists = []
            for row in results:
                playlist = Playlist(
                    name=row[1],
                    owner_id=row[2]
                )
                playlist.id = row[0]
                playlists.append(playlist)
            
            logger.debug(f"Retrieved {len(playlists)} playlists for owner: {owner_id}")
            return playlists
            
        except Exception as e:
            logger.error(f"Failed to read playlists by owner {owner_id}: {e}")
            raise
    
    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Add a song to a playlist (create junction table entry).
        
        Args:
            playlist_id (str): ID of playlist
            song_id (str): ID of song to add
            
        Returns:
            bool: True if successful, False if song already in playlist
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = """
            INSERT INTO playlist_songs (playlist_id, song_id)
            VALUES (?, ?)
            """
            
            params = (playlist_id, song_id)
            self.db.execute_update(query, params)
            
            logger.info(f"Song {song_id} added to playlist {playlist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add song {song_id} to playlist {playlist_id}: {e}")
            raise
    
    def get_playlist_songs(self, playlist_id: str) -> List[str]:
        """Get all song IDs in a playlist.
        
        Args:
            playlist_id (str): ID of playlist
            
        Returns:
            List[str]: List of song IDs in the playlist
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT song_id FROM playlist_songs WHERE playlist_id = ? ORDER BY added_at"
            results = self.db.execute_query(query, (playlist_id,))
            
            song_ids = [row[0] for row in results]
            logger.debug(f"Retrieved {len(song_ids)} songs from playlist {playlist_id}")
            return song_ids
            
        except Exception as e:
            logger.error(f"Failed to get songs for playlist {playlist_id}: {e}")
            raise
