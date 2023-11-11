# Description: This file contains the Telegram Bot logic
from telegram import Bot
from utils import get_all_posts
import os

# Define your constants
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID =  os.environ.get('TELEGRAM_CHAT_ID')
VALID_FLIAR_TEXT = os.environ.get('VALID_FLIAR_TEXT')

def main():
    # Initialize the Telegram Bot
    print(VALID_FLIAR_TEXT)
    valid_flair_texts = VALID_FLIAR_TEXT.split(',')

    if 'Task' in valid_flair_texts:
        print('Task is present')

if __name__ == "__main__":
    main()
