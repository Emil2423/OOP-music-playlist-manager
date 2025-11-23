"""
User Repository
Implements CRUD operations for User entities with validation and logging.
"""

from typing import List, Optional, Dict, Any
import logging
from src.repositories.base_repository import BaseRepository
from src.models.user import User

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """
    Repository for User entity persistence.
    
    Demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Single Responsibility: Handles only User data access
    - High Cohesion: All methods focus on User operations
    """
    
    def __init__(self, db=None):
        """Initialize UserRepository."""
        super().__init__(db)
        self._table_name = "users"
    
    def create(self, entity: User) -> str:
        """
        Create new user in database.
        
        Args:
            entity: User object
            
        Returns:
            str: User ID
            
        Raises:
            ValueError: If user is invalid
            RuntimeError: If database operation fails
        """
        if not isinstance(entity, User):
            raise ValueError("Entity must be a User instance")
        
        # Extract properties from User object
        username = entity._User__username if hasattr(entity, '_User__username') else None
        email = entity._User__email if hasattr(entity, '_User__email') else None
        user_id = entity.id
        
        if not username or not email:
            raise ValueError("Invalid user: username and email are required")
        
        try:
            query = """
                INSERT INTO users (id, username, email)
                VALUES (?, ?, ?)
            """
            self._db.execute_update(query, (user_id, username, email))
            logger.info(f"User created: {user_id} - {username} ({email})")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise RuntimeError(f"Failed to create user: {e}")
    
    def read(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Read user by ID.
        
        Args:
            entity_id: User ID
            
        Returns:
            dict: User data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not entity_id:
            raise ValueError("entity_id is required")
        
        try:
            query = "SELECT * FROM users WHERE id = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (entity_id,))
                row = cursor.fetchone()
                result = self._row_to_dict(row)
                
                if result:
                    logger.debug(f"User read: {entity_id}")
                else:
                    logger.warning(f"User not found: {entity_id}")
                
                return result
        except Exception as e:
            logger.error(f"Error reading user: {e}")
            raise RuntimeError(f"Failed to read user: {e}")
    
    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all users from database.
        
        Returns:
            list: List of all users
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            query = "SELECT * FROM users ORDER BY created_at DESC"
            with self._db.get_cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                results = [self._row_to_dict(row) for row in rows]
                logger.debug(f"Read {len(results)} users from database")
                return results
        except Exception as e:
            logger.error(f"Error reading all users: {e}")
            raise RuntimeError(f"Failed to read all users: {e}")
    
    def read_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Read user by username.
        
        Args:
            username: Username to search
            
        Returns:
            dict: User data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not username:
            raise ValueError("username is required")
        
        try:
            query = "SELECT * FROM users WHERE username = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (username,))
                row = cursor.fetchone()
                result = self._row_to_dict(row)
                
                if result:
                    logger.debug(f"User found by username: {username}")
                else:
                    logger.warning(f"User not found by username: {username}")
                
                return result
        except Exception as e:
            logger.error(f"Error reading user by username: {e}")
            raise RuntimeError(f"Failed to read user by username: {e}")
    
    def read_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Read user by email.
        
        Args:
            email: Email address to search
            
        Returns:
            dict: User data or None if not found
            
        Raises:
            RuntimeError: If database operation fails
        """
        if not email:
            raise ValueError("email is required")
        
        try:
            query = "SELECT * FROM users WHERE email = ?"
            with self._db.get_cursor() as cursor:
                cursor.execute(query, (email,))
                row = cursor.fetchone()
                result = self._row_to_dict(row)
                
                if result:
                    logger.debug(f"User found by email: {email}")
                else:
                    logger.warning(f"User not found by email: {email}")
                
                return result
        except Exception as e:
            logger.error(f"Error reading user by email: {e}")
            raise RuntimeError(f"Failed to read user by email: {e}")
