import requests
import time
from flask import Flask
from threading import Thread

# === CONFIGURATION ===
TELEGRAM_TOKEN = "8199243667:AAFV-tG72ngWGUxsJELA3aBTxhukAKtEcPU"
TELEGRAM_CHAT_ID = "7041542838"
TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjgyNTYwNjE4MDZmZjE2NTFlMWFkY2M4IiwiaWF0IjoxNzQ3Mjc5OTY5LCJleHAiOjMzMjUxNzQzOTY5fQ.B94s3TVeV0EI9_kDHqOHolWFUaMQ54wbVDh3uf8-AQU"  

# === KEEP ALIVE (for UptimeRobot or Railway) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === TELEGRAM FUNCTION ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram error:", e)

# === FETCH CANDLES ===
def fetch_candles(symbol="EURUSD", interval="5", limit=150):
    url = f"https://api.taapi.io/candles?secret={TAAPI_KEY}&exchange=fxcm&symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("value", [])
    except Exception as e:
        print("Fetch error:", e)
    return []

# === DETECTION LOGIC ===
def detect_liquidity_and_ifvg(candles):
    if len(candles) < 10:
        return False
    recent = candles[-1]
    prev = candles[-2]
    body_break = recent["close"] > prev["high"] or recent["close"] < prev["low"]
    wick_sweep = recent["high"] > max(c["high"] for c in candles[-10:-1]) or recent["low"] < min(c["low"] for c in candles[-10:-1])
    fair_value_gap = abs(prev["close"] - recent["open"]) > 0.1
    return body_break and wick_sweep and fair_value_gap

# === MAIN LOOP ===
def main_loop():
    send_telegram_message("🚀 Railway bot started successfully.")
    while True:
        candles = fetch_candles()
        if detect_liquidity_and_ifvg(candles):
            send_telegram_message("📊 EURUSD: IFVG + Liquidity Sweep + MSS Detected!")
        time.sleep(300)  

# === START EVERYTHING ===
if __name__ == "__main__":
    keep_alive()
    time.sleep(1)
    main_loop()
