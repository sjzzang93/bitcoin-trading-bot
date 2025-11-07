# 🚀 guity.kr 도메인 배포 가이드

**도메인:** guity.kr (또는 bot.guity.kr 추천)
**배포 시간:** 약 10분
**비용:** 100% 무료

---

## 📋 선택: 어떤 주소를 사용하시겠습니까?

### 옵션 1: 서브도메인 (추천) ⭐
```
https://bot.guity.kr
```
- ✅ 메인 도메인과 분리
- ✅ 나중에 다른 서비스 추가 가능
- ✅ 깔끔하고 명확

### 옵션 2: 루트 도메인
```
https://guity.kr
```
- ⚠️ 메인 사이트가 없다면 OK
- ⚠️ 다른 용도로 못씀

**이 가이드는 `bot.guity.kr`로 진행합니다!**

---

## 1️⃣ DNS 설정 (3분)

### guity.kr 도메인 관리 페이지 접속

어디서 구매하셨나요? (가비아, 후이즈, AWS Route53 등)

#### 설정 추가:
```
Type: A
Name: bot
Value: <Oracle VM Public IP - 나중에 입력>
TTL: 3600 (1시간)
```

**나중에 Oracle VM 만들고 IP 받으면 여기 입력!**

---

## 2️⃣ Oracle Cloud VM 생성 (5분)

### 1. Oracle Cloud 접속
https://cloud.oracle.com

### 2. VM 인스턴스 생성
1. **Compute** > **Instances** > **Create Instance**
2. 설정:
   ```
   Name: bitcoin-trading-bot
   Image: Ubuntu 22.04 Minimal
   Shape: VM.Standard.A1.Flex
     - OCPU count: 2
     - Memory (GB): 12
   ```

### 3. SSH 키 생성 (로컬 컴퓨터에서)
```bash
cd ~/.ssh
ssh-keygen -t rsa -b 4096 -f oracle_guity_key
cat oracle_guity_key.pub
```

공개키 내용을 복사해서 Oracle에 붙여넣기

### 4. VM 생성 완료 후
**Public IP 주소 확인하고 메모!**

예: `152.67.123.45`

### 5. DNS에 IP 입력
guity.kr DNS 설정으로 돌아가서:
```
Type: A
Name: bot
Value: 152.67.123.45  ← 여기에 받은 IP 입력
```

DNS 전파 대기 (5분~1시간, 보통 5분이면 OK)

---

## 3️⃣ Oracle Cloud 방화벽 열기 (2분)

### 1. Oracle Cloud 콘솔에서
1. **Networking** > **Virtual Cloud Networks**
2. 생성된 VCN 클릭
3. **Security Lists** > **Default Security List** 클릭
4. **Add Ingress Rules** 클릭

### 2. 규칙 추가 (3개)

**규칙 1: HTTP**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 80
Description: HTTP
```

**규칙 2: HTTPS**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 443
Description: HTTPS
```

**규칙 3: Streamlit (백업)**
```
Source CIDR: 0.0.0.0/0
Destination Port Range: 8501
Description: Streamlit Direct
```

---

## 4️⃣ 서버 접속 및 코드 업로드 (3분)

### 1. SSH 접속
```bash
ssh -i ~/.ssh/oracle_guity_key ubuntu@152.67.123.45
```

처음 접속 시 "yes" 입력

### 2. 코드 업로드

**방법 A: GitHub 사용 (추천)**
```bash
# 로컬 컴퓨터에서 먼저 GitHub에 push
cd /Users/fire/Desktop/testBIT

# .env 파일 제외 확인
cat .gitignore  # .env가 있는지 확인

git init
git add .
git commit -m "Trading bot initial commit"

# GitHub에서 새 repo 생성 후
git remote add origin https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git
git branch -M main
git push -u origin main

# 서버에서 클론
ssh -i ~/.ssh/oracle_guity_key ubuntu@YOUR_IP
git clone https://github.com/YOUR_USERNAME/bitcoin-trading-bot.git
cd bitcoin-trading-bot
```

**방법 B: 직접 업로드**
```bash
# 로컬에서
cd /Users/fire/Desktop/testBIT
scp -i ~/.ssh/oracle_guity_key -r * ubuntu@YOUR_IP:~/trading-bot/

# 서버 접속
ssh -i ~/.ssh/oracle_guity_key ubuntu@YOUR_IP
cd ~/trading-bot
```

---

## 5️⃣ 환경 변수 설정 (1분)

### 서버에서 .env 파일 생성
```bash
cd ~/bitcoin-trading-bot  # 또는 ~/trading-bot
nano .env
```

### 내용 입력:
```env
BITHUMB_API_KEY=your_bithumb_api_key_here
BITHUMB_SECRET_KEY=your_bithumb_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
TRADING_COIN=BTC
TRADING_CURRENCY=KRW
INVESTMENT_AMOUNT=50000
CHECK_INTERVAL=300
```

**저장:** `Ctrl + X` → `Y` → `Enter`

---

## 6️⃣ 자동 배포 실행! (2분)

### 배포 스크립트 실행
```bash
bash deploy_server.sh
```

### 스크립트 질문에 답변:

```
도메인을 연결하시겠습니까? (y/n): y

도메인 입력 (예: bot.yourdomain.com): bot.guity.kr

HTTPS (SSL) 인증서를 설치하시겠습니까? (y/n): y

이메일 주소 입력: your@email.com
```

