#!/usr/bin/env python
"""Check if .env variables are loading correctly."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(verbose=True)

# List of variables to check
variables = [
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USER_AGENT",
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
    "MONGO_USER",
    "MONGO_PASSWORD",
    "MONGO_URI",
    "MONGO_DB_NAME",
    "SUB_NAMES",
    "DISCORD_WEBHOOK_URL"
]

print("\n=== ENVIRONMENT VARIABLE CHECK ===\n")

all_present = True

for var in variables:
    value = os.environ.get(var)
    if value:
        # Show first and last few characters for sensitive values
        if any(x in var for x in ["TOKEN", "SECRET", "PASSWORD", "KEY", "WEBHOOK"]):
            display_value = f"{value[:3]}...{value[-3:]}" if len(value) > 10 else "[set]"
        else:
            display_value = value
        
        status = "✓"
    else:
        display_value = "[NOT SET]"
        status = "✗"
        all_present = False
    
    print(f"{status} {var}: {display_value}")

print("\n=== SUMMARY ===")
if all_present:
    print("✓ All required environment variables are set.\n")
else:
    print("✗ Some required environment variables are missing!\n")

# Print the current working directory
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

if __name__ == "__main__":
    pass 