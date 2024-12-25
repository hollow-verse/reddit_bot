from discord_webhook import DiscordWebhook, DiscordEmbed
from utils import get_all_posts
import os

def send_post_to_discord(post):
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    webhook = DiscordWebhook(url=webhook_url)
    
    subreddit = post.get('subreddit', 'Null')
    title = post.get('title', 'Null')
    posted_ago = post.get('posted_ago', 'Null')
    url = post.get('url', 'Null')
    text = post.get('selftext', 'Null')

    # Create embed
    embed = DiscordEmbed(
        title=f"New Post from r/{subreddit}",
        description=title,
        color='03b2f8'
    )
    
    embed.add_embed_field(name="Posted", value=posted_ago)
    embed.add_embed_field(name="URL", value=url)
    
    # Split text into chunks if it's too long
    if len(text) > 1000:
        text = text[:997] + "..."
    
    if text and text != 'Null':
        embed.add_embed_field(name="Content", value=text, inline=False)
    
    webhook.add_embed(embed)
    webhook.execute()

def main():
    filtered_sub_posts = get_all_posts()
    
    # Loop through all posts and send to Discord
    for posts in filtered_sub_posts:
        for post in posts:
            send_post_to_discord(post)

if __name__ == "__main__":
    main()
