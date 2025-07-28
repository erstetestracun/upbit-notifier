import requests
from bs4 import BeautifulSoup
import time
import os

URL = "https://upbit.com/service_center/notice"
CHECK_INTERVAL = 10  # seconds

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

latest_notice_id = None

def get_latest_notice():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    notice = soup.select_one('.list-item__title a')
    
    if notice:
        title = notice.text.strip()
        link = "https://upbit.com" + notice.get("href")
        notice_id = link.split("id=")[-1]  # extract ID from URL
        return notice_id, title, link
    return None, None, None

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
        notice_id, title, link = get_latest_notice()
        if notice_id and notice_id != latest_notice_id:
            if "[거래]" in title:
                latest_notice_id = notice_id
                message = f"🚨 <b>New TRADE Notice</b>:\n\n<b>{title}</b>\n\n🔗 {link}"
                send_telegram_message(message)
                print("✅ Sent:", title)
            else:
                print("ℹ️ Skipped (not 거래):", title)
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(CHECK_INTERVAL)
