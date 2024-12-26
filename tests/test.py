# Description: This file contains the Telegram Bot logic
from telegram import Bot
from utils import get_all_posts
import os
from typing import List

def main() -> None:
    try:
        VALID_FLAIRS = os.getenv('VALID_FLAIRS', 'Hiring,Hiring - Open,Task').split(',')
        sub_names = os.getenv('SUB_NAMES', '').split(',')
        
        if not sub_names or sub_names[0] == '':
            raise ValueError("No subreddit names configured")
            
        print(f"Monitoring subreddits: {sub_names}")
        print(f"Valid flairs: {VALID_FLAIRS}")
        
        if 'Task' in VALID_FLAIRS:
            get_all_posts()
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
