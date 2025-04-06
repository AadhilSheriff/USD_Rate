import requests
from bs4 import BeautifulSoup
import datetime

# Your Telegram Bot Token and Chat ID
BOT_TOKEN = "7688039054:AAEcyra7u7DTpONVV13dIPkrFyFeoFfYvwA"
CHAT_ID = "1016544405"

# Bank exchange rate URLs
BANK_URLS = {
    "HNB": "https://www.hnb.net/exchange-rates",
    "BOC": "https://www.boc.lk/rates-tariff",
    "NTB": "https://www.nationstrust.com/foreign-exchange-rates"
}

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("✅ Message sent to Telegram.")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")

def get_exchange_rate_from_bank(bank_name, url, row_identifier, buying_index, selling_index):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if not table:
            print(f"⚠ No table found for {bank_name}. Check HTML structure.")
            return

        rows = table.find_all("tr")
        usd_buying = usd_selling = None

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1 and row_identifier.lower() in cols[0].text.lower():
                try:
                    usd_buying = cols[buying_index].text.strip()
                    usd_selling = cols[selling_index].text.strip()
                except IndexError:
                    print(f"⚠ Index error in {bank_name}: {cols}")
                break

        if usd_buying and usd_selling:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            # Format USD rates to 2 decimal places
            buying = f"{float(usd_buying):.2f}"
            selling = f"{float(usd_selling):.2f}"

            rate_info = (
                f"{bank_name} 🇱🇰\n"
                f"💵 USD Buying: {buying} LKR\n"
                f"💴 USD Selling: {selling} LKR\n"
                f"📅 Date: {today}"
            )

            file_path = "C:/Users/Aadhil/Desktop/usd_to_lkr_rates.txt"
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(rate_info + "\n")

            print(f"✅ Saved: {rate_info}")
            send_telegram_message(rate_info)
        else:
            print(f"⚠ Could not find USD exchange rates for {bank_name}. Check HTML layout or row identifiers.")

    except Exception as e:
        print(f"❌ Error fetching exchange rate for {bank_name}: {e}")

def get_all_exchange_rates():
    bank_identifiers = {
        "HNB": {"row_identifier": "US Dollars", "buying_index": 2, "selling_index": 3},
        "BOC": {"row_identifier": "USD", "buying_index": 1, "selling_index": 2},
        "NTB": {"row_identifier": "USD", "buying_index": 2, "selling_index": 4}
    }

    for bank_name, url in BANK_URLS.items():
        bank_info = bank_identifiers.get(bank_name)
        if bank_info:
            get_exchange_rate_from_bank(
                bank_name,
                url,
                bank_info["row_identifier"],
                bank_info["buying_index"],
                bank_info["selling_index"]
            )

# Run the script
get_all_exchange_rates()
