"""Custom exception classes for music playlist manager.

This module defines a hierarchy of custom exceptions for more specific
error handling throughout the application. This follows best practices
for exception handling and promotes cleaner error management.

Exception Hierarchy:
    MusicPlaylistError (base)
    ├── EntityNotFoundError
    ├── ValidationError
    ├── DatabaseError
    ├── DuplicateEntityError
    └── AuthorizationError

Design Principles Applied:
- Single Responsibility: Each exception handles a specific error type
- Open/Closed: Easy to extend with new exception types
- Liskov Substitution: All exceptions can be caught as MusicPlaylistError
"""

import logging

logger = logging.getLogger(__name__)


class MusicPlaylistError(Exception):
    """Base exception class for all music playlist manager errors.
    
    All custom exceptions inherit from this class, allowing callers
    to catch all application-specific errors with a single except clause.
    
    Attributes:
        message (str): Human-readable error description
        details (dict): Additional error context
    
    Example:
        try:
            # Application code
        except MusicPlaylistError as e:
            logger.error(f"Application error: {e}")
    """
    
    def __init__(self, message="An error occurred in the music playlist manager", details=None):
        """Initialize MusicPlaylistError.
        
        Args:
            message (str): Error message
            details (dict, optional): Additional context about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        logger.debug(f"{self.__class__.__name__}: {message}")
    
    def __str__(self):
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class EntityNotFoundError(MusicPlaylistError):
    """Exception raised when an entity is not found in the database.
    
    Used when attempting to read, update, or delete an entity that
    doesn't exist in the system.
    
    Attributes:
        entity_type (str): Type of entity (User, Song, Playlist)
        entity_id (str): ID of the entity that wasn't found
    
    Example:
        raise EntityNotFoundError("User", user_id)
    """
    
    def __init__(self, entity_type, entity_id, message=None):
        """Initialize EntityNotFoundError.
        
        Args:
            entity_type (str): Type of entity (e.g., "User", "Song")
            entity_id (str): ID of the missing entity
            message (str, optional): Custom error message
        """
        self.entity_type = entity_type
        self.entity_id = entity_id
        
        if message is None:
            message = f"{entity_type} with ID '{entity_id}' not found"
        
        super().__init__(
            message=message,
            details={"entity_type": entity_type, "entity_id": entity_id}
        )


class ValidationError(MusicPlaylistError):
    """Exception raised when entity validation fails.
    
    Used when input data doesn't meet the required constraints
    (e.g., empty strings, invalid formats, negative durations).
    
    Attributes:
        field (str): Name of the field that failed validation
        value: The invalid value
        constraint (str): Description of the validation constraint
    
    Example:
        raise ValidationError("email", "invalid", "must contain @")
    """
    
    def __init__(self, field, value, constraint, message=None):
        """Initialize ValidationError.
        
        Args:
            field (str): Name of the invalid field
            value: The invalid value
            constraint (str): Description of the constraint violated
            message (str, optional): Custom error message
        """
        self.field = field
        self.value = value
        self.constraint = constraint
        
        if message is None:
            message = f"Validation failed for '{field}': {constraint}"
        
        super().__init__(
            message=message,
            details={"field": field, "value": str(value), "constraint": constraint}
        )


class DatabaseError(MusicPlaylistError):
    """Exception raised when a database operation fails.
    
    Wraps underlying SQLite errors with additional context
    for easier debugging and handling.
    
    Attributes:
        operation (str): Type of operation (CREATE, READ, UPDATE, DELETE)
        original_error (Exception): The original database exception
    
    Example:
        except sqlite3.Error as e:
            raise DatabaseError("CREATE", e, "users")
    """
    
    def __init__(self, operation, original_error, table=None, message=None):
        """Initialize DatabaseError.
        
        Args:
            operation (str): Database operation type
            original_error (Exception): Original exception from database
            table (str, optional): Table name involved
            message (str, optional): Custom error message
        """
        self.operation = operation
        self.original_error = original_error
        self.table = table
        
        if message is None:
            message = f"Database {operation} operation failed"
            if table:
                message += f" on table '{table}'"
            message += f": {str(original_error)}"
        
        super().__init__(
            message=message,
            details={
                "operation": operation,
                "table": table,
                "original_error": str(original_error)
            }
        )


class DuplicateEntityError(MusicPlaylistError):
    """Exception raised when attempting to create a duplicate entity.
    
    Used when a unique constraint would be violated
    (e.g., duplicate username or email).
    
    Attributes:
        entity_type (str): Type of entity
        field (str): Field that caused the duplicate
        value: The duplicate value
    
    Example:
        raise DuplicateEntityError("User", "username", "john_doe")
    """
    
    def __init__(self, entity_type, field, value, message=None):
        """Initialize DuplicateEntityError.
        
        Args:
            entity_type (str): Type of entity
            field (str): Field with duplicate value
            value: The duplicate value
            message (str, optional): Custom error message
        """
        self.entity_type = entity_type
        self.field = field
        self.value = value
        
        if message is None:
            message = f"{entity_type} with {field} '{value}' already exists"
        
        super().__init__(
            message=message,
            details={"entity_type": entity_type, "field": field, "value": str(value)}
        )


class AuthorizationError(MusicPlaylistError):
    """Exception raised when an unauthorized operation is attempted.
    
    Used when a user tries to perform an operation they don't have
    permission for (e.g., modifying another user's playlist).
    
    Attributes:
        user_id (str): ID of the user attempting the operation
        operation (str): The unauthorized operation
        resource (str): The protected resource
    
    Example:
        raise AuthorizationError(user_id, "delete", "playlist")
    """
    
    def __init__(self, user_id, operation, resource, message=None):
        """Initialize AuthorizationError.
        
        Args:
            user_id (str): ID of the unauthorized user
            operation (str): Operation attempted
            resource (str): Resource being accessed
            message (str, optional): Custom error message
        """
        self.user_id = user_id
        self.operation = operation
        self.resource = resource
        
        if message is None:
            message = f"User '{user_id}' is not authorized to {operation} this {resource}"
        
        super().__init__(
            message=message,
            details={
                "user_id": user_id,
                "operation": operation,
                "resource": resource
            }
        )
