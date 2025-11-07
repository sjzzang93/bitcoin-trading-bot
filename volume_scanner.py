"""
거래량 급증 감지 모듈
빗썸의 여러 코인을 스캔하여 거래량이 급증한 코인을 찾습니다.
"""

import requests
from typing import List, Dict, Optional
import time


class VolumeScanner:
    def __init__(self):
        self.base_url = "https://api.bithumb.com"
        self.previous_volumes = {}  # 이전 거래량 저장

        # 모니터링할 주요 코인 (빗썸 TOP 코인들)
        self.coins = [
            'BTC', 'ETH', 'XRP', 'ADA', 'DOT',
            'DOGE', 'MATIC', 'SOL', 'AVAX', 'LINK',
            'TRX', 'ETC', 'BCH', 'LTC', 'XLM',
            'ATOM', 'SAND', 'MANA', 'AXS', 'CHZ'
        ]

    def get_all_tickers(self) -> Optional[Dict]:
        """전체 코인의 현재 시세 조회"""
        try:
            url = f"{self.base_url}/public/ticker/ALL_KRW"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data['status'] == '0000':
                return data['data']
            else:
                print(f"시세 조회 실패: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"시세 조회 오류: {str(e)}")
            return None

    def calculate_volume_change(self, coin: str, current_volume: float) -> Optional[float]:
        """거래량 변화율 계산"""
        if coin not in self.previous_volumes:
            self.previous_volumes[coin] = current_volume
            return None

        prev_volume = self.previous_volumes[coin]
        if prev_volume == 0:
            return None

        change_rate = ((current_volume - prev_volume) / prev_volume) * 100
        self.previous_volumes[coin] = current_volume

        return change_rate

    def scan_volume_surge(self, min_surge_rate: float = 20.0) -> List[Dict]:
        """
        거래량 급증 코인 스캔

        Args:
            min_surge_rate: 최소 거래량 증가율 (기본 20%)

        Returns:
            급증한 코인 리스트 [{coin, price, volume, surge_rate, price_change}, ...]
        """
        try:
            all_data = self.get_all_tickers()
            if not all_data:
                return []

            surge_coins = []

            for coin in self.coins:
                if coin not in all_data:
                    continue

                coin_data = all_data[coin]

                # 거래량 (24시간)
                try:
                    volume_24h = float(coin_data.get('units_traded_24H', 0))
                    price = float(coin_data.get('closing_price', 0))
                    price_change = float(coin_data.get('fluctate_rate_24H', 0))

                    # 최소 거래량 필터 (너무 작은 코인 제외)
                    if volume_24h < 100:  # 24시간 거래량이 100 이하면 제외
                        continue

                    # 거래량 변화율 계산
                    volume_change = self.calculate_volume_change(coin, volume_24h)

                    # 초기 실행 시에는 건너뛰기
                    if volume_change is None:
                        continue

                    # 거래량이 급증한 경우
                    if volume_change >= min_surge_rate:
                        surge_coins.append({
                            'coin': coin,
                            'price': price,
                            'volume_24h': volume_24h,
                            'volume_change': volume_change,
                            'price_change_24h': price_change
                        })

                except (ValueError, TypeError) as e:
                    continue

            # 거래량 증가율 순으로 정렬
            surge_coins.sort(key=lambda x: x['volume_change'], reverse=True)

            return surge_coins

        except Exception as e:
            print(f"거래량 스캔 오류: {str(e)}")
            return []

    def get_top_momentum_coins(self, top_n: int = 5) -> List[Dict]:
        """
        모멘텀 상위 코인 조회
        거래량 증가 + 가격 상승을 종합 평가

        Returns:
            상위 N개 코인 정보
        """
        try:
            all_data = self.get_all_tickers()
            if not all_data:
                return []

            momentum_coins = []

            for coin in self.coins:
                if coin not in all_data:
                    continue

                coin_data = all_data[coin]

                try:
                    volume_24h = float(coin_data.get('units_traded_24H', 0))
                    price = float(coin_data.get('closing_price', 0))
                    price_change = float(coin_data.get('fluctate_rate_24H', 0))
                    acc_trade_value = float(coin_data.get('acc_trade_value_24H', 0))

                    # 최소 거래대금 필터 (1억원 이상)
                    if acc_trade_value < 100000000:
                        continue

                    # 모멘텀 스코어 계산
                    # 거래대금(가중치 0.4) + 가격변동률(가중치 0.6)
                    momentum_score = (acc_trade_value / 1000000000) * 0.4 + price_change * 0.6

                    momentum_coins.append({
                        'coin': coin,
                        'price': price,
                        'volume_24h': volume_24h,
                        'price_change_24h': price_change,
                        'trade_value_24h': acc_trade_value,
                        'momentum_score': momentum_score
                    })

                except (ValueError, TypeError):
                    continue

            # 모멘텀 스코어 순으로 정렬
            momentum_coins.sort(key=lambda x: x['momentum_score'], reverse=True)

            return momentum_coins[:top_n]

        except Exception as e:
            print(f"모멘텀 조회 오류: {str(e)}")
            return []

    def print_surge_report(self, surge_coins: List[Dict]):
        """거래량 급증 리포트 출력"""
        if not surge_coins:
            print("거래량 급증 코인 없음")
            return

        print("\n" + "="*80)
        print("🚀 거래량 급증 코인 발견!")
        print("="*80)

        for i, coin_info in enumerate(surge_coins, 1):
            print(f"\n[{i}] {coin_info['coin']}")
            print(f"    현재가: {coin_info['price']:,} KRW")
            print(f"    24시간 가격 변동: {coin_info['price_change_24h']:+.2f}%")
            print(f"    거래량 증가율: {coin_info['volume_change']:+.2f}%")
            print(f"    24시간 거래량: {coin_info['volume_24h']:,.2f}")

        print("="*80)

    def print_momentum_report(self, momentum_coins: List[Dict]):
        """모멘텀 리포트 출력"""
        if not momentum_coins:
            print("모멘텀 코인 없음")
            return

        print("\n" + "="*80)
        print("📈 단기 모멘텀 TOP 코인")
        print("="*80)

        for i, coin_info in enumerate(momentum_coins, 1):
            print(f"\n[{i}] {coin_info['coin']}")
            print(f"    현재가: {coin_info['price']:,} KRW")
            print(f"    24시간 가격 변동: {coin_info['price_change_24h']:+.2f}%")
            print(f"    24시간 거래대금: {coin_info['trade_value_24h']/100000000:,.0f}억원")
            print(f"    모멘텀 스코어: {coin_info['momentum_score']:.2f}")

        print("="*80)


# 테스트 코드
if __name__ == "__main__":
    scanner = VolumeScanner()

    print("거래량 스캐너 테스트")
    print("5초마다 거래량을 체크합니다... (Ctrl+C로 종료)\n")

    try:
        while True:
            # 방법 1: 거래량 급증 감지
            surge_coins = scanner.scan_volume_surge(min_surge_rate=15.0)
            if surge_coins:
                scanner.print_surge_report(surge_coins)

            # 방법 2: 모멘텀 상위 코인
            momentum_coins = scanner.get_top_momentum_coins(top_n=5)
            scanner.print_momentum_report(momentum_coins)

            print("\n다음 체크까지 60초 대기...\n")
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n스캐너 종료")
