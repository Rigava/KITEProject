import streamlit as st
from st_utils import get_historical_data, get_instruments,plot_ohlc
import pandas as pd
import datetime
from datetime import date, timedelta
from technical import add_indicators,compute_adx,compute_atr, plot_chart
from backtestStrategy import backtest_rsi_mean_reversion, backtest_rsi_mean_reversion_adx, plot_price_with_trades,performance_metrics, MACDIndicator
import matplotlib.pyplot as plt
import ta
import plotly.graph_objects as go
# import json
import numpy as np
import requests
import io

def enforce_kite_limits(interval, from_date, to_date):
    max_days = {
        "minute": 60,
        "3minute": 60,
        "5minute": 60,
        "15minute": 60,
        "hour": 180,
        "day": 2000
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
    df = add_indicators(df)
    df["ADX"] = compute_adx(df,14)
    df["ATR"] = compute_atr(df,14)
    df['%Change'] = ((df['close'] / df['EMA_50'])-1)*100
    if df is not None and not df.empty:
        st.success(f"{len(df)} rows loaded.")
        st.plotly_chart(plot_ohlc(df), use_container_width=True)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), file_name="historical_data.csv")
    else:
        st.error("No data received. Check token, dates, or interval.")
#SHORTLIST FEATURE

shortlist_option = st.sidebar.selectbox("select strategy",["RSI","MACD","Value","Breakout"])
rsi_low = st.sidebar.slider("RSI low for buy", min_value=1, max_value=100, value=30, step=1)
rsi_high = st.sidebar.slider("RSI high for sell", min_value=1, max_value=100, value=70, step=1) 
if st.button("Shortlist", use_container_width=True):
    Buy = []
    Sell = []
    Hold = []
    framelist = [] # add OHLC data
    data =[] # add fundamental data
    url = "https://raw.githubusercontent.com/Rigava/DataRepo{}.csv".format("NSE_FN0_upload")
    download = requests.get(url).content
    nse_data = pd.read_csv(io.StringIO(download.decode('utf-8')))   
    symbol_list = nse_data['zerodha name'].unique()
    # symbols_list = ["AARTI INDUSTRIES","ABB INDIA","GACM TECHNOLOGIES","STYRENIX PERFORMANCE","ACC","ADANI ENTERPRISES","ADOR WELDING","AEGIS LOGISTICS","SANWARIA CONSUMER","HAPPIEST MINDS TECHNO","ALEMBIC","ROUTE MOBILE","ANDHRA SUGARS","GODREJ AGROVET"]
    for stock in symbols_list:
        from_date, to_date = enforce_kite_limits(interval, from_date, to_date)
        df = get_historical_data(enctoken, symbol, interval, from_date, to_date)
        # df = yf.download(tickers=yf_tick, period="1y")
        # df.columns = df.columns.get_level_values(0)
        df = MACDIndicator(df)
        df = add_indicators(df)

        # Determine buy or sell recommendation based on last two rows of the data to provide buy & sell signals
        if shortlist_option=="MACD":                
            if df['Decision MACD'].iloc[-1]=='Buy':    
                Buy.append(stock)
            elif df['Decision MACD'].iloc[-1]=='Sell':
                Sell.append(stock)
            else:
                Hold.append(stock) 
        if shortlist_option=="RSI":
            if df["RSI"].iloc[-1] > rsi_low and df["RSI"].iloc[-2] < rsi_low: 
                Buy.append(stock)
            elif df["RSI"].iloc[-1] < rsi_high and df["RSI"].iloc[-2] > rsi_high:
                Sell.append(stock)
            else:
                Hold.append(stock)
    # Display stock data and recommendation
    st.write(":blue[List of stock with positive signal]")
    st.table({"Stocks":Buy})
    st.write(":blue[List of stock with negative signal]")
    st.table({"Stocks":Sell})

    
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
        
if st.button("Backtesting Mean reversion wih ADX regime"):  
    from_date, to_date = enforce_kite_limits(interval, from_date, to_date)
    df = get_historical_data(enctoken, symbol, interval, from_date, to_date)
    df = add_indicators(df)
    df["ADX"] = compute_adx(df,14)
    df["ATR"] = compute_atr(df,14)
    df['%Change'] = ((df['close'] / df['EMA_50'])-1)*100
    df = df.dropna()
    st.plotly_chart(plot_chart(df), use_container_width=True) 
    trades = backtest_rsi_mean_reversion_adx(df)
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
