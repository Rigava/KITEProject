import json
import os
import datetime
import requests
import pandas as pd
import plotly.graph_objects as go

def load_access_token():
    with open("loginCredential.json") as f:
        creds = json.load(f)
    api_key = creds["api_key"]
    
    token_file = f"AccessToken/{datetime.date.today()}.json"
    if os.path.exists(token_file):
        with open(token_file) as f:
            access_token = json.load(f)
    else:
        raise FileNotFoundError("Access token not found. Please login and generate it.")
    
    return access_token, api_key

def fetch_historical_data(api_key, access_token, token, interval,from_date, to_date):
    url = f"https://api.kite.trade/instruments/historical/{token}/{interval}"
    params = {
        "from": f"{from_date} 09:15:00",
        "to": f"{to_date} 15:30:00",
        "oi": "1"
    }
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}:{access_token}"
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        candles = response.json()["data"]["candles"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "open_interest"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    else:
        return pd.DataFrame()
    
def plot_ohlc(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(title="OHLC Chart", xaxis_title="Datetime", yaxis_title="Price")
    return fig
