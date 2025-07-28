import requests
from bs4 import BeautifulSoup
import time
import os

# Configuration
URL = "https://upbit.com/service_center/notice"
CHECK_INTERVAL = 1  # seconds
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Keep track of seen titles
seen_titles = set()

def log(msg):
    print(msg, flush=True)

def get_trade_notices():
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'ko-KR,ko;q=0.9'  # Ensure page loads in Korean
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.select('.list-item__title')

    log(f"🔍 Found {len(titles)} titles on the page.")

    trade_notices = []
    for tag in titles:
        title = tag.text.strip()
        if ("거래" in title or "Trade" in title) and title not in seen_titles:
            trade_notices.append(title)
            seen_titles.add(title)

    return trade_notices

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        log(f"❌ Failed to send Telegram message: {e}")

log("🚀 upbit_notifier started...")

while True:
    try:
        notices = get_trade_notices()
        if notices:
            for notice in notices:
                message = f"🚨 New TRADE Notice:\n\n<b>{notice}</b>\n\n🔗 {URL}"
                send_telegram_message(message)
                log(f"✅ Trade alert sent: {notice}")
        else:
            log("ℹ️ No new trade notices found")
    except Exception as e:
        log(f"❌ Error: {e}")

    time.sleep(CHECK_INTERVAL)
