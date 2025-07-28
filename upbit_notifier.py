import requests
from bs4 import BeautifulSoup
import time
import random
import sys
import os

# === CONFIGURATION ===
URL = "https://upbit.com/service_center/notice"
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")  # Set as env var on Render
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Store last known title
last_title = None

def log(msg):
    print(msg, flush=True)

def get_random_headers():
    return {
        'User-Agent': random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
        ]),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': URL,
        'Connection': 'keep-alive'
    }

def fetch_notice_html():
    try:
        response = requests.get(URL, headers=get_random_headers(), timeout=10)
        if "Access denied" in response.text or response.status_code == 403:
            log("⚠️ Blocked by Cloudflare. Retrying with ScraperAPI...")
            scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={URL}"
            response = requests.get(scraper_url, timeout=10)
        return response.text
    except Exception as e:
        log(f"❌ Error fetching page: {e}")
        return ""

def get_latest_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    titles = soup.select('.list-item__title')
    if titles:
        return titles[0].get_text(strip=True)
    return None

def send_telegram_notification(title):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        msg = f"🚀 New Upbit Listing Notice:\n\n{title}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        try:
            r = requests.post(url, json=payload)
            if r.status_code == 200:
                log("✅ Telegram notification sent.")
            else:
                log(f"⚠️ Telegram error: {r.text}")
        except Exception as e:
            log(f"❌ Telegram send failed: {e}")
    else:
        log("ℹ️ Telegram not configured.")

# === MAIN LOOP ===
log("🟢 upbit_notifier is running...")

while True:
    html = fetch_notice_html()
    if html:
        title = get_latest_title(html)
        if title:
            log(f"🔍 Found title: {title}")
            if title != last_title:
                log("📢 New trade notice detected!")
                last_title = title
                send_telegram_notification(title)
            else:
                log("ℹ️ No new trade notices.")
        else:
            log("⚠️ Could not find title on the page.")
    else:
        log("❌ Failed to fetch or parse the page.")

    # Sleep randomized between 1.1 to 2.5 seconds
    time.sleep(random.uniform(1.1, 2.5))
