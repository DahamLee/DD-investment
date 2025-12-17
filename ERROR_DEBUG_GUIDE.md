# 에러 디버깅 가이드

재무제표 데이터를 불러오는데 실패할 때 원인을 찾는 방법입니다.

## 🔍 에러 확인 방법

### 1. 프론트엔드에서 확인 (브라우저)

#### 브라우저 개발자 도구 열기
- **Chrome/Edge**: `F12` 또는 `Ctrl+Shift+I` (Mac: `Cmd+Option+I`)
- **Firefox**: `F12` 또는 `Ctrl+Shift+K`

#### 확인할 곳:

**1) Console 탭**
- 에러 메시지가 빨간색으로 표시됩니다
- `재무제표 로드 실패:` 로 시작하는 메시지 확인
- 전체 에러 스택 확인

**2) Network 탭**
- 페이지 새로고침 (`F5`)
- `/api/v1/stocks/financial-statements` 요청 찾기
- 클릭해서 확인:
  - **Status**: 200 (성공), 500 (서버 에러), 404 (경로 없음) 등
  - **Response**: 서버에서 반환한 에러 메시지
  - **Headers**: 요청/응답 헤더

**3) 화면에 표시된 에러 메시지**
- 페이지 상단에 빨간색 에러 메시지가 표시됩니다

### 2. 백엔드에서 확인 (터미널)

백엔드 서버를 실행한 터미널에서:
- 에러 메시지가 바로 표시됩니다
- `ERROR` 또는 `Exception` 키워드로 검색

### 3. 백엔드 로그 확인

```bash
# 백엔드 서버 로그 확인
# uvicorn으로 실행한 경우 터미널에 바로 표시됨

# 또는 로그 파일이 있다면
tail -f backend/logs/app.log
```

## 🐛 일반적인 에러 원인

### 1. 백엔드 서버가 실행되지 않음

**증상:**
- Network 탭에서 요청이 `Failed` 또는 `ERR_CONNECTION_REFUSED`
- Status: (failed) 또는 0

**해결:**
```bash
cd /app/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 데이터베이스 연결 실패

**증상:**
- 백엔드 로그에 `DB 연결 실패` 또는 `psycopg2.OperationalError`
- `connection refused` 또는 `authentication failed`

**확인:**
```bash
# .env.local 파일 확인
cat backend/.env.local | grep DATABASE

# 데이터베이스 연결 테스트
psql -h 121.134.7.122 -p 5432 -U postgres -d finance_db
```

**해결:**
- `.env.local` 파일의 DB 정보 확인
- DB 서버가 실행 중인지 확인
- 방화벽/네트워크 설정 확인

### 3. 데이터가 없음

**증상:**
- Status: 200 (성공)
- Response: `[]` (빈 배열)
- 화면에 "표시할 데이터가 없습니다" 메시지

**확인:**
```sql
-- 데이터베이스에서 직접 확인
SELECT * FROM test_table WHERE fs_code = '당기순이익' LIMIT 10;
SELECT DISTINCT quarter, year FROM test_table ORDER BY year DESC, quarter DESC;
```

**해결:**
- 다른 `fs_code`, `quarter`, `year` 값으로 시도
- ETL 스크립트로 데이터 수집 필요

### 4. 테이블이 없음

**증상:**
- 백엔드 로그에 `relation "test_table" does not exist`
- `table does not exist` 에러

**확인:**
```sql
-- 테이블 존재 확인
\dt test_table
-- 또는
SELECT * FROM information_schema.tables WHERE table_name = 'test_table';
```

**해결:**
- 테이블 생성 또는 ETL 스크립트 실행

### 5. API 경로 오류

**증상:**
- Status: 404 (Not Found)
- `Not Found` 메시지

**확인:**
```bash
# API 경로 테스트
curl http://localhost:8000/api/v1/stocks/financial-statements?fs_code=당기순이익&quarter=Q2&year=2025

# 또는 브라우저에서
http://localhost:8000/docs
```

**해결:**
- 백엔드 서버 재시작
- API 라우터 설정 확인

## 🛠️ 빠른 진단 명령어

### 1. 백엔드 서버 상태 확인
```bash
curl http://localhost:8000/api/v1/health
```

### 2. API 직접 테스트
```bash
curl "http://localhost:8000/api/v1/stocks/financial-statements?fs_code=당기순이익&quarter=Q2&year=2025&comparison_type=0"
```

### 3. 데이터베이스 연결 테스트
```bash
cd /app/backend
python3 -c "
from app.services.financial_statement_service import FinancialStatementService
service = FinancialStatementService()
conn = service._get_db_connection()
print('DB 연결 성공!')
service.close()
"
```

## 📝 에러 메시지 예시

### 정상 응답
```json
[
  {
    "stock_code": "005930",
    "quarter": "Q2",
    "year": 2025,
    "value": 1234567890,
    "change_pct": 0.15,
    "score": 8,
    "fs_code": "당기순이익"
  }
]
```

### 에러 응답
```json
{
  "detail": "재무제표 데이터를 불러오는데 실패했습니다: DB 연결 실패"
}
```

## 💡 추가 디버깅 팁

1. **브라우저 콘솔에서 네트워크 요청 확인**
   - Network 탭에서 요청 URL 확인
   - 요청 파라미터 확인 (fs_code, quarter, year 등)

2. **백엔드 로그 레벨 조정**
   - 더 자세한 로그를 보려면 로깅 레벨을 DEBUG로 설정

3. **단계별 테스트**
   - DB 연결 → SQL 쿼리 → 데이터 처리 → API 응답 순서로 확인


