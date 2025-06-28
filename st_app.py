import streamlit as st
from st_utils import load_access_token, fetch_historical_data,plot_ohlc
import pandas as pd
import datetime

# Load instrument list
instruments_df = pd.read_csv("https://api.kite.trade/instruments") # Contains 'token' and 'symbol'
# st.write(instruments_df.head())

# Sidebar controls
st.sidebar.title("Kite Dashboard Settings")
selected_equity = st.sidebar.selectbox("Select Instrument type",instruments_df["instrument_type"].unique(), index=0)
# Filter instruments based on selected type
instruments_df = instruments_df[instruments_df["instrument_type"] == selected_equity]
# Select instruments
st.sidebar.subheader("Select Instruments")
selected_symbols = st.sidebar.multiselect("Select symbol", instruments_df["tradingsymbol"].unique(), 
                                          default=instruments_df["tradingsymbol"].iloc[:1])
# from_date = st.sidebar.date_input("From Date", datetime.date.today())
# to_date = st.sidebar.date_input("To Date", datetime.date.today())
# --- Date/Interval ---
col1, col2, col3 = st.columns(3)
with col1:
    from_date = st.date_input("From Date")
with col2:
    to_date = st.date_input("To Date")
with col3:
    interval = st.selectbox("Interval", ["day", "5minute", "15minute", "hour"])
# Load access token
access_token, api_key = load_access_token()

# Main UI
st.title("📊 Kite Instrument Dashboard")
selected_df = instruments_df[instruments_df["tradingsymbol"].isin(selected_symbols)]
st.write(selected_df)
if st.button("Fetch Data"):
    result_df = pd.DataFrame()
    for symbol in selected_symbols:
        token = instruments_df[instruments_df["tradingsymbol"] == symbol]["instrument_token"].values[0]
        # Fetch historical data (dummy function, replace with actual API call)
        df = fetch_historical_data(api_key, access_token, token, interval, from_date, to_date)
        df["symbol"] = symbol
        result_df = pd.concat([result_df, df], ignore_index=True)
        # Display summary statistics
        st.subheader("Summary Statistics")
        st.write(dict(result_df.dtypes))      
    if not result_df.empty:
        st.success("Data fetched successfully!")
        st.success(f"{len(df)} rows loaded.")
        st.dataframe(result_df)
        # Plot
        for sym in result_df["symbol"].unique():
            st.subheader(f"Price Chart: {sym}")
            df_plot = result_df[result_df["symbol"] == sym][["timestamp", "open", "high", "low", "close"]]
            st.dataframe(df_plot)
            st.plotly_chart(plot_ohlc(df_plot))



        # Download
        csv = result_df.to_csv(index=False).encode()
        st.download_button("Download as CSV", csv, f"historical_data_{datetime.date.today()}.csv")
    else:
        st.warning("No data returned.")
    
