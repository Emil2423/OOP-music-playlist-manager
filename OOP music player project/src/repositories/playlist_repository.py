"""
Playlist Repository
Implements CRUD operations for Playlist entities with validation and logging.
"""

from typing import List, Optional, Dict, Any
import logging
import uuid
from src.repositories.base_repository import BaseRepository
from src.models.playlist import Playlist
from src.models.audio_track import AudioTrack

logger = logging.getLogger(__name__)


class PlaylistRepository(BaseRepository):
    """
    Repository for Playlist entity persistence.
    
    Demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Single Responsibility: Handles only Playlist data access
    - High Cohesion: All methods focus on Playlist operations
    """
    
    def __init__(self, db=None):
        """Initialize PlaylistRepository."""
        super().__init__(db)
        self._table_name = "playlists"
    
    def create(self, entity: Playlist) -> str:
        """
        Create new playlist in database.
        
        Args:
            entity: Playlist object
            
        Returns:
            str: Playlist ID
            
        Raises:
            ValueError: If playlist is invalid
            RuntimeError: If database operation fails
        """
        if not isinstance(entity, Playlist):
            raise ValueError("Entity must be a Playlist instance")
        
        if not entity.name or not entity.owner_id:
            raise ValueError("Invalid playlist: name and owner_id are required")
        
        try:
            # Generate new ID for playlist
            playlist_id = str(uuid.uuid4())
            query = """
                INSERT INTO playlists (id, name, owner_id)
                VALUES (?, ?, ?)
            """
            self._db.execute_update(query, (playlist_id, entity.name, entity.owner_id))
            logger.info(f"Playlist created: {playlist_id} - {entity.name} (owner: {entity.owner_id})")
            return playlist_id
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise RuntimeError(f"Failed to create playlist: {e}")
    
    def read(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Read playlist by ID.
        
        Args:
            entity_id: Playlist ID
            
        Returns:
            dict: Playlist data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id:
            raise ValueError("entity_id is required")
        
        try:
            query = "SELECT * FROM playlists WHERE id = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (entity_id,))
                row = cursor.fetchone()
                result = self._row_to_dict(row)
                
                if result:
                    logger.debug(f"Playlist read: {entity_id}")
                else:
                    logger.warning(f"Playlist not found: {entity_id}")
                
                return result
        except Exception as e:
            logger.error(f"Error reading playlist: {e}")
            raise RuntimeError(f"Failed to read playlist: {e}")
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all playlists from database.
        
        Returns:
            list: List of all playlists
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            query = "SELECT * FROM playlists ORDER BY created_at DESC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} playlists from database")
                return results
        except Exception as e:
            logger.error(f"Error reading all playlists: {e}")
            raise RuntimeError(f"Failed to read all playlists: {e}")
    
    def read_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """
        Read all playlists owned by a specific user.
        
        Args:
            owner_id: Owner user ID
            
        Returns:
            list: List of playlists owned by user
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not owner_id:
            raise ValueError("owner_id is required")
        
        try:
            query = "SELECT * FROM playlists WHERE owner_id = ? ORDER BY created_at DESC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (owner_id,))
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} playlists by owner {owner_id}")
                return results
        except Exception as e:
            logger.error(f"Error reading playlists by owner: {e}")
            raise RuntimeError(f"Failed to read playlists by owner: {e}")
    
    def add_track(self, playlist_id: str, song_id: str) -> str:
        """
        Add song to playlist.
        
        Args:
            playlist_id: Playlist ID
            song_id: Song ID
            
        Returns:
            str: ID of playlist_song junction record
            
        Raises:
            ValueError: If IDs are invalid
            RuntimeError: If database operation fails
        """
        if not playlist_id or not song_id:
            raise ValueError("playlist_id and song_id are required")
        
        try:
            # Get next position
            query = "SELECT MAX(position) FROM playlist_songs WHERE playlist_id = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (playlist_id,))
                result = cursor.fetchone()
                max_position = result[0] if result[0] is not None else 0
                next_position = max_position + 1
            
            # Insert track
            ps_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO playlist_songs (id, playlist_id, song_id, position)
                VALUES (?, ?, ?, ?)
            """
            self._db.execute_update(insert_query, (ps_id, playlist_id, song_id, next_position))
            logger.info(f"Track added to playlist {playlist_id}: {song_id} at position {next_position}")
            return ps_id
        except Exception as e:
            logger.error(f"Error adding track to playlist: {e}")
            raise RuntimeError(f"Failed to add track to playlist: {e}")
    
    def remove_track(self, playlist_id: str, song_id: str) -> bool:
        """
        Remove song from playlist.
        
        Args:
            playlist_id: Playlist ID
            song_id: Song ID
            
        Returns:
            bool: True if removal successful, False if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not playlist_id or not song_id:
            raise ValueError("playlist_id and song_id are required")
        
        try:
            query = """
                DELETE FROM playlist_songs
                WHERE playlist_id = ? AND song_id = ?
            """
            rows_affected = self._db.execute_update(query, (playlist_id, song_id))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Track removed from playlist {playlist_id}: {song_id}")
            else:
                logger.warning(f"Track not found in playlist {playlist_id}: {song_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error removing track from playlist: {e}")
            raise RuntimeError(f"Failed to remove track from playlist: {e}")
    
    def get_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Get all songs in a playlist.
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            list: List of songs with playlist metadata
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not playlist_id:
            raise ValueError("playlist_id is required")
        
        try:
            query = """
                SELECT s.*, ps.position, ps.added_at
                FROM playlist_songs ps
                JOIN songs s ON ps.song_id = s.id
                WHERE ps.playlist_id = ?
                ORDER BY ps.position ASC
            """
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (playlist_id,))
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} tracks from playlist {playlist_id}")
                return results
        except Exception as e:
            logger.error(f"Error reading playlist tracks: {e}")
            raise RuntimeError(f"Failed to read playlist tracks: {e}")
    
    def get_total_duration(self, playlist_id: str) -> int:
        """
        Calculate total duration of all songs in playlist.
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            int: Total duration in seconds
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not playlist_id:
            raise ValueError("playlist_id is required")
        
        try:
            query = """
                SELECT COALESCE(SUM(s.duration), 0) as total
                FROM playlist_songs ps
                JOIN songs s ON ps.song_id = s.id
                WHERE ps.playlist_id = ?
            """
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (playlist_id,))
                result = cursor.fetchone()
                total_duration = result[0] if result else 0
                logger.debug(f"Total duration for playlist {playlist_id}: {total_duration}s")
                return total_duration
        except Exception as e:
            logger.error(f"Error calculating playlist duration: {e}")
            raise RuntimeError(f"Failed to calculate playlist duration: {e}")
