"""
Database Connection Manager - Singleton Pattern
Manages SQLite3 connection lifecycle with proper resource management.
"""

import sqlite3
import logging
import os
from typing import Optional
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Singleton connection manager for SQLite3 database."""
    
    _instance: Optional['DatabaseConnection'] = None
    _lock = None
    
    def __new__(cls, db_path: str = "playlist_manager.db"):
        """Implement Singleton pattern using __new__."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "playlist_manager.db"):
        """Initialize connection only once."""
        if self._initialized:
            return
        
        self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._initialized = True
        logger.debug(f"DatabaseConnection initialized with db_path: {db_path}")
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection.
        
        Returns:
            sqlite3.Connection: Active database connection
            
        Raises:
            RuntimeError: If connection fails
        """
        if self._connection is not None:
            return self._connection
        
        try:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Database connection established: {self._db_path}")
            return self._connection
        except sqlite3.DatabaseError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise RuntimeError(f"Database connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            try:
                self._connection.close()
                self._connection = None
                logger.info("Database connection closed")
            except sqlite3.DatabaseError as e:
                logger.error(f"Error closing database connection: {e}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get active connection or establish one."""
        if self._connection is None:
            self.connect()
        return self._connection
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor.
        Ensures cursor is properly closed after use.
        
        Yields:
            sqlite3.Cursor: Database cursor for queries
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
            logger.debug("Database transaction committed")
        except sqlite3.DatabaseError as e:
            connection.rollback()
            logger.error(f"Database error - transaction rolled back: {e}")
            raise
        except Exception as e:
            connection.rollback()
            logger.error(f"Unexpected error - transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SELECT query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            sqlite3.Cursor: Cursor with query results
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor
        except sqlite3.DatabaseError as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            int: Number of affected rows
            
        Raises:
            sqlite3.DatabaseError: On database errors
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except sqlite3.DatabaseError as e:
            logger.error(f"Update execution failed: {e}")
            raise
    
    def reset(self) -> None:
        """Reset singleton instance (for testing purposes)."""
        self.disconnect()
        DatabaseConnection._instance = None
        self._initialized = False
        logger.info("DatabaseConnection singleton reset")
