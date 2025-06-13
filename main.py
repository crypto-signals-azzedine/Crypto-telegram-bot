import requests
import time
import ta
import pandas as pd

TELEGRAM_TOKEN = "7848358052:AAHCjIFYm43cM6ucbZG_9o7FIWJvCJIlQjE"
CHAT_ID = "6940108004"
SYMBOLS = ["IDUSDT", "HBARUSDT", "VETUSDT", "FLOKIUSDT", "SUPERUSDT"]
INTERVAL = "15m"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def fetch_klines(symbol, interval="15m", limit=100):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(BINANCE_URL, params=params)
    data = response.json()
    if isinstance(data, list):
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_base_vol",
            "taker_quote_vol", "ignore"
        ])
        df["close"] = df["close"].astype(float)
        return df
    return pd.DataFrame()

def analyze_symbol(symbol):
    try:
        df = fetch_klines(symbol, INTERVAL)
        if df.empty or len(df) < 22:
            print(f"🚫 لا توجد بيانات كافية لـ {symbol}")
            return

        df["ema9"] = ta.trend.ema_indicator(df["close"], window=9).fillna(0)
        df["ema21"] = ta.trend.ema_indicator(df["close"], window=21).fillna(0)
        df["rsi"] = ta.momentum.rsi(df["close"], window=14).fillna(0)

        latest = df.iloc[-1]
        price = latest["close"]
        ema9 = latest["ema9"]
        ema21 = latest["ema21"]
        rsi = latest["rsi"]

        if ema9 > ema21 and rsi > 50:
            sl = round(price * 0.985, 6)
            tp1 = round(price * 1.03, 6)
            tp2 = round(price * 1.05, 6)
            msg = f"📈 إشارة شراء: {symbol}\\nالسعر: {price}$\\nEMA: 9 > 21\\nRSI: {round(rsi, 2)}\\nSL: {sl}$\\nTP1: {tp1}$ - TP2: {tp2}$"
            send_telegram_message(msg)
        elif ema9 < ema21 and rsi < 50:
            sl = round(price * 1.015, 6)
            tp1 = round(price * 0.97, 6)
            tp2 = round(price * 0.95, 6)
            msg = f"📉 إشارة بيع: {symbol}\\nالسعر: {price}$\\nEMA: 9 < 21\\nRSI: {round(rsi, 2)}\\nSL: {sl}$\\nTP1: {tp1}$ - TP2: {tp2}$"
            send_telegram_message(msg)
        else:
            print(f"🔍 لا توجد إشارة حالياً على {symbol}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تحليل {symbol}: {e}")

while True:
    for symbol in SYMBOLS:
        analyze_symbol(symbol)
        time.sleep(5)
    time.sleep(60)
