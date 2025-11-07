# 🌐 가비아 DNS 설정 가이드 (guity.kr)

가비아에서 `guity.kr` 도메인의 DNS를 설정하는 방법입니다.

---

## 1️⃣ 가비아 로그인

https://www.gabia.com 접속 후 로그인

---

## 2️⃣ DNS 관리 페이지 이동

### 방법 1: My가비아에서
1. **My가비아** 클릭
2. **서비스 관리** → **도메인**
3. `guity.kr` 찾기
4. **관리** 버튼 클릭
5. **DNS 정보** 또는 **DNS 관리** 클릭

### 방법 2: 직접 링크
https://dns.gabia.com

---

## 3️⃣ DNS 레코드 추가

### 서브도메인 사용 (추천): `bot.guity.kr`

#### 레코드 추가 버튼 클릭 후:

```
타입(Type): A
호스트(Host): bot
값/위치(Value): <Oracle VM Public IP>
TTL: 3600 (1시간)
```

**예시:**
```
타입: A
호스트: bot
값: 152.67.123.45
TTL: 3600
```

#### 결과:
- `bot.guity.kr` → Oracle 서버로 연결

---

### 루트 도메인 사용: `guity.kr`

메인 도메인을 직접 사용하려면:

```
타입: A
호스트: @ (또는 비워두기)
값: <Oracle VM Public IP>
TTL: 3600
```

**예시:**
```
타입: A
호스트: @
값: 152.67.123.45
TTL: 3600
```

#### 결과:
- `guity.kr` → Oracle 서버로 연결

---

## 4️⃣ 설정 저장

1. **적용** 또는 **저장** 버튼 클릭
2. DNS 전파 대기 (5분~1시간, 보통 10분 이내)

---

## 5️⃣ DNS 전파 확인

### 터미널에서 확인 (Mac/Linux)
```bash
# 서브도메인 사용 시
nslookup bot.guity.kr
dig bot.guity.kr

# 루트 도메인 사용 시
nslookup guity.kr
dig guity.kr
```

### 온라인 도구
- https://dnschecker.org
- `bot.guity.kr` 입력
- 전세계 DNS 서버에서 IP 확인

### 정상 응답 예시:
```
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	bot.guity.kr
Address: 152.67.123.45
```

---

## 🎯 추천 설정

### 옵션 A: 서브도메인 (추천) ⭐
```
bot.guity.kr → Oracle IP
```
**장점:**
- 메인 도메인 따로 사용 가능
- 나중에 다른 서비스 추가 가능 (api.guity.kr, admin.guity.kr 등)
- 깔끔하고 명확

### 옵션 B: 루트 도메인
```
guity.kr → Oracle IP
```
**장점:**
- 짧은 주소
- 단순함

**단점:**
- 메인 사이트로 다른 용도 못씀
- www.guity.kr은 별도 설정 필요

---

## 🔧 추가 설정 (선택사항)

### www 리다이렉트 (루트 도메인 사용 시)

`guity.kr`과 `www.guity.kr` 둘 다 작동하게:

1. **CNAME 레코드 추가:**
```
타입: CNAME
호스트: www
값: guity.kr
TTL: 3600
```

또는

2. **A 레코드 2개:**
```
레코드 1:
타입: A
호스트: @
값: 152.67.123.45

레코드 2:
타입: A
호스트: www
값: 152.67.123.45
```

---

## 📱 가비아 앱에서 설정

### 모바일로도 가능!

1. **가비아 앱** 다운로드 (iOS/Android)
2. 로그인
3. **도메인 관리** → `guity.kr`
4. **DNS 관리**
5. A 레코드 추가
   - 호스트: `bot`
   - 값: Oracle IP
6. 저장

---

## ⏱️ DNS 전파 시간

### 가비아 DNS 전파 속도
- **국내:** 5~10분 (빠름)
- **해외:** 최대 1시간
- **최대:** 48시간 (거의 안 걸림)

### 빠른 확인 방법
```bash
# 가비아 DNS 서버에 직접 질의
nslookup bot.guity.kr ns.gabia.co.kr
```

---

## 🛠️ 트러블슈팅

### DNS가 안 먹혀요!

#### 1. 설정 재확인
- 가비아 DNS 관리 페이지 재확인
- 오타 확인 (bot vs bott)
- IP 주소 정확한지 확인

#### 2. 캐시 삭제
```bash
# Mac
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder

# Windows
ipconfig /flushdns

# Linux
sudo systemd-resolve --flush-caches
```

#### 3. 다른 DNS 서버로 확인
```bash
# Google DNS로 확인
nslookup bot.guity.kr 8.8.8.8

# Cloudflare DNS로 확인
nslookup bot.guity.kr 1.1.1.1
```

#### 4. 시간 대기
- DNS 전파는 시간이 필요합니다
- 10분 정도 기다렸다가 다시 확인

### 가비아 DNS 서버 주소
- ns.gabia.co.kr (Primary)
- ns1.gabia.co.kr (Secondary)
- ns2.gabia.co.kr (Tertiary)

---

## 📋 최종 체크리스트

### DNS 설정 전:
- [ ] Oracle VM 생성 완료
- [ ] Public IP 확인 (예: 152.67.123.45)
- [ ] 가비아 로그인 정보 확인

### DNS 설정:
- [ ] 가비아 DNS 관리 페이지 접속
- [ ] A 레코드 추가
  - 호스트: `bot`
  - 값: Oracle IP
  - TTL: 3600
- [ ] 저장/적용 클릭

### 설정 후:
- [ ] `nslookup bot.guity.kr` 확인
- [ ] 10분 대기
- [ ] 브라우저에서 `http://bot.guity.kr:8501` 접속 테스트
- [ ] Oracle 서버에서 `deploy_server.sh` 실행
- [ ] `https://bot.guity.kr` 최종 확인

---

## 🎯 다음 단계

DNS 설정 완료 후:

1. **`DEPLOY_GUITY_KR.md`** 파일 열기
2. **3️⃣ Oracle Cloud 방화벽 열기**부터 계속 진행
3. `deploy_server.sh` 실행 시 `bot.guity.kr` 입력

---

## 💡 팁

### 서브도메인 여러 개 만들기
나중에 다양한 서비스 추가 가능:

```
bot.guity.kr → 자동매매 봇
api.guity.kr → API 서버
admin.guity.kr → 관리자 페이지
test.guity.kr → 테스트 환경
```

각각 다른 IP나 같은 IP의 다른 포트로 연결 가능!

---

## 📞 가비아 고객센터

문제가 있으면:
- 📞 전화: 1544-4370
- 💬 채팅: 가비아 웹사이트 우측 하단
- 📧 이메일: help@gabia.com

보통 DNS 설정은 매우 간단하니 걱정 마세요! 😊

---

## 🎉 완료!

가비아 DNS 설정 끝!

**다음:** `DEPLOY_GUITY_KR.md` 파일로 돌아가서 배포 계속 진행하세요! 🚀
