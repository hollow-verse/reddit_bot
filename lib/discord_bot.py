from discord_webhook import DiscordWebhook, DiscordEmbed
from .utils import get_all_posts  # Changed to relative import
import os
from typing import Dict, Any, List
from logging import getLogger

logger = getLogger(__name__)

def create_embed(post: Dict[str, str]) -> DiscordEmbed:
    """Create a Discord embed from a post."""
    subreddit = post.get('subreddit', 'Unknown')
    title = post.get('title', 'No Title')
    posted_ago = post.get('posted_ago', 'Unknown')
    url = post.get('url', '#')
    text = post.get('selftext', '')

    embed = DiscordEmbed(
        title=f"New Post from r/{subreddit}",
        description=title,
        color='03b2f8'
    )
    
    embed.add_embed_field(name="Posted", value=posted_ago)
    embed.add_embed_field(name="URL", value=url)
    
    if text and text != 'Null':
        text = text[:997] + "..." if len(text) > 1000 else text
        embed.add_embed_field(name="Content", value=text, inline=False)
    
    return embed

def send_post_to_discord(post: Dict[str, str]) -> None:
    """Send a post to Discord using webhooks."""
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("Discord webhook URL not configured")

    try:
        webhook = DiscordWebhook(url=webhook_url)
        embed = create_embed(post)
        webhook.add_embed(embed)
        response = webhook.execute()
        
        if response.status_code not in (200, 204):
            logger.error(f"Discord webhook failed with status {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending Discord message: {str(e)}")
        raise

def main() -> None:
    try:
        filtered_sub_posts = get_all_posts()
        for posts in filtered_sub_posts:
            for post in posts:
                send_post_to_discord(post)
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
