# Airflow 설정 가이드

## 📋 개요

이 디렉토리는 Apache Airflow 설정을 위한 것입니다.

## 🚀 빠른 시작

### 1. Airflow 설치

```bash
pip install apache-airflow==2.8.0
pip install apache-airflow-providers-postgres==5.10.0
```

### 2. Airflow 초기화

```bash
# 환경변수 설정
export AIRFLOW_HOME=/app/airflow

# DB 초기화
airflow db init

# 관리자 사용자 생성
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 3. Airflow 실행

```bash
# 웹 서버 (별도 터미널)
airflow webserver --port 8080

# 스케줄러 (별도 터미널)
airflow scheduler
```

### 4. 웹 UI 접속

브라우저에서 `http://localhost:8080` 접속
- Username: admin
- Password: admin

## 📁 디렉토리 구조

```
airflow/
├── dags/              # DAG 파일들
│   └── stock_etl_dag.py
├── logs/              # 실행 로그
├── plugins/           # 커스텀 플러그인
└── README.md
```

## 🔧 설정

### 환경변수

```bash
# .env 파일에 추가
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://user:pass@host:5432/airflow
AIRFLOW__CORE__DAGS_FOLDER=/app/airflow/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
```

### Docker Compose (선택사항)

```yaml
# docker-compose.airflow.yml
version: '3.8'
services:
  airflow-webserver:
    image: apache/airflow:2.8.0
    ...
  airflow-scheduler:
    image: apache/airflow:2.8.0
    ...
```

## 📝 DAG 작성

`dags/stock_etl_dag.py` 파일을 참고하세요.

## 🎯 다음 단계

1. DAG 테스트: `airflow dags test stock_etl_pipeline 2024-01-01`
2. 작업 테스트: `airflow tasks test stock_etl_pipeline extract_stock_list 2024-01-01`
3. 웹 UI에서 모니터링



