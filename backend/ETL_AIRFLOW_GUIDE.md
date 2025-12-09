# ETL과 Airflow 관계 가이드

## 🔗 ETL과 Airflow의 관계

### 핵심 개념

**ETL** = **데이터 처리 프로세스** (무엇을 할지)
- Extract (추출)
- Transform (변환)
- Load (로드)

**Airflow** = **워크플로우 오케스트레이션 도구** (언제, 어떻게 실행할지)
- 스케줄링
- 의존성 관리
- 모니터링
- 재실행/재시도

### 비유로 이해하기

```
ETL = 요리 레시피 (무엇을 만들지)
Airflow = 요리사 (언제, 어떤 순서로 요리할지)
```

---

## 📊 현재 구조 vs Airflow 통합 구조

### 현재 구조 (수동 실행)

```
┌─────────────────┐
│  run_etl.py     │  ← 수동 실행
└────────┬────────┘
         │
    ┌────▼────┐
    │  ETL   │
    │Pipeline│
    └────────┘
```

**문제점:**
- 수동으로 실행해야 함
- 스케줄링 어려움
- 실패 시 재실행 수동
- 의존성 관리 어려움
- 모니터링 부족

### Airflow 통합 구조 (자동화)

```
┌─────────────────┐
│    Airflow      │  ← 스케줄러
│   Scheduler     │
└────────┬────────┘
         │
    ┌────▼────┐
    │  DAG   │  ← 워크플로우 정의
    │ (ETL)  │
    └────┬────┘
         │
    ┌────▼────┐
    │  ETL   │
    │Pipeline│  ← 실제 작업
    └────────┘
```

**장점:**
- 자동 스케줄링
- 의존성 자동 관리
- 실패 시 자동 재시도
- 웹 UI로 모니터링
- 로그 관리

---

## 🏗️ 구조 비교

### 1. ETL만 사용 (현재)

```python
# scripts/run_etl.py
python scripts/run_etl.py --type full
```

**실행 방법:**
- 수동 실행
- Cron으로 스케줄링 가능하지만 제한적

### 2. ETL + Airflow (권장)

```python
# airflow/dags/stock_etl_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from app.etl.pipeline import ETLPipeline

def run_stock_list_etl():
    pipeline = ETLPipeline()
    pipeline.run_stock_list_etl("KRX")

dag = DAG(
    'stock_etl',
    schedule_interval='0 2 * * *',  # 매일 새벽 2시
    ...
)
```

**실행 방법:**
- Airflow가 자동으로 스케줄링
- 웹 UI에서 모니터링
- 실패 시 자동 재시도

---

## 🎯 언제 Airflow를 사용해야 하나?

### Airflow를 사용해야 하는 경우

✅ **여러 ETL 작업을 조율**해야 할 때
- 주식 리스트 수집 → 시세 데이터 수집 → 재무제표 수집 (순차 실행)

✅ **정기적으로 자동 실행**이 필요할 때
- 매일 밤 자동으로 데이터 수집
- 주기적으로 데이터 업데이트

✅ **의존성 관리**가 필요할 때
- 작업 A가 끝나야 작업 B 실행
- 병렬 실행이 필요한 작업들

✅ **모니터링과 알림**이 필요할 때
- 실패 시 이메일/Slack 알림
- 실행 상태 대시보드

✅ **재시도 로직**이 필요할 때
- API 호출 실패 시 자동 재시도
- 네트워크 오류 복구

### Airflow 없이도 되는 경우

❌ **단순한 ETL 작업** 하나만 있을 때
- Cron으로 충분

❌ **수동 실행**만 필요할 때
- 필요할 때만 실행

❌ **리소스가 제한적**일 때
- Airflow는 추가 리소스 필요

---

## 📝 실제 예시

### 예시 1: 현재 구조 (ETL만)

```python
# scripts/run_etl.py
python scripts/run_etl.py --type full --update-prices

# Cron으로 스케줄링
0 2 * * * cd /app && python scripts/run_etl.py --type full
```

**장점:**
- 간단함
- 리소스 적음

