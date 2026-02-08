import matplotlib.pyplot as plt
from datetime import datetime
import ta
import plotly.graph_objects as go
import json
import pandas as pd
import numpy as np


# Technical Indicators
def add_indicators(df):
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    df["EMA_20"] = ta.trend.EMAIndicator(df["close"], 20).ema_indicator()
    df["EMA_50"] = ta.trend.EMAIndicator(df["close"], 50).ema_indicator()
    df["MACD"] = ta.trend.MACD(df["close"]).macd()
    df["MACD_SIGNAL"] = ta.trend.MACD(df["close"]).macd_signal()
    return df
def compute_adx(df, period=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]
    # Directional Movement
    up_move = high.diff()
    down_move = low.shift() - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    # True Range
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Wilder smoothing
    atr = tr.rolling(period).mean()
    plus_di = 100 * (
        pd.Series(plus_dm, index=df.index).rolling(period).mean() / atr
    )
    minus_di = 100 * (
        pd.Series(minus_dm, index=df.index).rolling(period).mean() / atr
    )
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(period).mean()
    return adx
def compute_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# Plotly Charts
def plot_chart(df):
    fig = go.Figure()
    fig.add_candlestick(
        x=df.date,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    )
    fig.add_trace(go.Scatter(
        x=df.date,
        y=df["EMA_20"],
        name="EMA 20"
    ))
    fig.add_trace(go.Scatter(
        x=df.date,
        y=df["EMA_50"],
        name="EMA 50"
    ))
    fig.update_layout(height=600)
    return fig
