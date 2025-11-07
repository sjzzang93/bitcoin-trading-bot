"""
단타 종목 추천을 위한 GPT 분석 모듈
거래량 급증 코인들을 GPT에게 분석시켜 최적의 매수 종목을 추천받습니다.
"""

from openai import OpenAI
from typing import Dict, List, Optional
import json


class ScalpingAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def recommend_coin(self, candidates: List[Dict]) -> Optional[Dict]:
        """
        거래량 급증 코인 후보들 중 최적의 매수 종목 추천

        Args:
            candidates: 거래량 급증 코인 리스트

        Returns:
            {
                "selected_coin": "XRP",
                "confidence": 85,
                "reason": "추천 이유",
                "entry_timing": "즉시" | "조정 대기",
                "risk_level": "낮음" | "중간" | "높음"
            }
        """
        try:
            if not candidates:
                return None

            # 후보 코인 정보를 텍스트로 변환
            prompt = self._create_recommendation_prompt(candidates)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 암호화폐 단타 매매 전문가입니다.
거래량이 급증한 코인들 중에서 단기 수익을 낼 가능성이 높은 코인을 선택해야 합니다.

반드시 다음 JSON 형식으로만 답변하세요:

{
    "selected_coin": "코인 심볼 (예: XRP)",
    "confidence": 0~100 사이의 숫자 (추천 확신도),
    "reason": "추천 이유를 한국어로 간단히 설명 (2-3문장)",
    "entry_timing": "즉시" 또는 "조정 대기",
    "risk_level": "낮음" 또는 "중간" 또는 "높음"
}

분석 기준:
1. 거래량 증가율 (높을수록 좋음)
2. 가격 변동률 (너무 과열되지 않은 것)
3. 거래대금 (충분한 유동성)
4. 단기 모멘텀 지속 가능성
5. 리스크 수준 (과도한 급등은 위험)

주의사항:
- 이미 30% 이상 급등한 코인은 주의
- 거래대금이 너무 적은 코인은 피하기
- 여러 후보 중 가장 안정적이면서 모멘텀 있는 것 선택"""
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

            # JSON 추출
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)

            # 결과 검증
            if not self._validate_recommendation(result):
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

    def _create_recommendation_prompt(self, candidates: List[Dict]) -> str:
        """후보 코인 정보를 프롬프트로 변환"""
        prompt = "=== 거래량 급증 코인 후보 목록 ===\n\n"

        for i, coin in enumerate(candidates, 1):
            prompt += f"[후보 {i}] {coin['coin']}\n"
            prompt += f"- 현재가: {coin['price']:,} KRW\n"
            prompt += f"- 24시간 가격 변동: {coin.get('price_change_24h', 0):+.2f}%\n"

            if 'volume_change' in coin:
                prompt += f"- 거래량 증가율: {coin['volume_change']:+.2f}%\n"

            if 'trade_value_24h' in coin:
                prompt += f"- 24시간 거래대금: {coin['trade_value_24h']/100000000:,.0f}억원\n"

            if 'momentum_score' in coin:
                prompt += f"- 모멘텀 스코어: {coin['momentum_score']:.2f}\n"

            prompt += "\n"

        prompt += "\n위 후보들 중 단타 매매에 가장 적합한 코인 1개를 선택하고 분석해주세요."

        return prompt

    def _validate_recommendation(self, result: Dict) -> bool:
        """GPT 응답 검증"""
        required_keys = ['selected_coin', 'confidence', 'reason', 'entry_timing', 'risk_level']

        for key in required_keys:
            if key not in result:
                return False

        if not (0 <= result['confidence'] <= 100):
            return False

        if result['entry_timing'] not in ['즉시', '조정 대기']:
            return False

        if result['risk_level'] not in ['낮음', '중간', '높음']:
            return False

        return True

    def analyze_exit_strategy(self, coin: str, entry_price: float, current_price: float,
                            profit_target: float = 5.0, stop_loss: float = -3.0) -> Dict:
        """
        현재 포지션에 대한 출구 전략 분석 (간단 버전)

        Args:
            coin: 코인 심볼
            entry_price: 진입가
            current_price: 현재가
            profit_target: 목표 수익률 (%)
            stop_loss: 손절률 (%)

        Returns:
            {
                "action": "hold" | "take_profit" | "stop_loss",
                "current_profit": 현재 수익률,
                "distance_to_target": 목표가까지 거리,
                "distance_to_stop": 손절선까지 거리
            }
        """
        # 현재 수익률 계산
        profit_rate = ((current_price - entry_price) / entry_price) * 100

        # 목표가/손절선 계산
        target_price = entry_price * (1 + profit_target / 100)
        stop_price = entry_price * (1 + stop_loss / 100)

        # 액션 결정
        if profit_rate >= profit_target:
            action = "take_profit"
        elif profit_rate <= stop_loss:
            action = "stop_loss"
        else:
            action = "hold"

        return {
            "action": action,
            "current_profit": profit_rate,
            "entry_price": entry_price,
            "current_price": current_price,
            "target_price": target_price,
            "stop_price": stop_price,
            "distance_to_target": profit_target - profit_rate,
            "distance_to_stop": profit_rate - stop_loss
        }


# 테스트 코드
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    analyzer = ScalpingAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))

    # 테스트용 후보 코인 데이터
    test_candidates = [
        {
            'coin': 'XRP',
            'price': 1500,
            'price_change_24h': 5.2,
            'volume_change': 45.3,
            'trade_value_24h': 25000000000,
            'momentum_score': 8.5
        },
        {
            'coin': 'ADA',
            'price': 800,
            'price_change_24h': 8.7,
            'volume_change': 32.1,
            'trade_value_24h': 15000000000,
            'momentum_score': 7.2
        },
        {
            'coin': 'DOGE',
            'price': 200,
            'price_change_24h': 15.3,
            'volume_change': 67.8,
            'trade_value_24h': 18000000000,
            'momentum_score': 9.1
        }
    ]

    print("GPT 종목 추천 테스트\n")

    recommendation = analyzer.recommend_coin(test_candidates)

    if recommendation:
        print("="*60)
        print(f"추천 코인: {recommendation['selected_coin']}")
        print(f"확신도: {recommendation['confidence']}%")
        print(f"진입 타이밍: {recommendation['entry_timing']}")
        print(f"리스크: {recommendation['risk_level']}")
        print(f"\n이유: {recommendation['reason']}")
        print("="*60)

    # 출구 전략 테스트
    print("\n출구 전략 테스트\n")
    exit_analysis = analyzer.analyze_exit_strategy(
        coin='XRP',
        entry_price=1500,
        current_price=1560,
        profit_target=5.0,
        stop_loss=-3.0
    )

    print(f"현재 수익률: {exit_analysis['current_profit']:.2f}%")
    print(f"액션: {exit_analysis['action']}")
    print(f"목표가까지: {exit_analysis['distance_to_target']:.2f}%")
    print(f"손절선까지: {exit_analysis['distance_to_stop']:.2f}%")
