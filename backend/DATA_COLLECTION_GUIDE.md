# 데이터 수집 전략 가이드

## 📊 데이터 유형별 수집 방법

### 1. **ETL 파이프라인 사용** (배치 수집)

다음과 같은 데이터는 **ETL에 넣어야 합니다:**

#### ✅ ETL에 넣어야 하는 데이터
- **재무제표 데이터** (SEC 데이터 포함)
  - 분기별/연간 재무제표
  - 대량의 과거 데이터
  - 정기적으로 업데이트되는 데이터
  
- **과거 시세 데이터**
  - 과거 1년 이상의 시세
  - 일봉, 주봉, 월봉 데이터
  - 대량의 히스토리컬 데이터
  
- **종목 기본 정보**
  - 전체 종목 리스트
  - 회사 정보, 업종 분류
  - 상장/상장폐지 정보
  
- **기업 공시 데이터**
  - 정기 공시
  - 주요 경영사항 공시
  
- **분석 지표 데이터**
  - PER, PBR, ROE, ROA 등
  - 기술적 지표 (RSI, MACD 등)

**이유:**
- 대량 데이터를 효율적으로 처리
- 정기적으로 자동 수집 가능 (스케줄러)
- DB에 저장하여 빠른 조회
- ML 모델 학습용 데이터 준비

---

### 2. **API 엔드포인트에서 직접 호출** (실시간/온디맨드)

다음과 같은 데이터는 **API 엔드포인트에서 직접 호출**합니다:

#### ✅ API에서 직접 호출해야 하는 데이터
- **실시간 현재가**
  - 사용자가 조회하는 순간의 가격
  - 실시간 변동률
  
- **실시간 차트 데이터**
  - 최근 몇 시간/일의 데이터
  - 사용자가 요청한 특정 기간
  
- **뉴스/공시 (최신)**
  - 최근 24시간 이내 뉴스
  - 실시간 공시 알림
  
- **시장 현황**
  - 현재 시장 지수
  - 거래량, 상승/하락 종목 수

**이유:**
- 실시간성이 중요
- 사용자 요청에 따른 즉시 응답 필요
- 캐싱으로 성능 최적화 가능
- DB에 저장할 필요 없는 일회성 데이터

---

## 🏗️ 권장 아키텍처

### 하이브리드 접근법 (권장)

```
┌─────────────────────────────────────────┐
│         사용자 요청 (API)                 │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼───┐     ┌────▼────┐
   │  ETL  │     │  API    │
   │       │     │Endpoint │
   └───┬───┘     └────┬────┘
       │              │
   ┌───▼──────────────▼───┐
   │   Database (PostgreSQL)│
   └───────────┬───────────┘
               │
        ┌──────▼──────┐
        │   Cache     │
        │  (Redis)    │
        └─────────────┘
```

### 데이터 흐름

#### 1. ETL 파이프라인 (정기 실행)
```python
# 스케줄러로 매일 밤 실행
python scripts/run_etl.py --type full --update-prices
```

**수집 데이터:**
- 전체 종목 리스트
- 과거 시세 데이터 (최근 1년)
- 재무제표 데이터 (분기별)
- SEC 데이터 (정기 공시)

**저장 위치:**
- `finance.stock` 테이블
- `finance.financial_statement_raw` 테이블
- (향후) `finance.stock_price` 테이블

#### 2. API 엔드포인트 (실시간)
```python
# app/api/v1/endpoints/stocks.py
@router.get("/stocks/{symbol}/current-price")
def get_current_price(symbol: str):
    # 실시간 API 호출
    price = fetch_realtime_price(symbol)
    return price
```

**호출 데이터:**
- 실시간 현재가
- 최근 차트 데이터 (캐시 활용)
- 최신 뉴스

**캐싱 전략:**
- Redis에 1-5분 캐시
- DB에 저장하지 않음

---

## 📝 구체적인 구현 예시

### SEC 데이터 수집 (ETL)

```python
# app/etl/fetch_api.py에 추가
class SECDataFetcher:
    """SEC 데이터 추출"""
    
    def fetch_sec_filings(self, ticker: str, form_type: str = "10-K"):
        """
        SEC 공시 데이터 추출
        
        Args:
            ticker: 종목 코드 (예: "AAPL")
            form_type: 공시 유형 (10-K, 10-Q, 8-K 등)
        """
        # SEC EDGAR API 호출
        # 또는 sec-api.io 같은 서비스 사용
        pass
```

**ETL 파이프라인에 통합:**
```python
# app/etl/pipeline.py
def run_sec_data_etl(self, tickers: List[str]):
    """SEC 데이터 ETL"""
    fetcher = SECDataFetcher()
    # ... 추출 → 전처리 → 로드
```

### 실시간 주식 데이터 (API)

```python
# app/api/v1/endpoints/stocks.py
@router.get("/stocks/{symbol}/realtime")
def get_realtime_data(symbol: str):
    """실시간 주식 데이터"""
    # 캐시 확인
    cached = redis_client.get(f"stock:{symbol}:realtime")
    if cached:
        return json.loads(cached)
    
    # API 호출
    data = fetch_realtime_from_api(symbol)
    
    # 캐시 저장 (1분)
    redis_client.setex(
        f"stock:{symbol}:realtime",
        60,
        json.dumps(data)
    )
    return data
```

---

## 🎯 결정 가이드라인

### ETL을 사용해야 하는 경우
- ✅ 데이터가 **대량**인가?
- ✅ **정기적으로 수집**해야 하는가?
- ✅ **과거 데이터**를 저장해야 하는가?
- ✅ **ML 모델 학습**에 사용되는가?
- ✅ **분석/랭킹**에 사용되는가?

→ **YES가 하나라도 있으면 ETL 사용**

### API에서 직접 호출해야 하는 경우
- ✅ **실시간성**이 중요한가?
- ✅ 사용자 **요청 시점**에만 필요한가?
- ✅ **최신 데이터**만 필요한가?
- ✅ **캐싱**으로 충분한가?

→ **YES가 하나라도 있으면 API 직접 호출**

---

## 💡 실제 예시

### 예시 1: SEC 10-K 공시 데이터
**→ ETL 사용**
- 이유: 대량 데이터, 정기 수집, 분석용
- 실행: 매 분기 말 자동 수집
- 저장: `finance.sec_filings` 테이블

### 예시 2: 현재 주식 가격
**→ API 직접 호출**
- 이유: 실시간성 중요
- 실행: 사용자 요청 시 즉시 호출
- 캐싱: Redis 1분 캐시

### 예시 3: 과거 1년 시세 데이터
**→ ETL 사용**
- 이유: 대량, 정기 수집, 차트/분석용
- 실행: 매일 밤 자동 업데이트
- 저장: `finance.stock_price` 테이블

### 예시 4: 최근 1일 차트 데이터
**→ API 직접 호출 (또는 하이브리드)**
- 이유: 실시간성, 최신 데이터
- 실행: 사용자 요청 시
- 캐싱: Redis 5분 캐시
- 참고: DB에 저장된 데이터와 병합 가능

---

## 🚀 구현 우선순위

1. **1단계**: ETL 파이프라인 완성
   - 재무제표 데이터 수집
   - 과거 시세 데이터 수집

2. **2단계**: API 엔드포인트 개선
   - 실시간 데이터 캐싱 추가
   - DB 데이터와 실시간 데이터 병합

3. **3단계**: 하이브리드 최적화
   - 자주 조회하는 데이터는 DB에 저장
   - 실시간 데이터는 캐시 활용

