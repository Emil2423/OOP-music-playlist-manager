"""Unit tests for database connection module.

Tests Singleton pattern implementation, connection management,
and parameterized query execution.
"""

import unittest
import os
import tempfile
import sqlite3
from pathlib import Path

from database.connection import DatabaseConnection
from database.schema import initialize_database


class TestDatabaseConnection(unittest.TestCase):
    """Test suite for DatabaseConnection Singleton class."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Use temporary database for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Reset singleton for each test
        DatabaseConnection.reset_instance()
    
    def tearDown(self):
        """Clean up after each test."""
        # Reset singleton
        DatabaseConnection.reset_instance()
        
        # Remove test database file
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_singleton_instance_creation(self):
        """Test that DatabaseConnection returns the same instance."""
        db1 = DatabaseConnection(self.test_db_path)
        db2 = DatabaseConnection(self.test_db_path)
        
        self.assertIs(db1, db2, "Singleton should return the same instance")
    
    def test_connection_establishment(self):
        """Test database connection is established correctly."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        self.assertIsNotNone(db.get_connection(), "Connection should be established")
        db.disconnect()
    
    def test_execute_query_without_connection_raises_error(self):
        """Test that query execution fails without connection."""
        db = DatabaseConnection(self.test_db_path)
        
        with self.assertRaises(RuntimeError):
            db.execute_query("SELECT * FROM nonexistent")
    
    def test_execute_update_creates_row(self):
        """Test that execute_update can insert data."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        # Create a test table
        db.execute_update("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert a row
        row_id = db.execute_update(
            "INSERT INTO test_table (name) VALUES (?)",
            ("test_row",)
        )
        
        self.assertGreater(row_id, 0, "Insert should return row ID")
        db.disconnect()
    
    def test_parameterized_queries_prevent_sql_injection(self):
        """Test that parameterized queries safely handle special characters."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        # Create test table
        db.execute_update("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            )
        """)
        
        # Insert with special characters using parameterized query
        db.execute_update(
            "INSERT INTO users (username) VALUES (?)",
            ("admin'; DROP TABLE users; --",)
        )
        
        # Verify table still exists and data was inserted
        results = db.execute_query("SELECT * FROM users")
        self.assertEqual(len(results), 1, "Row should be inserted")
        self.assertEqual(results[0][1], "admin'; DROP TABLE users; --")
        
        db.disconnect()
    
    def test_execute_transaction_commits_all_queries(self):
        """Test that transaction commits all queries atomically."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        # Create test table
        db.execute_update("""
            CREATE TABLE numbers (
                id INTEGER PRIMARY KEY,
                value INTEGER NOT NULL
            )
        """)
        
        # Execute transaction with multiple queries
        queries = [
            ("INSERT INTO numbers (value) VALUES (?)", (10,)),
            ("INSERT INTO numbers (value) VALUES (?)", (20,)),
            ("INSERT INTO numbers (value) VALUES (?)", (30,))
        ]
        
        success = db.execute_transaction(queries)
        
        self.assertTrue(success, "Transaction should succeed")
        
        # Verify all rows were inserted
        results = db.execute_query("SELECT * FROM numbers")
        self.assertEqual(len(results), 3, "All three rows should be inserted")
        
        db.disconnect()
    
    def test_execute_transaction_rollback_on_error(self):
        """Test that transaction rolls back on error."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        # Create test table
        db.execute_update("""
            CREATE TABLE numbers (
                id INTEGER PRIMARY KEY,
                value INTEGER NOT NULL
            )
        """)
        
        # Create invalid transaction (second query will fail)
        queries = [
            ("INSERT INTO numbers (value) VALUES (?)", (10,)),
            ("INSERT INTO invalid_table (value) VALUES (?)", (20,))  # This will fail
        ]
        
        # Transaction should raise exception
        with self.assertRaises(Exception):
            db.execute_transaction(queries)
        
        # Verify no rows were inserted (rollback worked)
        results = db.execute_query("SELECT * FROM numbers")
        self.assertEqual(len(results), 0, "Rollback should prevent any inserts")
        
        db.disconnect()
    
    def test_foreign_key_constraints_enabled(self):
        """Test that foreign key constraints are enforced."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        # Create parent and child tables with FK constraint
        db.execute_update("""
            CREATE TABLE parent (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        db.execute_update("""
            CREATE TABLE child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES parent(id)
            )
        """)
        
        # Try to insert child with non-existent parent
        with self.assertRaises(Exception):
            db.execute_update(
                "INSERT INTO child (parent_id) VALUES (?)",
                (999,)
            )
        
        db.disconnect()
    
    def test_disconnect_closes_connection(self):
        """Test that disconnect closes the connection."""
        db = DatabaseConnection(self.test_db_path)
        db.connect()
        
        self.assertIsNotNone(db._connection)
        
        db.disconnect()
        
        self.assertIsNone(db._connection)


if __name__ == '__main__':
    unittest.main()
