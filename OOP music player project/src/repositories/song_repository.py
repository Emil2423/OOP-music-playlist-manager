"""
Song Repository
Implements CRUD operations for Song entities with validation and logging.
"""

from typing import List, Optional, Dict, Any
import logging
from src.repositories.base_repository import BaseRepository
from src.models.song import Song
from src.services.track_factory import TrackFactory

logger = logging.getLogger(__name__)


class SongRepository(BaseRepository):
    """
    Repository for Song entity persistence.
    
    Demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Single Responsibility: Handles only Song data access
    - High Cohesion: All methods focus on Song operations
    """
    
    def __init__(self, db=None):
        """Initialize SongRepository."""
        super().__init__(db)
        self._table_name = "songs"
    
    def create(self, entity: Song) -> str:
        """
        Create new song in database.
        
        Args:
            entity: Song object
            
        Returns:
            str: Song ID
            
        Raises:
            ValueError: If song is invalid
            RuntimeError: If database operation fails
        """
        if not isinstance(entity, Song):
            raise ValueError("Entity must be a Song instance")
        
        if not entity.title or entity.duration <= 0 or not entity.artist or not entity.genre:
            raise ValueError("Invalid song: all fields required and duration must be positive")
        
        try:
            query = """
                INSERT INTO songs (id, title, duration, artist, genre)
                VALUES (?, ?, ?, ?, ?)
            """
            song_id = entity.id
            self._db.execute_update(
                query,
                (song_id, entity.title, entity.duration, entity.artist, entity.genre)
            )
            logger.info(f"Song created: {song_id} - {entity.title} by {entity.artist}")
            return song_id
        except Exception as e:
            logger.error(f"Error creating song: {e}")
            raise RuntimeError(f"Failed to create song: {e}")
    
    def read(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Read song by ID.
        
        Args:
            entity_id: Song ID
            
        Returns:
            dict: Song data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id:
            raise ValueError("entity_id is required")
        
        try:
            query = "SELECT * FROM songs WHERE id = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (entity_id,))
                row = cursor.fetchone()
                result = self._row_to_dict(row)
                
                if result:
                    logger.debug(f"Song read: {entity_id}")
                else:
                    logger.warning(f"Song not found: {entity_id}")
                
                return result
        except Exception as e:
            logger.error(f"Error reading song: {e}")
            raise RuntimeError(f"Failed to read song: {e}")
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all songs from database.
        
        Returns:
            list: List of all songs
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            query = "SELECT * FROM songs ORDER BY created_at DESC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} songs from database")
                return results
        except Exception as e:
            logger.error(f"Error reading all songs: {e}")
            raise RuntimeError(f"Failed to read all songs: {e}")
    
    def read_by_artist(self, artist: str) -> List[Dict[str, Any]]:
        """
        Read all songs by a specific artist.
        
        Args:
            artist: Artist name
            
        Returns:
            list: List of songs by artist
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not artist:
            raise ValueError("artist is required")
        
        try:
            query = "SELECT * FROM songs WHERE artist = ? ORDER BY title ASC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (artist,))
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} songs by {artist}")
                return results
        except Exception as e:
            logger.error(f"Error reading songs by artist: {e}")
            raise RuntimeError(f"Failed to read songs by artist: {e}")
    
    def read_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """
        Read all songs in a specific genre.
        
        Args:
            genre: Genre name
            
        Returns:
            list: List of songs in genre
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not genre:
            raise ValueError("genre is required")
        
        try:
            query = "SELECT * FROM songs WHERE genre = ? ORDER BY title ASC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (genre,))
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} songs in genre {genre}")
                return results
        except Exception as e:
            logger.error(f"Error reading songs by genre: {e}")
            raise RuntimeError(f"Failed to read songs by genre: {e}")
