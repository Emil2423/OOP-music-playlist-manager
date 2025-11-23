"""
Base Repository Class
Abstract base class implementing common CRUD operations and design patterns.
Demonstrates: Abstraction, Encapsulation, and Dependency Inversion (SOLID)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging
from src.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """
    Abstract base repository for all entity repositories.
    Implements common CRUD patterns and transaction handling.
    
    Design Principles:
    - Abstraction: Defines interface for subclasses
    - Encapsulation: Private db connection, public interface
    - Dependency Inversion: Depends on DatabaseConnection abstraction
    - Single Responsibility: Handles only data access logic
    """
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        """
        Initialize repository with database connection.
        
        Args:
            db: DatabaseConnection instance (uses Singleton if not provided)
        """
        self._db = db or DatabaseConnection()
        self._table_name: str = ""
    
    @abstractmethod
    def create(self, entity: Any) -> str:
        """
        Create new entity in database.
        
        Args:
            entity: Entity object to persist
            
        Returns:
            str: ID of created entity
            
        Raises:
            ValueError: If entity is invalid
            RuntimeError: If database operation fails
        """
        pass
    
    @abstractmethod
    def read(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Read entity by ID.
        
        Args:
            entity_id: ID of entity to retrieve
            
        Returns:
            dict: Entity data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        pass
    
    @abstractmethod
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all entities from table.
        
        Returns:
            list: List of all entities
            
        Raises:
            RuntimeError: If database operation fails
        """
        pass
    
    def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """
        Update entity (base implementation for common pattern).
        
        Args:
            entity_id: ID of entity to update
            data: Dictionary of fields to update
            
        Returns:
            bool: True if update successful, False if entity not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id or not data:
            raise ValueError("entity_id and data are required")
        
        # Subclasses should override for specific logic
        logger.debug(f"Update called on {self._table_name} with id={entity_id}")
        return False
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: ID of entity to delete
            
        Returns:
            bool: True if deletion successful, False if entity not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id:
            raise ValueError("entity_id is required")
        
        try:
            query = f"DELETE FROM {self._table_name} WHERE id = ?"
            rows_affected = self._db.execute_update(query, (entity_id,))
            success = rows_affected > 0
            
            if success:
                logger.info(f"Entity deleted from {self._table_name}: {entity_id}")
            else:
                logger.warning(f"No entity found to delete in {self._table_name}: {entity_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting from {self._table_name}: {e}")
            raise RuntimeError(f"Delete operation failed: {e}")
    
    def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: ID of entity to check
            
        Returns:
            bool: True if entity exists
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id:
            raise ValueError("entity_id is required")
        
        try:
            query = f"SELECT COUNT(*) FROM {self._table_name} WHERE id = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (entity_id,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error checking existence in {self._table_name}: {e}")
            raise RuntimeError(f"Existence check failed: {e}")
    
    def _row_to_dict(self, row: Any) -> Dict[str, Any]:
        """
        Convert sqlite3.Row to dictionary.
        
        Args:
            row: sqlite3.Row object
            
        Returns:
            dict: Row data as dictionary
        """
        if row is None:
            return None
        return dict(row) if row else None
