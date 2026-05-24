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

TOKEN = "PUT_YOUR_BOT_TOKEN"
CHAT_ID = "PUT_YOUR_CHAT_ID"

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
        # GET DATA
        # ============================

        gold_15m = yf.download(
            tickers="GC=F",
            period="1d",
            interval="15m"
        )

        gold_1h = yf.download(
            tickers="GC=F",
            period="5d",
            interval="1h"
        )

        gold_4h = yf.download(
            tickers="GC=F",
            period="1mo",
            interval="4h"
        )

        close_15m = gold_15m["Close"].squeeze()
        close_1h = gold_1h["Close"].squeeze()
        close_4h = gold_4h["Close"].squeeze()

        current_price = round(close_15m.iloc[-1], 1)

        # ============================
        # RSI MULTI TIMEFRAME
        # ============================

        rsi_15m = round(
            ta.momentum.RSIIndicator(close_15m).rsi().iloc[-1],
            2
        )

        rsi_1h = round(
            ta.momentum.RSIIndicator(close_1h).rsi().iloc[-1],
            2
        )

        rsi_4h = round(
            ta.momentum.RSIIndicator(close_4h).rsi().iloc[-1],
            2
        )

        bullish = 0
        bearish = 0

        if rsi_15m > 50:
            bullish += 1
        else:
            bearish += 1

        if rsi_1h > 50:
            bullish += 1
        else:
            bearish += 1

        if rsi_4h > 50:
            bullish += 1
        else:
            bearish += 1

        rsi_value = rsi_15m

        # ============================
        # SIGNALS
        # ============================

        signal = "WAIT"

        entry = current_price
        sl = 0
        tp1 = 0
        tp2 = 0
        confidence = 50

        # BUY
        if bullish >= 2 and rsi_value < 40:

            signal = "BUY"

            sl = round(current_price - 10, 1)
            tp1 = round(current_price + 15, 1)
            tp2 = round(current_price + 30, 1)

            confidence = 85

        # SELL
        elif bearish >= 2 and rsi_value > 60:

            signal = "SELL"

            sl = round(current_price + 10, 1)
            tp1 = round(current_price - 15, 1)
            tp2 = round(current_price - 30, 1)

            confidence = 85

        # ============================
        # TERMINAL
        # ============================

        print("\n===================================")

        print(f"Gold Price: {current_price}")

        print(f"15M RSI: {rsi_15m}")
        print(f"1H RSI: {rsi_1h}")
        print(f"4H RSI: {rsi_4h}")

        print(f"Signal: {signal}")

        # ============================
        # CHART
        # ============================

        df = gold_15m.copy()

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

15M RSI: {rsi_15m}
1H RSI: {rsi_1h}
4H RSI: {rsi_4h}

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
        # WAIT 15 MIN
        # ============================

        time.sleep(900)

    except Exception as e:

        print(f"Error: {e}")

        time.sleep(60)