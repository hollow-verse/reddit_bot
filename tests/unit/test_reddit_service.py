"""Unit tests for the Reddit service."""
import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import logging
from datetime import datetime
import pytz

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.reddit import RedditService

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestRedditService(unittest.TestCase):
    """Test cases for the Reddit service."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create patches for external dependencies
        self.praw_patch = patch('src.services.reddit.praw')
        self.mongo_patch = patch('src.services.reddit.MongoDBService')
        
        # Start patches
        self.mock_praw = self.praw_patch.start()
        self.mock_mongo = self.mongo_patch.start()
        
        # Create mock objects
        self.mock_reddit = MagicMock()
        self.mock_praw.Reddit.return_value = self.mock_reddit
        
        self.mock_mongo_service = MagicMock()
        self.mock_mongo.return_value = self.mock_mongo_service
        
        # Initialize the service
        self.reddit_service = RedditService()
        
        # Setup environment variables for testing
        os.environ['REDDIT_CLIENT_ID'] = 'test_client_id'
        os.environ['REDDIT_CLIENT_SECRET'] = 'test_client_secret'
        os.environ['REDDIT_USER_AGENT'] = 'test_user_agent'
        os.environ['SUB_NAMES'] = 'python,programming'
        os.environ['VALID_FLAIRS'] = 'Discussion,Help'
        
        print("✓ Setup complete: Created mock Reddit and MongoDB service")
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.praw_patch.stop()
        self.mongo_patch.stop()
        
        print("✓ Teardown complete: Stopped all patches")
    
    def test_create_client(self):
        """Test Reddit client creation with proper credentials."""
        # The client is already created in setUp, we just test the calls
        self.mock_praw.Reddit.assert_called_once_with(
            client_id='test_client_id',
            client_secret='test_client_secret',
            user_agent='test_user_agent'
        )
        
        print("✓ Test create_client: Reddit client created with correct credentials")
    
    def test_calculate_time_difference_minutes(self):
        """Test time difference calculation for minutes."""
        # Mock the datetime.now() to return a fixed time
        with patch('src.services.reddit.datetime') as mock_datetime:
            # Set fixed now time
            fixed_now = datetime(2023, 1, 1, 12, 10, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            mock_datetime.now.return_value = fixed_now
            
            # Use non-mocked datetime for the timestamp (10 minutes ago)
            post_time = datetime(2023, 1, 1, 12, 0, 0)
            post_time_utc = post_time.replace(tzinfo=pytz.UTC)
            timestamp = post_time_utc.timestamp()
            
            # Mock the utcfromtimestamp to return our fixed time
            mock_datetime.utcfromtimestamp.return_value = post_time
            
            # Test the function
            result = self.reddit_service.calculate_time_difference(timestamp)
            
            # Verify the result
            self.assertIn('10.00 minutes', result)
            
            print(f"✓ Test calculate_time_difference_minutes: Result '{result}' includes minutes")
    
    def test_calculate_time_difference_hours(self):
        """Test time difference calculation for hours."""
        # Mock the datetime.now() to return a fixed time
        with patch('src.services.reddit.datetime') as mock_datetime:
            # Set fixed now time
            fixed_now = datetime(2023, 1, 1, 14, 0, 0, tzinfo=pytz.timezone('Asia/Kolkata'))
            mock_datetime.now.return_value = fixed_now
            
            # Use non-mocked datetime for the timestamp (2 hours ago)
            post_time = datetime(2023, 1, 1, 12, 0, 0)
            post_time_utc = post_time.replace(tzinfo=pytz.UTC)
            timestamp = post_time_utc.timestamp()
            
            # Mock the utcfromtimestamp to return our fixed time
            mock_datetime.utcfromtimestamp.return_value = post_time
            
            # Test the function
            result = self.reddit_service.calculate_time_difference(timestamp)
            
            # Verify the result
            self.assertIn('2.00 hours', result)
            
            print(f"✓ Test calculate_time_difference_hours: Result '{result}' includes hours")
    
    def test_get_filtered_posts(self):
        """Test retrieving filtered posts from a subreddit."""
        # Mock the subreddit
        mock_subreddit = MagicMock()
        self.mock_reddit.subreddit.return_value = mock_subreddit
        
        # Create mock posts
        mock_post1 = MagicMock(
            id='post1',
            title='Test Post 1',
            link_flair_text='Discussion',
            created_utc=datetime(2023, 1, 1, 12, 0, 0).timestamp(),
            url='https://reddit.com/post1',
            selftext='Post content 1'
        )
        mock_post2 = MagicMock(
            id='post2',
            title='Test Post 2',
            link_flair_text='Help',
            created_utc=datetime(2023, 1, 1, 13, 0, 0).timestamp(),
            url='https://reddit.com/post2',
            selftext='Post content 2'
        )
        mock_post3 = MagicMock(
            id='post3',
            title='Test Post 3',
            link_flair_text='Invalid',  # This should be filtered out
            created_utc=datetime(2023, 1, 1, 14, 0, 0).timestamp(),
            url='https://reddit.com/post3',
            selftext='Post content 3'
        )
        
        # Setup mock post existence check
        self.mock_mongo_service.check_post_exists.side_effect = [False, False, False]
        
        # Setup mock time difference calculation
        with patch.object(
            self.reddit_service, 'calculate_time_difference',
            side_effect=['2 hours ago', '1 hour ago', '0 hours ago']
        ):
            # Setup the subreddit.new() to return our mock posts
            mock_subreddit.new.return_value = [mock_post1, mock_post2, mock_post3]
            
            # Call the function
            result = self.reddit_service.get_filtered_posts('python')
            
            # Verify results
            self.assertEqual(len(result), 2)  # Only 2 posts should pass the filter
            self.assertEqual(result[0]['id'], 'post1')
            self.assertEqual(result[1]['id'], 'post2')
            
            # Verify MongoDB calls
            self.mock_mongo_service.check_post_exists.assert_has_calls([
                call('post1', 'python'),
                call('post2', 'python')
            ])
            
            self.mock_mongo_service.insert_post.assert_has_calls([
                call('post1', 'python'),
                call('post2', 'python')
            ])
            
            print(f"✓ Test get_filtered_posts: Retrieved {len(result)} posts with correct filtering")
    
    def test_get_all_posts(self):
        """Test getting posts from all configured subreddits."""
        # Mock get_filtered_posts to return predefined results
        with patch.object(
            self.reddit_service, 'get_filtered_posts',
            side_effect=[
                [{'id': 'post1', 'subreddit': 'python'}], 
                [{'id': 'post2', 'subreddit': 'programming'}]
            ]
        ):
            # Call the function
            result = self.reddit_service.get_all_posts()
            
            # Verify the result
            self.assertEqual(len(result), 2)  # Two subreddits
            self.assertEqual(len(result[0]), 1)  # One post from first subreddit
            self.assertEqual(len(result[1]), 1)  # One post from second subreddit
            
            # Check the calls
            self.reddit_service.get_filtered_posts.assert_has_calls([
                call('python'),
                call('programming')
            ])
            
            print(f"✓ Test get_all_posts: Correctly retrieved posts from all configured subreddits")
    
    def test_empty_subreddit_names(self):
        """Test behavior when no subreddit names are configured."""
        os.environ['SUB_NAMES'] = ''
        
        # Call the function
        result = self.reddit_service.get_all_posts()
        
        # Verify the result
        self.assertEqual(result, [])
        
        print("✓ Test empty_subreddit_names: Correctly handled empty SUB_NAMES")

if __name__ == '__main__':
    unittest.main(verbosity=2) 