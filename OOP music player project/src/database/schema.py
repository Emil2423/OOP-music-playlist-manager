"""Database schema module for music playlist manager.

This module initializes the SQLite database with tables matching the
model classes defined in Student A's code. Creates tables for users,
songs, playlists, and their relationships.
"""

import logging
from typing import Optional
from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


def initialize_database(db_connection: Optional[DatabaseConnection] = None) -> None:
    """Initialize database schema with all required tables.
    
    Creates tables for User, Song, Playlist, and the many-to-many relationship
    between Playlist and Song. Idempotent - safe to call multiple times.
    
    Args:
        db_connection (Optional[DatabaseConnection]): Database connection instance.
            If None, uses the singleton instance.
            
    Raises:
        sqlite3.Error: If schema creation fails
        RuntimeError: If database not connected
        
    Note:
        Creates the following tables:
        - users: Stores user information
        - songs: Stores song/audio track information
        - playlists: Stores playlist information with owner references
        - playlist_songs: Junction table for many-to-many relationship
    """
    if db_connection is None:
        db_connection = DatabaseConnection()
    
    try:
        logger.info("Starting database schema initialization...")
        
        # Create users table
        create_users_query = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Create songs table (based on Song extends AudioTrack)
        create_songs_query = """
        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Create playlists table
        create_playlists_query = """
        CREATE TABLE IF NOT EXISTS playlists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        
        # Create playlist_songs junction table (many-to-many)
        create_playlist_songs_query = """
        CREATE TABLE IF NOT EXISTS playlist_songs (
            playlist_id TEXT NOT NULL,
            song_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playlist_id, song_id),
            FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
        )
        """
        
        # Execute all queries in transaction
        queries = [
            (create_users_query, ()),
            (create_songs_query, ()),
            (create_playlists_query, ()),
            (create_playlist_songs_query, ())
        ]
        
        db_connection.execute_transaction(queries)
        logger.info("Database schema initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise


def drop_all_tables(db_connection: Optional[DatabaseConnection] = None) -> None:
    """Drop all tables from the database.
    
    WARNING: This will delete all data. Use only for testing or development.
    
    Args:
        db_connection (Optional[DatabaseConnection]): Database connection instance.
            If None, uses the singleton instance.
            
    Raises:
        sqlite3.Error: If drop operation fails
        RuntimeError: If database not connected
    """
    if db_connection is None:
        db_connection = DatabaseConnection()
    
    try:
        logger.warning("Dropping all database tables - this will delete all data!")
        
        queries = [
            ("DROP TABLE IF EXISTS playlist_songs", ()),
            ("DROP TABLE IF EXISTS playlists", ()),
            ("DROP TABLE IF EXISTS songs", ()),
            ("DROP TABLE IF EXISTS users", ())
        ]
        
        db_connection.execute_transaction(queries)
        logger.info("All tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


def get_schema_status(db_connection: Optional[DatabaseConnection] = None) -> dict:
    """Get information about current database schema.
    
    Args:
        db_connection (Optional[DatabaseConnection]): Database connection instance.
            If None, uses the singleton instance.
            
    Returns:
        dict: Dictionary with table names as keys and column information as values
        
    Raises:
        sqlite3.Error: If query fails
        RuntimeError: If database not connected
    """
    if db_connection is None:
        db_connection = DatabaseConnection()
    
    try:
        schema_info = {}
        
        # Get list of all tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = db_connection.execute_query(tables_query)
        
        for table in tables:
            table_name = table[0]
            # Get columns for each table
            columns_query = f"PRAGMA table_info({table_name})"
            columns = db_connection.execute_query(columns_query)
            schema_info[table_name] = [col[1] for col in columns]  # col[1] is column name
        
        logger.debug(f"Schema status retrieved: {schema_info}")
        return schema_info
        
    except Exception as e:
        logger.error(f"Failed to get schema status: {e}")
        raise
