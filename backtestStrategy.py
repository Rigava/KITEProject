from datetime import datetime
import ta
import json
import pandas as pd
import numpy as np


def backtest_rsi_mean_reversion(df):
    df = df.copy()
    # df["RSI"] = compute_rsi(df["Close"])
    # df["ATR"] = compute_atr(df)
    # df['ADX'] = compute_adx(df)
    position = 0
    entry_price = None
    stop_loss = None
    trades = []

    for i in range(1, len(df)):
        price = float(df["Close"].iloc[i])
        rsi = df["RSI"].iloc[i]
        atr = df["ATR"].iloc[i]
        adx =  df["ADX"].iloc[i]
        # Skip invalid rows
        if pd.isna(rsi) or pd.isna(atr):
            continue

        # ENTRY
        if position == 0:
            if rsi <= 30 and adx < 20:
                position = 1
                entry_price = price
                stop_loss = price - 2 * atr
                entry_date = df.index[i]

            elif rsi >= 70 and adx < 20:
                position = -1
                entry_price = price
                stop_loss = price + 2 * atr
                entry_date = df.index[i]

        # EXIT
        else:
            exit_trade = False

            if position == 1:
                if rsi >= 50 or price <= stop_loss:
                    exit_trade = True

            elif position == -1:
                if rsi <= 50 or price >= stop_loss:
                    exit_trade = True

            if exit_trade:
                pnl = (price - entry_price) * position
                trades.append({
                    "Entry Date": entry_date,
                    "Entry Price": entry_price,
                    "Exit Date": df.index[i],
                    "Exit Price": price,
                    "Direction": position,
                    "PnL": pnl
                })
                position = 0

    return pd.DataFrame(trades)