스크립트가 자동으로:
- ✅ 시스템 패키지 설치
- ✅ Python 환경 설정
- ✅ systemd 서비스 생성
- ✅ nginx 설정
- ✅ Let's Encrypt SSL 인증서 설치
- ✅ 자동 시작 설정

---

## 7️⃣ 완료! 접속하기 🎉

### 웹 브라우저에서 접속
```
https://bot.guity.kr
```

### 또는 직접 IP 접속 (백업)
```
http://YOUR_IP:8501
```

---

## 🔍 상태 확인

### SSH로 서버 접속 후:

```bash
# 서비스 상태 확인
sudo systemctl status trading-bot

# 실시간 로그 보기
sudo journalctl -u trading-bot -f

# nginx 상태
sudo systemctl status nginx

# SSL 인증서 확인
sudo certbot certificates
```

---

## 🎮 봇 제어

### 대시보드에서 (https://bot.guity.kr)
- ▶️ 봇 시작
- 🛑 봇 중지
- 📊 실시간 모니터링
- 📈 수익률 확인

### 서버에서 (SSH)
```bash
# 재시작
sudo systemctl restart trading-bot

# 중지
sudo systemctl stop trading-bot

# 시작
sudo systemctl start trading-bot

# 로그 확인
sudo journalctl -u trading-bot -n 100
```

---

## 🔄 코드 업데이트

### Git 사용 시
```bash
ssh -i ~/.ssh/oracle_guity_key ubuntu@YOUR_IP
cd ~/bitcoin-trading-bot
git pull
sudo systemctl restart trading-bot
```

### 파일 직접 수정
```bash
# 로컬에서 수정 후
scp -i ~/.ssh/oracle_guity_key scalping_bot.py ubuntu@YOUR_IP:~/bitcoin-trading-bot/

# 서버에서 재시작
sudo systemctl restart trading-bot
```

---

## 📱 핸드폰 접속

### 어디서든 접속 가능!
- 집 WiFi
- 회사
- 카페
- 지하철
- 해외

**주소:** https://bot.guity.kr

홈 화면에 추가하면 앱처럼 사용 가능!

---

## 🛡️ 보안 팁

### 1. 기본 인증 추가 (선택)
더 강력한 보안을 원하면:

```bash
# nginx에 비밀번호 추가
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin

# nginx 설정 수정
sudo nano /etc/nginx/sites-available/trading-bot
```

location 블록에 추가:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### 2. IP 화이트리스트 (선택)
특정 IP만 접속 허용:

nginx 설정에 추가:
```nginx
allow YOUR_HOME_IP;
allow YOUR_OFFICE_IP;
deny all;
```

---

## 💰 비용

### Oracle Cloud Always Free
- VM: **영구 무료**
- Storage: **200GB 무료**
- 트래픽: **10TB/월 무료**
- Public IP: **무료**

### Let's Encrypt SSL
- **완전 무료**
- 자동 갱신 (90일마다)

### 도메인 (guity.kr)
- 이미 보유 중: **추가 비용 없음**

**총 비용: 0원!** 🎉

---

## 🔧 트러블슈팅

### bot.guity.kr 접속 안됨?

1. **DNS 전파 확인**
   ```bash
   # 로컬에서
   nslookup bot.guity.kr
   dig bot.guity.kr
   ```
   IP가 제대로 나오나요?

2. **방화벽 확인**
   ```bash
   # 서버에서
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

3. **nginx 확인**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   sudo systemctl restart nginx
   ```

4. **서비스 확인**
   ```bash
   sudo systemctl status trading-bot
   sudo journalctl -u trading-bot -n 50
   ```

### SSL 인증서 문제?
```bash
# 수동으로 재시도
sudo certbot --nginx -d bot.guity.kr

# 로그 확인
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### 봇이 안 돌아감?
```bash
# 로그 확인
sudo journalctl -u trading-bot -f

# 수동 실행으로 테스트
cd ~/bitcoin-trading-bot
source .venv/bin/activate
streamlit run dashboard.py
```

---

## 📊 모니터링

### 서버 리소스
```bash
# CPU/메모리
htop

# 디스크
df -h

# 네트워크
sudo netstat -tulpn
```

### 대시보드
- 실시간 거래 내역
- 수익률 차트
- 포지션 상태
- 최근 스캔 결과

---

## 🎯 최종 체크리스트

- [ ] DNS 설정: `bot.guity.kr` → Oracle IP
- [ ] Oracle VM 생성 및 방화벽 설정
- [ ] 코드 업로드 (Git 또는 SCP)
- [ ] .env 파일 생성 (API 키 입력)
- [ ] `deploy_server.sh` 실행
- [ ] https://bot.guity.kr 접속 확인
- [ ] 봇 시작 버튼 클릭
- [ ] 첫 거래 모니터링

---

## 🎊 완료!

이제 다음이 가능합니다:
- ✅ 컴퓨터 꺼도 24/7 실행
- ✅ https://bot.guity.kr 로 어디서든 접속
- ✅ 핸드폰으로 실시간 모니터링
- ✅ 자동 재시작 (서버 재부팅 시)
- ✅ 무료 SSL 보안
- ✅ 영구 무료 운영

**행복한 트레이딩 되세요! 🚀📈💰**

---

## 📞 다음 단계

배포 완료 후:
1. API 키 테스트
2. 소액으로 첫 거래 테스트
3. 로그 모니터링
4. 수익률 확인

궁금한 점이 있으면 언제든지 물어보세요! 😊
