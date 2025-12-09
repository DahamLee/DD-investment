"""
주식 데이터 ETL DAG

매일 새벽 2시에 실행되는 주식 데이터 수집 파이프라인
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

from app.core.database import get_db
from app.etl.pipeline import ETLPipeline

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
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
    tags=['etl', 'stock', 'finance'],
)


def extract_stock_list():
    """종목 리스트 수집"""
    try:
        db = next(get_db())
        pipeline = ETLPipeline(db)
        result = pipeline.run_stock_list_etl("KRX")
        pipeline.close()
        print(f"종목 리스트 수집 완료: {result}")
        return result
    except Exception as e:
        print(f"종목 리스트 수집 실패: {e}")
        raise


def extract_stock_prices(**context):
    """시세 데이터 수집"""
    try:
        # 이전 작업에서 종목 리스트 가져오기
        # 또는 DB에서 직접 조회
        db = next(get_db())
        from app.models.stock import Stock
        
        # 최근 업데이트된 종목들만 선택 (예: 상위 100개)
        stocks = db.query(Stock).limit(100).all()
        tickers = [stock.ticker for stock in stocks]
        
        if not tickers:
            print("수집할 종목이 없습니다")
            return
        
        pipeline = ETLPipeline(db)
        
        # 최근 1년 데이터 수집
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        result = pipeline.run_stock_price_etl(tickers, start_date, end_date)
        pipeline.close()
        print(f"시세 데이터 수집 완료: {result}")
        return result
    except Exception as e:
        print(f"시세 데이터 수집 실패: {e}")
        raise


def extract_financials(**context):
    """재무제표 데이터 수집"""
    try:
        db = next(get_db())
        from app.models.stock import Stock
        
        # 상위 50개 종목만 선택
        stocks = db.query(Stock).limit(50).all()
        tickers = [stock.ticker for stock in stocks]
        
        if not tickers:
            print("수집할 종목이 없습니다")
            return
        
        pipeline = ETLPipeline(db)
        result = pipeline.run_financial_data_etl(tickers)
        pipeline.close()
        print(f"재무제표 데이터 수집 완료: {result}")
        return result
    except Exception as e:
        print(f"재무제표 데이터 수집 실패: {e}")
        raise


# 작업 정의
task_extract_stock_list = PythonOperator(
    task_id='extract_stock_list',
    python_callable=extract_stock_list,
    dag=dag,
)

task_extract_stock_prices = PythonOperator(
    task_id='extract_stock_prices',
    python_callable=extract_stock_prices,
    dag=dag,
)

task_extract_financials = PythonOperator(
    task_id='extract_financials',
    python_callable=extract_financials,
    dag=dag,
)

# 의존성 설정
# task1 완료 후 task2, task3 병렬 실행
task_extract_stock_list >> [task_extract_stock_prices, task_extract_financials]



