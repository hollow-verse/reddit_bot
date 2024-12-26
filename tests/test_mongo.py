from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBTester:
    def __init__(self):
        self.user = os.getenv('MONGO_USER')
        self.password = os.getenv('MONGO_PASSWORD')
        self.uri = os.getenv('MONGO_URI')
        self.db_name = os.getenv('MONGO_DB_NAME')
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None

    def connect(self) -> bool:
        """Test MongoDB connection"""
        try:
            connection_string = f"mongodb+srv://{self.user}:{self.password}@{self.uri}"
            self.client = MongoClient(connection_string)
            self.db = self.client[self.db_name]
            self.collection = self.db['test_collection']
            
            # Ping the server to test connection
            self.client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False

    def test_crud_operations(self) -> bool:
        """Test basic CRUD operations"""
        try:
            # Test document
            test_doc = {
                "test_id": "test_1",
                "message": "Test message",
                "timestamp": datetime.utcnow()
            }

            # Create
            insert_result = self.collection.insert_one(test_doc)
            logger.info(f"✅ Created document with id: {insert_result.inserted_id}")

            # Read
            found_doc = self.collection.find_one({"test_id": "test_1"})
            if not found_doc:
                raise Exception("Failed to read document")
            logger.info("✅ Successfully read document")

            # Update
            update_result = self.collection.update_one(
                {"test_id": "test_1"},
                {"$set": {"message": "Updated test message"}}
            )
            if update_result.modified_count != 1:
                raise Exception("Failed to update document")
            logger.info("✅ Successfully updated document")

            # Delete
            delete_result = self.collection.delete_one({"test_id": "test_1"})
            if delete_result.deleted_count != 1:
                raise Exception("Failed to delete document")
            logger.info("✅ Successfully deleted document")

            return True
        except Exception as e:
            logger.error(f"❌ CRUD test failed: {str(e)}")
            return False
        
    def cleanup(self) -> None:
        """Clean up test data and close connection"""
        try:
            if self.collection:
                self.collection.delete_many({"test_id": "test_1"})
            if self.client:
                self.client.close()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {str(e)}")

def run_mongo_tests() -> None:
    """Run all MongoDB tests"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    tester = MongoDBTester()
    
    try:
        # Test connection
        if not tester.connect():
            raise Exception("Connection test failed")

        # Test CRUD operations
        if not tester.test_crud_operations():
            raise Exception("CRUD operations test failed")

        logger.info("✅ All MongoDB tests passed successfully!")
    except Exception as e:
        logger.error(f"❌ Tests failed: {str(e)}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    run_mongo_tests()
