#!/bin/bash
# Oracle Cloud 서버 자동 배포 스크립트
# 서버에 업로드 후 실행: bash deploy_server.sh

set -e

echo "🚀 비트코인 자동매매 봇 서버 배포 시작..."
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 시스템 업데이트
echo -e "${GREEN}[1/8]${NC} 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
echo -e "${GREEN}[2/8]${NC} 필수 패키지 설치 중..."
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx ufw htop

# 3. 방화벽 설정
echo -e "${GREEN}[3/8]${NC} 방화벽 설정 중..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8501/tcp  # Streamlit (백업)
sudo ufw --force enable

# 4. Python 가상환경 생성
echo -e "${GREEN}[4/8]${NC} Python 가상환경 설정 중..."
python3 -m venv .venv
source .venv/bin/activate

# 5. Python 패키지 설치
echo -e "${GREEN}[5/8]${NC} Python 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. .env 파일 확인
echo -e "${GREEN}[6/8]${NC} 환경 변수 확인 중..."
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env 파일이 없습니다!${NC}"
    echo "   .env.example을 복사하여 .env 파일을 만들어주세요:"
    echo "   cp .env.example .env"
    echo "   nano .env  # API 키 입력"
    exit 1
else
    echo -e "${GREEN}✅ .env 파일 발견${NC}"
fi

# 7. systemd 서비스 생성
echo -e "${GREEN}[7/8]${NC} systemd 서비스 설정 중..."
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

sudo tee /etc/systemd/system/trading-bot.service > /dev/null <<EOF
[Unit]
Description=Bitcoin Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/.venv/bin"
ExecStart=$CURRENT_DIR/.venv/bin/streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# 8. 도메인 설정 여부 확인
echo -e "${GREEN}[8/8]${NC} 웹 서버 설정..."
echo ""
read -p "도메인을 연결하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "도메인 입력 (예: bot.yourdomain.com): " DOMAIN

    # nginx 설정
    sudo tee /etc/nginx/sites-available/trading-bot > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    # SSL 설정
    echo ""
    read -p "HTTPS (SSL) 인증서를 설치하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "이메일 주소 입력: " EMAIL
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
        echo -e "${GREEN}✅ HTTPS 설정 완료!${NC}"
        echo -e "${GREEN}   접속 주소: https://$DOMAIN${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP만 사용합니다.${NC}"
        echo -e "${YELLOW}   접속 주소: http://$DOMAIN${NC}"
    fi
else
    PUBLIC_IP=$(curl -s ifconfig.me)
    echo -e "${YELLOW}⚠️  도메인 없이 IP로 접속합니다.${NC}"
    echo -e "${YELLOW}   접속 주소: http://$PUBLIC_IP:8501${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "✅ 서비스 상태 확인:"
echo -e "   ${YELLOW}sudo systemctl status trading-bot${NC}"
echo ""
echo -e "📊 로그 확인:"
echo -e "   ${YELLOW}sudo journalctl -u trading-bot -f${NC}"
echo ""
echo -e "🔄 재시작:"
echo -e "   ${YELLOW}sudo systemctl restart trading-bot${NC}"
echo ""
echo -e "🛑 중지:"
echo -e "   ${YELLOW}sudo systemctl stop trading-bot${NC}"
echo ""
echo -e "${GREEN}행복한 트레이딩 되세요! 🚀📈💰${NC}"
