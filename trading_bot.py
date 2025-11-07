import os
import time
from datetime import datetime
from dotenv import load_dotenv
from bithumb_api import BithumbAPI
from gpt_analyzer import GPTAnalyzer
from typing import Dict, Optional


class TradingBot:
    def __init__(self):
        # 환경 변수 로드
        load_dotenv()

        # API 초기화
        self.bithumb = BithumbAPI(
            api_key=os.getenv('BITHUMB_API_KEY'),
            secret_key=os.getenv('BITHUMB_SECRET_KEY')
        )
        self.gpt = GPTAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))

        # 설정값
        self.coin = os.getenv('TRADING_COIN', 'BTC')
        self.currency = os.getenv('TRADING_CURRENCY', 'KRW')
        self.investment_amount = float(os.getenv('INVESTMENT_AMOUNT', 50000))
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))  # 5분

        # 상태 추적
        self.position = None  # 'long' or None
        self.avg_buy_price = 0
        self.buy_amount = 0
        self.last_decision = "hold"

        print(f"===== 비트코인 자동매매 봇 시작 =====")
        print(f"거래 코인: {self.coin}")
        print(f"투자 금액: {self.investment_amount:,} KRW")
        print(f"체크 주기: {self.check_interval}초")
        print("=" * 40)

    def collect_market_data(self) -> Optional[Dict]:
        """시장 데이터 수집"""
        try:
            ticker = self.bithumb.get_ticker(self.coin, self.currency)
            orderbook = self.bithumb.get_orderbook(self.coin, self.currency)
            balance = self.bithumb.get_balance(self.coin)

            if not all([ticker, orderbook, balance]):
                print("시장 데이터 수집 실패")
                return None

            # 잔고 정보 파싱
            btc_balance = float(balance.get(f'total_{self.coin.lower()}', 0))
            krw_balance = float(balance.get('total_krw', 0))
            current_price = float(ticker.get('closing_price', 0))

            return {
                'ticker': ticker,
                'orderbook': orderbook,
                'balance': {
                    'btc_balance': btc_balance,
                    'krw_balance': krw_balance,
                    'btc_value': btc_balance * current_price
                },
                'current_price': current_price
            }
        except Exception as e:
            print(f"데이터 수집 오류: {str(e)}")
            return None

    def execute_trade(self, decision: Dict, market_data: Dict) -> bool:
        """매매 실행"""
        try:
            action = decision['decision']
            current_price = market_data['current_price']
            balance = market_data['balance']

            if action == 'buy':
                # 매수 실행
                if balance['krw_balance'] < self.investment_amount:
                    print(f"잔고 부족: {balance['krw_balance']:,} KRW")
                    return False

                # 투자 금액 조정 (제안된 비율 적용)
                buy_amount = self.investment_amount * decision['suggested_amount']

                print(f"\n[매수 실행]")
                print(f"금액: {buy_amount:,.0f} KRW")
                print(f"이유: {decision['reason']}")
                print(f"확신도: {decision['confidence']}%")

                result = self.bithumb.market_buy(self.coin, buy_amount)
                if result:
                    self.position = 'long'
                    self.avg_buy_price = current_price
                    self.buy_amount = buy_amount / current_price
                    return True

            elif action == 'sell':
                # 매도 실행
                if balance['btc_balance'] <= 0:
                    print("보유 코인 없음")
                    return False

                print(f"\n[매도 실행]")
                print(f"수량: {balance['btc_balance']:.8f} {self.coin}")
                print(f"이유: {decision['reason']}")
                print(f"확신도: {decision['confidence']}%")

                if self.avg_buy_price > 0:
                    profit_rate = ((current_price - self.avg_buy_price) / self.avg_buy_price) * 100
                    print(f"수익률: {profit_rate:+.2f}%")

                result = self.bithumb.market_sell(self.coin, balance['btc_balance'])
                if result:
                    self.position = None
                    self.avg_buy_price = 0
                    self.buy_amount = 0
                    return True

            else:  # hold
                print(f"\n[보유]")
                print(f"이유: {decision['reason']}")
                if self.position == 'long' and self.avg_buy_price > 0:
                    profit_rate = ((current_price - self.avg_buy_price) / self.avg_buy_price) * 100
                    print(f"현재 수익률: {profit_rate:+.2f}%")

            return False

        except Exception as e:
            print(f"매매 실행 오류: {str(e)}")
            return False

    def print_status(self, market_data: Dict):
        """현재 상태 출력"""
        ticker = market_data['ticker']
        balance = market_data['balance']

        print(f"\n{'='*60}")
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"현재가: {market_data['current_price']:,.0f} KRW")
        print(f"24시간 변동: {ticker.get('fluctate_rate_24H', 0)}%")
        print(f"보유 {self.coin}: {balance['btc_balance']:.8f} ({balance['btc_value']:,.0f} KRW)")
        print(f"보유 KRW: {balance['krw_balance']:,.0f} KRW")

        if self.position == 'long' and self.avg_buy_price > 0:
            profit_rate = ((market_data['current_price'] - self.avg_buy_price) / self.avg_buy_price) * 100
            print(f"평균 매수가: {self.avg_buy_price:,.0f} KRW")
            print(f"현재 수익률: {profit_rate:+.2f}%")

        print(f"{'='*60}")

    def run(self):
        """메인 실행 루프"""
        print("\n자동매매 시작... (Ctrl+C로 종료)")

        while True:
            try:
                # 1. 시장 데이터 수집
                market_data = self.collect_market_data()
                if not market_data:
                    print("데이터 수집 실패, 다음 주기 대기...")
                    time.sleep(self.check_interval)
                    continue

                # 2. 현재 상태 출력
                self.print_status(market_data)

                # 3. GPT 분석 요청
                print("\nGPT 분석 중...")
                decision = self.gpt.analyze_market(market_data)

                if not decision:
                    print("GPT 분석 실패, 다음 주기 대기...")
                    time.sleep(self.check_interval)
                    continue

                # 4. 매매 실행
                self.last_decision = decision['decision']
                self.execute_trade(decision, market_data)

                # 5. 다음 체크까지 대기
                print(f"\n다음 체크까지 {self.check_interval}초 대기...")
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                print("\n\n자동매매 종료")
                break
            except Exception as e:
                print(f"\n오류 발생: {str(e)}")
                print(f"{self.check_interval}초 후 재시도...")
                time.sleep(self.check_interval)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
