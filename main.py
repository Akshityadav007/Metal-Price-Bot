import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load env vars from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
METAL_API_KEY = os.getenv("METAL_API_KEY")

def get_metal_prices():
    headers = {
        "x-access-token": METAL_API_KEY,
        "Content-Type": "application/json"
    }

    gold_resp = requests.get("https://www.goldapi.io/api/XAU/INR", headers=headers)
    silver_resp = requests.get("https://www.goldapi.io/api/XAG/INR", headers=headers)

    gold_data = gold_resp.json()
    silver_data = silver_resp.json()

    gold_price = gold_data.get("price", "N/A")
    silver_price = silver_data.get("price", "N/A")

    message = (
    f"🪙 *आज के भाव*\n"
    f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    f"🥇 सोना : ₹{int(gold_price):,} / तोला\n"  # Gold price formatted
    f"🥈 चांदी : ₹{int(silver_price):,} / किलोग्राम"  # Silver price formatted
    )

    return message

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)


if __name__ == "__main__":
    try:
        message = get_metal_prices()        # get the prices
        print(message)
        # send_telegram_message(message)      # push them to telegram chat
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        # send_telegram_message('❌ Failed to fetch prices! ❌')