# 데이터베이스 마이그레이션 가이드

다른 DB 서버에서 데이터를 현재 DB로 옮기는 방법을 설명합니다.

> ⚠️ **보안 주의**: 이 문서의 예시에서 사용하는 비밀번호는 placeholder입니다. 실제 사용 시 `.env` 파일이나 환경 변수에서 비밀번호를 가져오거나, 명령줄에 직접 입력하세요.

## 🔐 비밀번호 관리 방법

### 방법 1: 환경 변수 사용 (권장)

```bash
# 환경 변수로 설정
export SOURCE_DB_PASSWORD="실제소스비밀번호"
export TARGET_DB_PASSWORD="실제타겟비밀번호"

# 스크립트 실행 시 환경 변수 사용
python scripts/migrate_with_schema_sync.py \
  --source-host 121.134.7.122 \
  --source-database finance_db \
  --source-user postgres \
  --source-password "$SOURCE_DB_PASSWORD" \
  --target-host 34.64.149.167 \
  --target-database finance_db \
  --target-user postgres \
  --target-password "$TARGET_DB_PASSWORD"
```

### 방법 2: .env 파일 사용

`.env` 파일에 비밀번호를 저장하고 스크립트에서 읽어오도록 수정할 수 있습니다 (현재는 미구현).

### 방법 3: 명령줄 직접 입력

```bash
# 비밀번호를 직접 입력 (히스토리에 남지 않음)
python scripts/migrate_with_schema_sync.py \
  --source-host 121.134.7.122 \
  --source-database finance_db \
  --source-user postgres \
  --source-password "$(read -s -p 'Source DB Password: ' && echo $REPLY)" \
  ...
```

---

## ⚠️ 중요: 스키마 동기화 먼저!

**개발계와 운영계를 함께 운영할 때는 반드시 스키마를 먼저 동기화해야 합니다!**

데이터를 옮기기 전에:
1. ✅ 두 DB의 Alembic 마이그레이션 버전 확인
2. ✅ 스키마 차이 확인 및 동기화
3. ✅ 그 다음 데이터 마이그레이션

---

## 📋 방법 0: 통합 스크립트 사용 (가장 권장)

**스키마 동기화 + 데이터 마이그레이션을 한 번에 실행**

```bash
cd /app/backend

# 개발계 → 운영계 마이그레이션 (스키마 동기화 포함)
python scripts/migrate_with_schema_sync.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-port 5432 \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호
```

### 옵션

- `--dry-run`: 실제로 변경하지 않고 확인만
- `--skip-schema-sync`: 스키마 동기화 건너뛰기 (이미 동기화된 경우)
- `--schema finance`: 특정 스키마만
- `--tables users email_verifications`: 특정 테이블만
- `--skip-tables lotto_numbers`: 특정 테이블 제외

---

## 📋 방법 1: 스키마 동기화만

두 DB의 스키마를 동일하게 맞추기:

```bash
cd /app/backend

# 스키마 동기화 (dry-run으로 먼저 확인)
python scripts/sync_schema.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-port 5432 \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호 \
  --dry-run

# 실제 실행
python scripts/sync_schema.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-port 5432 \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호
```

---

## 📋 방법 2: 데이터 마이그레이션만 (스키마 동기화 후)

### 기본 사용법

```bash
cd /app/backend

# 현재 .env의 타겟 DB로 마이그레이션
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호
```

### 특정 테이블만 복사

```bash
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --tables users email_verifications
```

### 스키마 지정 (finance 스키마)

```bash
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --schema finance
```

### 타겟 DB 직접 지정

```bash
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-port 5432 \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호
```

### 특정 테이블 제외

```bash
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --skip-tables alembic_version lotto_numbers
```

---

## 📋 방법 3: pg_dump / pg_restore 사용 (대용량 데이터)

### 전체 데이터베이스 덤프

```bash
# 소스 DB에서 덤프 생성
pg_dump -h 121.134.7.122 -p 5432 -U postgres -d finance_db \
  -F c -f /tmp/finance_db_backup.dump

# 타겟 DB로 복원
pg_restore -h host.docker.internal -p 5432 -U postgres -d finance_db \
  -c /tmp/finance_db_backup.dump
```

### 특정 스키마만 덤프

```bash
# finance 스키마만 덤프
pg_dump -h 121.134.7.122 -p 5432 -U postgres -d finance_db \
  -n finance -F c -f /tmp/finance_schema.dump

# 복원
pg_restore -h host.docker.internal -p 5432 -U postgres -d finance_db \
  -n finance /tmp/finance_schema.dump
```

### 특정 테이블만 덤프

```bash
# users 테이블만 덤프
pg_dump -h 121.134.7.122 -p 5432 -U postgres -d finance_db \
  -t users -F c -f /tmp/users_backup.dump

# 복원
pg_restore -h host.docker.internal -p 5432 -U postgres -d finance_db \
  /tmp/users_backup.dump
```

