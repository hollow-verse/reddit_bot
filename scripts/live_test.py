#!/usr/bin/env python
"""Live testing script to test each component with real credentials.

This script tests:
1. Reddit API connection
2. MongoDB connection
3. Telegram messaging
4. Discord messaging

Run with:
    poetry run python scripts/live_test.py
"""
import sys
import os
import asyncio
import logging
from datetime import datetime
import json
import re
from dotenv import load_dotenv

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up colorful logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - \033[1;32m%(levelname)s\033[0m - %(message)s' if sys.stdout.isatty() else '%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("LIVE_TEST")

# Function to read .env file directly 
def get_env_value(env_file_path, var_name):
    """Get an environment variable value directly from .env file."""
    if not os.path.exists(env_file_path):
        return None
        
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == var_name:
                        # Remove quotes if present
                        value = value.strip()
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        return value
    return None

# Load environment variables (normal way)
load_dotenv()

# Get environment variables directly from .env for problematic ones
env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
os.environ['REDDIT_CLIENT_ID'] = get_env_value(env_file_path, 'REDDIT_CLIENT_ID') or os.environ.get('REDDIT_CLIENT_ID', '')
os.environ['REDDIT_CLIENT_SECRET'] = get_env_value(env_file_path, 'REDDIT_CLIENT_SECRET') or os.environ.get('REDDIT_CLIENT_SECRET', '')

class LiveTester:
    """Test each component of the bot with real credentials."""
    
    def __init__(self):
        """Initialize the tester."""
        self.results = {
            "reddit_api": False,
            "mongodb": False,
            "telegram": False,
            "discord": False
        }
        self.last_post = None
    
    def test_reddit_api(self):
        """Test connection to Reddit API and post fetching."""
        try:
            logger.info("\033[1;36m=== Testing Reddit API ===\033[0m")
            
            # Check for Reddit credentials
            reddit_client_id = os.environ.get("REDDIT_CLIENT_ID")
            reddit_client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
            reddit_user_agent = os.environ.get("REDDIT_USER_AGENT")
            
            # Log (redacted) values for debugging
            logger.info(f"Reddit Client ID: {reddit_client_id[:3]}...{reddit_client_id[-3:] if reddit_client_id and len(reddit_client_id) > 6 else '[EMPTY]'}")
            logger.info(f"Reddit Client Secret: {reddit_client_secret[:3]}...{reddit_client_secret[-3:] if reddit_client_secret and len(reddit_client_secret) > 6 else '[EMPTY]'}")
            logger.info(f"Reddit User Agent: {reddit_user_agent[:10]}...{reddit_user_agent[-5:] if reddit_user_agent and len(reddit_user_agent) > 15 else reddit_user_agent}")
            
            # Check required environment variables
            required_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT", "SUB_NAMES"]
            self._check_env_vars(required_vars)
            
            # Import here to avoid errors if modules are missing
            import praw
            from src.services.reddit import RedditService
            
            # Test direct PRAW connection
            logger.info("Testing direct PRAW connection...")
            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_client_secret,
                user_agent=reddit_user_agent,
            )
            subreddit_names = os.environ.get("SUB_NAMES", "").split(",")
            if not subreddit_names or subreddit_names[0] == "":
                raise ValueError("SUB_NAMES environment variable is not set")
                
            # Test accessing a subreddit
            logger.info(f"Testing access to subreddit r/{subreddit_names[0]}...")
            subreddit = reddit.subreddit(subreddit_names[0])
            
            # Fetch the newest post
            logger.info("Fetching newest post...")
            posts = list(subreddit.new(limit=1))
            if not posts:
                logger.warning(f"No posts found in r/{subreddit_names[0]}")
            else:
                post = posts[0]
                logger.info(f"Found post: {post.title[:50]}...")
                logger.info(f"Post URL: {post.url}")
                self.last_post = {
                    "id": post.id,
                    "title": post.title,
                    "url": post.url,
                    "selftext": post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext,
                    "subreddit": subreddit_names[0],
                    "posted_ago": "Just now (test)",
                    "flair": post.link_flair_text or "No Flair"
                }
            
            # Test the RedditService
            logger.info("Testing RedditService...")
            # Create a mock MongoDB service to avoid actual DB operations
            from unittest.mock import MagicMock
            mock_mongo_service = MagicMock()
            mock_mongo_service.check_post_exists.return_value = False
            mock_mongo_service.cleanup_collection.return_value = None
            
            # Create the Reddit service with the mock MongoDB service
            reddit_service = RedditService()
            reddit_service.mongo_service = mock_mongo_service
            
            # Get posts from the first subreddit
            posts = reddit_service.get_filtered_posts(subreddit_names[0])
            logger.info(f"RedditService found {len(posts)} new posts")
            
            logger.info("\033[1;32m✓ Reddit API test passed!\033[0m")
            self.results["reddit_api"] = True
            return True
            
        except Exception as e:
            logger.error(f"\033[1;31m✗ Reddit API test failed: {str(e)}\033[0m")
            logger.exception(e)
            return False
    
    def test_mongodb(self):
        """Test connection to MongoDB and basic operations."""
        try:
            logger.info("\033[1;36m=== Testing MongoDB Connection ===\033[0m")
            
            # Check required environment variables
            required_vars = ["MONGO_USER", "MONGO_PASSWORD", "MONGO_URI", "MONGO_DB_NAME"]
            self._check_env_vars(required_vars)
            
            # Import here to avoid errors if modules are missing
            from src.services.mongodb import MongoDBService
            
            # Create MongoDB service
            logger.info("Connecting to MongoDB...")
            mongo_service = MongoDBService()
            
            # Test collection access with a test collection
            test_collection = "test_collection"
            logger.info(f"Testing collection access: {test_collection}")
            
            # Test insert
            test_id = f"test_{datetime.now().timestamp()}"
            logger.info(f"Inserting test document with ID: {test_id}")
            mongo_service.insert_post(test_id, test_collection)
            
            # Test exists check
            logger.info(f"Checking if document exists...")
            exists = mongo_service.check_post_exists(test_id, test_collection)
            if not exists:
                raise ValueError(f"Document with ID {test_id} was not found after insertion")
            
            # Test cleanup
            logger.info(f"Testing collection cleanup...")
            mongo_service.cleanup_collection(test_collection, max_documents=0)  # Remove all documents
            
            # Verify cleanup
            exists = mongo_service.check_post_exists(test_id, test_collection)
            if exists:
                logger.warning(f"Document with ID {test_id} still exists after cleanup")
            
            logger.info("\033[1;32m✓ MongoDB test passed!\033[0m")
            self.results["mongodb"] = True
            return True
            
        except Exception as e:
            logger.error(f"\033[1;31m✗ MongoDB test failed: {str(e)}\033[0m")
            logger.exception(e)
            return False
    
    async def test_telegram(self):
        """Test sending a message to Telegram."""
        try:
            logger.info("\033[1;36m=== Testing Telegram Messaging ===\033[0m")
            
            # Check required environment variables
            required_vars = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
            self._check_env_vars(required_vars)
            
            # Import here to avoid errors if modules are missing
            from telegram import Bot
            
            # Create Telegram bot
            token = os.environ.get("TELEGRAM_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            logger.info(f"Initializing Telegram bot with token: {token[:5]}...{token[-5:]}")
            
            bot = Bot(token=token)
            
            # Send a test message
            logger.info(f"Sending test message to chat ID: {chat_id}")
            test_message = f"🧪 Test message from Reddit Bot at {datetime.now()}"
            
            message = await bot.send_message(
                chat_id=chat_id,
                text=test_message,
                disable_notification=True  # Don't send a notification
            )
            
            logger.info(f"Test message sent successfully: {message.message_id}")
            
            # Test sending a post if we have one
            if self.last_post:
                logger.info("Sending a test post to Telegram...")
                post_message = f"""
*Test Post from r/{self.last_post['subreddit']}* [{self.last_post['flair']}]
*Title:* {self.last_post['title']}
*Posted:* {self.last_post['posted_ago']}
*URL:* {self.last_post['url']}

{self.last_post['selftext']}
                """
                
                post_sent = await bot.send_message(
                    chat_id=chat_id,
                    text=post_message,
                    parse_mode="Markdown",
                    disable_notification=True
                )
                
                logger.info(f"Test post sent successfully: {post_sent.message_id}")
            
            logger.info("\033[1;32m✓ Telegram test passed!\033[0m")
            self.results["telegram"] = True
            return True
            
        except Exception as e:
            logger.error(f"\033[1;31m✗ Telegram test failed: {str(e)}\033[0m")
            logger.exception(e)
            return False
    
    def test_discord(self):
        """Test sending a message to Discord."""
        try:
            logger.info("\033[1;36m=== Testing Discord Webhook ===\033[0m")
            
            # Check required environment variables
            required_vars = ["DISCORD_WEBHOOK_URL"]
            self._check_env_vars(required_vars)
            
            # Import here to avoid errors if modules are missing
            from discord_webhook import DiscordWebhook, DiscordEmbed
            
            # Get webhook URL
            webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
            logger.info(f"Using webhook URL: {webhook_url[:20]}...{webhook_url[-20:] if len(webhook_url) > 40 else webhook_url}")
            
            # Create a basic webhook
            logger.info("Sending basic test message...")
            test_message = f"🧪 Test message from Reddit Bot at {datetime.now()}"
            webhook = DiscordWebhook(url=webhook_url, content=test_message)
            response = webhook.execute()
            
            if response.status_code not in (200, 204):
                raise ValueError(f"Discord webhook failed with status code {response.status_code}")
            
            logger.info(f"Basic test message sent successfully")
            
            # Test sending a post with an embed if we have one
            if self.last_post:
                logger.info("Sending a test post with embed to Discord...")
                
                webhook = DiscordWebhook(url=webhook_url)
                embed = DiscordEmbed(
                    title=f"Test Post from r/{self.last_post['subreddit']} [{self.last_post['flair']}]",
                    description=self.last_post['title'],
                    color="03b2f8"
                )
                
                embed.add_embed_field(name="Posted", value=self.last_post['posted_ago'])
                embed.add_embed_field(name="URL", value=self.last_post['url'])
                
                if self.last_post['selftext']:
                    text = self.last_post['selftext']
                    text = text[:997] + "..." if len(text) > 1000 else text
                    embed.add_embed_field(name="Content", value=text, inline=False)
                
                webhook.add_embed(embed)
                response = webhook.execute()
                
                if response.status_code not in (200, 204):
                    raise ValueError(f"Discord webhook embed failed with status code {response.status_code}")
                
                logger.info(f"Test post with embed sent successfully")
            
            logger.info("\033[1;32m✓ Discord test passed!\033[0m")
            self.results["discord"] = True
            return True
            
        except Exception as e:
            logger.error(f"\033[1;31m✗ Discord test failed: {str(e)}\033[0m")
            logger.exception(e)
            return False
    
    def _check_env_vars(self, required_vars):
        """Check if required environment variables are set."""
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def print_summary(self):
        """Print a summary of the test results."""
        print("\n" + "=" * 50)
        print("\033[1;36mTEST SUMMARY\033[0m")
        print("=" * 50)
        
        for component, result in self.results.items():
            status = "\033[1;32m✓ PASS\033[0m" if result else "\033[1;31m✗ FAIL\033[0m"
            print(f"{component.ljust(15)}: {status}")
        
        print("=" * 50)

async def main():
    """Run the live tests."""
    logger.info("Starting live testing of Reddit Bot components")
    
    tester = LiveTester()
    
    # Test Reddit API
    tester.test_reddit_api()
    
    # Test MongoDB
    tester.test_mongodb()
    
    # Test Telegram
    await tester.test_telegram()
    
    # Test Discord
    tester.test_discord()
    
    # Print summary
    tester.print_summary()

# Entry point for running directly as a script
def run_main():
    """Entry point for running the script directly or via Poetry."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

if __name__ == "__main__":
    run_main() 