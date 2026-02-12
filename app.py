import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import pytz
import time

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Rajkumar Intraday Strength Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Rajkumar Intraday Strength Scanner")

IST = pytz.timezone("Asia/Kolkata")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Scanner Settings")

refresh_data = st.sidebar.checkbox("Auto Refresh (5 min)", value=False)
run_button = st.sidebar.button("🚀 Run Scanner")

STOCK_LIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "HDFCBANK.NS"
]

# ================= RSI FUNCTION =================
def calculate_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= STOCK ANALYSIS =================
def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.get_info()
        sector = info.get("sector", "Unknown")

        daily = ticker.history(period="30d", auto_adjust=False)
        if daily.empty or len(daily) < 15:
            return None

        prev_day = daily.iloc[-2]
        today = daily.iloc[-1]

        intraday = ticker.history(period="1d", interval="5m", auto_adjust=False)
        if intraday.empty or len(intraday) < 5:
            return None

        intraday = intraday.reset_index()
        if intraday['Datetime'].dt.tz is not None:
            intraday['Datetime'] = intraday['Datetime'].dt.tz_convert(IST)

        intraday['RSI'] = calculate_rsi(intraday['Close'])

        # -------- 5m Break Logic
        first_5min = intraday.iloc[0]
        first_high = first_5min['High']
        first_low = first_5min['Low']
        after_first = intraday.iloc[1:]

        break_5m_high = after_first[after_first['High'] > first_high]
        break_5m_low = after_first[after_first['Low'] < first_low]

        break_5m_high_time = break_5m_high.iloc[0]['Datetime'].strftime("%H:%M") if not break_5m_high.empty else None
        break_5m_low_time = break_5m_low.iloc[0]['Datetime'].strftime("%H:%M") if not break_5m_low.empty else None

        # -------- Prev Day Break
        prev_high_break = intraday[intraday['High'] > prev_day['High']]
        prev_low_break = intraday[intraday['Low'] < prev_day['Low']]

        prev_high_break_time = prev_high_break.iloc[0]['Datetime'].strftime("%H:%M") if not prev_high_break.empty else None
        prev_low_break_time = prev_low_break.iloc[0]['Datetime'].strftime("%H:%M") if not prev_low_break.empty else None

        # -------- Strength Logic
        price_change_pct = (today['Close'] - prev_day['Close']) / prev_day['Close'] * 100
        avg_range = (daily['High'] - daily['Low']).tail(10).mean()
        r_factor = abs(today['Close'] - prev_day['Close']) / avg_range if avg_range else 0
        volume_ratio = today['Volume'] / daily['Volume'].tail(10).mean()

        strength = r_factor * 3 + volume_ratio * 2 + (price_change_pct / 100) * 2

        return {
            "Stock": symbol,
            "Sector": sector,
            "Close": round(today['Close'], 2),
            "Change %": round(price_change_pct, 2),
            "RSI": round(intraday['RSI'].iloc[-1], 2),
            "R-Factor": round(r_factor, 2),
            "Volume Ratio": round(volume_ratio, 2),
            "Strength": round(strength, 2),
            "Break 5m High Time": break_5m_high_time,
            "Break 5m Low Time": break_5m_low_time,
            "Break Prev High Time": prev_high_break_time,
            "Break Prev Low Time": prev_low_break_time,
        }

    except Exception as e:
        return None

# ================= RUN SCANNER =================
@st.cache_data(ttl=300)
def run_scanner():
    results = []
    for stock in STOCK_LIST:
        res = analyze_stock(stock)
        if res:
            results.append(res)
        time.sleep(0.6)  # prevent rate limit
    return pd.DataFrame(results)

# ================= MAIN EXECUTION =================
if run_button or refresh_data:

    df = run_scanner()

    if df.empty:
        st.warning("No data available")
    else:
        df = df.sort_values("Strength", ascending=False)

        # ================= KPI ROW =================
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Stocks", len(df))
        col2.metric("Strongest Stock", df.iloc[0]["Stock"])
        col3.metric("Top Strength Score", df.iloc[0]["Strength"])
        col4.metric("Positive Stocks", len(df[df["Change %"] > 0]))

        st.markdown("---")

        # ================= SECTOR CHART =================
        st.subheader("📊 Sector Average Change %")

        sector_df = (
            df.groupby("Sector")["Change %"]
            .mean()
            .reset_index()
            .sort_values("Change %", ascending=False)
        )

        fig_sector = px.bar(
            sector_df,
            x="Sector",
            y="Change %",
            color="Change %",
            color_continuous_scale=["red", "yellow", "green"]
        )

        st.plotly_chart(fig_sector, use_container_width=True)

        # ================= STRENGTH CHART =================
        st.subheader("📈 Stock Strength Ranking")

        fig_strength = px.bar(
            df,
            x="Stock",
            y="Strength",
            color="Strength",
            color_continuous_scale=["red", "yellow", "green"]
        )

        st.plotly_chart(fig_strength, use_container_width=True)

        # ================= BREAKOUT SUMMARY =================
        st.subheader("🔥 Breakout Count by Sector")

        break_df = df.copy()
        break_df["Breakout"] = break_df[
            ["Break 5m High Time", "Break Prev High Time"]
        ].notna().any(axis=1)

        sector_break = (
            break_df.groupby("Sector")["Breakout"]
            .sum()
            .reset_index()
            .sort_values("Breakout", ascending=False)
        )

        fig_break = px.bar(
            sector_break,
            x="Sector",
            y="Breakout",
            color="Breakout",
            color_continuous_scale=["red", "orange", "green"]
        )

        st.plotly_chart(fig_break, use_container_width=True)

        # ================= TABLE =================
        st.subheader("📋 Detailed Stock Data")
        st.dataframe(df, use_container_width=True)

# ================= AUTO REFRESH =================
if refresh_data:
    time.sleep(300)
    st.rerun()
