import requests
import time
import hmac
import hashlib
import urllib.parse
from typing import Dict, Optional


class BithumbAPI:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.bithumb.com"

    def _get_signature(self, endpoint: str, params: Dict) -> tuple:
        """API 요청 서명 생성"""
        nonce = str(int(time.time() * 1000))
        params_str = urllib.parse.urlencode(params)

        payload = endpoint + chr(0) + params_str + chr(0) + nonce
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return signature, nonce

    def get_ticker(self, coin: str = "BTC", currency: str = "KRW") -> Optional[Dict]:
        """현재가 정보 조회"""
        try:
            url = f"{self.base_url}/public/ticker/{coin}_{currency}"
            response = requests.get(url)
            data = response.json()

            if data['status'] == '0000':
                return data['data']
            else:
                print(f"Ticker 조회 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"Ticker 조회 오류: {str(e)}")
            return None

    def get_orderbook(self, coin: str = "BTC", currency: str = "KRW") -> Optional[Dict]:
        """호가 정보 조회"""
        try:
            url = f"{self.base_url}/public/orderbook/{coin}_{currency}"
            response = requests.get(url)
            data = response.json()

            if data['status'] == '0000':
                return data['data']
            else:
                print(f"Orderbook 조회 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"Orderbook 조회 오류: {str(e)}")
            return None

    def get_balance(self, currency: str = "BTC") -> Optional[Dict]:
        """잔고 조회"""
        try:
            endpoint = "/info/balance"
            params = {
                "order_currency": currency,
                "payment_currency": "KRW"
            }

            signature, nonce = self._get_signature(endpoint, params)

            headers = {
                "Api-Key": self.api_key,
                "Api-Sign": signature,
                "Api-Nonce": nonce
            }

            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, headers=headers, data=params)
            data = response.json()

            if data['status'] == '0000':
                return data['data']
            else:
                print(f"잔고 조회 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"잔고 조회 오류: {str(e)}")
            return None

    def place_order(self, order_type: str, coin: str, amount: float, price: Optional[float] = None) -> Optional[Dict]:
        """
        주문 실행
        order_type: 'bid' (매수) or 'ask' (매도)
        coin: 코인 심볼 (예: 'BTC')
        amount: 주문 수량
        price: 주문 가격 (None이면 시장가)
        """
        try:
            endpoint = "/trade/place"

            params = {
                "order_currency": coin,
                "payment_currency": "KRW",
                "units": str(amount),
                "type": order_type
            }

            if price is not None:
                params["price"] = str(price)

            signature, nonce = self._get_signature(endpoint, params)

            headers = {
                "Api-Key": self.api_key,
                "Api-Sign": signature,
                "Api-Nonce": nonce
            }

            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, headers=headers, data=params)
            data = response.json()

            if data['status'] == '0000':
                print(f"주문 성공: {order_type} {amount} {coin}")
                return data
            else:
                print(f"주문 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"주문 오류: {str(e)}")
            return None

    def market_buy(self, coin: str, krw_amount: float) -> Optional[Dict]:
        """시장가 매수 (KRW 금액 기준)"""
        try:
            endpoint = "/trade/market_buy"

            params = {
                "order_currency": coin,
                "payment_currency": "KRW",
                "units": str(krw_amount)
            }

            signature, nonce = self._get_signature(endpoint, params)

            headers = {
                "Api-Key": self.api_key,
                "Api-Sign": signature,
                "Api-Nonce": nonce
            }

            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, headers=headers, data=params)
            data = response.json()

            if data['status'] == '0000':
                print(f"시장가 매수 성공: {krw_amount} KRW -> {coin}")
                return data
            else:
                print(f"시장가 매수 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"시장가 매수 오류: {str(e)}")
            return None

    def market_sell(self, coin: str, amount: float) -> Optional[Dict]:
        """시장가 매도 (코인 수량 기준)"""
        try:
            endpoint = "/trade/market_sell"

            params = {
                "order_currency": coin,
                "payment_currency": "KRW",
                "units": str(amount)
            }

            signature, nonce = self._get_signature(endpoint, params)

            headers = {
                "Api-Key": self.api_key,
                "Api-Sign": signature,
                "Api-Nonce": nonce
            }

            url = f"{self.base_url}{endpoint}"
            response = requests.post(url, headers=headers, data=params)
            data = response.json()

            if data['status'] == '0000':
                print(f"시장가 매도 성공: {amount} {coin}")
                return data
            else:
                print(f"시장가 매도 실패: {data['message']}")
                return None
        except Exception as e:
            print(f"시장가 매도 오류: {str(e)}")
            return None
