"""
알트코인 거래량 급증 단타 봇 (pybithumb 버전)
거래량 급증 코인을 찾아서 GPT 추천을 받아 매수하고,
목표 2% 수익 또는 손절 2%에 자동 매도합니다.
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv
import pybithumb
from volume_scanner import VolumeScanner
from scalping_analyzer import ScalpingAnalyzer
from trading_logger import TradingLogger
from typing import Optional, Dict


class ScalpingBotV2:
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()

        # API 초기화
        api_key = os.getenv('BITHUMB_API_KEY')
        secret_key = os.getenv('BITHUMB_SECRET_KEY')
        self.bithumb = pybithumb.Bithumb(api_key, secret_key)

        self.scanner = VolumeScanner()
        self.gpt = ScalpingAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = TradingLogger()

        # 설정값 (.env에서 로드)
        self.investment_amount = float(os.getenv('INVESTMENT_AMOUNT', 10000))
        self.profit_target = float(os.getenv('PROFIT_TARGET', 2.0))
        self.stop_loss = float(os.getenv('STOP_LOSS', -2.0))
        self.scan_interval = 10   # 종목 스캔 주기 (초) - 단타용 빠른 스캔
        self.monitor_interval = 1 # 포지션 모니터링 주기 (초) - 실시간 감시

        # 포지션 정보
        self.position = None  # {'coin': 'XRP', 'entry_price': 1500, 'amount': 0.5}

        print("=" * 80)
        print("🚀 알트코인 거래량 급증 단타 봇 시작")
        print("=" * 80)
        print(f"투자 금액: {self.investment_amount:,} KRW")
        print(f"수익 목표: +{self.profit_target}%")
        print(f"손절 기준: {self.stop_loss}%")
        print(f"종목 스캔 주기: {self.scan_interval}초")
        print("=" * 80)
        print()

    def find_trading_opportunity(self) -> Optional[str]:
        """거래 기회 찾기 - 알트코인 거래량 폭등 종목 발견"""
        print("\n" + "="*80)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 알트코인 거래량 폭등 종목 스캔 중...")
        print("="*80)

        # 1. 알트코인 거래량 폭등 종목 우선 스캔
        surge_coins = self.scanner.scan_altcoin_volume_surge(min_surge_rate=20.0, min_trade_value=30000000)

        if surge_coins:
            print("\n🔥 거래량 폭등 종목 발견!")
            self.scanner.print_altcoin_surge_report(surge_coins[:5])
            # 폭등 종목을 GPT에게 분석 요청
            momentum_coins = surge_coins[:5]
        else:
            # 폭등 종목이 없으면 모멘텀 상위 코인 조회
            momentum_coins = self.scanner.get_top_momentum_coins(top_n=5, altcoin_only=True)

        if not momentum_coins:
            print("❌ 거래 기회 없음")
            return None

        # 발견된 코인 출력
        if not surge_coins:
            print("\n📈 현재 모멘텀 상위 알트코인:")
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

        # 4. 진입 타이밍이 "즉시"이고 확신도가 50% 이상일 때만 매수
        if recommendation['entry_timing'] == '즉시' and recommendation['confidence'] >= 50:
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
            current_price = pybithumb.get_current_price(coin)
            if not current_price:
                print("❌ 시세 조회 실패")
                return False

            print(f"현재가: {current_price:,} KRW")
            print(f"투자 금액: {self.investment_amount:,} KRW")

            # 매수할 수량 계산
            buy_amount = self.investment_amount / current_price

            # 시장가 매수
            result = self.bithumb.buy_market_order(coin, self.investment_amount)

            if result:
                # 실제 체결 수량 (수수료 0.05% 제외)
                actual_amount = buy_amount * 0.9995

                self.position = {
                    'coin': coin,
                    'entry_price': current_price,
                    'amount': actual_amount,
                    'entry_time': datetime.now()
                }

                target_price = current_price * (1 + self.profit_target / 100)
                stop_price = current_price * (1 + self.stop_loss / 100)

                print(f"\n✅ 매수 성공!")
                print(f"   진입가: {current_price:,} KRW")
                print(f"   수량: {actual_amount:.8f} {coin}")
                print(f"   목표가: {target_price:,.0f} KRW (+{self.profit_target}%)")
                print(f"   손절가: {stop_price:,.0f} KRW ({self.stop_loss}%)")
                print("="*80)

                # 로그 기록
                self.logger.log_buy(coin, current_price, actual_amount, self.investment_amount)

                return True
            else:
                print("❌ 매수 실패")
                return False

        except Exception as e:
            print(f"❌ 매수 오류: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def monitor_position(self):
        """포지션 모니터링 및 자동 매도"""
        if not self.position:
            return

        coin = self.position['coin']
        entry_price = self.position['entry_price']

        # 현재가 조회
        current_price = pybithumb.get_current_price(coin)
        if not current_price:
            print("\r시세 조회 실패", end="", flush=True)
            return

        # 수익률 계산
        profit_rate = ((current_price - entry_price) / entry_price) * 100
        elapsed_time = (datetime.now() - self.position['entry_time']).seconds

        # 로그 업데이트
        self.logger.update_position(current_price, profit_rate)

        # 현재 상태 출력
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"{coin} | 진입: {entry_price:,.0f} → 현재: {current_price:,.0f} | "
              f"수익률: {profit_rate:+.2f}% | "
              f"경과: {elapsed_time}초 ({elapsed_time//60}분)", end="", flush=True)

        # 매도 조건 확인
        if profit_rate >= self.profit_target:
            print("\n\n" + "="*80)
            print(f"🎯 목표 수익률 달성! (+{self.profit_target}%)")
            print("="*80)
            self.execute_sell("익절")

        elif profit_rate <= self.stop_loss:
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
            current_price = pybithumb.get_current_price(coin)
            if current_price:
                profit_rate = ((current_price - entry_price) / entry_price) * 100

                print(f"진입가: {entry_price:,} KRW")
                print(f"현재가: {current_price:,} KRW")
                print(f"수익률: {profit_rate:+.2f}%")

            # 시장가 매도 (전량)
            result = self.bithumb.sell_market_order(coin, amount)

            if result:
                elapsed_time = (datetime.now() - self.position['entry_time']).seconds
                profit_amount = self.investment_amount * profit_rate / 100

                print(f"\n✅ 매도 완료!")
                print(f"   보유 시간: {elapsed_time}초 ({elapsed_time//60}분)")
                print(f"   예상 수익: {profit_amount:+,.0f} KRW")
                print(f"   예상 잔고: {10000 + profit_amount:,.0f} KRW")
                print("="*80)

                # 로그 기록
                self.logger.log_sell(coin, entry_price, current_price, amount, reason, profit_rate)

                # 포지션 초기화
                self.position = None
            else:
                print("❌ 매도 실패 - 다시 시도합니다")

        except Exception as e:
            print(f"❌ 매도 오류: {str(e)}")
            import traceback
            traceback.print_exc()

    def run(self):
        """메인 실행 루프"""
        print("\n🎮 자동매매 시작... (Ctrl+C로 종료)\n")

        try:
            while True:
                # 포지션이 없으면 새로운 기회 찾기
                if not self.position:
                    coin = self.find_trading_opportunity()

                    if coin:
                        # 매수 실행
                        success = self.execute_buy(coin)

                        if success:
                            print(f"\n📊 포지션 모니터링 시작... (매 {self.monitor_interval}초)")
                        else:
                            print(f"\n⏰ 다음 스캔까지 {self.scan_interval}초 대기...")
                            time.sleep(self.scan_interval)
                    else:
                        print(f"\n⏰ 다음 스캔까지 {self.scan_interval}초 대기...")
                        time.sleep(self.scan_interval)

                # 포지션이 있으면 모니터링
                else:
                    self.monitor_position()
                    time.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            print("\n\n" + "="*80)
            print("🛑 자동매매 종료")

            # 포지션이 남아있으면 경고
            if self.position:
                print(f"\n⚠️  경고: {self.position['coin']} 포지션이 남아있습니다!")
                print(f"    진입가: {self.position['entry_price']:,} KRW")
                print(f"    수량: {self.position['amount']:.8f}")
                print("    수동으로 매도하거나 봇을 다시 실행하세요.")

            print("="*80)

        except Exception as e:
            print(f"\n\n❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()

            if self.position:
                print(f"\n⚠️  {self.position['coin']} 포지션 확인 필요!")


if __name__ == "__main__":
    bot = ScalpingBotV2()
    bot.run()