**단점:**
- 모니터링 어려움
- 실패 시 수동 처리
- 의존성 관리 어려움

### 예시 2: Airflow 통합

```python
# airflow/dags/stock_etl_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from app.etl.pipeline import ETLPipeline

default_args = {
    'owner': 'data-team',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'stock_etl_pipeline',
    default_args=default_args,
    description='주식 데이터 ETL 파이프라인',
    schedule_interval='0 2 * * *',  # 매일 새벽 2시
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

# 작업 1: 종목 리스트 수집
def extract_stock_list():
    pipeline = ETLPipeline()
    pipeline.run_stock_list_etl("KRX")

task1 = PythonOperator(
    task_id='extract_stock_list',
    python_callable=extract_stock_list,
    dag=dag,
)

# 작업 2: 시세 데이터 수집 (작업 1 완료 후 실행)
def extract_stock_prices():
    pipeline = ETLPipeline()
    # DB에서 종목 리스트 가져와서 시세 수집
    pipeline.run_stock_price_etl(...)

task2 = PythonOperator(
    task_id='extract_stock_prices',
    python_callable=extract_stock_prices,
    dag=dag,
)

# 작업 3: 재무제표 수집 (작업 1 완료 후 실행, 병렬)
def extract_financials():
    pipeline = ETLPipeline()
    pipeline.run_financial_data_etl(...)

task3 = PythonOperator(
    task_id='extract_financials',
    python_callable=extract_financials,
    dag=dag,
)

# 의존성 설정
task1 >> [task2, task3]  # task1 완료 후 task2, task3 병렬 실행
```

**장점:**
- 자동 스케줄링
- 의존성 자동 관리
- 웹 UI 모니터링
- 실패 시 자동 재시도

**단점:**
- 추가 리소스 필요
- 설정 복잡도 증가

---

## 🚀 Airflow 통합 가이드

### 1단계: Airflow 설치

```bash
# requirements.txt에 추가
apache-airflow==2.8.0
apache-airflow-providers-postgres==5.10.0
```

### 2단계: Airflow 설정

```python
# airflow.cfg 또는 환경변수
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://...
AIRFLOW__CORE__DAGS_FOLDER=/app/airflow/dags
```

### 3단계: DAG 작성

```python
# airflow/dags/stock_etl_dag.py
# 위 예시 참고
```

### 4단계: Airflow 실행

```bash
# Airflow 초기화
airflow db init

# 웹 서버 시작
airflow webserver --port 8080

# 스케줄러 시작
airflow scheduler
```

---

## 💡 권장 접근법

### 단계별 도입

#### 1단계: 현재 (ETL만)
- 간단한 ETL 파이프라인
- 수동 실행 또는 Cron

#### 2단계: Airflow 도입 (권장)
- 여러 ETL 작업이 생길 때
- 정기적 자동 실행 필요할 때
- 의존성 관리 필요할 때

#### 3단계: 고급 기능
- 데이터 품질 체크
- ML 모델 학습 파이프라인
- 데이터 알림 시스템

---

## 📊 비교표

| 항목 | ETL만 | ETL + Airflow |
|------|-------|---------------|
| **스케줄링** | Cron 필요 | 자동 스케줄링 |
| **의존성 관리** | 수동 | 자동 |
| **모니터링** | 로그 파일 | 웹 UI |
| **재시도** | 수동 | 자동 |
| **복잡도** | 낮음 | 중간 |
| **리소스** | 낮음 | 중간 |
| **확장성** | 낮음 | 높음 |

---

## 🎯 결론

**ETL** = 데이터 처리 로직 (코드)
**Airflow** = 실행 관리 도구 (스케줄러)

**현재 프로젝트:**
- ETL 파이프라인은 이미 잘 구성되어 있음 ✅
- Airflow는 **선택사항**이지만, **여러 작업을 자동화**하려면 권장

**추천:**
1. 현재는 ETL만으로 시작
2. 작업이 복잡해지면 Airflow 도입
3. 점진적으로 Airflow로 마이그레이션


