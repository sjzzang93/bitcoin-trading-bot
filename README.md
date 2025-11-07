# 비트코인 GPT 자동매매 프로그램

ChatGPT API를 활용한 빗썸(Bithumb) 비트코인 자동매매 시스템입니다.

## 주요 기능

- GPT-4를 활용한 시장 데이터 분석
- 실시간 시세 조회 및 호가 분석
- 자동 매수/매도 실행
- 수익률 추적 및 포지션 관리

## 프로젝트 구조

```
testBIT/
├── bithumb_api.py      # 빗썸 API 연동 모듈
├── gpt_analyzer.py     # GPT 시장 분석 모듈
├── trading_bot.py      # 메인 자동매매 봇
├── requirements.txt    # 필요한 패키지 목록
├── .env.example        # 환경변수 예시 파일
└── README.md          # 이 파일
```

## 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 API 키를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
# Bithumb API Keys
BITHUMB_API_KEY=your_bithumb_api_key_here
BITHUMB_SECRET_KEY=your_bithumb_secret_key_here

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Trading Settings
TRADING_COIN=BTC
TRADING_CURRENCY=KRW
INVESTMENT_AMOUNT=50000
CHECK_INTERVAL=300
```

### 3. API 키 발급 방법

**빗썸 API 키:**
1. [빗썸](https://www.bithumb.com) 로그인
2. 마이페이지 > API 관리
3. API Key 발급 (거래 권한 필요)
4. IP 주소 등록 (보안 설정)

**OpenAI API 키:**
1. [OpenAI Platform](https://platform.openai.com) 가입
2. API Keys 메뉴에서 새 키 생성
3. 요금제 확인 (GPT-4 사용 시 비용 발생)

## 사용 방법

### 자동매매 시작

```bash
python trading_bot.py
```

### 종료

```
Ctrl + C
```

## 설정 옵션

`.env` 파일에서 다음 설정을 변경할 수 있습니다:

- `TRADING_COIN`: 거래할 코인 (기본값: BTC)
- `TRADING_CURRENCY`: 거래 통화 (기본값: KRW)
- `INVESTMENT_AMOUNT`: 1회 투자 금액 (기본값: 50000 KRW)
- `CHECK_INTERVAL`: 시장 체크 주기 (초 단위, 기본값: 300초 = 5분)

## GPT 분석 로직

GPT-4는 다음 데이터를 기반으로 분석합니다:

1. **현재가 정보**
   - 현재가, 시가, 고가, 저가
   - 24시간 변동률
   - 거래량 및 거래금액

2. **호가 정보**
   - 최고 매수 호가
   - 최저 매도 호가

3. **잔고 정보**
   - 보유 BTC 수량
   - 보유 KRW 금액

### GPT 응답 형식

```json
{
    "decision": "buy|sell|hold",
    "confidence": 85,
    "reason": "거래량이 급증하고 상승 추세가 명확하여 매수 진입",
    "suggested_amount": 0.8
}
```

- `decision`: 매수(buy), 매도(sell), 보유(hold)
- `confidence`: 확신도 (0~100)
- `reason`: 결정 이유
- `suggested_amount`: 투자 금액 비율 (0~1, 1 = 100%)

## 주의사항

1. **투자 위험**
   - 암호화폐 투자는 고위험 자산입니다
   - GPT의 분석이 항상 정확하지 않을 수 있습니다
   - 소액으로 충분히 테스트 후 사용하세요

2. **API 비용**
   - OpenAI GPT-4 API는 사용량에 따라 비용이 발생합니다
   - 체크 주기가 짧을수록 API 호출이 많아집니다

3. **거래소 제약**
   - 빗썸 API 호출 제한을 확인하세요
   - 최소 주문 금액 제한이 있을 수 있습니다

4. **보안**
   - `.env` 파일은 절대 공유하지 마세요
   - API 키가 노출되지 않도록 주의하세요
   - `.gitignore`에 `.env` 추가 권장

## 트러블슈팅

### "잔고 조회 실패" 오류
- API 키가 올바른지 확인
- API에 거래 권한이 부여되었는지 확인
- IP 주소가 등록되었는지 확인

### "GPT 분석 실패" 오류
- OpenAI API 키가 유효한지 확인
- API 크레딧 잔액 확인
- 네트워크 연결 확인

### "주문 실패" 오류
- 최소 주문 금액 이상인지 확인
- 잔고가 충분한지 확인
- 빗썸 거래 가능 시간인지 확인

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 실제 투자에 사용할 경우 모든 책임은 사용자에게 있습니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.
