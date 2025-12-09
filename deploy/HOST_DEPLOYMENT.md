# 호스트 컴퓨터에서 배포하기

⚠️ **중요**: 배포 스크립트는 **호스트 컴퓨터**에서 실행해야 합니다. Docker 컨테이너 내부가 아닙니다!

## 현재 상황 확인

현재 Docker 컨테이너 내부에서 작업 중이라면, 호스트 컴퓨터로 나가서 실행해야 합니다.

## 배포 방법

### 1. 호스트 컴퓨터로 이동

Docker 컨테이너 내부에서 작업 중이라면:
```bash
# 컨테이너에서 나가기
exit
```

또는 새 터미널을 열어서 호스트 컴퓨터에서 작업하세요.

### 2. 프로젝트 디렉토리로 이동

호스트 컴퓨터에서:
```bash
cd /app  # 또는 프로젝트가 있는 실제 경로
```

### 3. Docker 설치 확인

```bash
docker --version
docker compose version
```

### 4. 배포 실행

#### 방법 1: 자동 스크립트 사용 (권장)
```bash
chmod +x deploy/run-on-host.sh
./deploy/run-on-host.sh
```

이 스크립트는:
- ✅ Docker만 있으면 됩니다 (npm 설치 불필요)
- ✅ 자동으로 프론트엔드를 Docker로 빌드합니다
- ✅ 모든 서비스를 시작합니다

#### 방법 2: 수동 실행
```bash
# 1. 프론트엔드 빌드
cd frontend
npm install  # 처음이거나 package.json이 변경된 경우
npm run build
cd ..

# 2. Docker 컨테이너 시작
docker compose -f docker-compose.test.yml up -d --build
```

## 접속 정보

배포가 완료되면:

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

## 문제 해결

### "docker: command not found"
Docker가 설치되어 있지 않습니다. 설치가 필요합니다.

### "포트가 이미 사용 중입니다"
다른 서비스가 포트를 사용 중일 수 있습니다:
- 8080 포트: 다른 웹 서버
- 5433 포트: 다른 PostgreSQL 인스턴스

포트를 변경하거나 기존 서비스를 중지하세요.

### "프론트엔드 빌드 실패"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### "백엔드 연결 오류"
- `backend/.env` 파일이 존재하는지 확인
- 데이터베이스 컨테이너가 실행 중인지 확인: `docker compose -f docker-compose.test.yml ps`