---

## 📋 방법 4: SQL 덤프 사용

### SQL 파일로 덤프

```bash
# 덤프 생성
pg_dump -h 121.134.7.122 -p 5432 -U postgres -d finance_db \
  > /tmp/finance_db.sql

# 복원
psql -h host.docker.internal -p 5432 -U postgres -d finance_db \
  < /tmp/finance_db.sql
```

---

## ⚠️ 주의사항

### 1. 마이그레이션 전 확인사항

- ✅ **두 DB의 Alembic 버전 확인** (가장 중요!)
- ✅ 타겟 DB에 스키마가 생성되어 있는지 확인
- ✅ 타겟 DB에 테이블 구조가 동일한지 확인
- ✅ 외래키 제약조건 순서 확인

### 2. 올바른 순서

**방법 A: 통합 스크립트 사용 (권장)**
```bash
# 한 번에 스키마 동기화 + 데이터 마이그레이션
python scripts/migrate_with_schema_sync.py --source-host ... --target-host ...
```

**방법 B: 단계별 실행**
```bash
# 1단계: 스키마 동기화
python scripts/sync_schema.py --source-host ... --target-host ...

# 2단계: 데이터 마이그레이션
python scripts/migrate_database.py --source-host ...
```

**방법 C: 수동 실행**
```bash
# 1단계: 각 DB의 마이그레이션 버전 확인
cd /app/backend
alembic current  # 소스 DB
# .env 변경 후
alembic current  # 타겟 DB

# 2단계: 타겟 DB를 최신 버전으로 업그레이드
alembic upgrade head

# 3단계: 데이터 마이그레이션
python scripts/migrate_database.py --source-host ...
```

### 3. 데이터 무결성

- 외래키 제약조건이 있는 경우 순서대로 복사됩니다
- `users` → `finance.stock` → `finance.financial_account` → `finance.financial_statement_raw` 순서

### 4. 대용량 데이터

- 대용량 데이터(수 GB 이상)는 `pg_dump`/`pg_restore` 사용 권장
- 작은 데이터는 Python 스크립트 사용 가능

---

## 🔄 일반적인 마이그레이션 시나리오

### 시나리오 1: 개발 DB → 프로덕션 DB

**권장 방법 (통합 스크립트):**
```bash
cd /app/backend

# 스키마 동기화 + 데이터 마이그레이션 한 번에
python scripts/migrate_with_schema_sync.py \
  --source-host 121.134.7.122 \
  --source-port 5432 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-port 5432 \
  --target-database finance_db \
  --target-user postgres \
  --target-password ekgkaehddudABC123!
```

**단계별 방법:**
```bash
# 1. 스키마 동기화
python scripts/sync_schema.py \
  --source-host 121.134.7.122 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-database finance_db \
  --target-user postgres \
  --target-password ekgkaehddudABC123!

# 2. 데이터 마이그레이션
python scripts/migrate_database.py \
  --source-host 121.134.7.122 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host 34.64.149.167 \
  --target-database finance_db \
  --target-user postgres \
  --target-password ekgkaehddudABC123!
```

### 시나리오 2: 프로덕션 DB → 로컬 DB

**권장 방법:**
```bash
cd /app/backend

# 통합 스크립트 사용
python scripts/migrate_with_schema_sync.py \
  --source-host 34.64.149.167 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host host.docker.internal \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호
```

**또는 현재 .env 사용:**
```bash
# .env를 로컬로 설정 후
cp .env.local .env

# 통합 스크립트 (타겟은 .env 사용)
python scripts/migrate_with_schema_sync.py \
  --source-host 34.64.149.167 \
  --source-database finance_db \
  --source-user postgres \
  --source-password 소스DB비밀번호 \
  --target-host host.docker.internal \
  --target-database finance_db \
  --target-user postgres \
  --target-password 타겟DB비밀번호
```

---

## 🛠️ 트러블슈팅

### 연결 오류

```bash
# 연결 테스트
psql -h 121.134.7.122 -p 5432 -U postgres -d finance_db
```

### 권한 오류

- PostgreSQL의 `pg_hba.conf`에서 외부 연결 허용 확인
- 방화벽 설정 확인

### 스키마 오류

```bash
# 스키마 생성 확인
psql -h host.docker.internal -p 5432 -U postgres -d finance_db -c "\dn"
```

---

## 📝 참고

- Python 스크립트는 SQLAlchemy를 사용하여 데이터를 안전하게 복사합니다
- `pg_dump`는 PostgreSQL 공식 도구로 더 빠르지만 덜 유연합니다
- 대용량 데이터는 `pg_dump` 사용을 권장합니다

