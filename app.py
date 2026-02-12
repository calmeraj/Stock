import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📊 AI Stock Strength Dashboard")

# -----------------------------
# Function to fetch stock data
# -----------------------------
@st.cache_data(ttl=900)  # cache for 15 minutes
def get_stock_data(stocks):
    results = []

    for stock in stocks:
        try:
            data = yf.download(stock, period="10d", interval="1d", progress=False)

            if len(data) < 7:
                continue

            # Today's Change %
            today_change = ((data["Close"].iloc[-1] - data["Close"].iloc[-2])
                            / data["Close"].iloc[-2]) * 100

            # 7 Day Change %
            week_change = ((data["Close"].iloc[-1] - data["Close"].iloc[-7])
                           / data["Close"].iloc[-7]) * 100

            results.append({
                "Stock": stock,
                "Today %": round(today_change, 2),
                "7 Day %": round(week_change, 2)
            })

        except Exception:
            continue

    df = pd.DataFrame(results)
    return df


# -----------------------------
# Stock List (You can modify)
# -----------------------------
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "SBIN.NS",
    "ITC.NS"
]

if st.button("🚀 Run Analysis"):

    df = get_stock_data(stocks)

    if df.empty:
        st.warning("No data available")
    else:
        st.subheader("📋 Stock Data")
        st.dataframe(df, use_container_width=True)

        # -----------------------------
        # Chart - 7 Day Performance
        # -----------------------------
        st.subheader("📈 7 Day Performance")

        colors = ["green" if x >= 0 else "red" for x in df["7 Day %"]]

        plt.figure()
        plt.bar(df["Stock"], df["7 Day %"], color=colors)
        plt.xticks(rotation=45)
        plt.axhline(0)
        plt.xlabel("Stock")
        plt.ylabel("7 Day %")
        plt.title("7 Day Stock Performance")
        plt.tight_layout()

        st.pyplot(plt)

        # -----------------------------
        # Top Performers
        # -----------------------------
        st.subheader("🏆 Top Performers")

        top = df.sort_values(by="7 Day %", ascending=False)
        st.dataframe(top, use_container_width=True)
