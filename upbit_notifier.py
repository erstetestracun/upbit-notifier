import requests
from bs4 import BeautifulSoup
import time
import os

URL = "https://upbit.com/service_center/notice"
CHECK_INTERVAL = 5  # seconds

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # load from Render env var
CHAT_ID = os.getenv('CHAT_ID')

latest_title = ""

def get_latest_notice():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.select_one('.list-item__title')  # selector for the first notice title
    return title_tag.text.strip() if title_tag else None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

while True:
    try:
        current = get_latest_notice()
        if current and current != latest_title:
            if "[거래]" in current:  # Only trade-related
                latest_title = current
                message = f"🚨 New TRADE Notice:\n\n<b>{current}</b>\n\n🔗 {URL}"
                send_telegram_message(message)
                print("✅ Trade alert sent:", current)
            else:
                print("ℹ️ Non-trade notice, skipped:", current)
    except Exception as e:
        print("❌ Error:", e)
    
    time.sleep(CHECK_INTERVAL)
