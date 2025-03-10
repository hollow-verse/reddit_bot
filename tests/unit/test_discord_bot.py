"""Unit tests for the Discord bot."""
import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import logging
from typing import Dict, Any

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bots.discord import DiscordBot

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestDiscordBot(unittest.TestCase):
    """Test cases for the Discord bot."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create patches for external dependencies
        self.webhook_patch = patch('src.bots.discord.DiscordWebhook')
        self.embed_patch = patch('src.bots.discord.DiscordEmbed')
        self.reddit_patch = patch('src.bots.discord.RedditService')
        
        # Start patches
        self.mock_webhook_class = self.webhook_patch.start()
        self.mock_embed_class = self.embed_patch.start()
        self.mock_reddit_class = self.reddit_patch.start()
        
        # Create mock objects
        self.mock_webhook = MagicMock()
        self.mock_webhook_class.return_value = self.mock_webhook
        
        self.mock_embed = MagicMock()
        self.mock_embed_class.return_value = self.mock_embed
        
        self.mock_reddit = MagicMock()
        self.mock_reddit_class.return_value = self.mock_reddit
        
        # Setup mock response for webhook execution
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_webhook.execute.return_value = self.mock_response
        
        # Setup environment variables for testing
        os.environ['DISCORD_WEBHOOK_URL'] = 'https://example.com/webhook'
        
        # Initialize the service
        self.discord_bot = DiscordBot()
        
        print("✓ Setup complete: Created mock Discord Webhook and Reddit service")
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.webhook_patch.stop()
        self.embed_patch.stop()
        self.reddit_patch.stop()
        
        print("✓ Teardown complete: Stopped all patches")
    
    def test_initialization(self):
        """Test Discord bot initialization."""
        # Verify the webhook URL was set correctly
        self.assertEqual(self.discord_bot.webhook_url, 'https://example.com/webhook')
        
        # Verify the Reddit service was initialized
        self.mock_reddit_class.assert_called_once()
        
        print("✓ Test initialization: Discord bot initialized with correct parameters")
    
    def test_initialization_missing_webhook_url(self):
        """Test initialization with missing webhook URL."""
        # Remove the webhook URL from environment
        del os.environ['DISCORD_WEBHOOK_URL']
        
        # Attempt to create the bot, which should raise an exception
        with self.assertRaises(ValueError) as context:
            discord_bot = DiscordBot()
        
        # Verify the exception message
        self.assertEqual(str(context.exception), "Discord webhook URL is not configured")
        
        print("✓ Test initialization_missing_webhook_url: Correctly raised exception for missing webhook URL")
    
    def test_create_embed(self):
        """Test creating a Discord embed from a post."""
        # Create a sample post
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': 'This is a test post',
            'flair': 'Test Flair'
        }
        
        # Call the function
        result = self.discord_bot.create_embed(post)
        
        # Verify DiscordEmbed was instantiated with the correct parameters
        self.mock_embed_class.assert_called_once_with(
            title="New Post from r/test_subreddit [Test Flair]",
            description="Test Post",
            color='03b2f8'
        )
        
        # Verify embed fields were added
        self.mock_embed.add_embed_field.assert_has_calls([
            call(name="Posted", value="2 hours ago"),
            call(name="URL", value="https://reddit.com/test"),
            call(name="Content", value="This is a test post", inline=False)
        ])
        
        # Verify result
        self.assertEqual(result, self.mock_embed)
        
        print("✓ Test create_embed: Discord embed created with correct content")
    
    def test_create_embed_with_long_text(self):
        """Test creating a Discord embed with very long text."""
        # Create a sample post with long text
        long_text = 'x' * 2000  # Text longer than the 1000 character limit
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': long_text,
            'flair': 'Test Flair'
        }
        
        # Call the function
        result = self.discord_bot.create_embed(post)
        
        # Verify the embed was created
        self.mock_embed_class.assert_called_once()
        
        # Check the content field was truncated
        add_field_calls = self.mock_embed.add_embed_field.call_args_list
        content_call = [call for call in add_field_calls if call[1]['name'] == "Content"][0]
        self.assertLess(len(content_call[1]['value']), 2000)
        self.assertTrue(content_call[1]['value'].endswith('...'))
        
        print("✓ Test create_embed_with_long_text: Long post content correctly truncated")
    
    def test_create_embed_with_no_text(self):
        """Test creating a Discord embed with no text content."""
        # Create a sample post with no text
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': '',
            'flair': 'Test Flair'
        }
        
        # Call the function
        result = self.discord_bot.create_embed(post)
        
        # Verify the embed was created
        self.mock_embed_class.assert_called_once()
        
        # Check the content field was not added
        add_field_calls = self.mock_embed.add_embed_field.call_args_list
        content_calls = [call for call in add_field_calls if call[1]['name'] == "Content"]
        self.assertEqual(len(content_calls), 0)
        
        print("✓ Test create_embed_with_no_text: Empty content field correctly handled")
    
    def test_send_post(self):
        """Test sending a post to Discord."""
        # Create a sample post
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': 'This is a test post',
            'flair': 'Test Flair'
        }
        
        # Create a patch for create_embed
        with patch.object(self.discord_bot, 'create_embed', return_value=self.mock_embed) as mock_create_embed:
            # Call the function
            self.discord_bot.send_post(post)
            
            # Verify create_embed was called with the correct post
            mock_create_embed.assert_called_once_with(post)
            
            # Verify DiscordWebhook was instantiated with the correct URL
            self.mock_webhook_class.assert_called_once_with(url='https://example.com/webhook')
            
            # Verify the embed was added
            self.mock_webhook.add_embed.assert_called_once_with(self.mock_embed)
            
            # Verify execute was called
            self.mock_webhook.execute.assert_called_once()
            
            print("✓ Test send_post: Post correctly sent to Discord")
    
    def test_send_post_error(self):
        """Test sending a post to Discord with an error response."""
        # Create a sample post
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': 'This is a test post',
            'flair': 'Test Flair'
        }
        
        # Override the response status code to simulate an error
        self.mock_response.status_code = 400
        
        # Create a patch for create_embed
        with patch.object(self.discord_bot, 'create_embed', return_value=self.mock_embed) as mock_create_embed:
            # Call the function
            self.discord_bot.send_post(post)
            
            # Verify create_embed was called with the correct post
            mock_create_embed.assert_called_once_with(post)
            
            # Verify DiscordWebhook was instantiated with the correct URL
            self.mock_webhook_class.assert_called_once_with(url='https://example.com/webhook')
            
            # Verify the embed was added
            self.mock_webhook.add_embed.assert_called_once_with(self.mock_embed)
            
            # Verify execute was called
            self.mock_webhook.execute.assert_called_once()
            
            print("✓ Test send_post_error: Error response correctly handled")
    
    def test_process_posts_empty(self):
        """Test processing posts when there are none."""
        # Configure the mock to return empty posts
        self.mock_reddit.get_all_posts.return_value = []
        
        # Call the function
        self.discord_bot.process_posts()
        
        # Verify get_all_posts was called
        self.mock_reddit.get_all_posts.assert_called_once()
        
        # Verify send_post was NOT called (we didn't need to patch it)
        self.webhook_patch.assert_not_called()
        
        print("✓ Test process_posts_empty: No posts sent when no posts available")
    
    def test_process_posts(self):
        """Test processing and sending multiple posts."""
        # Configure the mock to return some posts
        self.mock_reddit.get_all_posts.return_value = [
            [{'id': 'post1', 'title': 'Post 1'}],
            [{'id': 'post2', 'title': 'Post 2'}, {'id': 'post3', 'title': 'Post 3'}]
        ]
        
        # Create a patch for the send_post method
        with patch.object(self.discord_bot, 'send_post') as mock_send_post:
            # Call the function
            self.discord_bot.process_posts()
            
            # Verify get_all_posts was called
            self.mock_reddit.get_all_posts.assert_called_once()
            
            # Verify send_post was called for each post
            self.assertEqual(mock_send_post.call_count, 3)
            mock_send_post.assert_has_calls([
                call({'id': 'post1', 'title': 'Post 1'}),
                call({'id': 'post2', 'title': 'Post 2'}),
                call({'id': 'post3', 'title': 'Post 3'})
            ])
            
            print("✓ Test process_posts: All posts processed and sent correctly")
    
    def test_run(self):
        """Test the run method."""
        # Create a patch for the process_posts method
        with patch.object(self.discord_bot, 'process_posts') as mock_process_posts:
            # Call the function
            self.discord_bot.run()
            
            # Verify process_posts was called
            mock_process_posts.assert_called_once()
            
            print("✓ Test run: Bot successfully executed process_posts")

if __name__ == '__main__':
    unittest.main(verbosity=2) 