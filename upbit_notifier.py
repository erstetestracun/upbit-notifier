print("=== upbit_notifier.py started ===")

import requests
from bs4 import BeautifulSoup
import time
import os

CHECK_INTERVAL = 10  # seconds
URL = "https://upbit.com/service_center/notice"

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_latest_notice():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.select_one('.list-item__title')
    return title_tag.text.strip() if title_tag else None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=payload)
    if not response.ok:
        log(f"❌ Telegram API error: {response.status_code} {response.text}")

log(f"TELEGRAM_TOKEN: {'set' if TELEGRAM_TOKEN else 'NOT SET'}")
log(f"CHAT_ID: {'set' if CHAT_ID else 'NOT SET'}")

latest_title = ""

while True:
    try:
        current = get_latest_notice()
        if current and current != latest_title:
            if "[거래]" in current or "Trade" in current:
                latest_title = current
                message = f"🚨 New TRADE Notice:\n\n<b>{current}</b>\n\n🔗 {URL}"
                send_telegram_message(message)
                log(f"✅ Trade alert sent: {current}")
            else:
                log(f"ℹ️ Non-trade notice skipped: {current}")
        else:
            log("ℹ️ No new trade notices found")
    except Exception as e:
        log(f"❌ Error: {e}")
    time.sleep(CHECK_INTERVAL)
