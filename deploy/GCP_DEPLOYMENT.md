# 🚀 GCP 배포 가이드

이 가이드는 DD-Investment 프로젝트를 Google Cloud Platform (GCP)에 배포하는 방법을 설명합니다.

## 📋 사전 준비

### 1. GCP 계정 및 프로젝트
- [ ] GCP 계정 생성 (무료 크레딧 $300 제공)
- [ ] 프로젝트 생성 또는 기존 프로젝트 선택
- [ ] 결제 계정 연결

### 2. 도메인 (선택사항)
- [ ] 도메인 구매 (예: yourdomain.com)
- [ ] DNS 설정 준비

---

## 🔧 1단계: GCP VM 인스턴스 생성

### GCP Console에서 생성

1. **GCP Console 접속**
   - https://console.cloud.google.com/
   - 프로젝트 선택

2. **Compute Engine → VM 인스턴스 생성**
   - 이름: `dd-investment-server`
   - 지역: `asia-northeast3` (서울)
   - 영역: `asia-northeast3-a` (또는 b, c)
   - 머신 유형: `e2-micro` (무료 크레딧) 또는 `e2-small`
   - 부팅 디스크: Ubuntu 22.04 LTS, 20GB
   - 방화벽: ✅ HTTP 트래픽 허용, ✅ HTTPS 트래픽 허용

3. **고급 옵션**
   - 스냅샷 스케줄: 비활성화 (비용 절감)

4. **생성** 클릭

### gcloud CLI로 생성 (선택사항)

```bash
gcloud compute instances create dd-investment-server \
  --zone=asia-northeast3-a \
  --machine-type=e2-micro \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-standard \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server
```

---

## 🔥 2단계: 방화벽 규칙 설정

### GCP Console에서

1. **VPC 네트워크 → 방화벽**
2. **방화벽 규칙 만들기**
   - 이름: `allow-http-https`
   - 방향: 수신
   - 대상: 모든 인스턴스
   - 소스 IP 범위: `0.0.0.0/0`
   - 프로토콜 및 포트: TCP `80`, `443`
   - 만들기

### gcloud CLI로 (선택사항)

```bash
# HTTP 허용
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server

# HTTPS 허용
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server
```

---

## 💻 3단계: VM에 SSH 접속

### GCP Console에서

1. **Compute Engine → VM 인스턴스**
2. **dd-investment-server** 선택
3. **SSH** 버튼 클릭

### 로컬에서 (gcloud CLI 설치 시)

```bash
gcloud compute ssh dd-investment-server --zone=asia-northeast3-a
```

---

## 🛠️ 4단계: 서버 초기 설정

VM에 SSH 접속 후 다음 명령어들을 실행하세요:

```bash
# 시스템 업데이트
sudo apt update
sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Git 설치
sudo apt install git -y

# Docker 그룹 적용 (새 세션 필요)
newgrp docker

# 설치 확인
docker --version
docker compose version
```

---

## 📦 5단계: 프로젝트 클론

```bash
# 프로젝트 디렉토리로 이동
cd ~

# Git 저장소 클론 (또는 프로젝트 업로드)
git clone https://github.com/your-username/DD-Investment.git
cd DD-Investment

# 또는 직접 파일 업로드
# scp -r /local/path user@gcp-server-ip:~/DD-Investment
```

---

## ⚙️ 6단계: 환경 변수 파일 설정

### .env.production 파일 생성

```bash
# cat으로 파일 생성
cat > backend/.env.production << 'EOF'
# Production environment
DEBUG=False
APP_NAME="DD Investment API"

# Database
# 옵션 1: VM 내부 PostgreSQL 사용
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=finance_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password-here

# 옵션 2: Cloud SQL 사용 (Cloud SQL 사용 시)
# DATABASE_HOST=34.64.149.167  # Cloud SQL IP 주소
# DATABASE_PORT=5432
# DATABASE_NAME=finance_db
# DATABASE_USER=postgres
# DATABASE_PASSWORD=your-cloud-sql-password

# GCP 프로젝트 정보
GCP_PROJECT_ID=your-project-id
GCP_REGION=asia-northeast3
GCP_INSTANCE_NAME=your-instance-name

# API keys
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
NEWS_API_KEY=your-news-api-key

# Security
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# 파일 확인
cat backend/.env.production
```

