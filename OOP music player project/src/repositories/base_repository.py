"""Base repository module providing abstract CRUD interface.

This module defines the abstract base repository class that all concrete
repositories inherit from, implementing the Repository pattern and
demonstrating SOLID principles (especially Liskov Substitution).
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Abstract base repository for data access abstraction.
    
    Provides common interface for CRUD operations following the Repository pattern.
    All concrete repositories inherit from this class, ensuring consistent behavior
    and enabling polymorphism.
    
    Demonstrates SOLID Principles:
    - Single Responsibility: Only handles data access logic
    - Open/Closed: Extensible through inheritance without modification
    - Liskov Substitution: All repositories can be used interchangeably
    - Interface Segregation: Contains only necessary CRUD methods
    - Dependency Inversion: Depends on abstraction, not concrete implementations
    
    Type Parameters:
        T: Type of entity this repository manages
    """
    
    def __init__(self):
        """Initialize base repository."""
        self.entity_name = self.__class__.__name__.replace('Repository', '')
        logger.debug(f"Initialized {self.__class__.__name__} for entity: {self.entity_name}")
    
    @abstractmethod
    def create(self, entity):
        """Create (persist) a new entity in the database.
        
        Converts a domain model instance to database record and inserts it.
        
        Args:
            entity: Domain model instance to persist
            
        Returns:
            int: ID or count of affected rows
            
        Raises:
            ValueError: If entity is invalid
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Validate entity attributes
            2. Extract values from entity properties
            3. Execute INSERT query with parameterized values
            4. Log operation and return ID
        """
        pass
    
    @abstractmethod
    def read_by_id(self, entity_id):
        """Read (retrieve) a single entity by ID from the database.
        
        Converts database record to domain model instance.
        
        Args:
            entity_id (str): Unique identifier of entity to retrieve
            
        Returns:
            object: Entity instance if found, None otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Query database for record with matching ID
            2. If found, convert to domain model instance
            3. Return domain model or None if not found
            4. Log operation
        """
        pass
    
    @abstractmethod
    def read_all(self):
        """Read (retrieve) all entities of this type from the database.
        
        Converts all database records to domain model instances.
        
        Returns:
            list: List of entity instances (empty list if none found)
            
        Raises:
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Query database for all records of this entity type
            2. Convert each record to domain model instance
            3. Return list of domain models
            4. Log operation
        """
        pass
    
    @abstractmethod
    def update(self, entity):
        """Update an existing entity in the database.
        
        Finds the entity by ID and updates its attributes.
        
        Args:
            entity: Domain model instance with updated attributes
            
        Returns:
            bool: True if update was successful, False if entity not found
            
        Raises:
            ValueError: If entity is invalid
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Validate entity attributes
            2. Check if entity exists
            3. Execute UPDATE query with parameterized values
            4. Log operation and return success status
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id):
        """Delete an entity from the database by ID.
        
        Permanently removes the entity and any related data.
        
        Args:
            entity_id (str): Unique identifier of entity to delete
            
        Returns:
            bool: True if deletion was successful, False if entity not found
            
        Raises:
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Check if entity exists
            2. Handle cascading deletes for related data
            3. Execute DELETE query
            4. Log operation and return success status
        """
        pass
    
    @abstractmethod
    def exists(self, entity_id):
        """Check if an entity with the given ID exists.
        
        Args:
            entity_id (str): Unique identifier to check
            
        Returns:
            bool: True if entity exists, False otherwise
            
        Raises:
            sqlite3.Error: If database operation fails
            
        Implementation Note:
            Concrete implementations should:
            1. Execute efficient COUNT query
            2. Return boolean result
            3. Log operation
        """
        pass
    
    def _log_operation(self, operation, entity_id=None):
        """Log a repository operation.
        
        Args:
            operation (str): Type of operation (CREATE, READ, UPDATE, DELETE)
            entity_id (str): ID of entity involved
        """
        msg = f"{operation} operation on {self.entity_name}"
        if entity_id:
            msg += f" (ID: {entity_id})"
        logger.info(msg)
