import yfinance as yf
import pandas as pd
import ta
import time
import asyncio
import mplfinance as mpf

from telegram import Bot
from datetime import datetime, UTC

# =========================================
# TELEGRAM DATA
# =========================================

TOKEN = "8859133218:AAGn4oXHaZELJJmrkjqskgsDrqj9dmjvdaw"
CHAT_ID = "1426294345"

bot = Bot(token=TOKEN)

print("ULTIMATE ICT BOT STARTED...\n")

# =========================================
# MARKET FILTER
# =========================================

def market_open():

    now = datetime.now(UTC)

    weekday = now.weekday()
    hour = now.hour

    if weekday == 5:
        return False

    if weekday == 6 and hour < 19:
        return False

    if weekday == 4 and hour >= 21:
        return False

    return True

# =========================================
# MAIN LOOP
# =========================================

while True:

    try:

        if not market_open():

            print("Market Closed...")

            time.sleep(1800)

            continue

        # =================================
        # GOLD DATA
        # =================================

        df = yf.download(
            "GC=F",
            period="5d",
            interval="15m",
            auto_adjust=True
        )

        if df.empty:

            print("No market data found...")

            time.sleep(60)

            continue

        # =================================
        # LAST 100 CANDLES
        # =================================

        df = df.tail(100)

        close = df["Close"]

        current_price = round(float(close.iloc[-1]), 1)

        # =================================
        # RSI
        # =================================

        rsi = round(
            ta.momentum.RSIIndicator(close).rsi().iloc[-1],
            2
        )

        signal = "WAIT"

        entry = current_price
        sl = 0
        tp1 = 0
        tp2 = 0
        confidence = 50

        # =================================
        # BUY
        # =================================

        if rsi < 35:

            signal = "BUY"

            sl = round(current_price - 10, 1)

            tp1 = round(current_price + 15, 1)

            tp2 = round(current_price + 30, 1)

            confidence = 85

        # =================================
        # SELL
        # =================================

        elif rsi > 65:

            signal = "SELL"

            sl = round(current_price + 10, 1)

            tp1 = round(current_price - 15, 1)

            tp2 = round(current_price - 30, 1)

            confidence = 85

        # =================================
        # CHART STYLE
        # =================================

        mc = mpf.make_marketcolors(
            up='#26a69a',
            down='#ef5350',
            wick='inherit',
            edge='inherit',
            volume='inherit'
        )

        s = mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            marketcolors=mc,
            facecolor='#131722',
            figcolor='#131722',
            gridcolor='#363c4e'
        )

        mpf.plot(
            df,
            type='candle',
            style=s,
            title=f'GOLD ICT ANALYSIS | {signal}',
            ylabel='Price',
            volume=False,
            figsize=(14, 8),
            savefig='chart.png'
        )

        # =================================
        # TELEGRAM MESSAGE
        # =================================

        caption = f"""
🔥 GOLD ICT PRO SIGNAL 🔥

Signal: {signal}

Entry: {entry}

SL: {sl}

TP1: {tp1}

TP2: {tp2}

RSI: {rsi}

Confidence: {confidence}%
"""

        async def send_signal():

            with open("chart.png", "rb") as photo:

                await bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=photo,
                    caption=caption
                )

        asyncio.run(send_signal())

        print("Signal Sent Successfully")

        # =================================
        # WAIT 15 MIN
        # =================================

        time.sleep(900)

    except Exception as e:

        print(f"Error: {e}")

        time.sleep(60)