from discord_bot import send_post_to_discord

def test_discord_message():
    # Sample post data
    test_post = {
        "subreddit": "TestSubreddit",
        "title": "Test Post Title",
        "posted_ago": "Just now",
        "url": "https://reddit.com/test",
        "selftext": "This is a test post content to verify Discord webhook integration."
    }
    
    try:
        send_post_to_discord(test_post)
        print("✅ Test message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test message: {str(e)}")

if __name__ == "__main__":
    test_discord_message()
