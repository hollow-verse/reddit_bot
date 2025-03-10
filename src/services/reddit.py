"""Reddit service for fetching posts from subreddits."""
import praw
import pytz
from datetime import datetime
import logging
import os
from typing import Dict, Any, List
import sys
from dotenv import load_dotenv

from src.services.mongodb import MongoDBService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RedditService:
    """Service for interacting with Reddit API."""
    
    def __init__(self):
        """Initialize the Reddit client and MongoDB service."""
        self.reddit = self._create_client()
        self.mongo_service = MongoDBService()
    
    def _create_client(self):
        """Create a Reddit client."""
        try:
            reddit = praw.Reddit(
                client_id=os.environ.get("REDDIT_CLIENT_ID"),
                client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
                user_agent=os.environ.get("REDDIT_USER_AGENT"),
            )
            logger.info("Connected to Reddit API")
            return reddit
        except Exception as e:
            logger.error(f"Failed to create Reddit client: {e}")
            raise
    
    def calculate_time_difference(self, utc_timestamp: float) -> str:
        """Calculate time difference between post creation and now."""
        utc_tz = pytz.utc
        utc_dt = datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=utc_tz)
        ist_tz = pytz.timezone("Asia/Kolkata")
        ist_dt = utc_dt.astimezone(ist_tz)
        now_dt = datetime.now(ist_tz)
        total_seconds_passed = (now_dt - ist_dt).total_seconds()
        minutes_passed = total_seconds_passed / 60

        if minutes_passed >= 60:
            hours_passed = minutes_passed / 60
            return f"{hours_passed:.2f} hours (created {ist_dt.strftime('%Y/%m/%d-%H:%M')})"
        else:
            return f"{minutes_passed:.2f} minutes (created {ist_dt.strftime('%Y/%m/%d-%H:%M')})"
    
    def get_filtered_posts(self, subreddit_name: str) -> List[Dict[str, Any]]:
        """Get filtered posts from a subreddit."""
        try:
            VALID_FLAIRS = os.getenv('VALID_FLAIRS', '').split(',')
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Clean up old post IDs
            self.mongo_service.cleanup_collection(subreddit_name)
            
            filtered_posts = []
            for post in subreddit.new(limit=20):
                # If VALID_FLAIRS is empty or post flair matches
                if not VALID_FLAIRS or VALID_FLAIRS[0] == '' or post.link_flair_text in VALID_FLAIRS:
                    # Skip if post already exists
                    if self.mongo_service.check_post_exists(post.id, subreddit_name):
                        continue
                    
                    # Add post data
                    posted_ago = self.calculate_time_difference(post.created_utc)
                    post_dict = {
                        "id": post.id,
                        "posted_ago": posted_ago,
                        "title": post.title,
                        "url": post.url,
                        "selftext": post.selftext,
                        "subreddit": subreddit_name,
                        "flair": post.link_flair_text
                    }
                    
                    # Save post ID and add to results
                    self.mongo_service.insert_post(post.id, subreddit_name)
                    filtered_posts.append(post_dict)
                    logger.debug(f"Found new post: {post.title}")
                    
            logger.info(f"Found {len(filtered_posts)} new posts in r/{subreddit_name}")
            return filtered_posts
        
        except Exception as e:
            logger.error(f"Error getting posts from r/{subreddit_name}: {e}")
            return []
    
    def get_all_posts(self) -> List[List[Dict[str, Any]]]:
        """Get all filtered posts from configured subreddits."""
        try:
            # Get subreddit names
            sub_names = os.getenv('SUB_NAMES', '').split(',')
            if not sub_names or sub_names[0] == '':
                logger.warning("No subreddits configured in SUB_NAMES")
                return []
                
            # Get posts from each subreddit
            filtered_posts = []
            for sub_name in sub_names:
                if sub_name.strip():  # Skip empty names
                    posts = self.get_filtered_posts(sub_name)
                    filtered_posts.append(posts)
                
            return filtered_posts
            
        except Exception as e:
            logger.error(f"Error in get_all_posts: {e}")
            return [] 