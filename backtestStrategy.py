from datetime import datetime
import ta
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def backtest_rsi_mean_reversion(df):
    df = df.copy()
    position = 0
    entry_price = None
    stop_loss = None
    trades = []

    for i in range(1, len(df)):
        price = float(df["price"].iloc[i])
        rsi = df["RSI"].iloc[i]
        atr = df["ATR"].iloc[i]
        adx =  df["ADX"].iloc[i]
        # Skip invalid rows
        if pd.isna(rsi) or pd.isna(atr):
            continue

        # ENTRY
        if position == 0:
            if rsi <= 30 :
                position = 1
                entry_price = price
                stop_loss = price - 2 * atr
                entry_index = df.index[i] # for plottung trades
                entry_date =df['date'].iloc[i]

            elif rsi >= 70:
                position = -1
                entry_price = price
                stop_loss = price + 2 * atr
                entry_index = df.index[i]
                entry_date =df['date'].iloc[i]

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
                exit_index = df.index[i]
                exit_date = df['date'].iloc[i]
                holding_period = exit_date - entry_date
                holding_counter = exit_index-entry_index
                pnl = (price - entry_price) * position
                trades.append({
                    # "Entry Index": entry_index,
                    "Entry Date": entry_date,
                    "Entry Price": entry_price,
                    # "Exit Index": df.index[i],
                    "Interval row": holding_counter,
                    "Duration": holding_period,
                    "Exit Date": df['date'].iloc[i],
                    "Exit Price": price,
                    "Direction": position,
                    "PnL": pnl
                })
                position = 0

    return pd.DataFrame(trades)
def backtest_rsi_mean_reversion_adx(df):
    df = df.copy()
    position = 0
    entry_price = None
    stop_loss = None
    trades = []

    for i in range(1, len(df)):
        price = float(df["price"].iloc[i])
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
                entry_index = df.index[i] # for plottung trades
                entry_date =df['date'].iloc[i]

            elif rsi >= 70 and adx < 20:
                position = -1
                entry_price = price
                stop_loss = price + 2 * atr
                entry_index = df.index[i]
                entry_date =df['date'].iloc[i]

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
                exit_index = df.index[i]
                exit_date = df['date'].iloc[i]
                holding_period = exit_date - entry_date
                holding_counter = exit_index-entry_index
                pnl = (price - entry_price) * position
                trades.append({
                    # "Entry Index": entry_index,
                    "Entry Date": entry_date,
                    "Entry Price": entry_price,
                    # "Exit Index": df.index[i],
                    "Interval row": holding_counter,
                    "Duration": holding_period,
                    "Exit Date": df['date'].iloc[i],
                    "Exit Price": price,
                    "Direction": position,
                    "PnL": pnl
                })
                position = 0

    return pd.DataFrame(trades)

def MACDIndicator(df):
    df['EMA12']= df.Close.ewm(span=12).mean()
    df['EMA26']= df.Close.ewm(span=26).mean()
    df['MACD'] = df.EMA12 - df.EMA26
    df['Signal'] = df.MACD.ewm(span=9).mean()
    df['MACD_diff']=df.MACD - df.Signal
    df.loc[(df['MACD_diff']>0) & (df.MACD_diff.shift(1)<0),'Decision MACD']='Buy'
    df.loc[(df['MACD_diff']<0) & (df.MACD_diff.shift(1)>0),'Decision MACD']='Sell'
    df.dropna()
    print('MACD indicators added')
    return df
    
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
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot price
    ax.plot(df.date, df["close"], label="Close Price")

    # Plot trades
    for _, trade in trades.iterrows():
        # entry = trade["Entry Index"] # index from the trade df is used to fetch the entry price in df (stock ohlc data) 
        # exit_ = trade["Exit Index"]
        direction = trade["Direction"]
        # entry_price = df.loc[entry, "close"]
        # exit_price = df.loc[exit_, "close"]
        entry = trade['Entry Date']
        exit_ = trade['Exit Date']
        entry_price = trade['Entry Price']
        exit_price = trade['Exit Price']
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
