"""Integration tests for Reddit API functionality."""
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import os
import sys
import logging
from datetime import datetime, timedelta

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.reddit import RedditService
from src.services.mongodb import MongoDBService

# Create more verbose output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRedditIntegration(unittest.TestCase):
    """Integration tests for Reddit API with mocked responses."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Setup environment variables for testing
        os.environ['REDDIT_CLIENT_ID'] = 'test_client_id'
        os.environ['REDDIT_CLIENT_SECRET'] = 'test_client_secret'
        os.environ['REDDIT_USER_AGENT'] = 'test_user_agent'
        os.environ['SUB_NAMES'] = 'python,programming'
        os.environ['VALID_FLAIRS'] = 'Discussion,Help'
        
        # Setup MongoDB environment variables
        os.environ['MONGO_USER'] = 'test_user'
        os.environ['MONGO_PASSWORD'] = 'test_password'
        os.environ['MONGO_URI'] = 'test.mongodb.net'
        os.environ['MONGO_DB_NAME'] = 'test_db'
        
        # Create mocks for external services
        self.setup_mocks()
        
        logger.info("✓ Integration test setup complete")
        
    def setup_mocks(self):
        """Set up mock objects for the Reddit API and MongoDB."""
        # Create a patch for the Reddit and MongoDB clients
        self.praw_patch = patch('src.services.reddit.praw')
        self.mongo_patch = patch('src.services.mongodb.MongoDBService')
        
        # Start patches
        self.mock_praw = self.praw_patch.start()
        self.mock_mongo_class = self.mongo_patch.start()
        
        # Create the mock Reddit client
        self.mock_reddit = MagicMock()
        self.mock_praw.Reddit.return_value = self.mock_reddit
        
        # Create mock MongoDB service
        self.mock_mongo_service = MagicMock()
        self.mock_mongo_class.return_value = self.mock_mongo_service
        
        # Configure MongoDB service to track existing posts
        self.existing_posts = set()
        self.mock_mongo_service.check_post_exists.side_effect = lambda post_id, collection: post_id in self.existing_posts
        self.mock_mongo_service.insert_post.side_effect = lambda post_id, collection: self.existing_posts.add(post_id)
        
        # Create a mock subreddit for each subreddit in SUB_NAMES
        self.subreddits = {}
        for sub_name in os.environ['SUB_NAMES'].split(','):
            mock_subreddit = MagicMock()
            self.subreddits[sub_name] = mock_subreddit
            
            # Configure a different set of mock posts for each subreddit
            if sub_name == 'python':
                mock_subreddit.new.return_value = self.create_mock_subreddit_posts('python', 5, ['Discussion', 'Help', 'Project'])
            elif sub_name == 'programming':
                mock_subreddit.new.return_value = self.create_mock_subreddit_posts('programming', 3, ['Discussion', 'Question'])
        
        # Configure the Reddit client to return the appropriate subreddit
        self.mock_reddit.subreddit.side_effect = lambda name: self.subreddits.get(name, MagicMock())
        
        # Initialize the Reddit service
        self.reddit_service = RedditService()
        
        # Replace the MongoDB service with our mock
        self.reddit_service.mongo_service = self.mock_mongo_service
        
        logger.info("✓ Mock Reddit API and MongoDB service configured")
    
    def create_mock_subreddit_posts(self, subreddit_name, count, flairs):
        """Create a list of mock Reddit posts."""
        posts = []
        now = datetime.now()
        
        for i in range(count):
            # Assign a flair from the list, cycling through them
            flair = flairs[i % len(flairs)]
            
            # Create a mock post
            mock_post = MagicMock()
            
            # Set basic post attributes
            mock_post.id = f"{subreddit_name}_post_{i}"
            mock_post.title = f"Test Post {i} in r/{subreddit_name}"
            mock_post.url = f"https://reddit.com/r/{subreddit_name}/comments/{mock_post.id}"
            mock_post.selftext = f"This is test post {i} content in r/{subreddit_name}"
            
            # Set the created time to be progressively older
            created_time = now - timedelta(hours=i)
            mock_post.created_utc = created_time.timestamp()
            
            # Set the flair
            mock_post.link_flair_text = flair
            
            # Add the post to our list
            posts.append(mock_post)
        
        logger.info(f"✓ Created {count} mock posts for r/{subreddit_name}")
        return posts
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.praw_patch.stop()
        self.mongo_patch.stop()
        
        logger.info("✓ Integration test teardown complete")
    
    def test_get_filtered_posts_python(self):
        """Test retrieving filtered posts from the Python subreddit."""
        # Call the function
        posts = self.reddit_service.get_filtered_posts('python')
        
        # Verify the Reddit API was called
        self.mock_reddit.subreddit.assert_called_with('python')
        
        # Check the number of posts returned (only those with valid flairs)
        # Python should have 3 posts with valid flairs (Discussion, Help)
        self.assertEqual(len(posts), 3)
        
        # Verify the content of the posts
        for post in posts:
            self.assertIn('python_post_', post['id'])
            self.assertIn('Test Post', post['title'])
            self.assertIn('r/python', post['title'])
            self.assertIn('https://reddit.com/r/python', post['url'])
            self.assertIn('This is test post', post['selftext'])
            self.assertIn(post['flair'], ['Discussion', 'Help'])
        
        logger.info(f"✓ Retrieved {len(posts)} filtered posts from r/python")
    
    def test_get_filtered_posts_programming(self):
        """Test retrieving filtered posts from the Programming subreddit."""
        # Call the function
        posts = self.reddit_service.get_filtered_posts('programming')
        
        # Verify the Reddit API was called
        self.mock_reddit.subreddit.assert_called_with('programming')
        
        # Check the number of posts returned (only those with valid flairs)
        # Programming should have 1 post with valid flairs (Discussion)
        self.assertEqual(len(posts), 1)
        
        # Verify the content of the posts
        for post in posts:
            self.assertIn('programming_post_', post['id'])
            self.assertIn('Test Post', post['title'])
            self.assertIn('r/programming', post['title'])
            self.assertIn('https://reddit.com/r/programming', post['url'])
            self.assertIn('This is test post', post['selftext'])
            self.assertEqual(post['flair'], 'Discussion')
        
        logger.info(f"✓ Retrieved {len(posts)} filtered posts from r/programming")
    
    def test_get_all_posts(self):
        """Test retrieving posts from all configured subreddits."""
        # Call the function
        all_posts = self.reddit_service.get_all_posts()
        
        # Verify the result structure
        self.assertEqual(len(all_posts), 2)  # Two subreddits
        
        # Check total number of posts across all subreddits
        total_posts = sum(len(posts) for posts in all_posts)
        self.assertEqual(total_posts, 4)  # 3 from Python, 1 from Programming
        
        logger.info(f"✓ Retrieved {total_posts} total posts from all subreddits")
    
    def test_duplicate_post_filtering(self):
        """Test that duplicate posts are filtered out."""
        # First call to get posts (should get all posts)
        first_call_posts = self.reddit_service.get_all_posts()
        first_call_total = sum(len(posts) for posts in first_call_posts)
        
        # Second call to get posts (should get no posts since all are now in MongoDB)
        second_call_posts = self.reddit_service.get_all_posts()
        second_call_total = sum(len(posts) for posts in second_call_posts)
        
        # Verify the first call got posts and the second call got none
        self.assertGreater(first_call_total, 0)
        self.assertEqual(second_call_total, 0)
        
        logger.info(f"✓ First call retrieved {first_call_total} posts, second call correctly filtered duplicates")

if __name__ == '__main__':
    unittest.main(verbosity=2) 