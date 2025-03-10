"""Integration tests for sending posts to Telegram and Discord."""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys
import logging
import asyncio
from typing import Dict, Any, List

# Configure path to import modules from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.bots.telegram import TelegramBot
from src.bots.discord import DiscordBot
from src.services.reddit import RedditService

# Create more verbose output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSendingIntegration(unittest.TestCase):
    """Integration tests for sending posts to messaging platforms."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Setup environment variables for testing
        os.environ['TELEGRAM_TOKEN'] = 'test_telegram_token'
        os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
        os.environ['DISCORD_WEBHOOK_URL'] = 'https://example.com/webhook'
        
        # Create mocks for external services
        self.setup_mocks()
        
        # Create sample posts for testing
        self.sample_posts = self.create_sample_posts()
        
        logger.info("✓ Integration test setup complete")
    
    def setup_mocks(self):
        """Set up mock objects for external services."""
        # Create patches for external dependencies
        self.telegram_bot_patch = patch('src.bots.telegram.Bot')
        self.discord_webhook_patch = patch('src.bots.discord.DiscordWebhook')
        self.discord_embed_patch = patch('src.bots.discord.DiscordEmbed')
        self.reddit_patch = patch('src.bots.telegram.RedditService')
        
        # Start patches
        self.mock_telegram_bot = self.telegram_bot_patch.start()
        self.mock_discord_webhook = self.discord_webhook_patch.start()
        self.mock_discord_embed = self.discord_embed_patch.start()
        self.mock_reddit = self.reddit_patch.start()
        
        # Configure mock bot instances
        self.mock_telegram_instance = AsyncMock()
        self.mock_telegram_bot.return_value = self.mock_telegram_instance
        
        self.mock_webhook_instance = MagicMock()
        self.mock_discord_webhook.return_value = self.mock_webhook_instance
        
        self.mock_embed_instance = MagicMock()
        self.mock_discord_embed.return_value = self.mock_embed_instance
        
        # Configure mock webhook response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_webhook_instance.execute.return_value = self.mock_response
        
        # Configure mock Reddit service
        self.mock_reddit_instance = MagicMock()
        self.mock_reddit.return_value = self.mock_reddit_instance
        self.mock_reddit_instance.get_all_posts.return_value = [self.sample_posts]
        
        logger.info("✓ Mocks configured for integration testing")
    
    def create_sample_posts(self):
        """Create a list of sample posts for testing."""
        return [
            {
                'id': 'test_post_1',
                'subreddit': 'python',
                'title': 'Test Post 1',
                'posted_ago': '2 hours ago',
                'url': 'https://reddit.com/r/python/test_post_1',
                'selftext': 'This is a test post 1 content',
                'flair': 'Discussion'
            },
            {
                'id': 'test_post_2',
                'subreddit': 'programming',
                'title': 'Test Post 2',
                'posted_ago': '1 hour ago',
                'url': 'https://reddit.com/r/programming/test_post_2',
                'selftext': 'This is a test post 2 content with longer text that might need truncation in some scenarios. ' * 10,
                'flair': 'Help'
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.telegram_bot_patch.stop()
        self.discord_webhook_patch.stop()
        self.discord_embed_patch.stop()
        self.reddit_patch.stop()
        
        logger.info("✓ Integration test teardown complete")
    
    async def test_telegram_send_post(self):
        """Test sending a post to Telegram."""
        # Initialize the Telegram bot
        telegram_bot = TelegramBot()
        
        # Call the function with our sample post
        await telegram_bot.send_post(self.sample_posts[0])
        
        # Verify send_message was called
        self.mock_telegram_instance.send_message.assert_called_once()
        
        # Check the call parameters
        call_args = self.mock_telegram_instance.send_message.call_args[1]
        self.assertEqual(call_args['chat_id'], 'test_chat_id')
        self.assertIn('python', call_args['text'])
        self.assertIn('Test Post 1', call_args['text'])
        self.assertIn('2 hours ago', call_args['text'])
        self.assertIn('https://reddit.com/r/python/test_post_1', call_args['text'])
        
        logger.info("✓ Successfully sent post to Telegram")
    
    async def test_telegram_process_posts(self):
        """Test processing and sending all posts to Telegram."""
        # Initialize the Telegram bot
        telegram_bot = TelegramBot()
        
        # Call the function
        await telegram_bot.process_posts()
        
        # Verify get_all_posts was called on the Reddit service
        self.mock_reddit_instance.get_all_posts.assert_called_once()
        
        # Verify send_message was called for each post
        self.assertEqual(self.mock_telegram_instance.send_message.call_count, 2)
        
        logger.info("✓ Successfully processed and sent all posts to Telegram")
    
    def test_discord_create_embed(self):
        """Test creating a Discord embed from a post."""
        # Initialize the Discord bot
        discord_bot = DiscordBot()
        
        # Call the function
        discord_bot.create_embed(self.sample_posts[0])
        
        # Verify DiscordEmbed was initialized with the correct parameters
        self.mock_discord_embed.assert_called_once_with(
            title="New Post from r/python [Discussion]",
            description="Test Post 1",
            color='03b2f8'
        )
        
        # Verify embed fields were added
        self.mock_embed_instance.add_embed_field.assert_any_call(name="Posted", value="2 hours ago")
        self.mock_embed_instance.add_embed_field.assert_any_call(name="URL", value="https://reddit.com/r/python/test_post_1")
        
        logger.info("✓ Successfully created Discord embed")
    
    def test_discord_send_post(self):
        """Test sending a post to Discord."""
        # Initialize the Discord bot
        discord_bot = DiscordBot()
        
        # Call the function
        discord_bot.send_post(self.sample_posts[0])
        
        # Verify DiscordWebhook was instantiated with the correct URL
        self.mock_discord_webhook.assert_called_once_with(url='https://example.com/webhook')
        
        # Verify the embed was added
        self.mock_webhook_instance.add_embed.assert_called_once()
        
        # Verify execute was called
        self.mock_webhook_instance.execute.assert_called_once()
        
        logger.info("✓ Successfully sent post to Discord")
    
    def test_discord_process_posts(self):
        """Test processing and sending all posts to Discord."""
        # Initialize the Discord bot
        discord_bot = DiscordBot()
        
        # Call the function
        discord_bot.process_posts()
        
        # Verify get_all_posts was called on the Reddit service
        self.mock_reddit_instance.get_all_posts.assert_called_once()
        
        # Verify Discord webhook was instantiated twice (once for each post)
        self.assertEqual(self.mock_discord_webhook.call_count, 2)
        
        # Verify execute was called for each post
        self.assertEqual(self.mock_webhook_instance.execute.call_count, 2)
        
        logger.info("✓ Successfully processed and sent all posts to Discord")
    
    def test_end_to_end_sending_flow(self):
        """Test the complete flow from getting posts to sending them to both platforms."""
        # Mock the Reddit service to return some posts
        reddit_service = MagicMock()
        reddit_service.get_all_posts.return_value = [self.sample_posts]
        
        # Initialize both bots with the mocked Reddit service
        with patch('src.bots.telegram.RedditService', return_value=reddit_service), \
             patch('src.bots.discord.RedditService', return_value=reddit_service):
            
            # Discord bot test
            discord_bot = DiscordBot()
            discord_bot.process_posts()
            
            # Verify Discord webhook execution
            self.assertEqual(self.mock_webhook_instance.execute.call_count, 2)
            
            # Create a mock for asyncio.get_event_loop
            with patch('src.bots.telegram.asyncio.get_event_loop') as mock_get_loop:
                # Create mock loop and run_until_complete
                mock_loop = MagicMock()
                mock_get_loop.return_value = mock_loop
                
                # Create a mock for the process_posts method result
                mock_process_posts_result = AsyncMock()
                
                # Run the Telegram bot
                with patch.object(TelegramBot, 'process_posts', return_value=mock_process_posts_result):
                    telegram_bot = TelegramBot()
                    telegram_bot.run()
                    
                    # Verify the event loop was used
                    mock_loop.run_until_complete.assert_called_once()
        
        logger.info("✓ Successfully tested end-to-end sending flow")

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
for name in dir(TestSendingIntegration):
    if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestSendingIntegration, name)):
        method = getattr(TestSendingIntegration, name)
        setattr(TestSendingIntegration, name, lambda self, method=method: run_async_test(method(self)))

if __name__ == '__main__':
    unittest.main(verbosity=2) 