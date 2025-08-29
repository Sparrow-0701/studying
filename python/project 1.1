import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta
import datetime as dt

today=dt.datetime.now().date()
period=today - dt.timedelta(days=700)

def get_trading_intensity(ticker, prd=period):
    data = yf.download(ticker, prd, progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    
    data.ta.sma(length=5, append=True)
    data.ta.sma(length=20, append=True)
    data.ta.sma(length=50, append=True)
    data.ta.sma(length=100, append=True)
    data.ta.sma(close='volume', length=700, append=True, col_names=('Average_Volume_700'))
    data.ta.rsi(length=14, append=True, col_names=('rsi_14'))
    
    latest_data = data.iloc[-1]
    latest_price=latest_data['Close']
    buy_score={'mean':0, 'sma':0, 'rsi':0 ,'volume':0, 'drawdown':0}
    high = data['Close'][-365:].max()
    drawdown = (latest_price - high)/high * 100
    
    
    
    """ #이평선(누적합)
    if latest_price >= latest_data['SMA_5']:
        buy_score['sma'] += 5
    if latest_price >= latest_data['SMA_20']:
        buy_score['sma'] += 20
    if latest_price >= latest_data['SMA_100']:
        buy_score['sma'] += 30
    #역배열
    if latest_data['SMA_5'] <= latest_data['SMA_20'] <= latest_data['SMA_50'] <= latest_data['SMA_100']:
        buy_score['sma'] -= 80
    
    #RSI
    if latest_data['rsi_14'] <= 30:
        buy_score['rsi'] += 40
    elif latest_data['rsi_14'] <= 50:
        buy_score['rsi'] += 20
    elif latest_data['rsi_14'] <= 70:
        buy_score['rsi'] -= 10
    elif latest_data['rsi_14'] > 70:
        buy_score['rsi'] -= 40
    
    #Drawdown
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
    elif drawdown > 0:
        buy_score['drawdown'] -= 10 """
    
    
    #눌림매수
    #RSI
    if latest_data['rsi_14'] <= 25:
        buy_score['rsi'] += 100
    elif latest_data['rsi_14'] <= 30:
        buy_score['rsi'] += 60
    elif latest_data['rsi_14'] <= 35:
        buy_score['rsi'] += 40
    
    #낙폭
    if drawdown <= -20:
        buy_score['drawdown'] += 50
    elif drawdown <= -10:
        buy_score['drawdown'] += 30
    elif drawdown <= -5:
        buy_score['drawdown'] += 20
    
    #이평선
    if latest_price >= latest_data['SMA_20'] and latest_price <= latest_data['SMA_5']:
        buy_score['sma'] += 30
    elif latest_price >= latest_data['SMA_50'] and latest_price <= latest_data['SMA_20']:
        buy_score['sma'] += 50
    elif latest_price >= latest_data['SMA_100'] and latest_price <= latest_data['SMA_50']:
        buy_score['sma'] += 80
    
    
    buy_score['mean'] = np.mean(list(buy_score.values())[1:])
    
    print(f"{buy_score}")


while True:
    ticker=input("분석할 티커를 입력하세요 (종료: stop): ")
    if ticker=='stop':
        print("프로그램을 종료합니다.")
        break
    
    get_trading_intensity(ticker)
