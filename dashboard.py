"""
웹 대시보드 - 핸드폰에서도 접속 가능!
실행: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import signal
import subprocess
from trading_logger import TradingLogger

# 페이지 설정
st.set_page_config(
    page_title="비트코인 단타 봇",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = TradingLogger()

# CSS 스타일
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-positive {
        color: #00ff00;
        font-size: 24px;
        font-weight: bold;
    }
    .metric-negative {
        color: #ff0000;
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def get_bot_status():
    """봇 실행 상태 확인"""
    if os.path.exists('bot.pid'):
        try:
            with open('bot.pid', 'r') as f:
                pid = int(f.read())
            # 프로세스가 실행 중인지 확인
            os.kill(pid, 0)
            return True, pid
        except:
            # PID 파일은 있지만 프로세스는 없음
            os.remove('bot.pid')
            return False, None
    return False, None

def start_bot():
    """봇 시작"""
    is_running, _ = get_bot_status()
    if not is_running:
        # 백그라운드로 봇 실행
        process = subprocess.Popen(
            ['python', 'scalping_bot.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        with open('bot.pid', 'w') as f:
            f.write(str(process.pid))
        return True
    return False

def stop_bot():
    """봇 중지"""
    is_running, pid = get_bot_status()
    if is_running and pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            if os.path.exists('bot.pid'):
                os.remove('bot.pid')
            return True
        except:
            pass
    return False

# 타이틀
st.title("🚀 비트코인 단타 자동매매 대시보드")

# 사이드바 - 봇 제어
with st.sidebar:
    st.header("⚙️ 봇 제어")

    is_running, pid = get_bot_status()

    if is_running:
        st.success(f"✅ 봇 실행 중 (PID: {pid})")

        if st.button("🛑 봇 중지", use_container_width=True):
            if stop_bot():
                st.success("봇을 중지했습니다!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("봇 중지 실패")
    else:
        st.warning("⚠️ 봇 중지됨")

        if st.button("▶️ 봇 시작", use_container_width=True):
            if start_bot():
                st.success("봇을 시작했습니다!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("봇이 이미 실행 중입니다")

    st.divider()

    # 자동 새로고침
    auto_refresh = st.checkbox("자동 새로고침 (5초)", value=True)

    if st.button("🔄 수동 새로고침", use_container_width=True):
        st.rerun()

# 메인 대시보드
col1, col2, col3 = st.columns(3)

# 현재 포지션
position = logger.get_current_position()

with col1:
    st.subheader("💰 현재 포지션")
    if position:
        profit_rate = position.get('profit_rate', 0)
        color_class = "metric-positive" if profit_rate > 0 else "metric-negative"

        st.markdown(f"**코인:** {position['coin']}")
        st.markdown(f"**진입가:** {position['entry_price']:,.0f} KRW")
        st.markdown(f"**현재가:** {position.get('current_price', position['entry_price']):,.0f} KRW")
        st.markdown(f'<p class="{color_class}">수익률: {profit_rate:+.2f}%</p>', unsafe_allow_html=True)

        # 진입 시간
        entry_time = position.get('entry_time', 'N/A')
        st.caption(f"진입: {entry_time}")
    else:
        st.info("포지션 없음")

# 통계
stats = logger.get_stats()

with col2:
    st.subheader("📊 거래 통계")
    st.metric("총 거래", f"{stats['total_trades']}회")
    st.metric("승률", f"{stats['win_rate']:.1f}%")
    st.metric("평균 수익률", f"{stats['avg_profit_rate']:+.2f}%")

with col3:
    st.subheader("🎯 목표")
    st.metric("익절 목표", "+3.0%", delta="목표가")
    st.metric("손절 기준", "-1.2%", delta="손절선")
    st.caption(f"승: {stats['win_trades']} / 패: {stats['lose_trades']}")

st.divider()

# 탭
tab1, tab2, tab3 = st.tabs(["📈 거래 내역", "🔍 최근 스캔", "📉 수익 차트"])

with tab1:
    st.subheader("거래 내역")

    trades = logger.get_trades()

    if trades:
        # 최근 거래부터 표시
        trades_reversed = list(reversed(trades))

        df = pd.DataFrame(trades_reversed)

        # 컬럼명 한글화
        df_display = df[['timestamp', 'coin', 'entry_price', 'exit_price', 'profit_rate', 'reason']].copy()
        df_display.columns = ['시간', '코인', '진입가', '청산가', '수익률(%)', '사유']

        # 수익률에 색상 적용
        def color_profit(val):
            color = 'color: green' if val > 0 else 'color: red'
            return color

        styled_df = df_display.style.applymap(color_profit, subset=['수익률(%)'])

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    else:
        st.info("거래 내역이 없습니다.")

with tab2:
    st.subheader("최근 스캔 결과")

    scans = logger.get_recent_scans(limit=5)

    if scans:
        for scan in reversed(scans):
            with st.expander(f"⏰ {scan['timestamp']}", expanded=False):
                if scan.get('gpt_recommendation'):
                    rec = scan['gpt_recommendation']

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.markdown(f"**추천 코인:** {rec.get('selected_coin', 'N/A')}")
                        st.markdown(f"**확신도:** {rec.get('confidence', 0)}%")

                    with col_b:
                        st.markdown(f"**진입 타이밍:** {rec.get('entry_timing', 'N/A')}")
                        st.markdown(f"**리스크:** {rec.get('risk_level', 'N/A')}")

                    st.markdown(f"**이유:** {rec.get('reason', 'N/A')}")

                st.markdown("**TOP 5 코인:**")
                for i, coin in enumerate(scan.get('top_coins', [])[:5], 1):
                    st.caption(f"{i}. {coin.get('coin', 'N/A')} - {coin.get('price_change_24h', 0):+.2f}%")

    else:
        st.info("스캔 내역이 없습니다.")

with tab3:
    st.subheader("누적 수익률 차트")

    trades = logger.get_trades()

    if trades:
        # 누적 수익률 계산
        cumulative_profit = []
        total = 0
        for trade in trades:
            total += trade['profit_rate']
            cumulative_profit.append(total)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            y=cumulative_profit,
            mode='lines+markers',
            name='누적 수익률',
            line=dict(color='#00ff00' if cumulative_profit[-1] > 0 else '#ff0000', width=3),
            fill='tozeroy'
        ))

        fig.update_layout(
            title="누적 수익률 변화",
            xaxis_title="거래 번호",
            yaxis_title="누적 수익률 (%)",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # 최종 수익률
        final_profit = cumulative_profit[-1]
        profit_color = "green" if final_profit > 0 else "red"

        st.markdown(f'<p style="font-size:24px; color:{profit_color}; text-align:center;">최종 누적: {final_profit:+.2f}%</p>', unsafe_allow_html=True)

    else:
        st.info("차트를 표시할 데이터가 없습니다.")

# 푸터
st.divider()
st.caption("💡 Tip: 핸드폰에서도 이 페이지에 접속할 수 있습니다! (같은 와이파이 필요)")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 자동 새로고침
if auto_refresh:
    time.sleep(5)
    st.rerun()
