"""User repository for data access layer.

Implements CRUD operations for User entities imported from Student A's models.
Demonstrates Repository pattern and polymorphism through BaseRepository inheritance.
"""

import logging
from database.connection import DatabaseConnection
from models.user import User
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for User entity persistence and retrieval.
    
    Implements CRUD operations for User objects by translating between
    domain models (from Student A's User class) and database records.
    
    Inheritance demonstrates:
    - Polymorphism: Implements abstract methods from BaseRepository
    - Liskov Substitution: Can substitute BaseRepository where needed
    - Single Responsibility: Focuses only on User persistence
    
    Database Table Schema:
        users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    def __init__(self, db_connection=None):
        """Initialize UserRepository with database connection.
        
        Args:
            db_connection (DatabaseConnection): Database connection instance.
                If None, uses singleton instance.
        """
        super().__init__()
        self.db = db_connection or DatabaseConnection()
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def create(self, user):
        """Create (persist) a new User in the database.
        
        Converts User domain model to database record and inserts it.
        Uses the user's UUID from Student A's User class.
        
        Args:
            user (User): User instance to persist (from Student A's models)
            
        Returns:
            str: ID of the created user
            
        Raises:
            ValueError: If user is invalid or not a User instance
            sqlite3.Error: If database operation fails (e.g., duplicate username/email)
            RuntimeError: If database not connected
            
        Example:
            >>> user = User(username="john_doe", email="john@example.com")
            >>> repo = UserRepository()
            >>> user_id = repo.create(user)
        """
        try:
            if not isinstance(user, User):
                raise ValueError("Entity must be a User instance")
            
            query = """
            INSERT INTO users (id, username, email)
            VALUES (?, ?, ?)
            """
            
            params = (
                user.id,
                user._User__username,  # Access private attribute
                user._User__email      # Access private attribute
            )
            
            self.db.execute_update(query, params)
            self._log_operation("CREATE", user.id)
            logger.debug(f"User created with ID: {user.id}, Username: {user._User__username}")
            return user.id
            
        except ValueError as e:
            logger.error(f"Invalid user entity: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def read_by_id(self, user_id):
        """Read (retrieve) a User by ID from the database.
        
        Queries database and converts record to User domain model instance.
        
        Args:
            user_id (str): Unique identifier (UUID) of user
            
        Returns:
            User: User instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = UserRepository()
            >>> user = repo.read_by_id("550e8400-e29b-41d4-a716-446655440000")
            >>> if user:
            ...     print(f"Found user: {user.username}")
        """
        try:
            query = "SELECT id, username, email FROM users WHERE id = ?"
            results = self.db.execute_query(query, (user_id,))
            
            if not results:
                logger.debug(f"No user found with ID: {user_id}")
                return None
            
            row = results[0]
            # Create User instance from database record
            user = User(
                username=row[1],
                email=row[2]
            )
            # Override the UUID to match database ID
            user._User__id = row[0]
            
            self._log_operation("READ", user_id)
            return user
            
        except Exception as e:
            logger.error(f"Failed to read user by ID {user_id}: {e}")
            raise
    
    def read_all(self):
        """Read (retrieve) all Users from the database.
        
        Returns:
            list: List of User instances (empty if none exist)
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
            
        Example:
            >>> repo = UserRepository()
            >>> all_users = repo.read_all()
            >>> print(f"Found {len(all_users)} users")
        """
        try:
            query = "SELECT id, username, email FROM users ORDER BY created_at DESC"
            results = self.db.execute_query(query)
            
            users = []
            for row in results:
                user = User(
                    username=row[1],
                    email=row[2]
                )
                # Override the UUID to match database ID
                user._User__id = row[0]
                users.append(user)
            
            logger.info(f"Retrieved {len(users)} users from database")
            return users
            
        except Exception as e:
            logger.error(f"Failed to read all users: {e}")
            raise
    
    def exists(self, user_id):
        """Check if a User with the given ID exists.
        
        Args:
            user_id (str): User ID to check
            
        Returns:
            bool: True if user exists, False otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT COUNT(*) FROM users WHERE id = ?"
            result = self.db.execute_query(query, (user_id,))
            exists = result[0][0] > 0
            
            if exists:
                logger.debug(f"User with ID {user_id} exists")
            
            return exists
            
        except Exception as e:
            logger.error(f"Failed to check if user exists: {e}")
            raise
    
    def read_by_username(self, username):
        """Read a User by username.
        
        Args:
            username (str): Username to search for
            
        Returns:
            User: User instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT id, username, email FROM users WHERE username = ?"
            results = self.db.execute_query(query, (username,))
            
            if not results:
                logger.debug(f"No user found with username: {username}")
                return None
            
            row = results[0]
            user = User(
                username=row[1],
                email=row[2]
            )
            user._User__id = row[0]
            
            logger.debug(f"User found with username: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to read user by username {username}: {e}")
            raise
    
    def read_by_email(self, email):
        """Read a User by email.
        
        Args:
            email (str): Email to search for
            
        Returns:
            User: User instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            RuntimeError: If database not connected
        """
        try:
            query = "SELECT id, username, email FROM users WHERE email = ?"
            results = self.db.execute_query(query, (email,))
            
            if not results:
                logger.debug(f"No user found with email: {email}")
                return None
            
            row = results[0]
            user = User(
                username=row[1],
                email=row[2]
            )
            user._User__id = row[0]
            
            logger.debug(f"User found with email: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to read user by email {email}: {e}")
            raise
