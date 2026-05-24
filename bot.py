import yfinance as yf
import ta
import time
import asyncio
import mplfinance as mpf
import pandas as pd

from telegram import Bot
from PIL import Image, ImageDraw

# =========================================
# TELEGRAM DATA
# =========================================

TOKEN = "8859133218:AAGn4oXHaZELJJmrkjqskgsDrqj9dmjvdaw"

CHAT_ID = "1426294345"

bot = Bot(token=TOKEN)

print("ULTIMATE ICT SMART MONEY BOT STARTED...\n")

# =========================================
# MAIN LOOP
# =========================================

while True:

    try:

        # =========================================
        # DOWNLOAD GOLD DATA
        # =========================================

        df = yf.download(

            "GC=F",

            period="5d",

            interval="15m"

        )

        df.dropna(inplace=True)

        df.columns = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume"

        ]

        close_prices = df["Close"]

        highs = df["High"]

        lows = df["Low"]

        opens = df["Open"]

        # =========================================
        # RSI
        # =========================================

        rsi = ta.momentum.RSIIndicator(

            close=close_prices

        ).rsi()

        # =========================================
        # MACD
        # =========================================

        macd = ta.trend.MACD(close_prices)

        macd_line = macd.macd()

        signal_line = macd.macd_signal()

        # =========================================
        # LAST VALUES
        # =========================================

        last_price = round(float(close_prices.iloc[-1]), 2)

        last_rsi = round(float(rsi.iloc[-1]), 2)

        last_macd = round(float(macd_line.iloc[-1]), 2)

        last_signal = round(float(signal_line.iloc[-1]), 2)

        # =========================================
        # MARKET STRUCTURE
        # =========================================

        structure = "RANGE"

        recent_high = highs.iloc[-5:].max()

        previous_high = highs.iloc[-10:-5].max()

        recent_low = lows.iloc[-5:].min()

        previous_low = lows.iloc[-10:-5].min()

        if recent_high > previous_high:

            structure = "BULLISH BOS"

        elif recent_low < previous_low:

            structure = "BEARISH BOS"

        # =========================================
        # LIQUIDITY SWEEP DETECTION
        # =========================================

        liquidity_sweep = "NO"

        # Buy Side Liquidity Sweep
        if (

            highs.iloc[-2] > highs.iloc[-3]

            and close_prices.iloc[-2] < highs.iloc[-3]

        ):

            liquidity_sweep = "BUY SIDE SWEEP"

        # Sell Side Liquidity Sweep
        elif (

            lows.iloc[-2] < lows.iloc[-3]

            and close_prices.iloc[-2] > lows.iloc[-3]

        ):

            liquidity_sweep = "SELL SIDE SWEEP"

        # =========================================
        # FAIR VALUE GAP DETECTION
        # =========================================

        fvg = "NO FVG"

        # Bullish FVG
        if lows.iloc[-1] > highs.iloc[-3]:

            fvg = "BULLISH FVG"

        # Bearish FVG
        elif highs.iloc[-1] < lows.iloc[-3]:

            fvg = "BEARISH FVG"

        # =========================================
        # SMART ENTRY SYSTEM
        # =========================================

        signal = "WAIT"

        confidence = 50

        # BUY
        if (

            structure == "BULLISH BOS"

            and liquidity_sweep == "SELL SIDE SWEEP"

            and last_macd > last_signal

            and last_rsi > 50

        ):

            signal = "BUY"

            confidence = 92

        # SELL
        elif (

            structure == "BEARISH BOS"

            and liquidity_sweep == "BUY SIDE SWEEP"

            and last_macd < last_signal

            and last_rsi < 50

        ):

            signal = "SELL"

            confidence = 92

        # =========================================
        # ENTRY / TP / SL
        # =========================================

        entry = last_price

        if signal == "BUY":

            stop_loss = round(entry - 15, 2)

            take_profit_1 = round(entry + 15, 2)

            take_profit_2 = round(entry + 30, 2)

        elif signal == "SELL":

            stop_loss = round(entry + 15, 2)

            take_profit_1 = round(entry - 15, 2)

            take_profit_2 = round(entry - 30, 2)

        else:

            stop_loss = 0

            take_profit_1 = 0

            take_profit_2 = 0

        # =========================================
        # TERMINAL INFO
        # =========================================

        print("\n===================================")

        print(f"Gold Price: {last_price}")

        print(f"RSI: {last_rsi}")

        print(f"MACD: {last_macd}")

        print(f"Structure: {structure}")

        print(f"Liquidity Sweep: {liquidity_sweep}")

        print(f"FVG: {fvg}")

        print(f"Signal: {signal}")

        # =========================================
        # PROFESSIONAL CHART
        # =========================================

        addplots = []

        if signal != "WAIT":

            entry_line = pd.Series(

                [entry] * len(df),

                index=df.index

            )

            sl_line = pd.Series(

                [stop_loss] * len(df),

                index=df.index

            )

            tp1_line = pd.Series(

                [take_profit_1] * len(df),

                index=df.index

            )

            tp2_line = pd.Series(

                [take_profit_2] * len(df),

                index=df.index

            )

            addplots.append(

                mpf.make_addplot(

                    entry_line,

                    linestyle="--"

                )

            )

            addplots.append(

                mpf.make_addplot(

                    sl_line,

                    linestyle="--"

                )

            )

            addplots.append(

                mpf.make_addplot(

                    tp1_line,

                    linestyle="--"

                )

            )

            addplots.append(

                mpf.make_addplot(

                    tp2_line,

                    linestyle="--"

                )

            )

        chart_path = "gold_chart.png"

        mpf.plot(

            df.tail(120),

            type="candle",

            style="nightclouds",

            volume=False,

            figsize=(14, 8),

            title=f"GOLD SMART MONEY | {signal}",

            ylabel="PRICE",

            addplot=addplots,

            savefig=chart_path

        )

        # =========================================
        # CREATE PREMIUM PANEL
        # =========================================

        chart = Image.open(chart_path)

        chart = chart.resize((1000, 700))

        final_img = Image.new(

            "RGB",

            (1450, 700),

            (10, 10, 10)

        )

        final_img.paste(chart, (0, 0))

        draw = ImageDraw.Draw(final_img)

        # COLORS

        WHITE = (255, 255, 255)

        GREEN = (0, 255, 100)

        RED = (255, 80, 80)

        GOLD = (255, 215, 0)

        # SIGNAL COLOR

        signal_color = WHITE

        if signal == "BUY":

            signal_color = GREEN

        elif signal == "SELL":

            signal_color = RED

        # =========================================
        # ANALYSIS PANEL
        # =========================================

        draw.text(

            (1040, 40),

            "ICT SMART MONEY",

            fill=GOLD

        )

        draw.text(

            (1040, 110),

            f"SIGNAL: {signal}",

            fill=signal_color

        )

        draw.text(

            (1040, 170),

            f"PRICE: {last_price}",

            fill=WHITE

        )

        draw.text(

            (1040, 230),

            f"RSI: {last_rsi}",

            fill=WHITE

        )

        draw.text(

            (1040, 290),

            f"MACD: {last_macd}",

            fill=WHITE

        )

        draw.text(

            (1040, 350),

            f"STRUCTURE:",

            fill=GOLD

        )

        draw.text(

            (1040, 390),

            structure,

            fill=WHITE

        )

        draw.text(

            (1040, 450),

            "LIQUIDITY:",

            fill=GOLD

        )

        draw.text(

            (1040, 490),

            liquidity_sweep,

            fill=WHITE

        )

        draw.text(

            (1040, 550),

            f"FVG: {fvg}",

            fill=WHITE

        )

        draw.text(

            (1040, 610),

            f"CONFIDENCE: {confidence}%",

            fill=GOLD

        )

        final_path = "final_analysis.png"

        final_img.save(final_path)

        # =========================================
        # TELEGRAM MESSAGE
        # =========================================

        caption = f"""
🔥 GOLD SMART MONEY SIGNAL 🔥

Signal: {signal}

Entry: {entry}

SL: {stop_loss}

TP1: {take_profit_1}

TP2: {take_profit_2}

Structure: {structure}

Liquidity: {liquidity_sweep}

FVG: {fvg}

Confidence: {confidence}%
"""

        # =========================================
        # SEND TO TELEGRAM
        # =========================================

        async def send_photo():

            with open(final_path, "rb") as photo:

                await bot.send_photo(

                    chat_id=CHAT_ID,

                    photo=photo,

                    caption=caption

                )

        asyncio.run(send_photo())

        print("\nSignal Sent To Telegram Successfully")

        # =========================================
        # UPDATE EVERY 15 MIN
        # =========================================

        time.sleep(900)

    except Exception as e:

        print("Error:", e)

        time.sleep(30)