"""MongoDB service for storing and retrieving Reddit posts."""
import pymongo
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDBService:
    """Service for interacting with MongoDB."""
    
    def __init__(self):
        """Initialize the MongoDB client."""
        self.client = self._create_client()
        self.db = self.client[os.environ.get("MONGO_DB_NAME")]
    
    def _create_client(self):
        """Create a MongoDB client."""
        try:
            mongo_user = os.environ.get("MONGO_USER")
            mongo_pass = os.environ.get("MONGO_PASSWORD")
            mongo_uri = os.environ.get("MONGO_URI")
            mongo_db = os.environ.get("MONGO_DB_NAME")
            
            if not all([mongo_user, mongo_pass, mongo_uri, mongo_db]):
                logger.warning("MongoDB credentials not fully configured")
                
            srv = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_uri}/?retryWrites=true&w=majority"
            client = pymongo.MongoClient(srv)
            
            # Test connection
            client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
            
            return client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def insert_post(self, post_id, collection_name):
        """Insert a post ID into a collection."""
        try:
            collection = self.db[collection_name]
            collection.insert_one({"id": post_id})
            logger.debug(f"Inserted post ID {post_id} into collection {collection_name}")
        except Exception as e:
            logger.error(f"Failed to insert post {post_id}: {e}")
            raise
    
    def check_post_exists(self, post_id, collection_name):
        """Check if a post ID exists in a collection."""
        try:
            collection = self.db[collection_name]
            id_count = collection.count_documents({"id": post_id})
            return bool(id_count)
        except Exception as e:
            logger.error(f"Failed to check post {post_id}: {e}")
            raise
    
    def cleanup_collection(self, collection_name, max_documents=100):
        """Delete all documents in a collection if it exceeds the max count."""
        try:
            collection = self.db[collection_name]
            docs_count = collection.count_documents({})
            if docs_count > max_documents:
                logger.info(f"Cleaning up collection {collection_name}, removing {docs_count} documents")
                collection.delete_many({})
        except Exception as e:
            logger.error(f"Failed to clean up collection {collection_name}: {e}")
            raise 