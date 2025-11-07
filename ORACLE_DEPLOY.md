# 🚀 Oracle Cloud 배포 가이드 (영구 무료)

컴퓨터를 꺼도 24/7 자동매매가 계속 실행됩니다!

---

## 📋 준비물

- Oracle Cloud 계정 (무료)
- 신용카드 (본인 확인용, 과금 안됨)
- 이메일 주소

---

## 1️⃣ Oracle Cloud 계정 생성

### 1. 회원가입
1. https://www.oracle.com/cloud/free/ 접속
2. **Start for free** 클릭
3. 정보 입력:
   - 국가: South Korea
   - 이메일 주소
   - 이름
4. 이메일 인증 완료

### 2. 계정 설정
1. Home Region 선택: **South Korea Central (Seoul)**
2. 신용카드 정보 입력 (본인 확인용, $1 임시 승인 후 취소됨)
3. ⚠️ **Always Free** 옵션만 사용하면 과금 없음!

---

## 2️⃣ VM 인스턴스 생성

### 1. 인스턴스 만들기
1. Oracle Cloud 콘솔 접속
2. **Compute** > **Instances** 클릭
3. **Create Instance** 클릭

### 2. 설정
```
Name: bitcoin-trading-bot
Image: Ubuntu 22.04 (또는 최신 LTS)
Shape: VM.Standard.A1.Flex (ARM, Always Free)
  - OCPU: 2
  - Memory: 12 GB
```

### 3. SSH 키 생성
```bash
# 로컬 컴퓨터에서
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_key

# 공개키 복사
cat ~/.ssh/oracle_key.pub
```

4. 복사한 공개키를 Oracle Cloud에 붙여넣기
5. **Create** 클릭

### 4. Public IP 확인
인스턴스 생성 후 **Public IP** 주소 확인 (예: 152.67.123.45)

---

## 3️⃣ 방화벽 설정

### 1. Oracle Cloud 방화벽
1. **Networking** > **Virtual Cloud Networks**
2. 생성된 VCN 클릭
3. **Security Lists** > **Default Security List** 클릭
4. **Add Ingress Rules** 클릭

추가할 규칙:
```
Source CIDR: 0.0.0.0/0
Destination Port: 8501
Description: Streamlit Dashboard
```

### 2. Ubuntu 방화벽 (서버에서)
```bash
# SSH로 서버 접속 후
sudo ufw allow 8501/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

---

## 4️⃣ 서버 접속 및 설정

### 1. SSH 접속
```bash
# 로컬 컴퓨터에서
ssh -i ~/.ssh/oracle_key ubuntu@YOUR_PUBLIC_IP
```

### 2. 서버 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Python 설치
```bash
sudo apt install -y python3 python3-pip python3-venv git
```

---

## 5️⃣ 프로젝트 배포

### 방법 A: Git 사용 (추천)

#### 1. GitHub에 코드 업로드
```bash
# 로컬 컴퓨터에서
cd /Users/fire/Desktop/testBIT

# Git 초기화 (아직 안했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub repo 생성 후
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

⚠️ **중요**: `.env` 파일은 업로드하지 마세요! (이미 .gitignore에 포함됨)

#### 2. 서버에서 클론
```bash
# SSH로 서버 접속 후
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 방법 B: 직접 업로드

```bash
# 로컬 컴퓨터에서
cd /Users/fire/Desktop/testBIT
scp -i ~/.ssh/oracle_key -r * ubuntu@YOUR_PUBLIC_IP:~/trading-bot/
```

---

## 6️⃣ 환경 설정

### 1. .env 파일 생성
```bash
# 서버에서
cd ~/YOUR_REPO  # 또는 ~/trading-bot
nano .env
```

`.env` 내용 붙여넣기:
```env
BITHUMB_API_KEY=your_key_here
BITHUMB_SECRET_KEY=your_secret_here
OPENAI_API_KEY=your_openai_key_here
TRADING_COIN=BTC
TRADING_CURRENCY=KRW
INVESTMENT_AMOUNT=50000
CHECK_INTERVAL=300
```

저장: `Ctrl + X`, `Y`, `Enter`

### 2. 패키지 설치
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 테스트 실행
```bash
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 접속:
```
http://YOUR_PUBLIC_IP:8501
```

작동하면 `Ctrl + C`로 중지

---

## 7️⃣ 자동 실행 설정 (systemd)

