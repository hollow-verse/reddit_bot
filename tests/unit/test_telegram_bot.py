"""Unit tests for the Telegram bot."""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call
import os
import sys
import logging
import asyncio
from typing import Dict, Any

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bots.telegram import TelegramBot

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestTelegramBot(unittest.TestCase):
    """Test cases for the Telegram bot."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create patches for external dependencies
        self.bot_patch = patch('src.bots.telegram.Bot')
        self.reddit_patch = patch('src.bots.telegram.RedditService')
        
        # Start patches
        self.mock_bot_class = self.bot_patch.start()
        self.mock_reddit_class = self.reddit_patch.start()
        
        # Create mock objects
        self.mock_bot = AsyncMock()
        self.mock_bot_class.return_value = self.mock_bot
        
        self.mock_reddit = MagicMock()
        self.mock_reddit_class.return_value = self.mock_reddit
        
        # Setup environment variables for testing
        os.environ['TELEGRAM_TOKEN'] = 'test_token'
        os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
        
        # Initialize the service
        self.telegram_bot = TelegramBot()
        
        print("✓ Setup complete: Created mock Telegram Bot and Reddit service")
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.bot_patch.stop()
        self.reddit_patch.stop()
        
        print("✓ Teardown complete: Stopped all patches")
    
    def test_initialization(self):
        """Test Telegram bot initialization."""
        # Verify the Bot class was initialized with the correct token
        self.mock_bot_class.assert_called_once_with(token='test_token')
        
        # Verify the chat ID was set correctly
        self.assertEqual(self.telegram_bot.chat_id, 'test_chat_id')
        
        # Verify the Reddit service was initialized
        self.mock_reddit_class.assert_called_once()
        
        print("✓ Test initialization: Telegram bot initialized with correct parameters")
    
    def test_initialization_missing_token(self):
        """Test initialization with missing token."""
        # Remove the token from environment
        del os.environ['TELEGRAM_TOKEN']
        
        # Attempt to create the bot, which should raise an exception
        with self.assertRaises(ValueError) as context:
            telegram_bot = TelegramBot()
        
        # Verify the exception message
        self.assertEqual(str(context.exception), "Telegram bot token is not configured")
        
        print("✓ Test initialization_missing_token: Correctly raised exception for missing token")
    
    def test_initialization_missing_chat_id(self):
        """Test initialization with missing chat ID."""
        # Remove the chat ID from environment
        del os.environ['TELEGRAM_CHAT_ID']
        
        # Attempt to create the bot, which should raise an exception
        with self.assertRaises(ValueError) as context:
            telegram_bot = TelegramBot()
        
        # Verify the exception message
        self.assertEqual(str(context.exception), "Telegram chat ID is not configured")
        
        print("✓ Test initialization_missing_chat_id: Correctly raised exception for missing chat ID")
    
    async def test_send_post(self):
        """Test sending a post to Telegram."""
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
        await self.telegram_bot.send_post(post)
        
        # Verify send_message was called with the correct parameters
        self.mock_bot.send_message.assert_called_once()
        call_args = self.mock_bot.send_message.call_args
        
        # Check the call parameters
        self.assertEqual(call_args[1]['chat_id'], 'test_chat_id')
        self.assertIn('test_subreddit', call_args[1]['text'])
        self.assertIn('Test Post', call_args[1]['text'])
        self.assertIn('2 hours ago', call_args[1]['text'])
        self.assertIn('https://reddit.com/test', call_args[1]['text'])
        self.assertIn('This is a test post', call_args[1]['text'])
        self.assertIn('Test Flair', call_args[1]['text'])
        self.assertEqual(call_args[1]['parse_mode'], 'Markdown')
        
        print("✓ Test send_post: Post correctly sent to Telegram")
    
    async def test_send_post_with_long_text(self):
        """Test sending a post with very long text to Telegram."""
        # Create a sample post with long text
        long_text = 'x' * 5000  # Text longer than the 3000 character limit
        post = {
            'subreddit': 'test_subreddit',
            'title': 'Test Post',
            'posted_ago': '2 hours ago',
            'url': 'https://reddit.com/test',
            'selftext': long_text,
            'flair': 'Test Flair'
        }
        
        # Call the function
        await self.telegram_bot.send_post(post)
        
        # Verify send_message was called with the correct parameters
        self.mock_bot.send_message.assert_called_once()
        call_args = self.mock_bot.send_message.call_args
        
        # Check the text was truncated
        self.assertLess(len(call_args[1]['text']), 5000)
        self.assertIn('...', call_args[1]['text'])  # Should include ellipsis
        
        print("✓ Test send_post_with_long_text: Long post text correctly truncated")
    
    async def test_process_posts_empty(self):
        """Test processing posts when there are none."""
        # Configure the mock to return empty posts
        self.mock_reddit.get_all_posts.return_value = []
        
        # Call the function
        await self.telegram_bot.process_posts()
        
        # Verify get_all_posts was called
        self.mock_reddit.get_all_posts.assert_called_once()
        
        # Verify send_post was NOT called
        self.assertEqual(self.mock_bot.send_message.call_count, 0)
        
        print("✓ Test process_posts_empty: No posts sent when no posts available")
    
    async def test_process_posts(self):
        """Test processing and sending multiple posts."""
        # Configure the mock to return some posts
        self.mock_reddit.get_all_posts.return_value = [
            [{'id': 'post1', 'title': 'Post 1'}],
            [{'id': 'post2', 'title': 'Post 2'}, {'id': 'post3', 'title': 'Post 3'}]
        ]
        
        # Create a patch for the send_post method
        with patch.object(self.telegram_bot, 'send_post', new_callable=AsyncMock) as mock_send_post:
            # Call the function
            await self.telegram_bot.process_posts()
            
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
        """Test the run method using an event loop."""
        # Create a patch for asyncio.get_event_loop
        with patch('src.bots.telegram.asyncio.get_event_loop') as mock_get_loop:
            # Create a mock event loop
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            
            # Create a patch for the process_posts method
            with patch.object(self.telegram_bot, 'process_posts', new_callable=AsyncMock) as mock_process_posts:
                # Call the function
                self.telegram_bot.run()
                
                # Verify get_event_loop was called
                mock_get_loop.assert_called_once()
                
                # Verify run_until_complete was called with the process_posts coroutine
                mock_loop.run_until_complete.assert_called_once()
                
                # Verify close was called
                mock_loop.close.assert_called_once()
                
                print("✓ Test run: Event loop correctly created, used, and closed")

# Run the async tests
def run_async_test(coro):
    """Run an async test using asyncio."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)

# Replace the test methods with wrapped versions
for name in dir(TestTelegramBot):
    if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestTelegramBot, name)):
        method = getattr(TestTelegramBot, name)
        setattr(TestTelegramBot, name, lambda self, method=method: run_async_test(method(self)))

if __name__ == '__main__':
    unittest.main(verbosity=2) 