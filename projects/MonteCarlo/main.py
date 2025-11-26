import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


apikey = "BiZdW7mT53NrkMsw9XCYN6bI5brH350y"

# 1. 설정 및 데이터 수집 함수
#환율 데이터 수집
@st.cache_data(ttl=3600)
def get_exchange_data(start_date, end_date, auth_key):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    collected_data = []

    my_bar = st.progress(0, text = "환율 데이터를 수집 중입니다...")
    total_days = len(date_range)

    for i, target_date in enumerate(date_range):
        my_bar.progress((i + 1) / total_days, text=f"환율 수집 중: {target_date.strftime('%Y-%m-%d')}")
        
        search_date_str = target_date.strftime("%Y%m%d")
        display_date = target_date.strftime("%Y-%m-%d")
        
        url = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
        params = {
            "authkey": auth_key,
            "searchdate": search_date_str,
            "data": "AP01"
        }
        
        try:
            response = requests.get(url, params=params, timeout=3)
            
            if response.status_code == 200 and response.json():
                json_data = response.json()
                daily_record = {'Date': pd.to_datetime(display_date)}
                
                for item in json_data:
                    if item['cur_unit'] == "USD":
                        rate = float(item['deal_bas_r'].replace(",", ""))
                        daily_record['USD_KRW'] = rate
                        break
                
                if 'USD_KRW' in daily_record:
                    collected_data.append(daily_record)
            
            time.sleep(0.05) 
            
        except Exception:
            continue

    my_bar.empty()
    
    if not collected_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(collected_data)
    df.set_index('Date', inplace=True)
    return df

#주식 데이터 수집
@st.cache_data(ttl=3600)
def get_stock_data(tickers, start_date, end_date):
    try:
        df = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        if df.empty:
            return pd.DataFrame()

        if 'Adj Close' in df.columns:
            df = df['Adj Close']
        elif 'Close' in df.columns:
            df = df['Close']
        else:
            try:
                df = df.xs('Adj Close', axis=1, level=0)
            except KeyError:
                df = df.xs('Close', axis=1, level=0)

        if isinstance(df, pd.Series):
            df = df.to_frame(name=tickers[0])
            
        return df
    except Exception as e:
        st.error(f"주가 데이터 수집 에러: {e}")
        return pd.DataFrame()


# 두 함수 결합
def get_merged_market_data(tickers, start, end, auth_key):
    df_stock = get_stock_data(tickers, start, end)
    df_exchange = get_exchange_data(start, end, auth_key)
    
    if df_stock.empty or df_exchange.empty:
        return None

    merged_df = df_stock.join(df_exchange, how='left')
    merged_df['USD_KRW'] = merged_df['USD_KRW'].ffill()
    merged_df['USD_KRW'] = merged_df['USD_KRW'].bfill()
    
    return merged_df


# 2. 몬테카를로 시뮬레이션 함수
def run_monte_carlo(hist_returns, start_price, days, simulations):
    """
    [역사적 부트스트래핑 방식]
    과거 수익률 분포에서 무작위 복원 추출하여 미래 경로 생성
    """
    # size=(days, simulations) -> 미래 날짜 x 시뮬레이션 횟수만큼 뽑기
    random_returns = np.random.choice(hist_returns, size=(days, simulations), replace=True)
    
    # 누적 수익률 계산
    cum_returns = np.exp(np.cumsum(random_returns, axis=0))
    
    # 가격 경로 생성
    price_paths = np.zeros((days + 1, simulations))
    price_paths[0] = start_price
    price_paths[1:] = start_price * cum_returns
    
    return price_paths



#---------------------------------------UI-------------------------------------------


# 3. Streamlit 
st.set_page_config(page_title="Portfolio Pathfinder", page_icon="🛡️", layout="wide")


#사이드바
with st.sidebar:
    st.header("⚙️ 포트폴리오 설정")
    tickers_input = st.text_input("종목 티커 (쉼표 구분)", value="AAPL, GOOGL, NVDA")
    tickers = [t.strip().upper() for t in tickers_input.split(',')]
    
    investment = st.number_input("초기 투자금 (원화)", value=10000000, step=1000000)
    
    api=st.text_input("한국수출입은행 API 키(있는 경우)")
    
    period = st.date_input("과거 데이터 기간", value=(pd.to_datetime("2025-11-01"), pd.to_datetime("2025-11-08")))
    
    # 예측 기간 (일)
    forecast_days = st.slider("미래 예측 기간 (일)", 10, 60, 20)
    simulations = st.slider("시뮬레이션 횟수", 1000, 50000, 2000)
    
    run_btn = st.button("🚀 분석 실행")

st.title("Portfolio PathFinder")
st.markdown(f"**대상:** {tickers} | **투자금:** {investment:,}원 | **분석모델:** Monte Carlo Simulation")

tab1, tab2, tab3 = st.tabs(["📊 데이터(Data)", "🔍 통계(Stats)", "🎲 시뮬레이션(VaR)"])

