"""Unit tests for the MongoDB service."""
import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import logging

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.mongodb import MongoDBService

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestMongoDBService(unittest.TestCase):
    """Test cases for the MongoDB service."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create patches for external dependencies
        self.pymongo_patch = patch('src.services.mongodb.pymongo')
        
        # Start patches
        self.mock_pymongo = self.pymongo_patch.start()
        
        # Create mock objects
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        
        # Configure mock returns
        self.mock_pymongo.MongoClient.return_value = self.mock_client
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        
        # Setup environment variables for testing
        os.environ['MONGO_USER'] = 'test_user'
        os.environ['MONGO_PASSWORD'] = 'test_password'
        os.environ['MONGO_URI'] = 'test.mongodb.net'
        os.environ['MONGO_DB_NAME'] = 'test_db'
        
        # Initialize the service
        self.mongodb_service = MongoDBService()
        
        print("✓ Setup complete: Created mock MongoDB client")
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.pymongo_patch.stop()
        
        print("✓ Teardown complete: Stopped all patches")
    
    def test_create_client(self):
        """Test MongoDB client creation with proper credentials."""
        # Verify MongoDB client was created with the correct connection string
        self.mock_pymongo.MongoClient.assert_called_once()
        connection_str = self.mock_pymongo.MongoClient.call_args[0][0]
        
        # Check if the connection string contains the credentials
        self.assertIn('test_user', connection_str)
        self.assertIn('test_password', connection_str)
        self.assertIn('test.mongodb.net', connection_str)
        
        # Verify ping was called to test the connection
        self.mock_client.admin.command.assert_called_once_with('ping')
        
        print("✓ Test create_client: MongoDB client created with correct credentials")
    
    def test_insert_post(self):
        """Test inserting a post ID into a collection."""
        # Call the function
        self.mongodb_service.insert_post('test_post_id', 'test_collection')
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify insert_one was called with the correct document
        self.mock_collection.insert_one.assert_called_once_with({'id': 'test_post_id'})
        
        print("✓ Test insert_post: Post ID correctly inserted into collection")
    
    def test_check_post_exists_true(self):
        """Test checking if a post exists when it does."""
        # Configure the mock to return a count of 1 (post exists)
        self.mock_collection.count_documents.return_value = 1
        
        # Call the function
        result = self.mongodb_service.check_post_exists('test_post_id', 'test_collection')
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify count_documents was called with the correct query
        self.mock_collection.count_documents.assert_called_once_with({'id': 'test_post_id'})
        
        # Verify the result
        self.assertTrue(result)
        
        print("✓ Test check_post_exists_true: Correctly detected existing post")
    
    def test_check_post_exists_false(self):
        """Test checking if a post exists when it doesn't."""
        # Configure the mock to return a count of 0 (post doesn't exist)
        self.mock_collection.count_documents.return_value = 0
        
        # Call the function
        result = self.mongodb_service.check_post_exists('test_post_id', 'test_collection')
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify count_documents was called with the correct query
        self.mock_collection.count_documents.assert_called_once_with({'id': 'test_post_id'})
        
        # Verify the result
        self.assertFalse(result)
        
        print("✓ Test check_post_exists_false: Correctly detected non-existing post")
    
    def test_cleanup_collection_under_limit(self):
        """Test cleanup when document count is under the limit."""
        # Configure the mock to return a count under the limit
        self.mock_collection.count_documents.return_value = 50
        
        # Call the function
        self.mongodb_service.cleanup_collection('test_collection')
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify count_documents was called
        self.mock_collection.count_documents.assert_called_once_with({})
        
        # Verify delete_many was NOT called
        self.mock_collection.delete_many.assert_not_called()
        
        print("✓ Test cleanup_collection_under_limit: No documents deleted when under limit")
    
    def test_cleanup_collection_over_limit(self):
        """Test cleanup when document count is over the limit."""
        # Configure the mock to return a count over the limit
        self.mock_collection.count_documents.return_value = 150
        
        # Call the function
        self.mongodb_service.cleanup_collection('test_collection')
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify count_documents was called
        self.mock_collection.count_documents.assert_called_once_with({})
        
        # Verify delete_many was called with the correct query
        self.mock_collection.delete_many.assert_called_once_with({})
        
        print("✓ Test cleanup_collection_over_limit: Documents deleted when over limit")
    
    def test_cleanup_collection_custom_limit(self):
        """Test cleanup with a custom document limit."""
        # Configure the mock to return a count over the custom limit
        self.mock_collection.count_documents.return_value = 30
        
        # Call the function with a custom limit
        self.mongodb_service.cleanup_collection('test_collection', max_documents=20)
        
        # Verify the collection was accessed
        self.mock_db.__getitem__.assert_called_with('test_collection')
        
        # Verify count_documents was called
        self.mock_collection.count_documents.assert_called_once_with({})
        
        # Verify delete_many was called with the correct query
        self.mock_collection.delete_many.assert_called_once_with({})
        
        print("✓ Test cleanup_collection_custom_limit: Documents deleted when over custom limit")
    
    def test_mongodb_connection_error(self):
        """Test behavior when MongoDB connection fails."""
        # Recreate the patches to simulate a connection error
        self.pymongo_patch.stop()
        self.pymongo_patch = patch('src.services.mongodb.pymongo')
        self.mock_pymongo = self.pymongo_patch.start()
        
        # Configure the mock to raise an exception on client creation
        self.mock_pymongo.MongoClient.side_effect = Exception("Connection failed")
        
        # Attempt to create the service, which should raise the exception
        with self.assertRaises(Exception) as context:
            mongodb_service = MongoDBService()
        
        # Verify the exception message
        self.assertEqual(str(context.exception), "Connection failed")
        
        print("✓ Test mongodb_connection_error: Correctly handled MongoDB connection error")

if __name__ == '__main__':
    unittest.main(verbosity=2) 