from datetime import datetime
import ta
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        price = float(df["close"].iloc[i])
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
    
def performance_metrics(trades,sy):
    if trades.empty:
        return {}

    wins = trades[trades["PnL"] > 0]
    losses = trades[trades["PnL"] < 0]

    return {
        "Stok": sy,
        "Trades": len(trades),
        "Win Rate": round(len(wins) / len(trades), 2),
        "Avg Win": wins["PnL"].mean(),
        "Avg Loss": losses["PnL"].mean(),
        "Expectancy": trades["PnL"].mean(),
        "Total PnL": trades["PnL"].sum()
    }
def plot_price_with_trades(df, trades, ticker):
    fig, ax = plt.subplots(figsize=(14, 6))

    # Plot price
    ax.plot(df.index, df["close"], label="Close Price")

    # Plot trades
    for _, trade in trades.iterrows():
        entry = trade["Entry Date"]
        exit_ = trade["Exit Date"]
        direction = trade["Direction"]

        entry_price = df.loc[entry, "close"]
        exit_price = df.loc[exit_, "close"]

        if direction == 1:
            ax.scatter(entry, entry_price, marker="^",color='green')
            ax.scatter(exit_, exit_price, marker="v",color='red')
        else:
            ax.scatter(entry, entry_price, marker="v",color='blue')
            ax.scatter(exit_, exit_price, marker="^",color = 'red')

        ax.plot([entry, exit_], [entry_price, exit_price])

    ax.set_title(f"{ticker} – RSI Mean Reversion Trades")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()

    return fig
