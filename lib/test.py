# Description: This file contains the Telegram Bot logic
from telegram import Bot
from utils import get_all_posts
import os

def main():
    VALID_FLIAR_TEXT = 'Hiring,Hiring - Open,Task'.split(',')
    sub_names = os.getenv('SUB_NAMES', '[]').split(',')
    print(sub_names)
    print(VALID_FLIAR_TEXT)
    if 'Task' in VALID_FLIAR_TEXT:
        get_all_posts()
   

if __name__ == "__main__":
    main()
