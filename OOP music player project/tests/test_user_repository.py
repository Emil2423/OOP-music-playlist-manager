"""Unit tests for user repository module.

Tests CRUD operations for User entities and repository inheritance.
"""

import unittest
import os
import tempfile

from src.database.connection import DatabaseConnection
from src.database.schema import initialize_database
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.repositories.base_repository import BaseRepository


class TestUserRepository(unittest.TestCase):
    """Test suite for UserRepository class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for entire test class."""
        cls.test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.test_db_path = cls.test_db_file.name
        cls.test_db_file.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after entire test class."""
        if os.path.exists(cls.test_db_path):
            os.unlink(cls.test_db_path)
    
    def setUp(self):
        """Set up test fixtures before each test."""
        DatabaseConnection.reset_instance()
        
        self.db = DatabaseConnection(self.test_db_path)
        self.db.connect()
        
        initialize_database(self.db)
        
        self.repo = UserRepository(self.db)
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.execute_update("DELETE FROM playlists")
        self.db.execute_update("DELETE FROM users")
        self.db.disconnect()
        DatabaseConnection.reset_instance()
    
    def test_repository_inheritance(self):
        """Test that UserRepository inherits from BaseRepository."""
        self.assertIsInstance(self.repo, BaseRepository)
    
    def test_create_user_returns_id(self):
        """Test that create_user persists and returns ID."""
        user = User(username="john_doe", email="john@example.com")
        
        user_id = self.repo.create(user)
        
        self.assertIsNotNone(user_id)
        self.assertEqual(user_id, user.id)
    
    def test_create_user_with_invalid_entity_raises_error(self):
        """Test that create raises ValueError for non-User object."""
        with self.assertRaises(ValueError):
            self.repo.create("not a user")
    
    def test_create_user_with_duplicate_username_raises_error(self):
        """Test that duplicate username raises exception."""
        user1 = User(username="john", email="john1@example.com")
        user2 = User(username="john", email="john2@example.com")
        
        self.repo.create(user1)
        
        with self.assertRaises(Exception):  # sqlite3.IntegrityError
            self.repo.create(user2)
    
    def test_create_user_with_duplicate_email_raises_error(self):
        """Test that duplicate email raises exception."""
        user1 = User(username="user1", email="john@example.com")
        user2 = User(username="user2", email="john@example.com")
        
        self.repo.create(user1)
        
        with self.assertRaises(Exception):  # sqlite3.IntegrityError
            self.repo.create(user2)
    
    def test_read_by_id_returns_user(self):
        """Test that read_by_id retrieves created user."""
        original_user = User(username="jane_doe", email="jane@example.com")
        
        user_id = self.repo.create(original_user)
        retrieved_user = self.repo.read_by_id(user_id)
        
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user._User__username, "jane_doe")
        self.assertEqual(retrieved_user._User__email, "jane@example.com")
    
    def test_read_by_id_returns_none_for_nonexistent_id(self):
        """Test that read_by_id returns None for non-existent ID."""
        result = self.repo.read_by_id("nonexistent-id")
        self.assertIsNone(result)
    
    def test_read_all_returns_all_users(self):
        """Test that read_all returns all created users."""
        users_data = [
            ("user1", "user1@example.com"),
            ("user2", "user2@example.com"),
            ("user3", "user3@example.com")
        ]
        
        for username, email in users_data:
            user = User(username=username, email=email)
            self.repo.create(user)
        
        all_users = self.repo.read_all()
        
        self.assertEqual(len(all_users), 3)
    
    def test_read_all_returns_empty_list_when_no_users(self):
        """Test that read_all returns empty list when database is empty."""
        all_users = self.repo.read_all()
        self.assertEqual(len(all_users), 0)
    
    def test_exists_returns_true_for_existing_user(self):
        """Test that exists returns True for created user."""
        user = User(username="test_user", email="test@example.com")
        user_id = self.repo.create(user)
        
        self.assertTrue(self.repo.exists(user_id))
    
    def test_exists_returns_false_for_nonexistent_user(self):
        """Test that exists returns False for non-existent ID."""
        self.assertFalse(self.repo.exists("nonexistent-id"))
    
    def test_read_by_username_returns_user(self):
        """Test that read_by_username finds user by username."""
        user = User(username="alice", email="alice@example.com")
        self.repo.create(user)
        
        found_user = self.repo.read_by_username("alice")
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user._User__username, "alice")
        self.assertEqual(found_user._User__email, "alice@example.com")
    
    def test_read_by_username_returns_none_for_nonexistent_username(self):
        """Test that read_by_username returns None for unknown username."""
        result = self.repo.read_by_username("unknown_user")
        self.assertIsNone(result)
    
    def test_read_by_email_returns_user(self):
        """Test that read_by_email finds user by email."""
        user = User(username="bob", email="bob@example.com")
        self.repo.create(user)
        
        found_user = self.repo.read_by_email("bob@example.com")
        
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user._User__username, "bob")
        self.assertEqual(found_user._User__email, "bob@example.com")
    
    def test_read_by_email_returns_none_for_nonexistent_email(self):
        """Test that read_by_email returns None for unknown email."""
        result = self.repo.read_by_email("unknown@example.com")
        self.assertIsNone(result)
    
    def test_create_multiple_users_with_unique_ids(self):
        """Test that each created user has a unique ID."""
        users = []
        for i in range(5):
            user = User(username=f"user{i}", email=f"user{i}@example.com")
            user_id = self.repo.create(user)
            users.append(user_id)
        
        # Check all IDs are unique
        self.assertEqual(len(users), len(set(users)))
    
    def test_user_attributes_preserved_after_round_trip(self):
        """Test that user attributes are preserved through database round-trip."""
        original = User(username="charlie", email="charlie@example.com")
        
        user_id = self.repo.create(original)
        retrieved = self.repo.read_by_id(user_id)
        
        self.assertEqual(retrieved._User__username, original._User__username)
        self.assertEqual(retrieved._User__email, original._User__email)
        self.assertEqual(retrieved.id, original.id)
    
    def test_special_characters_in_username(self):
        """Test that special characters in username are handled correctly."""
        user = User(
            username="user_with-special.chars123",
            email="special@example.com"
        )
        
        user_id = self.repo.create(user)
        retrieved = self.repo.read_by_id(user_id)
        
        self.assertEqual(retrieved._User__username, user._User__username)


if __name__ == '__main__':
    unittest.main()
