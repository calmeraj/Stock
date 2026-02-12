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
    page_title="Market Pulse - Rajkumar",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Market Pulse")

IST = pytz.timezone("Asia/Kolkata")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Scanner Settings")

run_button = st.sidebar.button("🚀 Run Scanner")
auto_refresh = st.sidebar.checkbox("Auto Refresh (5 min)", value=False)

# STOCK_LIST = [
#     "RELIANCE.NS",
#     "TCS.NS",
#     "INFY.NS",
#     "ICICIBANK.NS",
#     "HDFCBANK.NS"
# ]
STOCK_LIST = ['IDEA.NS','BSE.NS', 'INDUSTOWER.NS', 'RBLBANK.NS', 'GLENMARK.NS', 'KFINTECH.NS', 'NATIONALUM.NS', 'EICHERMOT.NS', 'ASTRAL.NS', 'M&M.NS', 'VEDL.NS', 'ASHOKLEY.NS']
# , 
#  'VOLTAS.NS', 'CHOLAFIN.NS','BIOCON.NS', 'CAMS.NS', 'ANGELONE.NS', 'EXIDEIND.NS', 'MARUTI.NS', 'UNOMINDA.NS', 'IRFC.NS', 'NMDC.NS', 'SAIL.NS', 'NYKAA.NS', 'ABCAPITAL.NS', 'TVSMOTOR.NS', 
#  'POWERGRID.NS', 'AMBER.NS', 'DRREDDY.NS', 'LTF.NS', 'RELIANCE.NS', 'PNBHOUSING.NS', 'NAUKRI.NS', 'SHRIRAMFIN.NS', 'PHOENIXLTD.NS', 'PFC.NS', 'PAYTM.NS', 'KAYNES.NS', 'INOXWIND.NS', 
#  'IREDA.NS', 'CANBK.NS', 'CDSL.NS','NUVAMA.NS', 'ETERNAL.NS', 'MAXHEALTH.NS', 'TATAPOWER.NS', 'PPLPHARMA.NS', 'BDL.NS', 'BHARTIARTL.NS', 'SBILIFE.NS', 
#  'AUROPHARMA.NS', 'SUZLON.NS', 'LAURUSLABS.NS', 'RVNL.NS', 'YESBANK.NS', 'MFSL.NS', 'SONACOMS.NS','SUNPHARMA.NS', 'OIL.NS', 'HDFCLIFE.NS', 'SAMMAANCAP.NS', 'KPITTECH.NS', 'HINDALCO.NS', 
#  'IIFL.NS', 'BAJAJFINSV.NS', 'ALKEM.NS', 'BHEL.NS', 'HINDZINC.NS', 'HUDCO.NS', 'BANDHANBNK.NS', 'AXISBANK.NS', 'TATASTEEL.NS', 'RECLTD.NS', 'IDFCFIRSTB.NS', 'NBCC.NS', 'BHARATFORG.NS', '360ONE.NS', 
#  'ASIANPAINT.NS', 'BOSCHLTD.NS', 'TATAELXSI.NS', 'MUTHOOTFIN.NS', 'IRCTC.NS', 'UNIONBANK.NS', 'BANKINDIA.NS', 'FEDERALBNK.NS', 'SHREECEM.NS', 'TITAGARH.NS', 'JSWENERGY.NS', 'PNB.NS', 'COALINDIA.NS', 
#  'BAJFINANCE.NS', 'MOTHERSON.NS', 'JINDALSTEL.NS', 'INDUSINDBK.NS', 'JUBLFOOD.NS', 'LUPIN.NS', 'HEROMOTOCO.NS', 'HDFCBANK.NS', 'ZYDUSLIFE.NS', 'BAJAJ-AUTO.NS', 'MANAPPURAM.NS', 'BANKBARODA.NS', 'TATACONSUM.NS', 'CONCOR.NS', 'ADANIENT.NS', 'DALBHARAT.NS', 'JSWSTEEL.NS', 'HDFCAMC.NS', 'CUMMINSIND.NS', 'DIXON.NS', 'ADANIGREEN.NS', 
#  'INDIANB.NS', 'KALYANKJIL.NS', 'INDHOTEL.NS', 'TRENT.NS', 'LICHSGFIN.NS', 'IOC.NS', 'BLUESTARCO.NS', 'CROMPTON.NS', 'LICI.NS', 'BRITANNIA.NS', 'BPCL.NS', 'HAVELLS.NS', 'PGEL.NS', 'OFSS.NS', 'AMBUJACEM.NS', 'ICICIBANK.NS', 'TIINDIA.NS', 'GRASIM.NS', 
#  'FORTIS.NS', 'SBICARD.NS', 'HFCL.NS', 'KOTAKBANK.NS', 'HINDPETRO.NS', 'SUPREMEIND.NS', 'LTIM.NS', 'AUBANK.NS', 'ADANIENSOL.NS', 'NESTLEIND.NS', 'DLF.NS', 'SBIN.NS', 'NHPC.NS', 'MAZDOCK.NS', 'NCC.NS', 'ULTRACEMCO.NS', 'POLYCAB.NS', 'DELHIVERY.NS', 'GAIL.NS', 'NTPC.NS', 'INDIGO.NS', 'PETRONET.NS', 'BEL.NS', 
#  'ADANIPORTS.NS', 'APLAPOLLO.NS', 'IEX.NS', 'MCX.NS', 'ICICIPRULI.NS', 'CGPOWER.NS', 'WIPRO.NS', 'TORNTPHARM.NS', 'TATACHEM.NS', 'TATATECH.NS', 'ONGC.NS', 'GMRAIRPORT.NS', 'TITAN.NS', 
#  'MANKIND.NS', 'UNITDSPR.NS', 'HAL.NS', 'DMART.NS', 'PIDILITIND.NS', 'PAGEIND.NS', 'ABB.NS', 'MARICO.NS', 'UPL.NS', 'SOLARINDS.NS', 'LT.NS', 'DABUR.NS', 'GODREJCP.NS', 'PATANJALI.NS', 'APOLLOHOSP.NS', 'HINDUNILVR.NS', 'INFY.NS', 'SYNGENE.NS', 'SRF.NS', 'LODHA.NS', 
#  'CYIENT.NS', 'TECHM.NS', 'TCS.NS', 'CIPLA.NS', 'ICICIGI.NS', 'COLPAL.NS', 'HCLTECH.NS', 'IGL.NS', 'OBEROIRLTY.NS', 'COFORGE.NS', 'DIVISLAB.NS', 'GODREJPROP.NS', 'PIIND.NS', 'ITC.NS', 'SIEMENS.NS', 'KEI.NS', 'MPHASIS.NS', 'POLICYBZR.NS', 'TORNTPOWER.NS', 'PRESTIGE.NS', 'PERSISTENT.NS', 'VBL.NS'] 

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

        daily = ticker.history(period="30d")
        if daily.empty or len(daily) < 15:
            return None

        prev_day = daily.iloc[-2]
        today = daily.iloc[-1]

        intraday = ticker.history(period="1d", interval="5m")
        if intraday.empty or len(intraday) < 5:
            return None

        intraday = intraday.reset_index()

        if intraday["Datetime"].dt.tz is not None:
            intraday["Datetime"] = intraday["Datetime"].dt.tz_convert(IST)

        intraday["RSI"] = calculate_rsi(intraday["Close"])

        # ===== 5m Break Logic =====
        first_candle = intraday.iloc[0]
        first_high = first_candle["High"]
        first_low = first_candle["Low"]

        after_first = intraday.iloc[1:]

        break_5m_high = after_first[after_first["High"] > first_high]
        break_5m_low = after_first[after_first["Low"] < first_low]

        break_5m_high_time = (
            break_5m_high.iloc[0]["Datetime"].strftime("%H:%M")
            if not break_5m_high.empty else None
        )

        break_5m_low_time = (
            break_5m_low.iloc[0]["Datetime"].strftime("%H:%M")
            if not break_5m_low.empty else None
        )

        # ===== Prev Day Break =====
        prev_high_break = intraday[intraday["High"] > prev_day["High"]]
        prev_low_break = intraday[intraday["Low"] < prev_day["Low"]]

        prev_high_break_time = (
            prev_high_break.iloc[0]["Datetime"].strftime("%H:%M")
            if not prev_high_break.empty else None
        )

        prev_low_break_time = (
            prev_low_break.iloc[0]["Datetime"].strftime("%H:%M")
            if not prev_low_break.empty else None
        )

        # ===== Strength Logic =====
        price_change_pct = (today["Close"] - prev_day["Close"]) / prev_day["Close"] * 100
        avg_range = (daily["High"] - daily["Low"]).tail(10).mean()
        r_factor = abs(today["Close"] - prev_day["Close"]) / avg_range if avg_range else 0
        volume_ratio = today["Volume"] / daily["Volume"].tail(10).mean()

        strength = r_factor * 3 + volume_ratio * 2 + (price_change_pct / 100) * 2

        return {
            "Stock": symbol,
            "Sector": sector,
            "Close": round(today["Close"], 2),
            "Change %": round(price_change_pct, 2),
            "RSI": round(intraday["RSI"].iloc[-1], 2),
            "R-Factor": round(r_factor, 2),
            "Volume Ratio": round(volume_ratio, 2),
            "Strength": round(strength, 2),
            "Break 5m High Time": break_5m_high_time,
            "Break 5m Low Time": break_5m_low_time,
            "Break Prev High Time": prev_high_break_time,
            "Break Prev Low Time": prev_low_break_time,
        }

    except:
        return None

