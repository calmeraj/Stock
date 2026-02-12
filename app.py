# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import matplotlib.pyplot as plt

# st.set_page_config(layout="wide")

# st.title("📊 AI Stock Strength Dashboard")

# # -----------------------------
# # Function to fetch stock data
# # -----------------------------
# @st.cache_data(ttl=900)  # cache for 15 minutes
# def get_stock_data(stocks):
#     results = []

#     for stock in stocks:
#         try:
#             data = yf.download(stock, period="10d", interval="1d", progress=False)

#             if len(data) < 7:
#                 continue

#             # Today's Change %
#             today_change = ((data["Close"].iloc[-1] - data["Close"].iloc[-2])
#                             / data["Close"].iloc[-2]) * 100

#             # 7 Day Change %
#             week_change = ((data["Close"].iloc[-1] - data["Close"].iloc[-7])
#                            / data["Close"].iloc[-7]) * 100

#             results.append({
#                 "Stock": stock,
#                 "Today %": round(today_change, 2),
#                 "7 Day %": round(week_change, 2)
#             })

#         except Exception:
#             continue

#     df = pd.DataFrame(results)
#     return df


# # -----------------------------
# # Stock List (You can modify)
# # -----------------------------
# stocks = [
#     "RELIANCE.NS",
#     "TCS.NS",
#     "INFY.NS",
#     "HDFCBANK.NS",
#     "ICICIBANK.NS",
#     "LT.NS",
#     "SBIN.NS",
#     "ITC.NS"
# ]

# if st.button("🚀 Run Analysis"):

#     df = get_stock_data(stocks)

#     if df.empty:
#         st.warning("No data available")
#     else:
#         st.subheader("📋 Stock Data")
#         st.dataframe(df, use_container_width=True)

#         # -----------------------------
#         # Chart - 7 Day Performance
#         # -----------------------------
#         st.subheader("📈 7 Day Performance")

#         # colors = ["green" if x >= 0 else "red" for x in df["7 Day %"]]
#         df["7 Day %"] = pd.to_numeric(df["7 Day %"], errors="coerce")

#         colors = ["green" if float(x) >= 0 else "red"
#             for x in df["7 Day %"].fillna(0)]

#         plt.figure()
#         plt.bar(df["Stock"], df["7 Day %"], color=colors)
#         plt.xticks(rotation=45)
#         plt.axhline(0)
#         plt.xlabel("Stock")
#         plt.ylabel("7 Day %")
#         plt.title("7 Day Stock Performance")
#         plt.tight_layout()

#         st.pyplot(plt)

#         # -----------------------------
#         # Top Performers
#         # -----------------------------
#         st.subheader("🏆 Top Performers")

#         top = df.sort_values(by="7 Day %", ascending=False)
#         st.dataframe(top, use_container_width=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

st.set_page_config(layout="wide")
st.title("📊 Rajkumar Intraday Strength Scanner")

IST = pytz.timezone("Asia/Kolkata")

# ---------------- STOCK LIST ----------------
STOCK_LIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "HDFCBANK.NS"
]

# ---------------- RSI ----------------
def calculate_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ---------------- STOCK ANALYSIS ----------------
def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        sector = info.get("sector", "Unknown")

        # Daily data
        daily = ticker.history(period="30d")
        if daily.empty or len(daily) < 15:
            return None

        prev_day = daily.iloc[-2]
        today = daily.iloc[-1]

        # Intraday 5m
        intraday = ticker.history(period="1d", interval="5m")
        if intraday.empty or len(intraday) < 5:
            return None

        intraday = intraday.reset_index()
        intraday['Datetime'] = intraday['Datetime'].dt.tz_convert(IST)

        intraday['RSI'] = calculate_rsi(intraday['Close'])

        # Opening Range
        open_range = intraday[
            (intraday['Datetime'].dt.time >= datetime.strptime("09:15", "%H:%M").time()) &
            (intraday['Datetime'].dt.time <= datetime.strptime("09:20", "%H:%M").time())
        ]

        if open_range.empty:
            return None

        orb_high = open_range['High'].max()
        orb_low = open_range['Low'].min()

        after_open = intraday[
            intraday['Datetime'].dt.time > datetime.strptime("09:19", "%H:%M").time()
        ]

        orb_high_break = after_open[after_open['High'] > orb_high]
        prev_high_break = intraday[intraday['High'] > prev_day['High']]

        breakout_type = None
        breakout_time = None

        if not orb_high_break.empty:
            breakout_type = "ORB_HIGH"
            breakout_time = orb_high_break.iloc[0]['Datetime'].strftime("%H:%M")
        elif not prev_high_break.empty:
            breakout_type = "PREV_HIGH"
            breakout_time = prev_high_break.iloc[0]['Datetime'].strftime("%H:%M")

        # Strength Logic
        price_change_pct = (today['Close'] - prev_day['Close']) / prev_day['Close'] * 100
        avg_range = (daily['High'] - daily['Low']).tail(10).mean()
        r_factor = abs(today['Close'] - prev_day['Close']) / avg_range if avg_range else 0
        volume_ratio = today['Volume'] / daily['Volume'].tail(10).mean()

        strength = (
            r_factor * 3 +
            volume_ratio * 2 +
            (price_change_pct / 100) * 2
        )

        return {
            "Stock": symbol,
            "Sector": sector,
            "Close": round(today['Close'], 2),
            "Change %": round(price_change_pct, 2),
            "RSI": round(intraday['RSI'].iloc[-1], 2),
            "R-Factor": round(r_factor, 2),
            "Volume Ratio": round(volume_ratio, 2),
            "Strength": round(strength, 2),
            "Breakout Type": breakout_type,
            "Breakout Time": breakout_time
        }

    except:
        return None


# ---------------- RUN SCANNER ----------------
@st.cache_data(ttl=600)
def run_scanner():
    results = []

    for stock in STOCK_LIST:
        res = analyze_stock(stock)
        if res:
            results.append(res)

    return pd.DataFrame(results)


# ---------------- UI ----------------
if st.button("🚀 Run Scanner"):

    df = run_scanner()

    if df.empty:
        st.warning("No data collected")
    else:
        df = df.sort_values("Strength", ascending=False)

        st.subheader("📋 Stock Strength")
        st.dataframe(df, use_container_width=True)

        # -------- Sector Strength
        sector_df = (
            df.groupby("Sector")["Strength"]
            .mean()
            .reset_index()
            .sort_values("Strength", ascending=False)
        )

        st.subheader("📊 Sector Strength")
        st.dataframe(sector_df, use_container_width=True)
