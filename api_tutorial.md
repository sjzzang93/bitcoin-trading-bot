# API 키 연동 완벽 가이드

## 1. 환경 변수(.env) 방식 - 가장 안전하고 권장되는 방법

### 왜 .env 파일을 사용하나요?
- API 키를 코드에 직접 쓰면 Github 등에 올릴 때 노출될 위험
- .env 파일은 .gitignore에 추가되어 Git에 올라가지 않음
- 키 관리가 편리함

### 단계별 설정

#### Step 1: .env 파일 생성
```bash
# 프로젝트 폴더에서
cp .env.example .env
```

#### Step 2: .env 파일 편집
```env
# .env 파일 내용
BITHUMB_API_KEY=your_actual_api_key_here
BITHUMB_SECRET_KEY=your_actual_secret_key_here
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

#### Step 3: Python에서 불러오기
```python
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
api_key = os.getenv('BITHUMB_API_KEY')
secret_key = os.getenv('BITHUMB_SECRET_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

print(f"API 키: {api_key}")
```

---

## 2. API 키 발급 방법

### 빗썸 API 키 발급

#### 단계 1: 빗썸 로그인
1. https://www.bithumb.com 접속
2. 로그인

#### 단계 2: API 관리 페이지
1. 우측 상단 프로필 클릭
2. 마이페이지 → API 관리
3. "API Key 발급" 클릭

#### 단계 3: 권한 설정
- **필수 권한:**
  - ✅ 자산조회 (잔고 확인용)
  - ✅ 거래 (매수/매도용)
- **선택 권한:**
  - ❌ 출금 (보안상 체크 해제 권장)

#### 단계 4: IP 주소 등록
```bash
# 내 IP 확인 방법
curl ifconfig.me
```
- 나온 IP를 빗썸 API 설정에 등록
- 집/회사 등 여러 곳에서 사용 시 모두 등록 필요

#### 단계 5: 키 복사
- **API Key**: 공개 키 (ID 같은 역할)
- **Secret Key**: 비밀 키 (비밀번호 같은 역할)
- ⚠️ Secret Key는 한 번만 보여주므로 바로 복사!

---

### OpenAI API 키 발급

#### 단계 1: OpenAI 가입
1. https://platform.openai.com 접속
2. 계정 생성 (Google 계정으로 가능)

#### 단계 2: 결제 정보 등록
1. Settings → Billing
2. 신용카드 등록
3. 크레딧 충전 (최소 $5~)

#### 단계 3: API 키 생성
1. 좌측 메뉴 → API keys
2. "Create new secret key" 클릭
3. 이름 입력 (예: "bitcoin-trading-bot")
4. 키 복사 (한 번만 보여줌!)

#### 단계 4: 사용량 제한 설정 (권장)
1. Settings → Limits
2. Monthly budget 설정 (예: $10)
3. 예상치 못한 과금 방지

---

## 3. 빗썸 API 서명(Signature) 동작 원리

빗썸은 보안을 위해 모든 거래 요청에 서명이 필요합니다.

### 서명 생성 과정

```python
import hmac
import hashlib
import time
import urllib.parse

# 1. 현재 시간(nonce) 생성
nonce = str(int(time.time() * 1000))

# 2. 요청 파라미터
endpoint = "/info/balance"
params = {
    "order_currency": "BTC",
    "payment_currency": "KRW"
}

# 3. 파라미터를 문자열로 변환
params_str = urllib.parse.urlencode(params)

# 4. 서명할 데이터 만들기
# 형식: endpoint + NULL + params + NULL + nonce
payload = endpoint + chr(0) + params_str + chr(0) + nonce

# 5. HMAC-SHA512로 서명 생성
secret_key = "your_secret_key"
signature = hmac.new(
    secret_key.encode('utf-8'),
    payload.encode('utf-8'),
    hashlib.sha512
).hexdigest()

# 6. 헤더에 포함
headers = {
    "Api-Key": "your_api_key",
    "Api-Sign": signature,
    "Api-Nonce": nonce
}
```

### 왜 이렇게 복잡하게 하나요?

1. **재생 공격(Replay Attack) 방지**
   - nonce(시간값)로 같은 요청을 재사용할 수 없음

2. **변조 방지**
   - 파라미터가 조금이라도 바뀌면 서명이 달라짐

3. **신원 확인**
   - Secret Key를 아는 사람만 올바른 서명 생성 가능

---

## 4. OpenAI API 사용법

OpenAI는 더 간단합니다 - API 키만 헤더에 넣으면 됩니다.

```python
from openai import OpenAI

# 클라이언트 초기화
client = OpenAI(api_key="your_openai_api_key")

# GPT-4 호출
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "당신은 투자 전문가입니다."},
        {"role": "user", "content": "비트코인 시장을 분석해주세요."}
    ],
    temperature=0.7,
    max_tokens=500
)

# 응답 받기
answer = response.choices[0].message.content
print(answer)
```

### 주요 파라미터 설명

- **model**: 사용할 모델 (`gpt-4`, `gpt-3.5-turbo` 등)
- **messages**: 대화 내역
  - `system`: AI의 역할/성격 설정
  - `user`: 사용자 질문
  - `assistant`: AI 응답 (대화 이어갈 때)
- **temperature**: 창의성 (0=엄격, 1=창의적)
- **max_tokens**: 최대 응답 길이

---

## 5. 실습: API 연동 테스트 프로그램

간단한 테스트 프로그램을 만들어봅시다.

```python
# test_api.py
from dotenv import load_dotenv
import os
from bithumb_api import BithumbAPI
from gpt_analyzer import GPTAnalyzer

