"""Database connection module implementing Singleton pattern.

This module provides centralized database connection management
for the music playlist manager application. Uses SQLite3 as the backend.
"""

import sqlite3
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Singleton class for managing SQLite database connections.
    
    Implements the Singleton pattern to ensure only one database connection
    exists throughout the application lifetime.
    
    Attributes:
        _instance (DatabaseConnection): Singleton instance
        _connection (sqlite3.Connection): SQLite connection object
        _db_path (str): Path to SQLite database file
    """
    
    _instance = None
    _connection = None
    
    # Calculate default path: workspace_root/music_playlist.db
    _base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    _default_db_path = os.path.join(_base_dir, "music_playlist.db")
    _db_path = _default_db_path
    
    def __new__(cls, db_path=None):
        """Create or return the singleton instance.
        
        Args:
            db_path (str, optional): Path to SQLite database file. 
                                   If None, uses default path in data directory.
            
        Returns:
            DatabaseConnection: Singleton instance of DatabaseConnection
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            if db_path is None:
                # Ensure data directory exists
                os.makedirs(os.path.dirname(cls._default_db_path), exist_ok=True)
                cls._instance._db_path = cls._default_db_path
            else:
                cls._instance._db_path = db_path
                
            logger.debug(f"Creating new DatabaseConnection instance with db_path: {cls._instance._db_path}")
        return cls._instance
    
    def connect(self):
        """Establish connection to SQLite database.
        
        Creates a new connection if one doesn't exist. Enables foreign key
        constraints for referential integrity.
        
        Raises:
            sqlite3.Error: If connection fails
            
        Note:
            Should be called during application initialization.
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self._db_path)
                # Enable foreign key constraints
                self._connection.execute("PRAGMA foreign_keys = ON")
                self._connection.row_factory = sqlite3.Row
                logger.info(f"Database connection established to {self._db_path}")
            except sqlite3.Error as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
    
    def disconnect(self):
        """Close the database connection.
        
        Commits any pending transactions and closes the connection.
        Safe to call even if already disconnected.
        
        Note:
            Should be called during application shutdown.
        """
        if self._connection is not None:
            try:
                self._connection.commit()
                self._connection.close()
                self._connection = None
                logger.info("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query, params=()):
        """Execute SELECT query and return results.
        
        Args:
            query (str): SQL SELECT query with parameterized placeholders (?)
            params (tuple): Query parameters to prevent SQL injection
            
        Returns:
            list: List of result rows (as tuples)
            
        Raises:
            sqlite3.Error: If query execution fails
            RuntimeError: If database not connected
            
        Example:
            >>> rows = db.execute_query(
            ...     "SELECT * FROM songs WHERE artist = ?",
            ...     ("The Beatles",)
            ... )
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            logger.debug(f"Query executed: {query} with params: {params}")
            return results
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e} - Query: {query}")
            raise
    
    def execute_update(self, query, params=()):
        """Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query (str): SQL INSERT/UPDATE/DELETE query with parameterized placeholders (?)
            params (Tuple): Query parameters to prevent SQL injection
            
        Returns:
            int: Last inserted row ID for INSERT queries, or rows affected
            
        Raises:
            sqlite3.Error: If query execution fails
            RuntimeError: If database not connected
            
        Example:
            >>> song_id = db.execute_update(
            ...     "INSERT INTO songs (title, artist, genre, duration) VALUES (?, ?, ?, ?)",
            ...     ("Imagine", "John Lennon", "Rock", 183)
            ... )
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            logger.debug(f"Update executed: {query} with params: {params}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            self._connection.rollback()
            logger.error(f"Update execution failed: {e} - Query: {query}")
            raise
    
    def execute_transaction(self, queries):
        """Execute multiple queries in a single transaction.
        
        All queries must succeed for the transaction to commit. If any query
        fails, all changes are rolled back.
        
        Args:
            queries (list): List of (query, params) tuples
            
        Returns:
            bool: True if transaction succeeded, False otherwise
            
        Raises:
            sqlite3.Error: If transaction execution fails
            RuntimeError: If database not connected
            
        Example:
            >>> queries = [
            ...     ("INSERT INTO users (username, email) VALUES (?, ?)",
            ...      ("john_doe", "john@example.com")),
            ...     ("INSERT INTO playlists (name, user_id) VALUES (?, ?)",
            ...      ("My Playlist", 1))
            ... ]
            >>> success = db.execute_transaction(queries)
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        try:
            cursor = self._connection.cursor()
            for query, params in queries:
                cursor.execute(query, params)
            self._connection.commit()
            logger.info(f"Transaction completed successfully with {len(queries)} queries")
            return True
        except sqlite3.Error as e:
            self._connection.rollback()
            logger.error(f"Transaction failed, rolled back: {e}")
            raise
    
    def get_connection(self):
        """Get the underlying SQLite connection object.
        
        Returns:
            sqlite3.Connection: Active database connection
            
        Raises:
            RuntimeError: If database not connected
            
        Note:
            Use with caution. Prefer using execute_query/execute_update methods.
        """
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection
    
    def close_connection(self):
        """Alias for disconnect() for consistency.
        
        Note:
            Deprecated: Use disconnect() instead
        """
        self.disconnect()
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing purposes only).
        
        Warning:
            This method should ONLY be used in test fixtures to reset
            the singleton state between tests.
        """
        if cls._instance is not None and cls._instance._connection is not None:
            cls._instance.disconnect()
        cls._instance = None
        logger.debug("Singleton instance reset")
