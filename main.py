import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict
from zoneinfo import ZoneInfo  # Built-in from Python 3.9+

INDIA_TZ = ZoneInfo("Asia/Kolkata")
now = datetime.now(INDIA_TZ)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
METAL_API_KEY = os.getenv("METAL_API_KEY")

def get_metal_prices():
    try:
        # Step 1: Get USD to INR forex rate
        url = f"https://api.metals.dev/v1/latest?api_key={METAL_API_KEY}&currency=INR&unit=kg"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        res = requests.get(url, headers=headers)
        data = res.json()

        # get gold/silver price
        gold = data['metals']['mcx_gold']
        silver = data['metals']['mcx_silver']

        # Apply Indian market premium (3% for gold, 5% for silver)
        INDIAN_GOLD_PREMIUM = 1.03
        INDIAN_SILVER_PREMIUM = 1.05
        gold_24k = (gold * INDIAN_GOLD_PREMIUM) / 100
        silver = silver * INDIAN_SILVER_PREMIUM

        # Format with Indian numbering
        def format_price(price):
            return f"₹{price:,.2f}"

        message = (
            f"🪙 *भारतीय बाजार भाव* (MCX)\n"
            f"📅 {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')}\n\n"
            f"🥇 सोना (24K): {format_price(gold_24k)} / तोला\n"
            f"🥈 चांदी: {format_price(silver)} / किलोग्राम\n\n"
            f"*Note*: Includes 3% (gold) & 5% (silver) Indian market premium"
        )
        
        return message

    except Exception as e:
        return (
            f"🪙 *Error Fetching Prices*\n"
            f"📅 {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')}\n\n"
            f"⚠️ {str(e)}\n"
            f"Please check API status"
        )

# Telegram function remains same
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message, 
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)



if __name__ == "__main__":
    try:
        prices = get_metal_prices()
        print(prices)
        # send_telegram_message(prices)
    except Exception as e:
        print(f"Error: {str(e)}")
        # send_telegram_message(
        #     (
        #         f"🪙 *भारतीय बाजार भाव* (MCX-adjusted)\n"
        #         f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n"
        #         f"Failed to fetch prices!"
        #         )
        # )