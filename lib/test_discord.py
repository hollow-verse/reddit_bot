from discord_bot import send_post_to_discord
from typing import Dict, Any

def create_test_post() -> Dict[str, str]:
    return {
        "subreddit": "TestSubreddit",
        "title": "Test Post Title",
        "posted_ago": "Just now",
        "url": "https://reddit.com/test",
        "selftext": "This is a test post content to verify Discord webhook integration."
    }

def test_discord_message() -> None:
    test_post = create_test_post()
    
    try:
        send_post_to_discord(test_post)
        print("✅ Test message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test message: {str(e)}")
        raise

def run_all_tests() -> None:
    tests = [test_discord_message]
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"Test {test.__name__} failed: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
