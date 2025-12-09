# Alembic 마이그레이션 완전 가이드

상황별로 필요한 명령어와 프로세스를 정리한 실전 가이드입니다.

---

## 📋 목차

1. [기본 명령어](#기본-명령어)
2. [상황별 가이드](#상황별-가이드)
3. [일반적인 워크플로우](#일반적인-워크플로우)
4. [문제 해결](#문제-해결)

---

## 기본 명령어

### 현재 상태 확인

```bash
cd /app/backend

# 현재 적용된 마이그레이션 버전 확인
alembic current

# 마이그레이션 히스토리 전체 보기
alembic history

# 특정 리비전 상세 정보 보기
alembic show <revision_id>
```

**예시 출력:**
```
# alembic current
2fcfa10330f0 (head)

# alembic history
2fcfa10330f0 -> add_us_stock_tables (head)
4c6c78c2b494 -> initial_migration
```

---

## 상황별 가이드

### 🆕 상황 1: 처음 프로젝트 시작 (초기 마이그레이션)

**언제**: 새로운 프로젝트에서 처음 DB 스키마를 만들 때

```bash
cd /app/backend

# 1. 모델 정의 완료 후 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 2. 생성된 파일 확인 (alembic/versions/xxxxx_initial_migration.py)
# 3. 파일 내용 검토 (필요시 수정)

# 4. 마이그레이션 적용
alembic upgrade head
```

**체크리스트:**
- ✅ 모델이 모두 `app/models/__init__.py`에 import 되어 있는지
- ✅ 생성된 마이그레이션 파일 내용 검토
- ✅ `upgrade()`와 `downgrade()` 함수 확인

---

### 🔄 상황 2: 모델 변경 후 (새 마이그레이션 생성)

**언제**: 기존 모델을 수정하거나 새 모델을 추가했을 때

```bash
cd /app/backend

# 1. 모델 파일 수정 (예: app/models/us_stock.py)
# 2. 마이그레이션 자동 생성
alembic revision --autogenerate -m "add_us_stock_tables"

# 3. 생성된 파일 검토
# - 불필요한 변경사항 제거
# - 커스텀 로직 추가 (데이터 마이그레이션 등)

# 4. 적용
alembic upgrade head
```

**주의사항:**
- `--autogenerate`는 완벽하지 않음 → 반드시 검토 필요
- 데이터 마이그레이션이 필요하면 `upgrade()` 함수에 추가
- 컬럼 삭제 시 데이터 손실 주의

---

### ✅ 상황 3: 마이그레이션 적용 (DB 업데이트)

**언제**: 마이그레이션 파일을 생성한 후 DB에 반영할 때

```bash
cd /app/backend

# 방법 1: 최신까지 모두 적용 (가장 많이 사용)
alembic upgrade head

# 방법 2: 한 단계만 적용
alembic upgrade +1

# 방법 3: 특정 리비전까지 적용
alembic upgrade <revision_id>

# 방법 4: 현재 상태 확인 후 적용
alembic current
alembic upgrade head
```

**실행 전 체크:**
- ✅ 데이터베이스 백업 (프로덕션인 경우 필수)
- ✅ 현재 마이그레이션 상태 확인: `alembic current`
- ✅ 적용할 마이그레이션 확인: `alembic history`

---

### ⏪ 상황 4: 마이그레이션 롤백 (되돌리기)

**언제**: 마이그레이션 적용 후 문제가 생겼을 때

```bash
cd /app/backend

# 방법 1: 한 단계 롤백 (가장 안전)
alembic downgrade -1

# 방법 2: 특정 리비전으로 롤백
alembic downgrade <revision_id>

# 방법 3: 모든 마이그레이션 롤백 (주의!)
alembic downgrade base
```

**주의:**
- ⚠️ `downgrade`는 데이터 손실을 일으킬 수 있음
- ⚠️ 프로덕션에서는 신중하게 사용
- ⚠️ 롤백 전 데이터 백업 필수

---

### 🔍 상황 5: 현재 상태 확인

**언제**: 어떤 마이그레이션이 적용되어 있는지 확인하고 싶을 때

```bash
cd /app/backend

# 현재 적용된 리비전 확인
alembic current

# 전체 히스토리 보기
alembic history

# 특정 리비전 상세 정보
alembic show <revision_id>

# 적용되지 않은 마이그레이션 확인
alembic heads  # 최신 리비전
alembic current  # 현재 리비전
# heads와 current가 다르면 적용되지 않은 마이그레이션 있음
```

---

### 🔀 상황 6: 브랜치 충돌 해결

**언제**: 여러 개발자가 동시에 마이그레이션을 만들었을 때

```bash
cd /app/backend

# 1. 현재 상태 확인
alembic current
alembic history

# 2. 충돌하는 리비전 확인
# 예: 2fcfa10330f0 (내가 만든 것)
#     abc123def45 (다른 사람이 만든 것)

# 3. 병합 마이그레이션 생성
alembic merge -m "Merge branches" 2fcfa10330f0 abc123def45

# 4. 생성된 병합 마이그레이션 검토
# 5. 적용
alembic upgrade head
```

---

### 🛠️ 상황 7: 수동 마이그레이션 생성

**언제**: `--autogenerate`로 감지되지 않는 변경사항이 있을 때
(예: 데이터 마이그레이션, 복잡한 로직)

```bash
cd /app/backend

# 빈 마이그레이션 파일 생성
alembic revision -m "custom_data_migration"

# 생성된 파일 수정
# alembic/versions/xxxxx_custom_data_migration.py
# upgrade()와 downgrade() 함수에 로직 작성
```

**예시:**
```python
def upgrade() -> None:
    # 데이터 마이그레이션 로직
    op.execute("UPDATE finance.us_stock SET currency = 'USD' WHERE currency IS NULL")

def downgrade() -> None:
    # 롤백 로직
    op.execute("UPDATE finance.us_stock SET currency = NULL WHERE currency = 'USD'")
```

---

### 🔄 상황 8: 개발/운영 환경 동기화

**언제**: 개발 환경에서 마이그레이션을 적용한 후 운영 환경에도 적용할 때

#### 개발 환경 (로컬)
```bash
cd /app/backend

# 1. 마이그레이션 생성 및 적용
alembic revision --autogenerate -m "add_new_feature"
alembic upgrade head

# 2. Git에 커밋
git add alembic/versions/xxxxx_add_new_feature.py
git commit -m "Add migration: add_new_feature"
git push
```

#### 운영 환경 (서버)
```bash
cd /app/backend

# 1. 코드 업데이트 (Git pull)
git pull

# 2. 현재 상태 확인
alembic current

# 3. 적용되지 않은 마이그레이션 확인
alembic history

# 4. 백업 (중요!)
# pg_dump 또는 다른 백업 방법 사용

# 5. 마이그레이션 적용
alembic upgrade head

# 6. 확인
alembic current
```

---

## 일반적인 워크플로우

### 📝 개발 중 일상적인 워크플로우

```bash
# 1. 모델 수정
# app/models/us_stock.py 수정

# 2. 마이그레이션 생성
cd /app/backend
alembic revision --autogenerate -m "describe_your_change"

# 3. 생성된 파일 검토
# alembic/versions/xxxxx_describe_your_change.py 확인

# 4. 적용
alembic upgrade head

# 5. 테스트
# 애플리케이션 실행하여 테스트

# 6. 문제 있으면 롤백
alembic downgrade -1
# 수정 후 다시 적용
alembic upgrade head
```

### 🚀 배포 전 체크리스트

```bash
# 1. 현재 상태 확인
alembic current

# 2. 적용되지 않은 마이그레이션 확인
alembic heads
alembic history

# 3. 모든 마이그레이션이 적용되었는지 확인
# (heads == current 여야 함)

# 4. 마이그레이션 파일이 Git에 커밋되었는지 확인
git status

# 5. 테스트 환경에서 먼저 적용
alembic upgrade head

# 6. 문제 없으면 운영 환경 적용
```

---

## 문제 해결

### ❌ 오류 1: "Can't locate revision identified by 'xxxxx'"

**원인**: DB에 기록된 리비전이 마이그레이션 파일에 없음

**해결:**
```bash
# 1. 현재 DB 상태 확인
alembic current

# 2. 마이그레이션 파일 확인
ls alembic/versions/

# 3. 누락된 파일이 있으면 복구하거나
# 4. DB의 alembic_version 테이블 직접 수정 (주의!)
# 또는
# 5. 특정 리비전으로 강제 설정
alembic stamp <revision_id>
```

---

### ❌ 오류 2: "Target database is not up to date"

**원인**: 적용되지 않은 마이그레이션이 있음

**해결:**
```bash
# 1. 상태 확인
alembic current
alembic heads

# 2. 적용되지 않은 마이그레이션 확인
alembic history

# 3. 적용
alembic upgrade head
```

---

### ❌ 오류 3: "Multiple heads detected"

**원인**: 브랜치 충돌 (여러 마이그레이션이 같은 부모를 가짐)

**해결:**
```bash
# 1. 충돌 확인
alembic heads  # 여러 개 출력됨

# 2. 병합 마이그레이션 생성
alembic merge -m "Merge branches" <revision1> <revision2>

# 3. 적용
alembic upgrade head
```

---

### ❌ 오류 4: "Table already exists"

**원인**: DB에 이미 테이블이 있는데 마이그레이션이 다시 생성하려고 함

**해결:**
```bash
# 방법 1: 마이그레이션 파일에서 해당 테이블 생성 부분 제거
# 방법 2: DB를 초기화하고 처음부터 적용
# 방법 3: 특정 리비전으로 스탬프 설정
alembic stamp <revision_id>
```

---

### ❌ 오류 5: "Column already exists" 또는 "Column does not exist"

**원인**: 모델과 DB 상태가 불일치

**해결:**
```bash
# 1. 현재 DB 상태 확인
alembic current

# 2. 모델 변경사항 자동 감지
alembic revision --autogenerate -m "sync_models"

# 3. 생성된 마이그레이션 검토 (불필요한 부분 제거)

# 4. 적용
alembic upgrade head
```

---

## 유용한 팁

### 💡 팁 1: 마이그레이션 파일 검토 필수

`--autogenerate`는 완벽하지 않으므로 항상 생성된 파일을 검토하세요:

```python
# 생성된 파일에서 확인할 것들:
# 1. 불필요한 변경사항 제거
# 2. 데이터 마이그레이션 로직 추가
# 3. 외래 키 제약조건 순서 확인
# 4. 인덱스 생성/삭제 확인
```

### 💡 팁 2: 롤백 가능한 마이그레이션 작성

모든 `upgrade()`에는 대응하는 `downgrade()`가 있어야 합니다:

```python
def upgrade() -> None:
    op.add_column('finance.us_stock', sa.Column('new_field', sa.String(50)))

def downgrade() -> None:
    op.drop_column('finance.us_stock', 'new_field')
```

### 💡 팁 3: 의미 있는 메시지 작성

마이그레이션 메시지는 나중에 찾기 쉽게 작성:

```bash
# 좋은 예
alembic revision --autogenerate -m "add_us_stock_tables"
alembic revision --autogenerate -m "add_index_to_ticker_column"

# 나쁜 예
alembic revision --autogenerate -m "update"
alembic revision --autogenerate -m "fix"
```

### 💡 팁 4: 개발/운영 환경 분리

환경별로 다른 DB를 사용하므로 각각 마이그레이션 적용:

```bash
# 개발 환경
export DATABASE_URL="postgresql://user:pass@localhost:5432/dev_db"
alembic upgrade head

# 운영 환경
export DATABASE_URL="postgresql://user:pass@prod-server:5432/prod_db"
alembic upgrade head
```

---

## 명령어 치트시트

```bash
# 상태 확인
alembic current              # 현재 리비전
alembic history              # 전체 히스토리
alembic show <rev>           # 특정 리비전 상세

# 마이그레이션 생성
alembic revision --autogenerate -m "message"  # 자동 생성
alembic revision -m "message"                 # 수동 생성
alembic merge -m "message" <rev1> <rev2>      # 병합

# 적용
alembic upgrade head         # 최신까지
alembic upgrade +1           # 한 단계
alembic upgrade <rev>        # 특정 리비전까지

# 롤백
alembic downgrade -1         # 한 단계
alembic downgrade <rev>      # 특정 리비전으로
alembic downgrade base       # 모두 롤백

# 기타
alembic heads                # 최신 리비전들
alembic stamp <rev>          # 특정 리비전으로 강제 설정
```

---

## 참고 자료

- [Alembic 공식 문서](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- 프로젝트 내 `DB_MIGRATION_GUIDE.md` (더 자세한 내용)

