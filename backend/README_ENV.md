# 환경별 DB 설정 관리

## 📁 환경 파일 구조

```
backend/
├── .env                 # (사용 안 함 - 각 compose 파일이 직접 환경별 파일 참조)
├── .env.development    # 개발용 (docker-compose.yml, docker-compose.test.yml에서 사용)
├── .env.local          # 로컬 개발용 (선택사항)
├── .env.production     # 프로덕션용 (docker-compose.prod.yml에서 사용)
└── env.example         # 예시 파일 (Git 포함)
```

## 🔄 환경별 사용 방법

### 개발 환경
```bash
# docker-compose.yml이 자동으로 .env.development 사용
docker compose up -d
```

### 테스트 환경
```bash
# docker-compose.test.yml이 자동으로 .env.development 사용
docker compose -f docker-compose.test.yml up -d
```

### 프로덕션 환경
```bash
# docker-compose.prod.yml이 자동으로 .env.production 사용
docker compose -f docker-compose.prod.yml up -d
```

**✅ 복사할 필요 없음!** 각 compose 파일이 해당 환경의 .env 파일을 직접 참조합니다.

## 📊 DB 서버 정보

### 로컬 DB
- Host: `121.134.7.122`
- Port: `5432`
- Database: `finance_db`

### GCP DB
- Host: `34.64.149.167`
- Port: `5432`
- Database: `finance_db`
- Project: `ddinvestment`
- Region: `asia-northeast3`

## 🔒 보안

`.env` 파일들은 `.gitignore`에 포함되어 Git에 커밋되지 않습니다.

## ⚡ 빠른 명령어

```bash
# 개발 환경 DB 확인
cat backend/.env.development | grep DATABASE_HOST

# 프로덕션 환경 DB 확인
cat backend/.env.production | grep DATABASE_HOST
```

## 📝 Docker Compose 파일별 환경 변수 매핑

| Compose 파일 | 사용하는 .env 파일 | 용도 |
|-------------|-------------------|------|
| `docker-compose.yml` | `.env.development` | 로컬 개발 |
| `docker-compose.test.yml` | `.env.development` | 테스트/스테이징 |
| `docker-compose.prod.yml` | `.env.production` | 프로덕션 배포 |



