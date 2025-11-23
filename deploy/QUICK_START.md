# 빠른 시작 가이드

## 📋 배포 명령어 요약

### 1️⃣ 처음 배포하기
```bash
./deploy/run-on-host.sh
```
- 프론트엔드 빌드 + 모든 서비스 시작
- 코드 변경 후에도 사용

### 2️⃣ 재시작하기 (코드 변경 없을 때)
```bash
./deploy/restart.sh
```
- 이미 빌드된 파일 사용
- 빠르게 재시작

### 3️⃣ 중지하기
```bash
docker compose -f docker-compose.test.yml down
```

## 🔄 일반적인 작업 흐름

### 시나리오 1: 처음 배포
```bash
# 1. 배포
./deploy/run-on-host.sh

# 2. 테스트 후 중지
docker compose -f docker-compose.test.yml down
```

### 시나리오 2: 재시작 (코드 변경 없음)
```bash
# 1. 중지된 상태에서 재시작
./deploy/restart.sh

# 2. 다시 중지
docker compose -f docker-compose.test.yml down
```

### 시나리오 3: 코드 변경 후 재배포
```bash
# 1. 코드 수정 (Cursor에서)
# 2. 재배포
./deploy/run-on-host.sh
```

## 📝 자주 묻는 질문

### Q: 중지 후 다시 시작할 때 .sh 파일을 또 실행해야 하나요?
**A: 상황에 따라 다릅니다!**

- **코드 변경 없음**: `./deploy/restart.sh` (빠름)
- **코드 변경 있음**: `./deploy/run-on-host.sh` (빌드 필요)

### Q: restart.sh와 run-on-host.sh의 차이는?
- **restart.sh**: 이미 빌드된 파일 사용, 빠른 재시작
- **run-on-host.sh**: 프론트엔드 다시 빌드, 완전 재배포

### Q: 언제 어떤 스크립트를 사용하나요?
- 처음 배포: `run-on-host.sh`
- 코드 변경 없이 재시작: `restart.sh`
- 코드 변경 후 재배포: `run-on-host.sh`

## 🎯 권장 사용법

```bash
# 처음 배포
./deploy/run-on-host.sh

# 테스트 중 중지
docker compose -f docker-compose.test.yml down

# 다시 시작 (코드 변경 없음)
./deploy/restart.sh

# 코드 수정 후
./deploy/run-on-host.sh
```


