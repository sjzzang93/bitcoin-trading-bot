#!/bin/bash
# 비트코인 자동매매 봇 시작 스크립트

echo "🚀 비트코인 단타 자동매매 봇 시작..."

# 가상환경 활성화
if [ -d ".venv" ]; then
    echo "✅ 가상환경 활성화..."
    source .venv/bin/activate
else
    echo "⚠️  가상환경이 없습니다. 생성 중..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# 환경변수 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "   .env.example을 참고하여 .env 파일을 만들어주세요."
    exit 1
fi

echo "✅ 환경 설정 완료"
echo ""
echo "📊 Streamlit 대시보드를 시작합니다..."
echo "   로컬 접속: http://localhost:8501"
echo ""
echo "💡 외부 접속을 원하시면 별도 터미널에서:"
echo "   ngrok http 8501"
echo ""

# Streamlit 실행
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