# ================= RUN SCANNER =================
@st.cache_data(ttl=300)
def run_scanner():
    results = []
    for stock in STOCK_LIST:
        res = analyze_stock(stock)
        if res:
            results.append(res)
        time.sleep(0.6)
    return pd.DataFrame(results)

# ================= MAIN EXECUTION =================
if run_button or auto_refresh:

    df = run_scanner()

    if df.empty:
        st.warning("No data available")
    else:

        df = df.sort_values("Strength", ascending=False)

        # ===== KPI CARDS =====
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Stocks", len(df))
        col2.metric("Strongest Stock", df.iloc[0]["Stock"])
        col3.metric("Top Strength", df.iloc[0]["Strength"])
        col4.metric("Positive Stocks", len(df[df["Change %"] > 0]))

        st.markdown("---")

        # ================= MARKET PULSE =================
        st.markdown("## 🔥 Market Pulse")

        col_left, col_right = st.columns(2)

        # ===== Breakout Beacon =====
        with col_left:
            st.markdown("### 🚨 Breakout Beacon")
        
            breakout_df = df[
                df["Break 5m High Time"].notna() |
                df["Break Prev High Time"].notna() |
                df["Break Prev Low Time"].notna()
            ].copy()
        
            if not breakout_df.empty:
        
                # ===== ADD LATEST BREAK TIME COLUMN =====
                def get_latest_break(row):
                    times = [
                        row["Break 5m High Time"],
                        row["Break 5m Low Time"],
                        row["Break Prev High Time"],
                        row["Break Prev Low Time"],
                    ]
        
                    times = [t for t in times if pd.notna(t)]
        
                    if times:
                        return max(times, key=lambda t: datetime.strptime(t, "%H:%M"))
                    else:
                        return None
        
                breakout_df["Latest Break Time"] = breakout_df.apply(get_latest_break, axis=1)
        
                # Optional: sort by latest time descending
                breakout_df = breakout_df.sort_values("Latest Break Time", ascending=False)
        
                st.dataframe(
                    breakout_df[
                        [
                            "Stock",
                            "Break 5m High Time",
                            "Break 5m Low Time",
                            "Break Prev High Time",
                            "Break Prev Low Time",
                            "Latest Break Time",
                        ]
                    ],
                    use_container_width=True
                )
        
            else:
                st.info("No breakout stocks")

        # with col_left:
        #     st.markdown("### 🚨 Breakout Beacon")

        #     breakout_df = df[
        #         df["Break 5m High Time"].notna() |
        #         df["Break Prev High Time"].notna() |
        #         df["Break Prev Low Time"].notna()
        #     ]
            
            

        #     if not breakout_df.empty:
        #         st.dataframe(breakout_df, use_container_width=True)
        #     else:
        #         st.info("No breakout stocks")

        # ===== Intraday Boost =====
        with col_right:
            st.markdown("### 🚀 Intraday Boost")

            boost_df = df.sort_values("R-Factor", ascending=False).head(10)
            boost_df["Direction"] = np.where(
                boost_df["Change %"] > 0, "UP", "DOWN"
            )
            boost_df = boost_df[['Stock','Close','Change %','Strength','Direction']]

            if not boost_df.empty:
                st.dataframe(boost_df, use_container_width=True)
            else:
                st.info("No breakout stocks")
                     

            # fig_boost = px.bar(
            #     boost_df,
            #     x="Stock",
            #     y="R-Factor",
            #     color="Direction",
            #     color_discrete_map={
            #         "UP": "green",
            #         "DOWN": "red"
            #     }
            # )

            # st.plotly_chart(fig_boost, use_container_width=True)

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

        # ================= TABLE =================
        st.subheader("📋 Detailed Data")
        st.dataframe(df, use_container_width=True)

# ===== AUTO REFRESH =====
if auto_refresh:
    time.sleep(300)
    st.rerun()
