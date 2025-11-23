# 로컬 테스트 배포 가이드

현재 호스팅 PC에서 배포를 테스트할 수 있습니다.

## 사전 준비

### 1. Docker 및 Docker Compose 설치 확인
```bash
docker --version
docker compose version
```

### 2. 프론트엔드 빌드
프론트엔드를 먼저 빌드해야 합니다:
```bash
cd /app/frontend
npm install
npm run build
cd /app
```

## 배포 방법

### 방법 1: 자동 스크립트 사용 (권장)
```bash
./deploy/test-deploy.sh
```

### 방법 2: 수동 배포
```bash
# 1. 프론트엔드 빌드
cd /app/frontend
npm install
npm run build
cd /app

# 2. Docker 컨테이너 시작
docker compose -f docker-compose.test.yml up -d --build
```

## 접속 정보

배포가 완료되면 다음 주소로 접속할 수 있습니다:

- **프론트엔드**: http://localhost:8080
- **백엔드 API**: http://localhost:8080/api
- **데이터베이스**: localhost:5433

## 유용한 명령어

### 컨테이너 상태 확인
```bash
docker compose -f docker-compose.test.yml ps
```

### 로그 확인
```bash
# 모든 서비스 로그
docker compose -f docker-compose.test.yml logs -f

# 특정 서비스 로그
docker compose -f docker-compose.test.yml logs -f backend
docker compose -f docker-compose.test.yml logs -f nginx
```

### 컨테이너 중지
```bash
docker compose -f docker-compose.test.yml down
```

### 컨테이너 중지 및 볼륨 삭제
```bash
docker compose -f docker-compose.test.yml down -v
```

### 특정 서비스만 재시작
```bash
docker compose -f docker-compose.test.yml restart backend
```

## 문제 해결

### 포트 충돌
포트 8080이나 5433이 이미 사용 중인 경우:
- `docker-compose.test.yml` 파일에서 포트 번호를 변경하세요

### 프론트엔드 빌드 오류
```bash
cd /app/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 데이터베이스 연결 오류
- `backend/.env` 파일의 데이터베이스 설정을 확인하세요
- 컨테이너가 모두 실행 중인지 확인: `docker compose -f docker-compose.test.yml ps`

### Nginx 502 오류
- 백엔드 컨테이너가 실행 중인지 확인
- 백엔드 로그 확인: `docker compose -f docker-compose.test.yml logs backend`

## 프로덕션 배포로 전환

테스트가 완료되면 프로덕션 배포로 전환할 수 있습니다:

1. SSL 인증서 발급
2. `docker-compose.prod.yml` 사용
3. `deploy/nginx.conf` 설정 확인 (도메인명 변경)






