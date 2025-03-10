#!/usr/bin/env python
"""Script to run the Discord bot."""
import sys
import os
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bots.discord import DiscordBot

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the Discord bot."""
    bot = DiscordBot()
    bot.run()

if __name__ == "__main__":
    main() 