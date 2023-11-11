# Description: This file contains the Telegram Bot logic
from telegram import Bot
from utils import get_all_posts
import os

# Define your constants
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID =  os.environ.get('TELEGRAM_CHAT_ID')

def main():
    # Initialize the Telegram Bot
    bot = Bot(token=TELEGRAM_TOKEN)

    # Get filtered subreddit posts
    filtered_sub_posts = get_all_posts()

    # Loop through the posts and send each one to Telegram
    for posts in filtered_sub_posts:
        for post in posts:
            send_post_to_telegram(bot, post, TELEGRAM_CHAT_ID)

def send_post_to_telegram(bot, post, chat_id):
    subreddit = post.get('subreddit', 'Null')
    title = post.get('title', 'Null')
    posted_ago = f"{post.get('posted_ago', 'Null')} hours"
    url = post.get('url', 'Null')
    text = post.get('selftext', 'Null')

    msg = f"""
        Subreddit: {subreddit}
        Title: {title}
        Posted Ago: {posted_ago}
        URL: {url}
        Text: {text}
    """
    
    bot.send_message(chat_id=chat_id, text=msg)

if __name__ == "__main__":
    main()
