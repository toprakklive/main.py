import requests
import time
from datetime import datetime
from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = "8199243667:AAFV-tG72ngWGUxsJELA3aBTxhukAKtEcPU"
TELEGRAM_CHAT_ID = "7041542838"

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except:
        pass

def fetch_candles(symbol="EURUSD", interval="5", limit=150):
    url = f"https://api.taapi.io/candles?secret=demo&exchange=fxcm&symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("value", [])
    return []

def detect_liquidity_and_ifvg(candles):
    if len(candles) < 10:
        return False
    recent = candles[-1]
    prev = candles[-2]
    body_break = recent["close"] > prev["high"] or recent["close"] < prev["low"]
    wick_sweep = recent["high"] > max(c["high"] for c in candles[-10:-1]) or recent["low"] < min(c["low"] for c in candles[-10:-1])
    gap = abs(prev["close"] - recent["open"]) > 0.1
    return body_break and wick_sweep and gap

def main_loop():
    keep_alive()
    while True:
        candles = fetch_candles()
        if detect_liquidity_and_ifvg(candles):
            send_telegram_message("EURUSD: IFVG + Liquidity Sweep + MSS Detected!")
        time.sleep(300)

if __name__ == "__main__":
    main_loop()
    
 if __name__ == "__main__":
    send_telegram_message("Test mesajı: Bot Railway'de çalışıyor!")
    main_loop()

