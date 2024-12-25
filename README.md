# reddit_bot
Telegram bot to scrape posts from reddit

## Setup Instructions

### Dependencies

The project requires the following dependencies, which are specified in the `pyproject.toml` file:

- Python 3.11.8
- discord-webhook ^1.3.0
- praw ^7.7.1
- pymongo ^4.7.0
- python-telegram-bot ^21.1.1
- pytz ^2024.1

### Environment Variables

The following environment variables need to be set for the project to work correctly. These can be found in the `.test.env` file:

- **Telegram Configuration**
  - `TELEGRAM_TOKEN`
  - `TELEGRAM_CHAT_ID`

- **MongoDB Configuration**
  - `MONGO_USER`
  - `MONGO_PASSWORD`
  - `MONGO_URI`
  - `MONGO_DB_NAME`

- **Reddit Configuration**
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET`
  - `REDDIT_PASSWORD`
  - `REDDIT_USER_AGENT`
  - `REDDIT_USERNAME`

- **Discord Configuration**
  - `DISCORD_WEBHOOK_URL`

- **Other Configuration**
  - `VALID_FLAIRS`
  - `SUB_NAMES`

## Usage Instructions

### Running the Bot

To run the Telegram bot, execute the following command:

```bash
poetry run python3 lib/bot.py
```

### Testing the Discord Integration

To test the Discord integration, execute the following command:

```bash
poetry run python3 lib/test_discord.py
```

## CI/CD Setup

The project uses GitHub Actions for CI/CD. The workflow file `.github/workflows/master.yml` and the custom action `.github/actions/setup_py_env/action.yml` are used for this setup.

### Workflow File

The workflow file `.github/workflows/master.yml` is configured to extract Reddit posts and send them to Telegram. It runs on a schedule and uses the environment variables specified in the repository.

### Custom Action

The custom action `.github/actions/setup_py_env/action.yml` is used for dependency management. It checks cached dependencies and installs them through poetry if needed.
