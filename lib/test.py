import os

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
    sub_names = os.getenv('SUB_NAMES')
    sub_names_2 = sub_names.split(',')
    for sub_name in sub_names_2:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"test {sub_name} dsadsa")


if __name__ == "__main__":
    main()
