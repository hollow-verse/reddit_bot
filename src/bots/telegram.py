"""Telegram bot for sending Reddit posts to a channel."""
from telegram import Bot
import asyncio
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.services.reddit import RedditService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot for sending Reddit posts to a channel."""
    
    def __init__(self):
        """Initialize the Telegram bot."""
        self.token = os.environ.get('TELEGRAM_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID', os.environ.get('TELEGRAM_CHAT'))
        
        if not self.token:
            raise ValueError("Telegram bot token is not configured")
        if not self.chat_id:
            raise ValueError("Telegram chat ID is not configured")
        
        self.bot = Bot(token=self.token)
        self.reddit_service = RedditService()
    
    async def send_post(self, post: Dict[str, Any]) -> None:
        """Send a post to Telegram channel."""
        try:
            subreddit = post.get('subreddit', 'Unknown')
            title = post.get('title', 'No Title')
            posted_ago = post.get('posted_ago', 'Unknown')
            url = post.get('url', 'No URL')
            text = post.get('selftext', '')
            flair = post.get('flair', 'No Flair')
            
            # Format the message
            message = f"""
*New Post from r/{subreddit}* [{flair}]
*Title:* {title}
*Posted:* {posted_ago}
*URL:* {url}

{text[:3000] + '...' if len(text) > 3000 else text}
            """
            
            await self.bot.send_message(
                chat_id=self.chat_id, 
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            
            logger.info(f"Sent post '{title}' to Telegram channel")
        
        except Exception as e:
            logger.error(f"Failed to send post to Telegram: {str(e)}")
    
    async def process_posts(self) -> None:
        """Process and send all posts to Telegram."""
        try:
            filtered_posts = self.reddit_service.get_all_posts()
            
            # Count total posts
            total_posts = sum(len(posts) for posts in filtered_posts)
            if total_posts == 0:
                logger.info("No new posts to send to Telegram")
                return
            
            logger.info(f"Sending {total_posts} posts to Telegram")
            
            # Process each post
            for posts in filtered_posts:
                for post in posts:
                    await self.send_post(post)
                    # Add a delay between posts to avoid rate limiting
                    await asyncio.sleep(1)
        
        except Exception as e:
            logger.error(f"Error processing posts for Telegram: {str(e)}")
    
    def run(self) -> None:
        """Run the Telegram bot."""
        try:
            logger.info("Starting Telegram bot")
            
            # Create and run the event loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.process_posts())
            
            logger.info("Telegram bot completed successfully")
        
        except Exception as e:
            logger.error(f"Telegram bot failed: {str(e)}")
        
        finally:
            # Close the event loop
            try:
                loop = asyncio.get_event_loop()
                loop.close()
            except:
                pass 