컴퓨터를 꺼도, 서버가 재부팅돼도 자동으로 실행됩니다!

### 1. systemd 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/trading-bot.service
```

내용:
```ini
[Unit]
Description=Bitcoin Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/YOUR_REPO
Environment="PATH=/home/ubuntu/YOUR_REPO/.venv/bin"
ExecStart=/home/ubuntu/YOUR_REPO/.venv/bin/streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

⚠️ `YOUR_REPO`를 실제 폴더명으로 변경!

### 2. 서비스 활성화
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

### 3. 상태 확인
```bash
sudo systemctl status trading-bot
```

### 4. 로그 확인
```bash
sudo journalctl -u trading-bot -f
```

---

## 8️⃣ 접속하기

### 핸드폰/컴퓨터 어디서든 접속
```
http://YOUR_PUBLIC_IP:8501
```

예: `http://152.67.123.45:8501`

---

## 9️⃣ 유용한 명령어

### 봇 제어
```bash
# 상태 확인
sudo systemctl status trading-bot

# 중지
sudo systemctl stop trading-bot

# 시작
sudo systemctl start trading-bot

# 재시작
sudo systemctl restart trading-bot

# 자동 실행 해제
sudo systemctl disable trading-bot
```

### 로그 확인
```bash
# 실시간 로그
sudo journalctl -u trading-bot -f

# 최근 100줄
sudo journalctl -u trading-bot -n 100

# 오늘 로그만
sudo journalctl -u trading-bot --since today
```

### 코드 업데이트
```bash
# Git 사용 시
cd ~/YOUR_REPO
git pull
sudo systemctl restart trading-bot

# 직접 업로드 시
# 로컬에서: scp -i ~/.ssh/oracle_key file.py ubuntu@IP:~/YOUR_REPO/
sudo systemctl restart trading-bot
```

---

## 🔒 보안 강화 (선택사항)

### 1. 도메인 연결 (선택)
무료 도메인 (Freenom, 또는 구매)을 IP에 연결하면:
```
http://mybot.com
```

### 2. HTTPS 설정 (nginx + Let's Encrypt)
```bash
# nginx 설치
sudo apt install -y nginx certbot python3-certbot-nginx

# nginx 설정
sudo nano /etc/nginx/sites-available/trading-bot
```

설정 내용:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

활성화:
```bash
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# HTTPS (도메인 있는 경우)
sudo certbot --nginx -d yourdomain.com
```

### 3. 비밀번호 보호
Streamlit에 기본 인증 추가 (선택)

---

## 💰 비용

### Oracle Cloud Always Free
- ✅ VM: 영구 무료
- ✅ Storage: 200GB 무료
- ✅ Bandwidth: 10TB/월 무료
- ✅ IP: 2개 무료

**진짜 무료입니다!** 단, Always Free 리소스만 사용하세요.

---

## 📊 모니터링

### 서버 상태
```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크
sudo netstat -tulpn | grep 8501
```

### 대시보드에서
- 봇 시작/중지
- 실시간 거래 내역
- 수익률 차트
- 포지션 현황

---

## 🛠️ 트러블슈팅

### 포트 접속 안됨
1. Oracle Cloud 방화벽 규칙 확인
2. Ubuntu UFW 확인: `sudo ufw status`
3. 서비스 실행 확인: `sudo systemctl status trading-bot`

### 서비스 실행 실패
```bash
# 로그 확인
sudo journalctl -u trading-bot -n 50

# 수동 실행으로 테스트
cd ~/YOUR_REPO
source .venv/bin/activate
streamlit run dashboard.py
```

### SSH 접속 안됨
- 키 권한 확인: `chmod 600 ~/.ssh/oracle_key`
- 올바른 사용자명: `ubuntu` (Oracle Ubuntu 이미지)

### 메모리 부족
- swap 추가:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🎉 완료!

이제:
- ✅ 컴퓨터 꺼도 24/7 실행
- ✅ 어디서든 접속 가능
- ✅ 자동 재시작
- ✅ 100% 무료
- ✅ 영구 사용 가능

**해피 트레이딩! 🚀📈💰**

---

## 📞 다음 단계

1. Oracle Cloud 계정 만들기
2. VM 인스턴스 생성
3. 이 가이드 따라하기
4. 봇 실행!

궁금한 점이 있으면 문서를 다시 확인하세요! 😊
