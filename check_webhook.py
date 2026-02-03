import requests
token = "8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y"
url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
r = requests.get(url)
print(r.json())
