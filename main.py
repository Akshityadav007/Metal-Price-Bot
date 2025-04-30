import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
METAL_API_KEY = os.getenv("METAL_API_KEY")

def get_metal_prices():
    try:
        # Step 1: Get USD to INR forex rate
        forex_url = f"https://api.metalpriceapi.com/v1/latest?api_key={METAL_API_KEY}&base=USD&currencies=INR"
        forex_data = requests.get(forex_url).json()
        usd_to_inr = forex_data['rates']['INR']
        
        # Step 2: Get metal prices in USD per troy ounce
        metals_url = f"https://api.metalpriceapi.com/v1/latest?api_key={METAL_API_KEY}&base=USD&currencies=XAU,XAG"
        metals_data = requests.get(metals_url).json()
        
        # Convert to INR per gram (1 troy oz = 31.1035g)
        gold_per_gram = (1 / metals_data['rates']['XAU']) * usd_to_inr / 31.1035
        silver_per_gram = (1 / metals_data['rates']['XAG']) * usd_to_inr / 31.1035

        # Apply Indian market premium (3% for gold, 5% for silver)
        INDIAN_GOLD_PREMIUM = 1.03
        INDIAN_SILVER_PREMIUM = 1.05
        gold_22k = (gold_per_gram * INDIAN_GOLD_PREMIUM) * (22/24)
        silver = silver_per_gram * INDIAN_SILVER_PREMIUM

        # Format with Indian numbering
        def format_price(price):
            return f"₹{price:,.2f}"

        message = (
            f"🪙 *भारतीय बाजार भाव* (MCX-adjusted)\n"
            f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n"
            f"🥇 सोना (22K): {format_price(gold_22k)}/ग्राम\n"
            f"🥈 चांदी: {format_price(silver)}/ग्राम\n\n"
            f"*Note*: Includes 3% (gold) & 5% (silver) Indian market premium"
        )
        
        return message

    except Exception as e:
        return (
            f"🪙 *Error Fetching Prices*\n"
            f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n"
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
        send_telegram_message(prices)
    except Exception as e:
        print(f"Error: {str(e)}")
        send_telegram_message(
            (
                f"🪙 *भारतीय बाजार भाव* (MCX-adjusted)\n"
                f"📅 {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n"
                f"Failed to fetch prices!"
                )
        )