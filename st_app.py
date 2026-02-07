import streamlit as st
from st_utils import get_historical_data, get_instruments,plot_ohlc
import pandas as pd
import datetime
from datetime import date, timedelta
from technical import add_indicators,compute_adx,compute_atr, plot_chart
from backtestStrategy import backtest_rsi_mean_reversion,plot_price_with_trades,performance_metrics
import matplotlib.pyplot as plt
import ta
import plotly.graph_objects as go
# import json
import numpy as np

def enforce_kite_limits(interval, from_date, to_date):
    max_days = {
        "minute": 60,
        "3minute": 60,
        "5minute": 60,
        "15minute": 60,
        "hour": 180,
        "day": 5000
    }

    allowed_days = max_days.get(interval, 60)
    actual_days = (to_date - from_date).days

    if actual_days > allowed_days:
        from_date = to_date - timedelta(days=allowed_days)

    return from_date, to_date

st.title("📊 Zerodha Kite Dashboard")
# --- Login Token ---
enctoken = st.text_input("🔐 Paste enctoken", type="password")
if not enctoken:
    st.warning("Enter your enctoken from Kite login to proceed.")
    st.stop()
# --- Load instruments ---
# @st.cache_data(ttl=3600)
def load_symbols(enctoken):
    df = get_instruments(enctoken)
    return df
symbols = load_symbols(enctoken)
symbol = st.selectbox("Index", symbols)


# from_date = st.sidebar.date_input("From Date", datetime.date.today())
# to_date = st.sidebar.date_input("To Date", datetime.date.today())
# --- Date/Interval ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    from_date = st.date_input("From Date", datetime.date.today() - datetime.timedelta(days=30))
with col2:
    to_date = st.date_input("To Date" , datetime.date.today())
with col3:
    interval = st.selectbox("Interval", ["day", "5minute", "15minute", "hour"])
# --- Indicators ---
with col4:
    indicators = st.multiselect("Select Strategy", ["Mean reversion", "EMA", "RSI", "MACD"], default=["Mean reversion"])



# --- Fetch Data ---
if st.button("Fetch Data"):
    from_date, to_date = enforce_kite_limits(interval, from_date, to_date)
    df = get_historical_data(enctoken, symbol, interval, from_date, to_date)
    if df is not None and not df.empty:
        st.success(f"{len(df)} rows loaded.")
        st.plotly_chart(plot_ohlc(df), use_container_width=True)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), file_name="historical_data.csv")
    else:
        st.error("No data received. Check token, dates, or interval.")
        
if st.button("Backtesting Mean reversion"):  
    from_date, to_date = enforce_kite_limits(interval, from_date, to_date)
    df = get_historical_data(enctoken, symbol, interval, from_date, to_date)
    df = add_indicators(df)
    df["ADX"] = compute_adx(df,14)
    df["ATR"] = compute_atr(df,14)
    df['%Change'] = ((df['close'] / df['EMA_50'])-1)*100
    df = df.dropna()
    st.plotly_chart(plot_chart(df), use_container_width=True) 
    trades = backtest_rsi_mean_reversion(df)
    st.plotly_chart(plot_price_with_trades(df,trades,symbol))
    metrics = performance_metrics(trades,symbol)
    result = pd.DataFrame([metrics])
    with st.expander("Show the backtest trades and performance",expanded = False):
        st.dataframe(trades)
        st.dataframe(result)
          
# if st.button("Optimize"):
#         result_df = pd.DataFrame()
#         for symbol in selected_symbols:
#             token = instruments_df[instruments_df["tradingsymbol"] == symbol]["instrument_token"].values[0]
#             # Fetch historical data (dummy function, replace with actual API call)
#             df = fetch_historical_data(api_key, access_token, token, interval, from_date, to_date)
#             df["symbol"] = symbol
#             result_df = pd.concat([result_df, df], ignore_index=True)
#             st.write("Optimizing SMA for", symbol)
#             # Add SMA indicators
#             best_fast, best_slow, best_profit = optimize_sma(df,50, 200)
#             st.write("In-sample PF", best_profit, "Best Fast", best_fast, "Best Slow", best_slow)
