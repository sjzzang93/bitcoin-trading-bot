import requests
import time
import hmac
import hashlib
import urllib.parse
import base64
from typing import Dict, Optional


class BithumbAPI:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.bithumb.com"

    def _usec_time(self):
        """마이크로초 단위 타임스탬프 생성"""
        mt = time.time()
        mt_array = str(mt).split(".")
        return mt_array[0] + mt_array[1][:3]

    def _get_signature(self, endpoint: str, params: Dict) -> tuple:
        """API 요청 서명 생성"""
        # endpoint를 params에 추가
        endpoint_item_array = {"endpoint": endpoint}
        uri_array = dict(endpoint_item_array, **params)

        params_str = urllib.parse.urlencode(uri_array)
        nonce = self._usec_time()

        # 서명 데이터 생성: endpoint + chr(0) + params + chr(0) + nonce
        data = endpoint + chr(0) + params_str + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        utf8_key = self.secret_key.encode('utf-8')

        # HMAC-SHA512 해시 생성
        h = hmac.new(bytes(utf8_key), utf8_data, hashlib.sha512)
        hex_output = h.hexdigest()
        utf8_hex_output = hex_output.encode('utf-8')

        # Base64 인코딩 (중요!)
        api_sign = base64.b64encode(utf8_hex_output)
        signature = api_sign.decode('utf-8')

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
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
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
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
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
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
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
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
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