# .env 파일 로드
load_dotenv()

print("=== API 연동 테스트 ===\n")

# 1. 환경 변수 확인
print("1. 환경 변수 확인")
bithumb_key = os.getenv('BITHUMB_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

print(f"빗썸 API 키: {bithumb_key[:10]}..." if bithumb_key else "❌ 없음")
print(f"OpenAI API 키: {openai_key[:10]}..." if openai_key else "❌ 없음")
print()

# 2. 빗썸 공개 API 테스트 (키 불필요)
print("2. 빗썸 시세 조회 (공개 API)")
bithumb = BithumbAPI(
    os.getenv('BITHUMB_API_KEY', ''),
    os.getenv('BITHUMB_SECRET_KEY', '')
)

ticker = bithumb.get_ticker('BTC')
if ticker:
    print(f"✅ 성공!")
    print(f"   현재가: {float(ticker['closing_price']):,} KRW")
    print(f"   24시간 변동: {ticker['fluctate_rate_24H']}%")
else:
    print("❌ 실패")
print()

# 3. 빗썸 잔고 조회 (인증 필요)
print("3. 빗썸 잔고 조회 (인증 API)")
if bithumb_key:
    balance = bithumb.get_balance('BTC')
    if balance:
        print(f"✅ 성공!")
        print(f"   보유 BTC: {balance.get('total_btc', 0)}")
        print(f"   보유 KRW: {float(balance.get('total_krw', 0)):,} KRW")
    else:
        print("❌ 실패 - API 키/Secret 키 확인")
else:
    print("⏭️  건너뜀 (API 키 없음)")
print()

# 4. OpenAI API 테스트
print("4. OpenAI GPT 테스트")
if openai_key:
    gpt = GPTAnalyzer(openai_key)

    # 간단한 질문
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 비용 절감을 위해 3.5 사용
            messages=[
                {"role": "user", "content": "안녕하세요! 간단히 인사해주세요."}
            ],
            max_tokens=50
        )
        print(f"✅ 성공!")
        print(f"   GPT 응답: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
else:
    print("⏭️  건너뜀 (API 키 없음)")

print("\n=== 테스트 완료 ===")
```

---

## 6. 보안 체크리스트

### ✅ 반드시 지켜야 할 것

- [ ] .env 파일을 .gitignore에 추가
- [ ] API 키를 코드에 직접 쓰지 않기
- [ ] Secret Key를 절대 공유하지 않기
- [ ] Github 등에 업로드 전 .env 확인

### ✅ 권장 사항

- [ ] 빗썸 API 출금 권한 비활성화
- [ ] IP 주소 제한 설정
- [ ] OpenAI 월 예산 제한 설정
- [ ] 테스트는 소액으로만

---

## 7. 자주 발생하는 오류

### 오류 1: "Api-Sign이 올바르지 않습니다"
**원인:** Secret Key가 잘못됨 또는 서명 생성 오류
**해결:**
- Secret Key 재확인
- 시간 동기화 확인 (nonce 오류 가능)

### 오류 2: "IP가 등록되지 않았습니다"
**원인:** 현재 IP가 빗썸에 미등록
**해결:**
```bash
curl ifconfig.me  # IP 확인 후 빗썸에 등록
```

### 오류 3: "OpenAI API rate limit exceeded"
**원인:** 너무 많은 요청 또는 크레딧 부족
**해결:**
- 요청 간격 늘리기
- 크레딧 충전

### 오류 4: ".env 파일을 찾을 수 없음"
**원인:** .env 파일이 없거나 다른 위치에 있음
**해결:**
```bash
# 현재 디렉토리 확인
pwd

# .env 파일 존재 확인
ls -la .env

# 없으면 생성
cp .env.example .env
```

---

## 8. 연습 문제

### 초급: 환경 변수 읽기
```python
# 문제: .env에서 값을 읽어 출력하세요
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: TRADING_COIN 값을 읽어서 출력하세요
```

### 중급: 빗썸 API 호출
```python
# 문제: 이더리움(ETH) 현재가를 조회하세요
from bithumb_api import BithumbAPI

api = BithumbAPI('', '')  # 공개 API는 키 불필요

# TODO: ETH 시세를 조회하고 현재가를 출력하세요
```

### 고급: GPT에게 질문하기
```python
# 문제: GPT에게 비트코인 투자 조언을 받으세요
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# TODO: "비트코인 투자 시 주의사항을 3가지만 알려주세요" 질문하기
```

---

## 9. 다음 단계

API 연동을 마스터했다면:

1. **실전 테스트**
   ```bash
   python test_api.py  # API 테스트 실행
   ```

2. **자동매매 봇 실행**
   ```bash
   python trading_bot.py
   ```

3. **커스터마이징**
   - GPT 프롬프트 수정
   - 매매 전략 변경
   - 알림 기능 추가

---

## 도움이 필요하시면?

- 빗썸 API 문서: https://apidocs.bithumb.com
- OpenAI API 문서: https://platform.openai.com/docs
- Python dotenv 문서: https://pypi.org/project/python-dotenv/
