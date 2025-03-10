#!/usr/bin/env python
"""Script to sync GitHub secrets."""
import sys
import os
import logging
from dotenv import load_dotenv

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.github import sync_github_secrets

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the GitHub secrets sync utility."""
    sync_github_secrets()

if __name__ == "__main__":
    main() 