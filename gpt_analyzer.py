from openai import OpenAI
from typing import Dict, Optional
import json


class GPTAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def analyze_market(self, market_data: Dict) -> Optional[Dict]:
        """
        시장 데이터를 분석하여 매매 결정 반환

        Returns:
            {
                "decision": "buy" | "sell" | "hold",
                "confidence": 0-100,
                "reason": "분석 이유",
                "suggested_amount": 투자 금액 비율 (0-1)
            }
        """
        try:
            # 시장 데이터를 GPT가 분석하기 쉬운 형태로 변환
            prompt = self._create_analysis_prompt(market_data)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # GPT-4o-mini 사용 (가성비 최고)
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 비트코인 전문 트레이더입니다.
주어진 시장 데이터를 분석하여 매수, 매도, 보유 결정을 내려야 합니다.
반드시 다음 JSON 형식으로만 답변하세요:

{
    "decision": "buy" 또는 "sell" 또는 "hold",
    "confidence": 0~100 사이의 숫자 (확신도),
    "reason": "결정 이유를 한국어로 간단히 설명",
    "suggested_amount": 0~1 사이의 숫자 (투자 금액 비율, 1 = 100%)
}

분석 시 고려사항:
- 현재가 대비 24시간 변동률
- 거래량 변화
- 매수/매도 호가 차이
- 전반적인 시장 심리
- 리스크 관리 (과도한 투자 지양)"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=500
            )

            # GPT 응답 파싱
            result_text = response.choices[0].message.content.strip()

            # JSON 추출 (마크다운 코드 블록 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # 결과 검증
            if not self._validate_result(result):
                print("GPT 응답 형식이 올바르지 않습니다.")
                return None

            return result

        except json.JSONDecodeError as e:
            print(f"GPT 응답 파싱 오류: {str(e)}")
            print(f"응답 내용: {result_text}")
            return None
        except Exception as e:
            print(f"GPT 분석 오류: {str(e)}")
            return None

    def _create_analysis_prompt(self, market_data: Dict) -> str:
        """시장 데이터를 분석용 프롬프트로 변환"""
        ticker = market_data.get('ticker', {})
        orderbook = market_data.get('orderbook', {})
        balance = market_data.get('balance', {})

        prompt = f"""
=== 비트코인 시장 데이터 ===

[현재가 정보]
- 현재가: {ticker.get('closing_price', 'N/A'):,} KRW
- 시가: {ticker.get('opening_price', 'N/A'):,} KRW
- 고가: {ticker.get('max_price', 'N/A'):,} KRW
- 저가: {ticker.get('min_price', 'N/A'):,} KRW
- 전일 대비: {ticker.get('fluctate_rate_24H', 'N/A')}%
- 거래량 (24H): {ticker.get('units_traded_24H', 'N/A')}
- 거래금액 (24H): {ticker.get('acc_trade_value_24H', 'N/A'):,} KRW

[호가 정보]
- 매수 호가 (최고): {orderbook.get('bids', [{}])[0].get('price', 'N/A') if orderbook.get('bids') else 'N/A'} KRW
- 매도 호가 (최저): {orderbook.get('asks', [{}])[0].get('price', 'N/A') if orderbook.get('asks') else 'N/A'} KRW

[내 잔고]
- 보유 BTC: {balance.get('btc_balance', 0)} BTC
- 보유 KRW: {balance.get('krw_balance', 0):,} KRW
- BTC 평가금액: {balance.get('btc_value', 0):,} KRW

위 데이터를 기반으로 매매 결정을 내려주세요.
"""
        return prompt

    def _validate_result(self, result: Dict) -> bool:
        """GPT 응답 결과 검증"""
        required_keys = ['decision', 'confidence', 'reason', 'suggested_amount']

        for key in required_keys:
            if key not in result:
                return False

        if result['decision'] not in ['buy', 'sell', 'hold']:
            return False

        if not (0 <= result['confidence'] <= 100):
            return False

        if not (0 <= result['suggested_amount'] <= 1):
            return False

        return True

    def get_simple_decision(self, current_price: float, avg_buy_price: float, profit_rate: float) -> str:
        """
        간단한 매매 결정 (GPT 없이 기본 로직)
        수익률 기반 매도 판단
        """
        if profit_rate >= 5.0:  # 5% 이상 수익
            return "sell"
        elif profit_rate <= -3.0:  # 3% 이상 손실 (손절)
            return "sell"
        else:
            return "hold"
