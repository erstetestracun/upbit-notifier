import requests
from bs4 import BeautifulSoup
import time
import os

URL = "https://upbit.com/service_center/notice"
CHECK_INTERVAL = 10  # seconds

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Store all notified titles here
notified_titles = set()

def get_latest_notices():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Select all notice titles on the page (assuming .list-item__title selects each title)
    titles = [tag.text.strip() for tag in soup.select('.list-item__title')]
    return titles

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {msg}")

while True:
    try:
        latest_notices = get_latest_notices()
        new_trade_notices = []

        for title in latest_notices:
            # Check if title is trade-related AND not notified before
            if (("[거래]" in title) or ("[Trade]" in title)) and (title not in notified_titles):
                new_trade_notices.append(title)

        # Send Telegram message for each new trade notice
        for title in reversed(new_trade_notices):  # reversed = oldest first
            message = f"🚨 New TRADE Notice:\n\n<b>{title}</b>\n\n🔗 {URL}"
            send_telegram_message(message)
            log(f"✅ Trade alert sent: {title}")
            notified_titles.add(title)

        if not new_trade_notices:
            log("ℹ️ No new trade notices found")

    except Exception as e:
        log(f"❌ Error: {e}")

    time.sleep(CHECK_INTERVAL)
