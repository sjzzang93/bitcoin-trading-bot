"""
단타 자동매매 봇
거래량 급증 코인을 찾아서 GPT 추천을 받아 매수하고,
수익 3% 또는 손절 3%에 자동 매도합니다.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
from bithumb_api import BithumbAPI
from volume_scanner import VolumeScanner
from scalping_analyzer import ScalpingAnalyzer
from trading_logger import TradingLogger
from typing import Optional, Dict


class ScalpingBot:
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()

        # API 초기화
        self.bithumb = BithumbAPI(
            api_key=os.getenv('BITHUMB_API_KEY'),
            secret_key=os.getenv('BITHUMB_SECRET_KEY')
        )
        self.scanner = VolumeScanner()
        self.gpt = ScalpingAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = TradingLogger()

        # 설정값
        self.investment_amount = float(os.getenv('INVESTMENT_AMOUNT', 50000))
        self.profit_target = 3.0   # 수익 목표 3%
        self.stop_loss = -1.2      # 손절 -1.2%
        self.scan_interval = 60   # 종목 스캔 주기 (초)
        self.monitor_interval = 5 # 포지션 모니터링 주기 (초)

        # 포지션 정보
        self.position = None  # {'coin': 'XRP', 'entry_price': 1500, 'amount': 0.5}

        print("=" * 80)
        print("🚀 단타 자동매매 봇 시작")
        print("=" * 80)
        print(f"투자 금액: {self.investment_amount:,} KRW")
        print(f"수익 목표: +{self.profit_target}%")
        print(f"손절 기준: {self.stop_loss}%")
        print(f"종목 스캔 주기: {self.scan_interval}초")
        print("=" * 80)
        print()

    def find_trading_opportunity(self) -> Optional[str]:
        """거래 기회 찾기 - 거래량 급증 코인 발견"""
        print("\n" + "="*80)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 거래량 급증 코인 스캔 중...")
        print("="*80)

        # 1. 모멘텀 상위 코인 조회
        momentum_coins = self.scanner.get_top_momentum_coins(top_n=5)

        if not momentum_coins:
            print("❌ 거래 기회 없음")
            return None

        # 발견된 코인 출력
        self.scanner.print_momentum_report(momentum_coins)

        # 2. GPT에게 최적 종목 추천 요청
        print("\n🤖 GPT 분석 중...")
        recommendation = self.gpt.recommend_coin(momentum_coins)

        if not recommendation:
            print("❌ GPT 추천 실패")
            return None

        # 3. 추천 결과 출력
        print("\n" + "="*80)
        print("💡 GPT 추천 결과")
        print("="*80)
        print(f"추천 코인: {recommendation['selected_coin']}")
        print(f"확신도: {recommendation['confidence']}%")
        print(f"진입 타이밍: {recommendation['entry_timing']}")
        print(f"리스크: {recommendation['risk_level']}")
        print(f"이유: {recommendation['reason']}")
        print("="*80)

        # 로그 기록
        self.logger.log_scan(momentum_coins, recommendation)

        # 4. 진입 타이밍이 "즉시"이고 확신도가 60% 이상일 때만 매수
        if recommendation['entry_timing'] == '즉시' and recommendation['confidence'] >= 60:
            return recommendation['selected_coin']
        else:
            print(f"\n⏸️  매수 보류 (진입 타이밍: {recommendation['entry_timing']}, 확신도: {recommendation['confidence']}%)")
            return None

    def execute_buy(self, coin: str) -> bool:
        """매수 실행"""
        try:
            print(f"\n" + "="*80)
            print(f"💰 {coin} 매수 시도")
            print("="*80)

            # 현재가 조회
            ticker = self.bithumb.get_ticker(coin, 'KRW')
            if not ticker:
                print("❌ 시세 조회 실패")
                return False

            current_price = float(ticker['closing_price'])
            print(f"현재가: {current_price:,} KRW")
            print(f"투자 금액: {self.investment_amount:,} KRW")

            # 시장가 매수
            result = self.bithumb.market_buy(coin, self.investment_amount)

            if result:
                # 실제 체결 수량 계산 (수수료 제외)
                buy_amount = self.investment_amount / current_price * 0.9995  # 수수료 0.05% 가정

                self.position = {
                    'coin': coin,
                    'entry_price': current_price,
                    'amount': buy_amount,
                    'entry_time': datetime.now()
                }

                print(f"\n✅ 매수 성공!")
                print(f"   진입가: {current_price:,} KRW")
                print(f"   수량: {buy_amount:.8f} {coin}")
                print(f"   목표가: {current_price * 1.03:,.0f} KRW (+3%)")
                print(f"   손절가: {current_price * 0.97:,.0f} KRW (-3%)")
                print("="*80)

                # 로그 기록
                self.logger.log_buy(coin, current_price, buy_amount, self.investment_amount)

                return True
            else:
                print("❌ 매수 실패")
                return False

        except Exception as e:
            print(f"❌ 매수 오류: {str(e)}")
            return False

    def monitor_position(self):
        """포지션 모니터링 및 자동 매도"""
        if not self.position:
            return

        coin = self.position['coin']
        entry_price = self.position['entry_price']

        # 현재가 조회
        ticker = self.bithumb.get_ticker(coin, 'KRW')
        if not ticker:
            print("시세 조회 실패")
            return

        current_price = float(ticker['closing_price'])

        # 출구 전략 분석
        exit_strategy = self.gpt.analyze_exit_strategy(
            coin=coin,
            entry_price=entry_price,
            current_price=current_price,
            profit_target=self.profit_target,
            stop_loss=self.stop_loss
        )

        # 현재 상태 출력
        profit_rate = exit_strategy['current_profit']
        elapsed_time = (datetime.now() - self.position['entry_time']).seconds

        # 로그 업데이트
        self.logger.update_position(current_price, profit_rate)

        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"{coin} | 진입: {entry_price:,.0f} → 현재: {current_price:,.0f} | "
              f"수익률: {profit_rate:+.2f}% | "
              f"경과: {elapsed_time}초", end="", flush=True)

        # 매도 조건 확인
        if exit_strategy['action'] == 'take_profit':
            print("\n\n" + "="*80)
            print(f"🎯 목표 수익률 달성! (+{self.profit_target}%)")
            print("="*80)
            self.execute_sell("익절")

        elif exit_strategy['action'] == 'stop_loss':
            print("\n\n" + "="*80)
            print(f"🛑 손절선 도달! ({self.stop_loss}%)")
            print("="*80)
            self.execute_sell("손절")

    def execute_sell(self, reason: str):
        """매도 실행"""
        if not self.position:
            return

        try:
            coin = self.position['coin']
            amount = self.position['amount']
            entry_price = self.position['entry_price']

            print(f"💸 {coin} 매도 시도 (사유: {reason})")

            # 현재가 조회
            ticker = self.bithumb.get_ticker(coin, 'KRW')
            if ticker:
                current_price = float(ticker['closing_price'])
                profit_rate = ((current_price - entry_price) / entry_price) * 100

                print(f"진입가: {entry_price:,} KRW")
                print(f"현재가: {current_price:,} KRW")
                print(f"수익률: {profit_rate:+.2f}%")

            # 시장가 매도
            result = self.bithumb.market_sell(coin, amount)

            if result:
                elapsed_time = (datetime.now() - self.position['entry_time']).seconds
                print(f"\n✅ 매도 완료!")
                print(f"   보유 시간: {elapsed_time}초 ({elapsed_time//60}분)")
                print(f"   예상 수익: {self.investment_amount * profit_rate / 100:+,.0f} KRW")
                print("="*80)

                # 로그 기록
                self.logger.log_sell(coin, entry_price, current_price, amount, reason, profit_rate)

                # 포지션 초기화
                self.position = None
            else:
                print("❌ 매도 실패")

        except Exception as e:
            print(f"❌ 매도 오류: {str(e)}")

    def run(self):
        """메인 실행 루프"""
        print("\n자동매매 시작... (Ctrl+C로 종료)\n")

        try:
            while True:
                # 포지션이 없으면 새로운 기회 찾기
                if not self.position:
                    coin = self.find_trading_opportunity()

                    if coin:
                        # 매수 실행
                        success = self.execute_buy(coin)

                        if success:
                            print(f"\n포지션 모니터링 시작... (매 {self.monitor_interval}초)")
                        else:
                            print(f"\n다음 스캔까지 {self.scan_interval}초 대기...")
                            time.sleep(self.scan_interval)
                    else:
                        print(f"\n다음 스캔까지 {self.scan_interval}초 대기...")
                        time.sleep(self.scan_interval)

                # 포지션이 있으면 모니터링
                else:
                    self.monitor_position()
                    time.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("자동매매 종료")

            # 포지션이 남아있으면 경고
            if self.position:
                print(f"\n⚠️  경고: {self.position['coin']} 포지션이 남아있습니다!")
                print("수동으로 매도하거나 봇을 다시 실행하세요.")

            print("="*80)

        except Exception as e:
            print(f"\n\n오류 발생: {str(e)}")
            if self.position:
                print(f"⚠️  {self.position['coin']} 포지션 확인 필요!")


if __name__ == "__main__":
    bot = ScalpingBot()
    bot.run()
