import os
import requests

ENV_VARS = {
    'Telegram': ['TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID'],
    'MongoDB': ['MONGO_USER', 'MONGO_PASSWORD', 'MONGO_URI', 'MONGO_DB_NAME'],
    'Reddit': ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_PASSWORD', 
               'REDDIT_USER_AGENT', 'REDDIT_USERNAME'],
    'Other': ['VALID_FLAIRS', 'SUB_NAMES'],
    'Discord': ['DISCORD_WEBHOOK_URL'],
    'GitHub': ['PAT_GITHUB_TOKEN']
}

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def get_env_values():
    message = "🔍 Environment Variables Check:\n```\n"
    
    for category, vars in ENV_VARS.items():
        message += f"\n{category}:\n"
        for var in vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive data by showing only first 4 chars
                masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else value
                message += f"{var}: ✅ Value: {masked_value}\n"
            else:
                message += f"{var}: ❌ Missing\n"
    
    message += "```"
    return message

def main():
    if not WEBHOOK_URL:
        print("Discord webhook URL not found!")
        return
        
    try:
        message = get_env_values()
        response = requests.post(WEBHOOK_URL, json={"content": message})
        response.raise_for_status()
        print("Environment variables status sent to Discord")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    main()

