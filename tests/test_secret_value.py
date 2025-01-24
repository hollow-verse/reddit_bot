import os
import requests

test_secret_value = os.getenv('TEST_SECRET_VALUE')
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def main():
    if test_secret_value:
        print("Secret value exists")
        requests.post(WEBHOOK_URL, json={f"content": "Secret value found {test_secret_value}"})

main()

