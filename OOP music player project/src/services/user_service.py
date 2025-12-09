"""User service module for business logic layer.

This service encapsulates all business logic related to User management,
providing a clean API that orchestrates between the presentation layer (CLI)
and the data access layer (repositories).

Design Principles Applied:
- Single Responsibility: Only handles User business logic
- Dependency Inversion: Depends on repository abstractions
- GRASP Controller: Coordinates use case operations
"""

import logging
import re
from models.user import User
from repositories.user_repository import UserRepository
from exceptions.custom_exceptions import (
    EntityNotFoundError,
    ValidationError,
    DuplicateEntityError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class UserService:
    """Service class for User business operations.
    
    Provides high-level operations for user management including
    validation, business rule enforcement, and coordination with repositories.
    
    Attributes:
        user_repo (UserRepository): Repository for user persistence
    
    Example:
        >>> service = UserService()
        >>> user = service.create_user("john_doe", "john@example.com")
        >>> all_users = service.get_all_users()
    """
    
    # Email validation regex pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Username constraints
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 30
    
    def __init__(self, user_repo=None):
        """Initialize UserService with repository.
        
        Args:
            user_repo (UserRepository, optional): User repository instance.
                If None, creates a new instance.
        """
        self.user_repo = user_repo or UserRepository()
        logger.debug("UserService initialized")
    
    def _validate_username(self, username):
        """Validate username format and constraints.
        
        Args:
            username (str): Username to validate
            
        Raises:
            ValidationError: If username is invalid
        """
        if not username or not username.strip():
            raise ValidationError("username", username, "cannot be empty")
        
        username = username.strip()
        
        if len(username) < self.MIN_USERNAME_LENGTH:
            raise ValidationError(
                "username", username,
                f"must be at least {self.MIN_USERNAME_LENGTH} characters"
            )
        
        if len(username) > self.MAX_USERNAME_LENGTH:
            raise ValidationError(
                "username", username,
                f"must be at most {self.MAX_USERNAME_LENGTH} characters"
            )
        
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValidationError(
                "username", username,
                "can only contain letters, numbers, underscores, and hyphens"
            )
    
    def _validate_email(self, email):
        """Validate email format.
        
        Args:
            email (str): Email to validate
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email or not email.strip():
            raise ValidationError("email", email, "cannot be empty")
        
        email = email.strip()
        
        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError("email", email, "must be a valid email format")
    
    def create_user(self, username, email):
        """Create a new user with validation.
        
        Validates input, checks for duplicates, creates user, and persists.
        
        Args:
            username (str): Unique username for the user
            email (str): Unique email address
            
        Returns:
            User: Created user instance with ID
            
        Raises:
            ValidationError: If input validation fails
            DuplicateEntityError: If username or email already exists
            DatabaseError: If persistence fails
            
        Example:
            >>> user = service.create_user("john_doe", "john@example.com")
            >>> print(f"Created user with ID: {user.id}")
        """
        logger.info(f"Creating user: username={username}")
        
        # Validate inputs
        self._validate_username(username)
        self._validate_email(email)
        
        # Auto-capitalize username
        username = username.strip().title()
        email = email.strip().lower()
        
        # Check for duplicate username
        existing = self.user_repo.read_by_username(username)
        if existing:
            raise DuplicateEntityError("User", "username", username)
        
        # Check for duplicate email
        existing = self.user_repo.read_by_email(email)
        if existing:
            raise DuplicateEntityError("User", "email", email)
        
        # Create and persist user
        try:
            user = User(username=username, email=email)
            self.user_repo.create(user)
            logger.info(f"User created successfully: ID={user.id}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError("CREATE", e, "users")
    
    def get_user_by_id(self, user_id):
        """Get a user by ID.
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            User: User instance
            
        Raises:
            EntityNotFoundError: If user not found
        """
        logger.debug(f"Getting user by ID: {user_id}")
        
        user = self.user_repo.read_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        
        return user
    
    def get_user_by_username(self, username):
        """Get a user by username.
        
        Args:
            username (str): Username to search for
            
        Returns:
            User: User instance
            
        Raises:
            EntityNotFoundError: If user not found
        """
        logger.debug(f"Getting user by username: {username}")
        
        user = self.user_repo.read_by_username(username)
        if not user:
            raise EntityNotFoundError("User", username, f"User with username '{username}' not found")
        
        return user
    
    def get_all_users(self):
        """Get all users.
        
        Returns:
            list: List of all User instances
        """
        logger.debug("Getting all users")
        return self.user_repo.read_all()
    
    def update_user(self, user_id, new_username=None, new_email=None):
        """Update user information.
        
        Args:
            user_id (str): ID of user to update
            new_username (str, optional): New username
            new_email (str, optional): New email
            
        Returns:
            User: Updated user instance
            
        Raises:
            EntityNotFoundError: If user not found
            ValidationError: If new values are invalid
            DuplicateEntityError: If new username/email already exists
            DatabaseError: If update fails
        """
        logger.info(f"Updating user: ID={user_id}")
        
        # Get existing user
        user = self.get_user_by_id(user_id)
        
        # Validate and check for duplicate username
        if new_username and new_username.strip().title() != user.username:
            self._validate_username(new_username)
            new_username = new_username.strip().title()
            
            existing = self.user_repo.read_by_username(new_username)
            if existing and existing.id != user_id:
                raise DuplicateEntityError("User", "username", new_username)
            
            user.username = new_username
        
        # Validate and check for duplicate email
        if new_email and new_email.strip().lower() != user.email:
            self._validate_email(new_email)
            new_email = new_email.strip().lower()
            
            existing = self.user_repo.read_by_email(new_email)
            if existing and existing.id != user_id:
                raise DuplicateEntityError("User", "email", new_email)
            
            user.email = new_email
        
        # Persist changes
        try:
            success = self.user_repo.update(user)
            if not success:
                raise DatabaseError("UPDATE", Exception("Update returned False"), "users")
            logger.info(f"User updated successfully: ID={user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError("UPDATE", e, "users")
    
    def delete_user(self, user_id):
        """Delete a user by ID.
        
        Note: This will fail if the user has playlists (foreign key constraint).
        
        Args:
            user_id (str): ID of user to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            EntityNotFoundError: If user not found
            DatabaseError: If deletion fails (e.g., has playlists)
        """
        logger.info(f"Deleting user: ID={user_id}")
        
        # Verify user exists
        self.get_user_by_id(user_id)
        
        try:
            success = self.user_repo.delete(user_id)
            if not success:
                raise DatabaseError("DELETE", Exception("Delete returned False"), "users")
            logger.info(f"User deleted successfully: ID={user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            if isinstance(e, DatabaseError):
                raise
            raise DatabaseError("DELETE", e, "users")
