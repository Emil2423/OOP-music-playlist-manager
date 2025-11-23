"""
Database Schema and Migration Management
Handles database initialization and schema creation for all entities.
"""

import logging
from src.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class DatabaseSchema:
    """Manages database schema creation and migrations."""
    
    # SQL definitions for tables
    USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    SONGS_TABLE = """
    CREATE TABLE IF NOT EXISTS songs (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        duration INTEGER NOT NULL CHECK(duration > 0),
        artist TEXT NOT NULL,
        genre TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    PLAYLISTS_TABLE = """
    CREATE TABLE IF NOT EXISTS playlists (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        owner_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """
    
    PLAYLIST_SONGS_TABLE = """
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id TEXT PRIMARY KEY,
        playlist_id TEXT NOT NULL,
        song_id TEXT NOT NULL,
        position INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(playlist_id, position),
        FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
        FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
    )
    """
    
    # Index definitions for performance
    INDICES = [
        "CREATE INDEX IF NOT EXISTS idx_playlists_owner_id ON playlists(owner_id)",
        "CREATE INDEX IF NOT EXISTS idx_playlist_songs_playlist_id ON playlist_songs(playlist_id)",
        "CREATE INDEX IF NOT EXISTS idx_playlist_songs_song_id ON playlist_songs(song_id)",
    ]
    
    @staticmethod
    def initialize_database() -> None:
        """
        Initialize database schema by creating all tables and indices.
        
        Raises:
            RuntimeError: If schema initialization fails
        """
        db = DatabaseConnection()
        
        try:
            with db.get_cursor() as cursor:
                # Create tables
                cursor.execute(DatabaseSchema.USERS_TABLE)
                cursor.execute(DatabaseSchema.SONGS_TABLE)
                cursor.execute(DatabaseSchema.PLAYLISTS_TABLE)
                cursor.execute(DatabaseSchema.PLAYLIST_SONGS_TABLE)
                
                # Create indices
                for index_sql in DatabaseSchema.INDICES:
                    cursor.execute(index_sql)
                
                logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise RuntimeError(f"Schema initialization failed: {e}")
    
    @staticmethod
    def drop_all_tables() -> None:
        """
        Drop all tables from database.
        WARNING: This will delete all data. Use for testing only.
        
        Raises:
            RuntimeError: If drop operation fails
        """
        db = DatabaseConnection()
        tables = ["playlist_songs", "playlists", "songs", "users"]
        
        try:
            with db.get_cursor() as cursor:
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logger.warning("All tables dropped from database")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise RuntimeError(f"Drop tables failed: {e}")
