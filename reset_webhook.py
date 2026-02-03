import requests
token = "8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y"
ngrok_url = "https://hyetological-fumblingly-eliseo.ngrok-free.dev"
webhook_url = f"{ngrok_url}/webhook/telegram-intake"

# Delete first
requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook")

# Set again
r = requests.get(f"https://api.telegram.org/bot{token}/setWebhook", params={"url": webhook_url})
print(r.json())