**중요:** 실제 값으로 변경하세요:
- `DATABASE_PASSWORD`: 강력한 비밀번호
- `SECRET_KEY`: 랜덤 문자열 (예: `openssl rand -hex 32`)
- `GCP_PROJECT_ID`: GCP Console 상단에서 확인
- API 키들: 실제 API 키 입력

---

## 🚀 7단계: 배포 실행

```bash
# 배포 스크립트 실행 권한 부여
chmod +x deploy/run-prod.sh

# 배포 실행
./deploy/run-prod.sh
```

또는 확인 없이 실행:

```bash
SKIP_CONFIRMATION=true ./deploy/run-prod.sh
```

---

## 🌐 8단계: 도메인 및 SSL 설정 (선택사항)

### 도메인 DNS 설정

도메인 제공업체에서 DNS 설정:

```
A 레코드: yourdomain.com → GCP VM 외부 IP
A 레코드: www.yourdomain.com → GCP VM 외부 IP
```

**GCP VM 외부 IP 확인:**
```bash
# GCP Console → Compute Engine → VM 인스턴스 → 외부 IP
# 또는
gcloud compute instances describe dd-investment-server \
  --zone=asia-northeast3-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

### SSL 인증서 설치

```bash
# Certbot 설치
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# nginx 컨테이너 중지 (임시)
docker compose -f docker-compose.prod.yml stop nginx

# SSL 인증서 발급
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com

# docker-compose.prod.yml에서 nginx.conf 사용하도록 변경
# (이미 설정되어 있음)

# nginx 재시작
docker compose -f docker-compose.prod.yml up -d nginx
```

---

## ✅ 9단계: 배포 확인

```bash
# 컨테이너 상태 확인
docker compose -f docker-compose.prod.yml ps

# 로그 확인
docker compose -f docker-compose.prod.yml logs -f

# 웹 브라우저에서 접속 테스트
# http://your-gcp-vm-ip 또는 https://yourdomain.com
```

---

## 🔄 유지보수 명령어

### 재시작
```bash
# 전체 재시작
docker compose -f docker-compose.prod.yml restart

# 특정 서비스만 재시작
docker compose -f docker-compose.prod.yml restart backend
```

### 중지
```bash
# 컨테이너 중지
docker compose -f docker-compose.prod.yml down

# 볼륨까지 삭제 (주의!)
docker compose -f docker-compose.prod.yml down -v
```

### 로그 확인
```bash
# 모든 서비스 로그
docker compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx
```

### 코드 업데이트 후 재배포
```bash
# Git에서 최신 코드 가져오기
git pull

# 재배포
./deploy/run-prod.sh
```

---

## 🔐 SSL 인증서 자동 갱신

Let's Encrypt 인증서는 90일마다 갱신이 필요합니다.

### Cron 작업 설정

```bash
# crontab 편집
sudo crontab -e

# 다음 줄 추가 (매일 새벽 3시에 갱신 시도)
0 3 * * * certbot renew --quiet && cd /home/user/DD-Investment && docker compose -f docker-compose.prod.yml restart nginx
```

---

## 💰 비용 예상

### Compute Engine (e2-micro)
- 무료 크레딧: $300 (90일간)
- 이후: 월 약 $6-10 (24시간 실행 시)

### Cloud SQL (선택사항)
- 가장 작은 인스턴스: 월 약 $7-15
- 또는 VM에서 직접 PostgreSQL: 무료

### 총 예상 비용
- 무료 크레딧 기간: **$0**
- 이후: **월 $6-25** (사용량에 따라)

---

## 🐛 문제 해결

### 포트가 이미 사용 중
```bash
# 포트 사용 확인
sudo lsof -i :80
sudo lsof -i :443

# 다른 프로세스 중지
sudo systemctl stop apache2  # Apache가 실행 중인 경우
```

### Docker 권한 문제
```bash
# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
newgrp docker
```

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker compose -f docker-compose.prod.yml logs

# 환경 변수 확인
cat backend/.env.production
```

### SSL 인증서 오류
```bash
# 인증서 확인
sudo certbot certificates

# 인증서 재발급
sudo certbot renew --force-renewal
```

---

## 📞 추가 리소스

- [GCP Compute Engine 문서](https://cloud.google.com/compute/docs)
- [Docker 공식 문서](https://docs.docker.com/)
- [Let's Encrypt 문서](https://letsencrypt.org/docs/)

---

**마지막 업데이트**: 2024년 11월




