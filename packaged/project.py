import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta
import datetime as dt
import streamlit as st

today=dt.datetime.now().date()
period=today - dt.timedelta(days=700)

def get_trading_intensity(ticker, prd=period):
    data = yf.download(ticker, start=prd, progress=False, auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
        
    if data.empty:
        st.error(f"'{ticker}'에 대한 데이터를 가져오는 데 실패했습니다. 티커를 확인해 주세요.")
        return None
    
    data.ta.sma(length=5, append=True)
    data.ta.sma(length=20, append=True)
    data.ta.sma(length=50, append=True)
    data.ta.sma(length=100, append=True)
    data.ta.sma(close='volume', length=700, append=True, col_names=('Average_Volume_700'))
    data.ta.rsi(length=14, append=True, col_names=('rsi_14'))
    
    latest_data = data.iloc[-1]
    latest_price=latest_data['Close']
    buy_score={'sma':0, 'rsi':0 ,'volume':0, 'drawdown':0}
    high = data['Close'][-365:].max()
    drawdown = (latest_price - high)/high * 100
    
    #반등 매매
    #RSI
    if latest_data['rsi_14'] <= 25:
        buy_score['rsi'] += 100
    elif latest_data['rsi_14'] <= 30:
        buy_score['rsi'] += 60
    elif latest_data['rsi_14'] <= 35:
        buy_score['rsi'] += 40
    elif latest_data['rsi_14'] <= 40:
        buy_score['rsi'] += 20
    
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
    
    #역배열 이평선일 경우
    if latest_price <= latest_data['SMA_20']<= latest_data['SMA_50']<= latest_data['SMA_100']:
        buy_score['sma'] -= 120
    
    return buy_score

ticker=st.text_input("분석할 티커를 입력하세요(한국 주식 예시:486450.KS): ")

if st.button:
    if ticker:
        result = get_trading_intensity(ticker)
        total = sum(result.values())
        
        st.subheader(f"{ticker.upper()}의 매수 강도 지표")
        
        col, col2 = st.columns(2)
        with col:
            st.write(f'총점: {total}점')
        with col2:
            st.write('세부 점수:')
            st.json(result)
    else:
        st.warning("티커를 입력해 주세요.")
