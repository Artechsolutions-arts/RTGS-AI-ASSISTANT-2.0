import requests
url = "http://localhost:8000/analyze"
p = {"message_text": "Book an appointment for tomorrow at 2:00 pm"}
r = requests.post(url, json=p)
print(r.json())
