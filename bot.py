from telegram import Bot
import config
from utils import get_all_posts

token = config.telegram['token']
chat_id = config.telegram['chat_id']

bot = Bot(token=token)

def tele_send_text(posts, chat_id):
    for post in posts:
        msg = f"""
            Subreddit: {post.get('subreddit', 'Null')} \n
            Title: {post.get('title', 'Null')} \n
            Posted Ago: {post.get('posted_ago', 'Null')} hours \n
            Url: {post.get('url', 'Null')} \n
            Text: {post.get('selftext', 'Null')}
            """
        bot.send_message(chat_id=chat_id, text=msg)

filtered_sub_posts = get_all_posts()

for sub_post in filtered_sub_posts:
    tele_send_text(sub_post, chat_id)

