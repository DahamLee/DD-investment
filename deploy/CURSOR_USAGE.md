# Docker 배포 후 Cursor 사용 가이드

## ✅ Cursor는 정상적으로 사용 가능합니다!

Docker로 배포해도 **Cursor IDE는 계속 사용할 수 있습니다**. 

## 왜 Cursor를 사용할 수 있나요?

### 1. Cursor는 호스트에서 실행됩니다
- Cursor IDE는 호스트 컴퓨터에서 실행되는 애플리케이션입니다
- Docker 컨테이너와는 **완전히 독립적**입니다

### 2. 파일 편집은 호스트에서 합니다
- Cursor로 파일을 편집하면 → 호스트의 파일 시스템이 변경됩니다
- Docker 컨테이너는 빌드된 이미지를 사용하므로 → 호스트 파일 변경이 즉시 반영되지 않습니다

### 3. 개발 vs 배포 모드

#### 개발 모드 (Cursor 사용 + 실시간 반영)
```bash
# docker-compose.yml 사용 (볼륨 마운트 있음)
docker compose up
```
- ✅ Cursor로 파일 편집 가능
- ✅ 변경사항이 컨테이너에 실시간 반영
- ✅ 개발 중 권장

#### 배포 모드 (Cursor 사용 가능, 재빌드 필요)
```bash
# docker-compose.test.yml 사용 (볼륨 마운트 없음)
docker compose -f docker-compose.test.yml up -d
```
- ✅ Cursor로 파일 편집 가능
- ⚠️ 변경사항 반영하려면 재빌드 필요
- ✅ 프로덕션/테스트 환경

## 작업 흐름

### 개발 중 (Cursor 사용)
```bash
# 1. 개발 모드로 시작
docker compose up

# 2. Cursor에서 파일 편집
# → 변경사항이 자동으로 컨테이너에 반영됨

# 3. 브라우저에서 확인
# → http://localhost:8000 (백엔드)
# → http://localhost:5173 (프론트엔드)
```

### 배포 테스트 (Cursor 사용)
```bash
# 1. 배포 모드로 시작
./deploy/run-on-host.sh

# 2. Cursor에서 파일 편집 가능
# → 파일은 편집되지만 컨테이너에는 반영 안 됨

# 3. 변경사항 반영하려면 재빌드
docker compose -f docker-compose.test.yml up -d --build

# 4. 브라우저에서 확인
# → http://localhost:8080
```

## 자주 묻는 질문

### Q: Docker 배포 후 Cursor에서 파일을 편집할 수 있나요?
**A: 네, 가능합니다!** Cursor는 호스트에서 실행되므로 언제든지 파일을 편집할 수 있습니다.

### Q: 편집한 내용이 바로 반영되나요?
**A: 배포 모드에서는 재빌드가 필요합니다.**
- 개발 모드 (`docker-compose.yml`): 즉시 반영 ✅
- 배포 모드 (`docker-compose.test.yml`): 재빌드 필요 ⚠️

### Q: 어떤 에러가 발생했나요?
구체적인 에러 메시지를 알려주시면 해결 방법을 제시하겠습니다.

## 문제 해결

### "파일을 저장할 수 없습니다"
→ 파일 권한 문제일 수 있습니다:
```bash
# 파일 권한 확인
ls -la /app

# 필요시 권한 수정
sudo chown -R $USER:$USER /app
```

### "컨테이너 내부에서 Cursor를 실행하려고 했습니다"
→ Cursor는 **호스트에서만** 실행할 수 있습니다:
```bash
# 컨테이너에서 나가기
exit

# 호스트에서 Cursor 실행
cursor /app
```

### "변경사항이 반영되지 않습니다"
→ 배포 모드에서는 재빌드가 필요합니다:
```bash
# 프론트엔드 변경 시
cd frontend
npm run build
cd ..
docker compose -f docker-compose.test.yml up -d --build

# 백엔드 변경 시
docker compose -f docker-compose.test.yml up -d --build
```

## 권장 작업 방식

1. **개발 중**: `docker-compose.yml` 사용 (실시간 반영)
2. **배포 테스트**: `docker-compose.test.yml` 사용 (재빌드 필요)
3. **Cursor 사용**: 항상 호스트에서 사용 가능 ✅

## 추가 도움

구체적인 에러 메시지를 알려주시면 더 정확한 해결 방법을 제시하겠습니다!

