"""
API 연동 테스트 프로그램
각 API가 제대로 동작하는지 단계별로 확인합니다.
"""

from dotenv import load_dotenv
import os
from bithumb_api import BithumbAPI
from openai import OpenAI

# .env 파일 로드
load_dotenv()

print("=" * 60)
print("API 연동 테스트 프로그램")
print("=" * 60)
print()

# ===== 1. 환경 변수 확인 =====
print("📋 1단계: 환경 변수 확인")
print("-" * 60)

bithumb_key = os.getenv('BITHUMB_API_KEY')
bithumb_secret = os.getenv('BITHUMB_SECRET_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

if bithumb_key and len(bithumb_key) > 10:
    print(f"✅ 빗썸 API 키: {bithumb_key[:10]}...{bithumb_key[-5:]}")
else:
    print("❌ 빗썸 API 키: 설정되지 않음")

if bithumb_secret and len(bithumb_secret) > 10:
    print(f"✅ 빗썸 Secret 키: {bithumb_secret[:10]}...{bithumb_secret[-5:]}")
else:
    print("❌ 빗썸 Secret 키: 설정되지 않음")

if openai_key and len(openai_key) > 10:
    print(f"✅ OpenAI API 키: {openai_key[:10]}...{openai_key[-5:]}")
else:
    print("❌ OpenAI API 키: 설정되지 않음")

print()

# ===== 2. 빗썸 공개 API 테스트 (API 키 불필요) =====
print("🌐 2단계: 빗썸 공개 API 테스트 (시세 조회)")
print("-" * 60)

bithumb = BithumbAPI(
    bithumb_key or '',
    bithumb_secret or ''
)

ticker = bithumb.get_ticker('BTC', 'KRW')
if ticker:
    print("✅ 비트코인 시세 조회 성공!")
    print(f"   현재가: {float(ticker['closing_price']):,} KRW")
    print(f"   시가: {float(ticker['opening_price']):,} KRW")
    print(f"   고가: {float(ticker['max_price']):,} KRW")
    print(f"   저가: {float(ticker['min_price']):,} KRW")
    print(f"   24시간 변동률: {ticker['fluctate_rate_24H']}%")
    print(f"   거래량: {ticker['units_traded_24H']}")
else:
    print("❌ 시세 조회 실패")

print()

# ===== 3. 빗썸 호가 조회 =====
print("📊 3단계: 빗썸 호가 조회")
print("-" * 60)

orderbook = bithumb.get_orderbook('BTC', 'KRW')
if orderbook:
    print("✅ 호가 조회 성공!")

    if orderbook.get('bids'):
        print(f"   매수 호가 (최고): {orderbook['bids'][0]['price']} KRW")
        print(f"   매수 수량: {orderbook['bids'][0]['quantity']}")

    if orderbook.get('asks'):
        print(f"   매도 호가 (최저): {orderbook['asks'][0]['price']} KRW")
        print(f"   매도 수량: {orderbook['asks'][0]['quantity']}")
else:
    print("❌ 호가 조회 실패")

print()

# ===== 4. 빗썸 인증 API 테스트 (잔고 조회) =====
print("🔐 4단계: 빗썸 인증 API 테스트 (잔고 조회)")
print("-" * 60)

if bithumb_key and bithumb_secret:
    print("API 키가 설정되어 있습니다. 잔고를 조회합니다...")

    balance = bithumb.get_balance('BTC')
    if balance:
        print("✅ 잔고 조회 성공!")
        print(f"   보유 BTC: {balance.get('total_btc', 0)}")
        print(f"   사용 가능 BTC: {balance.get('available_btc', 0)}")
        print(f"   보유 KRW: {float(balance.get('total_krw', 0)):,} KRW")
        print(f"   사용 가능 KRW: {float(balance.get('available_krw', 0)):,} KRW")
    else:
        print("❌ 잔고 조회 실패")
        print("   - API 키/Secret 키가 올바른지 확인하세요")
        print("   - 빗썸에서 API 거래 권한이 활성화되어 있는지 확인하세요")
        print("   - IP 주소가 등록되어 있는지 확인하세요")
else:
    print("⏭️  건너뜀 (API 키가 설정되지 않음)")
    print("   .env 파일에 BITHUMB_API_KEY와 BITHUMB_SECRET_KEY를 설정하세요")

print()

# ===== 5. OpenAI API 테스트 =====
print("🤖 5단계: OpenAI API 테스트")
print("-" * 60)

if openai_key:
    print("OpenAI API 키가 설정되어 있습니다. GPT를 호출합니다...")

    try:
        client = OpenAI(api_key=openai_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 테스트는 저렴한 모델 사용
            messages=[
                {
                    "role": "system",
                    "content": "당신은 친절한 AI 어시스턴트입니다."
                },
                {
                    "role": "user",
                    "content": "안녕하세요! API 테스트 중입니다. 간단히 인사해주세요."
                }
            ],
            max_tokens=100,
            temperature=0.7
        )

        answer = response.choices[0].message.content

        print("✅ OpenAI API 호출 성공!")
        print(f"   GPT 응답: {answer}")
        print(f"   사용 토큰: {response.usage.total_tokens}")
        print(f"   모델: {response.model}")

    except Exception as e:
        print("❌ OpenAI API 호출 실패")
        print(f"   오류: {str(e)}")
        print("   - API 키가 올바른지 확인하세요")
        print("   - OpenAI 크레딧이 충분한지 확인하세요")
        print("   - 인터넷 연결을 확인하세요")
else:
    print("⏭️  건너뜀 (OpenAI API 키가 설정되지 않음)")
    print("   .env 파일에 OPENAI_API_KEY를 설정하세요")

print()

# ===== 종합 결과 =====
print("=" * 60)
print("📊 테스트 결과 요약")
print("=" * 60)

test_results = []

# 공개 API는 항상 성공해야 함
test_results.append(("빗썸 시세 조회", ticker is not None))
test_results.append(("빗썸 호가 조회", orderbook is not None))

# 인증 API는 키가 있을 때만
if bithumb_key and bithumb_secret:
    test_results.append(("빗썸 잔고 조회 (인증)", balance is not None if 'balance' in locals() else False))

if openai_key:
    test_results.append(("OpenAI GPT 호출", 'answer' in locals()))

for test_name, result in test_results:
    status = "✅ 성공" if result else "❌ 실패"
    print(f"{test_name:30s} {status}")

print()
success_count = sum(1 for _, result in test_results if result)
total_count = len(test_results)

if success_count == total_count:
    print("🎉 모든 테스트를 통과했습니다!")
    print("이제 trading_bot.py를 실행할 수 있습니다.")
else:
    print(f"⚠️  {total_count}개 중 {success_count}개 테스트 통과")
    print("실패한 테스트를 확인하고 .env 파일 설정을 점검하세요.")

print()
print("=" * 60)
print("다음 단계:")
print("1. 모든 테스트가 성공하면: python trading_bot.py")
print("2. 문제가 있으면: api_tutorial.md 참고")
print("=" * 60)
