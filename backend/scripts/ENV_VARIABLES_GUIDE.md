# 환경 변수 사용 가이드

## 🔍 환경 변수란?

환경 변수(Environment Variable)는 현재 터미널 세션에서 사용할 수 있는 변수입니다. 
비밀번호 같은 민감한 정보를 코드나 명령줄에 직접 입력하지 않고, 변수로 저장해서 사용할 수 있습니다.

## 📝 기본 사용법

### 1. 환경 변수 설정

```bash
# 현재 터미널 세션에서만 유효
export SOURCE_DB_PASSWORD="실제소스비밀번호"
export TARGET_DB_PASSWORD="실제타겟비밀번호"
```

### 2. 환경 변수 사용

```bash
# $변수명 형태로 사용
python scripts/migrate_with_schema_sync.py \
  --source-password "$SOURCE_DB_PASSWORD" \
  --target-password "$TARGET_DB_PASSWORD"
```

### 3. 환경 변수 확인

```bash
# 설정된 환경 변수 확인
echo $SOURCE_DB_PASSWORD

# 모든 환경 변수 확인
env | grep DB
```

## 🎯 실제 사용 예시

### 예시 1: 간단한 마이그레이션

```bash
# 1단계: 환경 변수 설정
export SOURCE_DB_PASSWORD="ekgkaehddudABC123!"
export TARGET_DB_PASSWORD="lee1367"

# 2단계: 스크립트 실행
cd /app/backend
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

### 예시 2: 한 줄로 실행

```bash
# 환경 변수 설정과 실행을 한 줄로
export SOURCE_DB_PASSWORD="ekgkaehddudABC123!" && \
export TARGET_DB_PASSWORD="lee1367" && \
cd /app/backend && \
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

## ⚠️ 주의사항

### 1. 터미널 세션 종료 시 사라짐

환경 변수는 현재 터미널 세션에서만 유효합니다. 터미널을 닫으면 사라집니다.

```bash
# 현재 세션에서만 유효
export MY_PASSWORD="secret123"

# 새 터미널을 열면 사라짐
```

### 2. 히스토리에 남지 않음 (안전)

환경 변수를 사용하면 명령줄 히스토리에 비밀번호가 남지 않습니다.

```bash
# ❌ 나쁜 예: 히스토리에 비밀번호가 남음
python script.py --password "secret123"

# ✅ 좋은 예: 히스토리에 비밀번호가 안 남음
export PASSWORD="secret123"
python script.py --password "$PASSWORD"
```

### 3. 환경 변수 영구 저장 (선택사항)

터미널을 닫아도 유지하려면 `.bashrc` 또는 `.zshrc`에 추가할 수 있지만, **비밀번호는 절대 추가하지 마세요!**

```bash
# .zshrc 또는 .bashrc에 추가 (비밀번호 제외)
export SOURCE_DB_HOST="121.134.7.122"
export SOURCE_DB_USER="postgres"
# 비밀번호는 추가하지 않음!
```

## 🔄 다른 방법과 비교

### 방법 1: 환경 변수 (권장)

```bash
export PASSWORD="secret"
python script.py --password "$PASSWORD"
```

**장점:**
- 히스토리에 남지 않음
- 여러 명령어에서 재사용 가능
- 보안상 안전

**단점:**
- 터미널 세션 종료 시 사라짐

### 방법 2: 직접 입력

```bash
python script.py --password "secret123"
```

**장점:**
- 간단함

**단점:**
- 히스토리에 비밀번호가 남음 (보안 위험!)
- 매번 입력해야 함

### 방법 3: .env 파일 (스크립트가 지원하는 경우)

```bash
# .env 파일에 저장 (Git에 올라가지 않음)
DATABASE_PASSWORD=secret123

# 스크립트가 자동으로 읽음
python script.py
```

**장점:**
- 영구 저장
- Git에 올라가지 않음

**단점:**
- 스크립트가 지원해야 함

## 💡 실전 팁

### 팁 1: 스크립트 파일로 만들기

```bash
# migrate.sh 파일 생성
#!/bin/bash
export SOURCE_DB_PASSWORD="ekgkaehddudABC123!"
export TARGET_DB_PASSWORD="lee1367"

cd /app/backend
python scripts/migrate_with_schema_sync.py \
  --source-host 121.134.7.122 \
  --source-database finance_db \
  --source-user postgres \
  --source-password "$SOURCE_DB_PASSWORD" \
  --target-host 34.64.149.167 \
  --target-database finance_db \
  --target-user postgres \
  --target-password "$TARGET_DB_PASSWORD"

# 실행 권한 부여
chmod +x migrate.sh

# 실행
./migrate.sh
```

### 팁 2: 환경 변수 확인 후 실행

```bash
# 환경 변수가 설정되어 있는지 확인
if [ -z "$SOURCE_DB_PASSWORD" ]; then
  echo "❌ SOURCE_DB_PASSWORD가 설정되지 않았습니다!"
  exit 1
fi

# 안전하게 실행
python script.py --password "$SOURCE_DB_PASSWORD"
```

### 팁 3: 환경 변수 일괄 설정

```bash
# 여러 환경 변수를 한 번에 설정
export SOURCE_DB_HOST="121.134.7.122"
export SOURCE_DB_PORT="5432"
export SOURCE_DB_NAME="finance_db"
export SOURCE_DB_USER="postgres"
export SOURCE_DB_PASSWORD="ekgkaehddudABC123!"

# 사용
python script.py \
  --source-host "$SOURCE_DB_HOST" \
  --source-port "$SOURCE_DB_PORT" \
  --source-database "$SOURCE_DB_NAME" \
  --source-user "$SOURCE_DB_USER" \
  --source-password "$SOURCE_DB_PASSWORD"
```

## 📚 추가 학습

- `export` 명령어: 환경 변수 설정
- `$변수명`: 환경 변수 사용
- `env`: 모든 환경 변수 확인
- `unset 변수명`: 환경 변수 삭제

```bash
# 환경 변수 삭제
unset SOURCE_DB_PASSWORD

# 확인 (아무것도 출력되지 않음)
echo $SOURCE_DB_PASSWORD
```

