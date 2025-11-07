# ⚡ 빠른 배포 가이드

컴퓨터 꺼도 24/7 실행! 5단계만 따라하세요!

---

## 📋 준비물

- [ ] Oracle Cloud 계정
- [ ] 도메인 (있으면 더 좋음, 없어도 됨)
- [ ] 5분의 시간

---

## 🚀 5단계 배포

### 1️⃣ Oracle Cloud VM 생성 (3분)

1. https://cloud.oracle.com 로그인
2. **Compute** > **Instances** > **Create Instance**
3. 설정:
   ```
   Name: bitcoin-bot
   Image: Ubuntu 22.04
   Shape: VM.Standard.A1.Flex (2 OCPU, 12GB)
   ```
4. SSH 키 생성:
   ```bash
   ssh-keygen -t rsa -f ~/.ssh/oracle_key
   cat ~/.ssh/oracle_key.pub
   ```
5. 공개키 붙여넣기 → **Create**
6. **Public IP** 메모!

### 2️⃣ 방화벽 열기 (1분)

Oracle Cloud 콘솔에서:
1. **Networking** > **Virtual Cloud Networks**
2. **Security Lists** > **Default Security List**
3. **Add Ingress Rules**:
   ```
   Source: 0.0.0.0/0
   Port: 8501
   ```

### 3️⃣ 코드 업로드 (1분)

**방법 A: Git (추천)**
```bash
# 로컬에서
cd /Users/fire/Desktop/testBIT
git init
git add .
git commit -m "init"

# GitHub에 push 후 서버에서
ssh -i ~/.ssh/oracle_key ubuntu@YOUR_IP
git clone https://github.com/YOUR_REPO.git
cd YOUR_REPO
```

**방법 B: 직접 업로드**
```bash
# 로컬에서
scp -i ~/.ssh/oracle_key -r /Users/fire/Desktop/testBIT ubuntu@YOUR_IP:~/trading-bot
```

### 4️⃣ .env 파일 설정 (30초)

```bash
# 서버에서
cd ~/trading-bot  # 또는 YOUR_REPO
nano .env
```

붙여넣기:
```env
BITHUMB_API_KEY=your_key
BITHUMB_SECRET_KEY=your_secret
OPENAI_API_KEY=your_openai_key
TRADING_COIN=BTC
TRADING_CURRENCY=KRW
INVESTMENT_AMOUNT=50000
CHECK_INTERVAL=300
```

저장: `Ctrl+X`, `Y`, `Enter`

### 5️⃣ 자동 배포 실행! (2분)

```bash
bash deploy_server.sh
```

스크립트가 묻는 질문들:
- 도메인 연결? → **y** (도메인 있으면) / **n** (없으면)
- 도메인 입력? → **bot.yourdomain.com**
- HTTPS 설치? → **y**
- 이메일 입력? → **your@email.com**

---

## 🎉 완료!

### 접속하기

**도메인이 있는 경우:**
```
https://bot.yourdomain.com
```

**도메인이 없는 경우:**
```
http://YOUR_PUBLIC_IP:8501
```

### 확인하기
```bash
# 상태 확인
sudo systemctl status trading-bot

# 로그 보기
sudo journalctl -u trading-bot -f
```

---

## 🔧 유용한 명령어

```bash
# 재시작
sudo systemctl restart trading-bot

# 중지
sudo systemctl stop trading-bot

# 시작
sudo systemctl start trading-bot

# 코드 업데이트 (Git 사용 시)
git pull
sudo systemctl restart trading-bot
```

---

## 💡 팁

### 도메인 DNS 설정
도메인 제공업체에서:
```
Type: A
Name: bot (또는 원하는 서브도메인)
Value: YOUR_PUBLIC_IP
TTL: 3600
```

### 비용
**100% 무료!** Oracle Cloud Always Free 사용

### 모니터링
대시보드에서:
- 봇 시작/중지
- 실시간 거래 내역
- 수익률 차트

---

## 📞 문제 해결

### 접속 안됨?
1. 방화벽 확인: `sudo ufw status`
2. 서비스 확인: `sudo systemctl status trading-bot`
3. Oracle Cloud 방화벽 규칙 재확인

### 로그 확인
```bash
sudo journalctl -u trading-bot -n 100
```

---

## 🎊 이게 끝!

이제:
- ✅ 컴퓨터 꺼도 24/7 실행
- ✅ 핸드폰 어디서든 접속
- ✅ 자동 재시작
- ✅ 영구 무료

**행복한 트레이딩! 🚀📈**

---

더 자세한 내용은 `ORACLE_DEPLOY.md` 참고!
