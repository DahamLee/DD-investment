# 배포 가이드

이 디렉토리에는 배포 관련 파일들이 있습니다.

## 파일 설명

- **`run-on-host.sh`** - 호스트 컴퓨터에서 실행하는 배포 스크립트 (npm 설치 불필요)
- **`test-deploy.sh`** - 컨테이너 내부에서도 사용 가능한 배포 스크립트
- **`nginx.test.conf`** - 테스트용 nginx 설정 (HTTP만, SSL 없음)
- **`nginx.conf`** - 프로덕션용 nginx 설정 (HTTPS, SSL 필요)
- **`HOST_DEPLOYMENT.md`** - 호스트 배포 상세 가이드
- **`TEST_DEPLOYMENT.md`** - 테스트 배포 가이드

## 빠른 시작

### 처음 배포하기

```bash
./deploy/run-on-host.sh
```

이 스크립트는:
- ✅ Docker만 있으면 됩니다 (npm 설치 불필요)
- ✅ 자동으로 프론트엔드를 Docker로 빌드합니다
- ✅ 모든 서비스를 시작합니다

### 재시작하기

#### 방법 1: 빠른 재시작 (코드 변경 없을 때)
```bash
./deploy/restart.sh
```
- ✅ 이미 빌드된 파일 사용
- ✅ 빠르게 재시작

#### 방법 2: 완전 재배포 (코드 변경 후)
```bash
./deploy/run-on-host.sh
```
- ✅ 프론트엔드 다시 빌드
- ✅ 모든 컨테이너 재빌드

### 중지하기

```bash
docker compose -f docker-compose.test.yml down
```

### 요구사항

- Docker
- Docker Compose

npm이나 Node.js는 **설치할 필요 없습니다** - Docker가 자동으로 처리합니다!

## 접속 정보

배포 완료 후:
- 프론트엔드: http://localhost:8080
- 백엔드 API: http://localhost:8080/api
- 데이터베이스: localhost:5433

## 문제 해결

### "npm: command not found"
→ `run-on-host.sh`를 사용하세요. 이 스크립트는 Docker를 사용해서 빌드하므로 npm이 필요 없습니다.

### "docker: command not found"
→ Docker를 설치해야 합니다: https://docs.docker.com/get-docker/

### 포트 충돌
→ `docker-compose.test.yml`에서 포트 번호를 변경하세요.

