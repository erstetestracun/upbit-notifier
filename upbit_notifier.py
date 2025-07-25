import requests

# Replace with your actual bot token and chat ID
BOT_TOKEN = "8187545298:AAHkqHbdRNzWNoTN-q1YY2nyiyyriIWgXVg"
CHAT_ID = "6183099068"

message = "✅ Hello from Render! If you're seeing this, your bot is live and working. 🚀"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, data=payload)

print("Telegram response:", response.status_code, response.text)
