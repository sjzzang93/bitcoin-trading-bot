# 🚀 배포 가이드 (완전 무료)

로컬 컴퓨터에서 봇을 실행하고 핸드폰으로 접속하는 방법입니다.

## 📋 준비물

- [x] Python 3.8 이상
- [x] .env 파일 (API 키 설정)
- [ ] ngrok 계정 (무료)

---

## 1️⃣ ngrok 설치

### Mac
```bash
# Homebrew가 있는 경우
brew install ngrok/ngrok/ngrok

# 또는 직접 다운로드
# https://ngrok.com/download
```

### Windows
1. https://ngrok.com/download 접속
2. Windows용 다운로드
3. 압축 해제 후 ngrok.exe를 원하는 폴더에 이동
4. 시스템 PATH 추가 (선택사항)

### Linux
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

---

## 2️⃣ ngrok 인증 (필수)

1. https://ngrok.com 에서 무료 회원가입
2. Dashboard에서 Authtoken 복사
3. 터미널에서 인증:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

---

## 3️⃣ 실행 방법

### 방법 A: 자동 스크립트 (추천)

```bash
# 한 번만 실행하면 끝!
./start.sh
```

### 방법 B: 수동 실행

#### 터미널 1: Streamlit 대시보드 실행
```bash
# 가상환경 활성화
source .venv/bin/activate

# 대시보드 실행
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

#### 터미널 2: ngrok 터널 생성
```bash
ngrok http 8501
```

---

## 4️⃣ 접속하기

### 로컬 접속 (같은 컴퓨터)
```
http://localhost:8501
```

### 같은 와이파이 접속 (핸드폰)
1. 컴퓨터의 IP 주소 확인:
   ```bash
   # Mac/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```

2. 핸드폰 브라우저에서:
   ```
   http://YOUR_COMPUTER_IP:8501
   ```
   예: `http://192.168.0.10:8501`

### 외부 접속 (어디서든)
ngrok 터미널에 표시된 URL 사용:
```
Forwarding   https://abcd-1234-5678.ngrok-free.app -> http://localhost:8501
```

👆 이 URL을 핸드폰 브라우저에 입력!

---

## 5️⃣ 봇 제어

대시보드 접속 후:
- **▶️ 봇 시작**: 자동매매 시작
- **🛑 봇 중지**: 자동매매 중지
- **🔄 수동 새로고침**: 데이터 갱신
- **자동 새로고침**: 5초마다 자동 갱신

---

## 🎯 최적화 팁

### 24/7 실행하기

#### Mac
```bash
# 화면 꺼짐 방지
caffeinate -d ./start.sh
```

#### Windows
- 전원 설정 > 절전 모드 > "안함"

#### Linux/서버
```bash
# nohup으로 백그라운드 실행
nohup streamlit run dashboard.py &

# 또는 screen 사용
screen -S trading-bot
streamlit run dashboard.py
# Ctrl+A, D로 detach
```

### ngrok 무료 플랜 제한
- 세션 시간: 2시간 (재시작 필요)
- 동시 터널: 1개
- 연결 수: 40/분

💡 **해결법**: 무료 회원가입 시 제한 완화!

---

## 🔐 보안 설정 (선택사항)

### Streamlit 비밀번호 설정

`.streamlit/config.toml` 생성:
```toml
[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false

# 비밀번호 보호 (선택)
[server]
enableXsrfProtection = true
```

### ngrok 비밀번호 설정
```bash
ngrok http 8501 --basic-auth="username:password"
```

---

## 🛠️ 트러블슈팅

### 포트 8501이 사용 중
```bash
# 프로세스 찾기
lsof -i :8501

# 종료
kill -9 PID
```

### ngrok 연결 안됨
- 인증 토큰 확인: `ngrok config check`
- 방화벽 확인
- ngrok 재시작

### 핸드폰에서 접속 안됨
- 같은 WiFi 확인
- 방화벽 설정 확인
- IP 주소 재확인

---

## 📱 모바일 최적화

대시보드는 반응형으로 제작되어 핸드폰에서도 잘 보입니다!

- ✅ 터치 스크롤 지원
- ✅ 자동 레이아웃 조정
- ✅ 실시간 차트
- ✅ 봇 제어

---

## 💰 비용

**100% 무료!**
- ✅ Streamlit: 무료
- ✅ ngrok: 무료 (제한적)
- ✅ 로컬 실행: 무료
- ⚠️ 전기세만 발생 (미미함)

---

## 🔄 자동 재시작 (선택)

### cron 사용 (Mac/Linux)
```bash
# crontab 편집
crontab -e

# 2시간마다 ngrok 재시작
0 */2 * * * pkill ngrok && cd /path/to/testBIT && ngrok http 8501 &
```

### Windows 작업 스케줄러
1. 작업 스케줄러 열기
2. 새 작업 만들기
3. 트리거: 2시간마다
4. 작업: ngrok 재시작 스크립트

---

## 🎉 완료!

이제 다음을 할 수 있습니다:
- ✅ 컴퓨터에서 봇 실행
- ✅ 핸드폰으로 모니터링
- ✅ 외출 중에도 거래 확인
- ✅ 100% 무료!

**즐거운 트레이딩 되세요! 🚀📈**
