"""Song repository for data access layer.

Implements CRUD operations for Song entities imported from Student A's models.
Demonstrates Repository pattern and polymorphism through BaseRepository inheritance.
"""

import logging
from database.connection import DatabaseConnection
from models.song import Song
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SongRepository(BaseRepository):
    """Repository for Song entity persistence and retrieval.
    
    Implements CRUD operations for Song objects by translating between
    domain models (from Student A's Song class) and database records.
    
    Inheritance demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Liskov Substitution: Can substitute BaseRepository where needed
    - Single Responsibility: Focuses only on Song persistence
    
    Database Table Schema:
        songs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    def __init__(self, db_connection=None):
        """Initialize SongRepository with database connection.
        
        Args:
            db_connection (DatabaseConnection): Database connection instance.
                If None, uses singleton instance.
        """
        super().__init__()
        self.db = db_connection or DatabaseConnection()
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def create(self, song):
        """Create (persist) a new Song in the database.
        
        Converts Song domain model to database record and inserts it.
        Uses the song's UUID from Student A's AudioTrack base class.
        
        Args:
            song (Song): Song instance to persist (from Student A's models)
            
        Returns:
            str: ID of the created song
            
        Raises:
            ValueError: If song is invalid or not a Song instance
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> song = Song(title="Imagine", artist="John Lennon", 
            ...            genre="Rock", duration=183)
            >>> repo = SongRepository()
            >>> song_id = repo.create(song)
        """
        try:
            if not isinstance(song, Song):
                raise ValueError("Entity must be a Song instance")
            
            query = """
            INSERT INTO songs (id, title, artist, genre, duration)
            VALUES (?, ?, ?, ?, ?)
            """
            
            params = (
                song.id,
                song.title,
                song.artist,
                song.genre,
                song.duration
            )
            
            self.db.execute_update(query, params)
            self._log_operation("CREATE", song.id)
            logger.debug(f"Song created with ID: {song.id}, Title: {song.title}")
            return song.id
            
        except ValueError as e:
            logger.error(f"Invalid song entity: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create song: {e}")
            raise
    
    def read_by_id(self, song_id):
        """Read (retrieve) a Song by ID from the database.
        
        Queries database and converts record to Song domain model instance.
        
        Args:
            song_id (str): Unique identifier (UUID) of song
            
        Returns:
            Song: Song instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = SongRepository()
            >>> song = repo.read_by_id("550e8400-e29b-41d4-a716-446655440000")
            >>> if song:
            ...     print(f"Found: {song.title} by {song.artist}")
        """
        try:
            query = "SELECT id, title, artist, genre, duration FROM songs WHERE id = ?"
            results = self.db.execute_query(query, (song_id,))
            
            if not results:
                logger.debug(f"No song found with ID: {song_id}")
                return None
            
            row = results[0]
            # Create Song instance from database record
            song = Song(
                title=row[1],
                artist=row[2],
                genre=row[3],
                duration=row[4]
            )
            # Override the UUID to match database ID
            song._AudioTrack__id = row[0]
            
            self._log_operation("READ", song_id)
            return song
            
        except Exception as e:
            logger.error(f"Failed to read song by ID {song_id}: {e}")
            raise
    
    def read_all(self):
        """Read (retrieve) all Songs from the database.
        
        Returns:
            list: List of Song instances (empty if none exist)
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = SongRepository()
            >>> all_songs = repo.read_all()
            >>> print(f"Found {len(all_songs)} songs")
        """
        try:
            query = "SELECT id, title, artist, genre, duration FROM songs ORDER BY created_at DESC"
            results = self.db.execute_query(query)
            
            songs = []
            for row in results:
                song = Song(
                    title=row[1],
                    artist=row[2],
                    genre=row[3],
                    duration=row[4]
                )
                # Override the UUID to match database ID
                song._AudioTrack__id = row[0]
                songs.append(song)
            
            logger.info(f"Retrieved {len(songs)} songs from database")
            return songs
            
        except Exception as e:
            logger.error(f"Failed to read all songs: {e}")
            raise
    
    def exists(self, song_id):
        """Check if a Song with the given ID exists.
        
        Args:
            song_id (str): Song ID to check
            
        Returns:
            bool: True if song exists, False otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT COUNT(*) FROM songs WHERE id = ?"
            result = self.db.execute_query(query, (song_id,))
            exists = result[0][0] > 0
            
            if exists:
                logger.debug(f"Song with ID {song_id} exists")
            
            return exists
            
        except Exception as e:
            logger.error(f"Failed to check if song exists: {e}")
            raise
    
    def read_by_artist(self, artist):
        """Read all Songs by a specific artist.
        
        Args:
            artist (str): Artist name
            
        Returns:
            list: List of songs by the artist
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT id, title, artist, genre, duration FROM songs WHERE artist = ? ORDER BY title"
            results = self.db.execute_query(query, (artist,))
            
            songs = []
            for row in results:
                song = Song(
                    title=row[1],
                    artist=row[2],
                    genre=row[3],
                    duration=row[4]
                )
                song._AudioTrack__id = row[0]
                songs.append(song)
            
            logger.debug(f"Retrieved {len(songs)} songs by artist: {artist}")
            return songs
            
        except Exception as e:
            logger.error(f"Failed to read songs by artist {artist}: {e}")
            raise
    
    def read_by_genre(self, genre):
        """Read all Songs of a specific genre.
        
        Args:
            genre (str): Genre name
            
        Returns:
            list: List of songs in the genre
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT id, title, artist, genre, duration FROM songs WHERE genre = ? ORDER BY artist, title"
            results = self.db.execute_query(query, (genre,))
            
            songs = []
            for row in results:
                song = Song(
                    title=row[1],
                    artist=row[2],
                    genre=row[3],
                    duration=row[4]
                )
                song._AudioTrack__id = row[0]
                songs.append(song)
            
            logger.debug(f"Retrieved {len(songs)} songs in genre: {genre}")
            return songs
            
        except Exception as e:
            logger.error(f"Failed to read songs by genre {genre}: {e}")
            raise
