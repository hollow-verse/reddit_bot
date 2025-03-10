"""Discord bot for sending Reddit posts to a channel."""
from discord_webhook import DiscordWebhook, DiscordEmbed
import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

from src.services.reddit import RedditService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DiscordBot:
    """Discord bot for sending Reddit posts to a channel."""
    
    def __init__(self):
        """Initialize the Discord bot."""
        self.webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        
        if not self.webhook_url:
            raise ValueError("Discord webhook URL is not configured")
        
        self.reddit_service = RedditService()
    
    def create_embed(self, post: Dict[str, Any]) -> DiscordEmbed:
        """Create a Discord embed from a post."""
        try:
            subreddit = post.get('subreddit', 'Unknown')
            title = post.get('title', 'No Title')
            posted_ago = post.get('posted_ago', 'Unknown')
            url = post.get('url', '#')
            text = post.get('selftext', '')
            flair = post.get('flair', 'No Flair')
            
            embed = DiscordEmbed(
                title=f"New Post from r/{subreddit} [{flair}]",
                description=title,
                color='03b2f8'
            )
            
            embed.add_embed_field(name="Posted", value=posted_ago)
            embed.add_embed_field(name="URL", value=url)
            
            if text and text != 'Null':
                # Truncate long text
                text = text[:997] + "..." if len(text) > 1000 else text
                embed.add_embed_field(name="Content", value=text, inline=False)
            
            return embed
        
        except Exception as e:
            logger.error(f"Failed to create Discord embed: {str(e)}")
            raise
    
    def send_post(self, post: Dict[str, Any]) -> None:
        """Send a post to Discord using webhooks."""
        try:
            webhook = DiscordWebhook(url=self.webhook_url)
            embed = self.create_embed(post)
            webhook.add_embed(embed)
            
            # Execute the webhook
            response = webhook.execute()
            
            if response.status_code not in (200, 204):
                logger.error(f"Discord webhook failed with status {response.status_code}")
            else:
                logger.info(f"Sent post '{post.get('title', 'Unknown')}' to Discord channel")
        
        except Exception as e:
            logger.error(f"Failed to send post to Discord: {str(e)}")
    
    def process_posts(self) -> None:
        """Process and send all posts to Discord."""
        try:
            filtered_posts = self.reddit_service.get_all_posts()
            
            # Count total posts
            total_posts = sum(len(posts) for posts in filtered_posts)
            if total_posts == 0:
                logger.info("No new posts to send to Discord")
                return
            
            logger.info(f"Sending {total_posts} posts to Discord")
            
            # Process each post
            for posts in filtered_posts:
                for post in posts:
                    self.send_post(post)
        
        except Exception as e:
            logger.error(f"Error processing posts for Discord: {str(e)}")
    
    def run(self) -> None:
        """Run the Discord bot."""
        try:
            logger.info("Starting Discord bot")
            self.process_posts()
            logger.info("Discord bot completed successfully")
        
        except Exception as e:
            logger.error(f"Discord bot failed: {str(e)}")
            raise 