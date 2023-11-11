# Description: This file contains the Telegram Bot logic
from telegram import Bot
from utils import get_all_posts
import os

# Define your constants
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID =  os.environ.get('TELEGRAM_CHAT_ID')


def main():
    # VALID_FLIAR_TEXT = os.environ.get('VALID_FLIAR_TEXT').split(',')
    sub_names = os.getenv('SUB_NAMES', '[]').split(',')
    # Initialize the Telegram Bot
    print(sub_names)
    # print(VALID_FLIAR_TEXT)
   

if __name__ == "__main__":
    main()