#버튼
if run_btn:
    
    if api!="":
        MY_AUTH_KEY = api
    else:
        MY_AUTH_KEY = apikey
        
    # 1. 데이터 수집
    market_df = get_merged_market_data(tickers, period[0], period[1], MY_AUTH_KEY)
    
    if market_df is not None and not market_df.empty:
        
        # --- 합성 포트폴리오 만들기 ---
        market_df['Portfolio_KRW'] = 0 #가치 칼럼 생성
        weight = investment / len(tickers) # 종목당 배분 금액
        
        # 기준일(첫날) 주가 대비 현재 주가 비율로 가치 산정
        base_prices = market_df[tickers].iloc[0]
        
        for t in tickers:
            if t in market_df.columns:
                stock_return = market_df[t] / base_prices[t] #현재 가격/원래 가격 --> 수익률
                exchange_return = market_df['USD_KRW'] / market_df['USD_KRW'].iloc[0] #현재 달러/원래 달러 --> 수익률
                
                market_df['Portfolio_KRW'] += (stock_return * exchange_return * weight) #각 수익률 * 종목당 투자금 --> 가치
        
        # ---------------- TAB 1: 데이터 시각화 ----------------
        with tab1:
            st.subheader("1. 원화 환산 포트폴리오 가치 추이")
            st.line_chart(market_df['Portfolio_KRW']) #자산 추이 그래프
            
            st.write("💡 **상세 데이터 (최근 5일)**")
            st.dataframe(market_df.tail()) # 데이터프레임 최근 5일

        # ---------------- TAB 2: 통계 분석 ----------------
        with tab2:
            st.subheader("2. 자산 간 상관관계 히트맵")
            
            # 상관관계 계산 (주가들 + 환율)
            analysis = tickers + ['USD_KRW']
            # 존재하는 컬럼만 선택  
            valid_cols = [c for c in analysis if c in market_df.columns]
            corr = market_df[valid_cols].corr()
            
            # Matplotlib으로 히트맵 그리기
            fig, ax = plt.subplots()
            cax = ax.matshow(corr, cmap='coolwarm')
            fig.colorbar(cax)
            ax.set_xticks(range(len(valid_cols)))
            ax.set_yticks(range(len(valid_cols)))
            ax.set_xticklabels(valid_cols, rotation=45)
            ax.set_yticklabels(valid_cols)
            st.pyplot(fig)
            
            st.info("빨간색에 가까울수록 같이 움직이고, 파란색일수록 반대로 움직입니다.")

        # ---------------- TAB 3: 몬테카를로 & VaR ----------------
        with tab3:
            st.subheader(f"3. 몬테카를로 시뮬레이션 (향후 {forecast_days}일)")
            
            # 일간 수익률 계산
            daily_returns = np.log(market_df['Portfolio_KRW'] / market_df['Portfolio_KRW'].shift(1)).dropna()
            
            # 현재 포트폴리오 가치 (가장 최근 값)
            current_value = market_df['Portfolio_KRW'].iloc[-1]
            
            # 시뮬레이션 실행
            with st.spinner(f'{simulations}개의 미래를 생성하는 중...'):
                sim_paths = run_monte_carlo(daily_returns, current_value, forecast_days, simulations)
            
            # --- 결과 1: 꺾은선 ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("##### 🍝 예상 자산 경로 (상위 100개 샘플)")
                fig_sim, ax_sim = plt.subplots(figsize=(10, 6))
                
                # 너무 많으면 느리니까 100개만 그림, 통계는 전체로 계산
                ax_sim.plot(sim_paths[:, :100], alpha=0.1, color='blue')
                ax_sim.set_title(f"Monte Carlo Paths ({simulations} Simulations)")
                ax_sim.set_xlabel("Days")
                ax_sim.set_ylabel("Portfolio Value (KRW)")
                
                # Y축 천단위 콤마
                ax_sim.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
                st.pyplot(fig_sim)
            
            # --- 결과 2: VaR 및 통계 ---
            with col2:
                # 마지막 날의 자산 가치 분포
                final_values = sim_paths[-1, :]
                
                # 95% VaR 계산 (하위 5% 지점)
                var_95_value = np.percentile(final_values, 5)
                # 현재 가치 대비 손실액
                var_amount = current_value - var_95_value
                
                # 평균 예상 가치
                mean_value = np.mean(final_values)
                
                st.markdown("### 📊 분석 결과")
                st.metric(label="현재 가치", value=f"{int(current_value):,}원")
                st.metric(label="평균 예상 가치", value=f"{int(mean_value):,}원", 
                          delta=f"{int(mean_value - current_value):,}원")
                
                st.divider()
                st.markdown(f"#### ⚠️ 95% VaR ({forecast_days}일)")
                st.error(f"최대 예상 손실: -{int(var_amount):,}원")
                st.caption(f"95% 확률로 포트폴리오 가치는 **{int(var_95_value):,}원** 이상을 유지합니다.")
                
            # 히스토그램 (분포도)
            st.markdown("##### 📉 최종 자산 가치 분포도")
            fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
            ax_hist.hist(final_values, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
            # VaR 선 긋기
            ax_hist.axvline(var_95_value, color='red', linestyle='dashed', linewidth=2, label=f'95% VaR: {int(var_95_value):,}W')
            ax_hist.legend()
            ax_hist.xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
            st.pyplot(fig_hist)

    else:
        st.error("데이터를 불러오지 못했습니다. 티커와 API 키를 확인해주세요.")

else:
    st.info("👈 사이드바에서 설정 후 [분석 실행]을 눌러주세요.")
