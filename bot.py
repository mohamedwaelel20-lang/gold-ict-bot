import yfinance as yf
import pandas as pd
import ta
import time
import asyncio
import mplfinance as mpf

from telegram import Bot
from datetime import datetime

# =========================================
# TELEGRAM DATA
# =========================================

TOKEN = "8859133218:AAGn4oXHaZELJJmrkjqskgsDrqj9dmjvdaw"
CHAT_ID = "1426294345"

bot = Bot(token=TOKEN)

print("ULTIMATE ICT BOT STARTED...\n")

# =========================================
# MARKET TIME FILTER
# =========================================

def market_open():

    now = datetime.utcnow()

    weekday = now.weekday()
    hour = now.hour

    # Saturday closed
    if weekday == 5:
        return False

    # Sunday open before market by 2h
    if weekday == 6 and hour < 19:
        return False

    # Friday close
    if weekday == 4 and hour >= 21:
        return False

    return True

# =========================================
# MAIN LOOP
# =========================================

while True:

    try:

        # ============================
        # MARKET CLOSED
        # ============================

        if not market_open():

            print("Market Closed...")
            time.sleep(1800)
            continue

        # ============================
        # GET GOLD DATA
        # ============================

        gold = yf.download(
            tickers="GC=F",
            period="1d",
            interval="15m"
        )

        close = gold["Close"].squeeze()

        current_price = round(close.iloc[-1], 1)

        # ============================
        # RSI
        # ============================

        rsi = ta.momentum.RSIIndicator(close)
        rsi_value = round(rsi.rsi().iloc[-1], 2)

        # ============================
        # ICT SIGNALS
        # ============================

        signal = "WAIT"

        entry = current_price
        sl = 0
        tp1 = 0
        tp2 = 0
        confidence = 50

        if rsi_value < 30:

            signal = "BUY"

            sl = round(current_price - 10, 1)
            tp1 = round(current_price + 15, 1)
            tp2 = round(current_price + 30, 1)

            confidence = 80

        elif rsi_value > 70:

            signal = "SELL"

            sl = round(current_price + 10, 1)
            tp1 = round(current_price - 15, 1)
            tp2 = round(current_price - 30, 1)

            confidence = 80

        # ============================
        # PRINT TERMINAL
        # ============================

        print("\n===================================")
        print(f"Gold Price: {current_price}")
        print(f"RSI: {rsi_value}")
        print(f"Signal: {signal}")

        # ============================
        # PREPARE CHART
        # ============================

        df = gold.copy()

        df.index.name = "Date"

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

        apds = []

        if signal == "BUY":

            apds.append(
                mpf.make_addplot(
                    [entry] * len(df),
                    color='lime',
                    width=1
                )
            )

        elif signal == "SELL":

            apds.append(
                mpf.make_addplot(
                    [entry] * len(df),
                    color='red',
                    width=1
                )
            )

        mpf.plot(
            df,
            type='candle',
            style=s,
            title=f'XAUUSD ICT ANALYSIS | {signal}',
            ylabel='Price',
            volume=False,
            figsize=(14, 8),
            addplot=apds,
            savefig='chart.png'
        )

        # ============================
        # TELEGRAM MESSAGE
        # ============================

        caption = f"""
🔥 GOLD ICT PRO SIGNAL 🔥

Signal: {signal}

Entry: {entry}

SL: {sl}

TP1: {tp1}

TP2: {tp2}

RSI: {rsi_value}

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

        print("\nSignal Sent To Telegram Successfully")

        # ============================
        # WAIT
        # ============================

        time.sleep(900)

    except Exception as e:

        print(f"Error: {e}")

        time.sleep(60)