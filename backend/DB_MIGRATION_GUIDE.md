# 데이터베이스 마이그레이션 가이드

이 문서는 Alembic을 사용한 데이터베이스 마이그레이션 방법과 다른 DB 서버에서 데이터를 옮기는 방법을 설명합니다.

## 목차
1. [Alembic 기본 사용법](#alembic-기본-사용법)
2. [마이그레이션 생성 및 적용](#마이그레이션-생성-및-적용)
3. [다른 DB 서버에서 데이터 옮기기](#다른-db-서버에서-데이터-옮기기)
4. [문제 해결](#문제-해결)

---

## Alembic 기본 사용법

### 초기 설정 확인

Alembic은 이미 프로젝트에 설정되어 있습니다:
- `backend/alembic/` - 마이그레이션 스크립트 디렉토리
- `backend/alembic.ini` - Alembic 설정 파일
- `backend/alembic/env.py` - 환경 설정 (Settings와 연동됨)

### 현재 마이그레이션 상태 확인

```bash
# 컨테이너 내부에서 실행
cd /app/backend
alembic current
```

### 마이그레이션 히스토리 확인

```bash
alembic history
```

---

## 마이그레이션 생성 및 적용

### 1. 초기 마이그레이션 생성 (최초 1회)

현재 데이터베이스 스키마를 기반으로 초기 마이그레이션을 생성합니다:

```bash
cd /app/backend
alembic revision --autogenerate -m "Initial migration"
```

이 명령은 `alembic/versions/` 디렉토리에 마이그레이션 파일을 생성합니다.

**주의**: 생성된 마이그레이션 파일을 검토하고 필요시 수정하세요.

### 2. 마이그레이션 적용

```bash
# 최신 마이그레이션까지 적용
alembic upgrade head

# 특정 리비전까지 적용
alembic upgrade <revision_id>

# 한 단계만 업그레이드
alembic upgrade +1
```

### 3. 마이그레이션 롤백

```bash
# 한 단계 롤백
alembic downgrade -1

# 특정 리비전으로 롤백
alembic downgrade <revision_id>

# 모든 마이그레이션 롤백
alembic downgrade base
```

### 4. 새로운 마이그레이션 생성 (모델 변경 후)

모델을 변경한 후:

```bash
# 자동으로 변경사항 감지하여 마이그레이션 생성
alembic revision --autogenerate -m "Add new column to users table"

# 수동으로 마이그레이션 생성 (자동 감지 불가능한 경우)
alembic revision -m "Custom migration description"
```

### 5. 빈 마이그레이션 생성 (수동 SQL 작성)

```bash
alembic revision -m "Custom SQL migration"
```

생성된 파일을 열어 `upgrade()`와 `downgrade()` 함수에 SQL을 작성합니다.

---

## 다른 DB 서버에서 데이터 옮기기

### 방법 1: pg_dump / pg_restore 사용 (PostgreSQL 권장)

#### 1단계: 원본 DB에서 덤프 생성

```bash
# 원본 서버에서 실행 (또는 원본 서버에 접속 가능한 곳에서)
pg_dump -h <원본_호스트> -U <사용자명> -d <데이터베이스명> \
  --no-owner --no-acl -F c -f backup.dump

# 또는 SQL 형식으로
pg_dump -h <원본_호스트> -U <사용자명> -d <데이터베이스명> \
  --no-owner --no-acl > backup.sql
```

**옵션 설명:**
- `--no-owner`: 소유자 정보 제외 (다른 사용자로 복원 가능)
- `--no-acl`: 권한 정보 제외
- `-F c`: 커스텀 형식 (압축됨, pg_restore 필요)
- `-F p`: SQL 텍스트 형식 (psql로 복원)

#### 2단계: 대상 DB에 스키마만 먼저 생성

```bash
# 대상 서버에서 마이그레이션 적용 (스키마 생성)
cd /app/backend
alembic upgrade head
```

#### 3단계: 데이터 복원

```bash
# 커스텀 형식 덤프인 경우
pg_restore -h <대상_호스트> -U <사용자명> -d <데이터베이스명> \
  --no-owner --no-acl --data-only backup.dump

# SQL 형식 덤프인 경우
psql -h <대상_호스트> -U <사용자명> -d <데이터베이스명> < backup.sql
```

**옵션 설명:**
- `--data-only`: 데이터만 복원 (스키마는 이미 있음)
- `--no-owner --no-acl`: 소유자/권한 정보 무시

### 방법 2: Python 스크립트로 데이터 이전

대용량 데이터나 특정 조건으로 필터링이 필요한 경우:

```python
# migrate_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, EmailVerification, Stock  # 필요한 모델들
from app.core.config import settings

# 원본 DB 연결
source_engine = create_engine("postgresql://user:pass@원본호스트:5432/dbname")
SourceSession = sessionmaker(bind=source_engine)

# 대상 DB 연결 (Settings 사용)
target_engine = create_engine(settings.database_url)
TargetSession = sessionmaker(bind=target_engine)

source_db = SourceSession()
target_db = TargetSession()

try:
    # 예: User 데이터 이전
    users = source_db.query(User).all()
    for user in users:
        target_db.merge(user)  # merge는 기존 데이터와 병합
    
    target_db.commit()
    print(f"✅ {len(users)}명의 사용자 데이터 이전 완료")
except Exception as e:
    target_db.rollback()
    print(f"❌ 오류 발생: {e}")
finally:
    source_db.close()
    target_db.close()
```

실행:
```bash
cd /app/backend
python migrate_data.py
```

### 방법 3: CSV로 내보내기/가져오기

#### 내보내기 (원본 DB)

```sql
-- psql에서 실행
\copy (SELECT * FROM users) TO '/tmp/users.csv' CSV HEADER;
\copy (SELECT * FROM email_verifications) TO '/tmp/email_verifications.csv' CSV HEADER;
```

#### 가져오기 (대상 DB)

```sql
-- psql에서 실행
\copy users FROM '/tmp/users.csv' CSV HEADER;
\copy email_verifications FROM '/tmp/email_verifications.csv' CSV HEADER;
```

### 방법 4: Docker를 통한 이전

컨테이너 내부에서 실행:

```bash
# 원본 DB에서 덤프
docker exec -i <원본_컨테이너> pg_dump -U postgres finance_db > backup.sql

# 대상 DB에 복원
docker exec -i <대상_컨테이너> psql -U postgres finance_db < backup.sql
```

---

## 문제 해결

### 마이그레이션 충돌

여러 개발자가 동시에 마이그레이션을 생성한 경우:

```bash
# 1. 현재 상태 확인
alembic current

# 2. 충돌하는 마이그레이션 확인
alembic history

# 3. 수동으로 병합 마이그레이션 생성
alembic merge -m "Merge branches" <revision1> <revision2>
```

### 마이그레이션 롤백 후 재적용

```bash
# 롤백
alembic downgrade -1

# 수정 후 재적용
alembic upgrade head
```

### 데이터베이스와 모델 불일치

```bash
# 현재 DB 상태 확인
alembic current

# 모델 변경사항 자동 감지
alembic revision --autogenerate -m "Sync models"

# 생성된 마이그레이션 검토 후 적용
alembic upgrade head
```

### 외래 키 제약 조건 오류

데이터 이전 시 외래 키 제약 조건을 일시적으로 비활성화:

```sql
-- PostgreSQL
ALTER TABLE <table_name> DISABLE TRIGGER ALL;
-- 데이터 삽입
ALTER TABLE <table_name> ENABLE TRIGGER ALL;
```

또는 pg_dump 시:
```bash
pg_dump --disable-triggers ...
```

---

## 모범 사례

1. **항상 백업**: 마이그레이션 적용 전 데이터베이스 백업
2. **테스트 환경에서 먼저**: 프로덕션 적용 전 테스트 환경에서 검증
3. **마이그레이션 검토**: `--autogenerate`로 생성된 마이그레이션은 반드시 검토
4. **원자적 마이그레이션**: 각 마이그레이션은 독립적으로 실행 가능해야 함
5. **롤백 가능**: 모든 마이그레이션은 `downgrade()` 함수로 롤백 가능해야 함

---

## 유용한 명령어 요약

```bash
# 현재 상태
alembic current

# 히스토리
alembic history

# 마이그레이션 생성
alembic revision --autogenerate -m "Description"

# 적용
alembic upgrade head

# 롤백
alembic downgrade -1

# 특정 리비전 확인
alembic show <revision_id>
```

---

## 참고 자료

- [Alembic 공식 문서](https://alembic.sqlalchemy.org/)
- [PostgreSQL pg_dump 문서](https://www.postgresql.org/docs/current/app-pgdump.html)
- [SQLAlchemy 마이그레이션 가이드](https://docs.sqlalchemy.org/en/20/core/metadata.html)

