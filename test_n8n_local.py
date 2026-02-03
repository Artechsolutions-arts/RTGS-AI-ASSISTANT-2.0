import requests
import json

# Local n8n URL inside the docker network would be http://n8n:5678, 
# but from the host it's http://localhost:5678
url = "http://localhost:5678/webhook/telegram-intake"

data = {
    "update_id": 12345,
    "message": {
        "message_id": 999,
        "from": {
            "id": 1287706792,
            "is_bot": False,
            "first_name": "Murali",
            "username": "murali_g"
        },
        "chat": {
            "id": 1287706792,
            "first_name": "Murali",
            "type": "private"
        },
        "date": 1706950000,
        "text": "Book an appointment for tomorrow at 2:00 pm"
    }
}

try:
    r = requests.post(url, json=data, timeout=5)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")
