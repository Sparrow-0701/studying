import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta

def get_trading_intensity(ticker, period='700d'):
    data = yf.download(ticker, period, progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    data.ta.sma(length=5, append=True)
    data.ta.sma(length=20, append=True)
    data.ta.sma(length=100, append=True)
    data.ta.sma(close='volume', length=365, append=True, col_names=('Average_Volume_365'))
    data.ta.rsi(length=365, append=True, col_names=('rsi_365'))
    
    latest_data = data.iloc[-1]
    
    buy_score={'mean':0, 'sma':0, 'rsi':0 ,'volume':0, 'drawdown':0}
    
    #이평선
    if latest_data['Close'] >= latest_data['SMA_5']:
        buy_score['sma'] += 5
    if latest_data['Close'] >= latest_data['SMA_20']:
        buy_score['sma'] += 20
    if latest_data['Close'] >= latest_data['SMA_100']:
        buy_score['sma'] += 30
    if latest_data['SMA_5'] <= latest_data['SMA_20'] <= latest_data['SMA_100']:
        buy_score['sma'] -= 70
    
    #RSI
    if latest_data['rsi_365'] <= 30:
        buy_score['rsi'] += 40
    elif latest_data['rsi_365'] <= 50:
        buy_score['rsi'] += 10
    elif latest_data['rsi_365'] <= 70:
        buy_score['rsi'] -= 10
    elif latest_data['rsi_365'] > 70:
        buy_score['rsi'] -= 40
    
    #Drawdown
    high = data['Close'][-180:].max()
    drawdown = (latest_data['Close'] - high)/high * 100
    if drawdown <= -30:
        buy_score['drawdown'] += 30
    elif drawdown <= -20:
        buy_score['drawdown'] += 20
    elif drawdown <= -10:
        buy_score['drawdown'] += 10
    elif drawdown <= -5:
        buy_score['drawdown'] += 5
    elif drawdown <= 0:
        buy_score['drawdown'] += 0
    
    buy_score['mean'] = np.mean(list(buy_score.values())[1:])
    
    print(f"{buy_score}")


ticker=input("티커:")

get_trading_intensity(ticker)
