from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from requests.structures import CaseInsensitiveDict
from zoneinfo import ZoneInfo  # Built-in from Python 3.9+
import os
from dotenv import load_dotenv
from main import send_telegram_message

load_dotenv()

METAL_API_KEY = os.getenv("METAL_API_KEY")
INDIA_TZ = ZoneInfo("Asia/Kolkata")
now = datetime.now(INDIA_TZ)


def get_metal_prices():
    try:
        # Step 1: Get USD to INR forex rate
        url = f"https://api.metals.dev/v1/latest?api_key={METAL_API_KEY}&currency=INR&unit=g"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"

        res = requests.get(url, headers=headers)
        data = res.json()

        # get gold/silver price
        if res.status_code != 200 or "metals" not in data:
            raise ValueError("Invalid API response")

        gold = data["metals"].get("mcx_gold")
        silver = data["metals"].get("mcx_silver")

        if gold is None or silver is None:
            raise ValueError("Gold or Silver price not found in API response")


        # Apply Indian market premium (3% for gold, 5% for silver)
        INDIAN_GOLD_PREMIUM = 1.03
        INDIAN_SILVER_PREMIUM = 1.05
        
        # Convert from grams to tola (gold) and kilograms (silver)
        gold_24k_per_tola = (gold * INDIAN_GOLD_PREMIUM) * 10
        silver_per_kg = (silver * INDIAN_SILVER_PREMIUM) * 1000


        # Format with Indian numbering
        def format_price(price):
            return f"₹{price:,.2f}"

        message = (
            f"🪙 *भारतीय बाजार भाव* (MCX)\n"
            f"📅 {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')}\n\n"
            
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🥇 *सोना (24K)*: {format_price(gold_24k_per_tola)} / तोला\n"
            f"🥈 *चांदी*: {format_price(silver_per_kg)} / किलोग्राम\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"

            f"📝 *Note*: Includes 3% (gold) & 5% (silver) Indian market premium"
        )
        return message

    except Exception as e:
        return (
            f"🪙 *Error Fetching Prices*\n"
            f"📅 {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')}\n\n"
            f"⚠️ {str(e)}\n"
            f"Please check API status"
        )


try:
    prices = get_metal_prices()
    send_telegram_message(prices)
except Exception as e:
    print(f"Error: {str(e)}")
    send_telegram_message(
        (
            f"🪙 *भारतीय बाजार भाव* (MCX)\n"
            f"📅 {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M')}\n\n"
            f"❌ Failed to fetch prices!"
        )
    )