# Reddit Bot

A bot that monitors Reddit posts and forwards them to both Discord and Telegram channels.

## Features

- Monitors configured subreddits for new posts
- Filters posts by specific flairs
- Forwards posts to Discord using webhooks
- Forwards posts to Telegram using the Telegram Bot API 
- Stores post history in MongoDB to prevent duplicates
- Runs every 15 minutes via GitHub Actions

## Project Structure

Well-organized structure for better maintainability:

```
reddit_bot/
├── src/                   # Source code package
│   ├── bots/              # Bot implementations
│   │   ├── discord.py     # Discord bot
│   │   └── telegram.py    # Telegram bot
│   ├── services/          # External services
│   │   ├── mongodb.py     # MongoDB service
│   │   └── reddit.py      # Reddit API service
│   └── utils/             # Utilities
│       └── github.py      # GitHub utility functions
├── scripts/               # Command-line scripts
│   ├── discord_bot.py     # Discord bot runner
│   ├── telegram_bot.py    # Telegram bot runner
│   └── sync_secrets.py    # GitHub secrets utility
├── pyproject.toml         # Poetry configuration
├── .env                   # Environment variables
├── .github/               # GitHub Actions workflows
│   └── workflows/
│       └── reddit-discord-sync.yml
└── README.md              # Documentation
```

## Setup Instructions

### Prerequisites

- Python 3.11.8
- Poetry for dependency management
- MongoDB database
- Discord webhook URL
- Telegram bot token
- Reddit API credentials

### Installation

1. Clone the repository
2. Install dependencies using Poetry:

```bash
poetry install
```

### Configuration

Create a `.env` file with the following environment variables:

```env
# Telegram Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# MongoDB Configuration  
MONGO_USER=your_mongodb_username
MONGO_PASSWORD=your_mongodb_password
MONGO_URI=your_mongodb_uri
MONGO_DB_NAME=your_database_name

# Reddit Configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent

# Discord Configuration
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Bot Configuration
VALID_FLAIRS=comma,separated,flairs
SUB_NAMES=comma,separated,subreddit_names
```

### Running the Bot

```bash
# Run Discord bot
poetry run discord-bot

# Run Telegram bot
poetry run telegram-bot

# Sync GitHub secrets
poetry run sync-secrets
```

## CI/CD

The project uses GitHub Actions for automated deployment:

- Runs every 15 minutes via cron schedule
- Uses Poetry for dependency management
- Caches dependencies for faster runs
- Configurable through GitHub repository secrets
- Automatically sends posts to both Discord and Telegram

## Dependencies

- discord-webhook ^1.3.0 - Discord integration
- praw ^7.7.1 - Reddit API wrapper
- pymongo ^4.7.0 - MongoDB driver
- python-telegram-bot ^21.1.1 - Telegram API wrapper
- python-dotenv ^1.0.1 - Environment variable management
- pytz ^2024.1 - Timezone handling

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.