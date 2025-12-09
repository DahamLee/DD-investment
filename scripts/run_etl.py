#!/usr/bin/env python3
"""
ETL 파이프라인 실행 스크립트

사용법:
    python scripts/run_etl.py --type stock_list --market KRX
    python scripts/run_etl.py --type stock_price --tickers 005930,000660
    python scripts/run_etl.py --type full
"""
import sys
import os
import argparse
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))

from app.core.database import get_db
from app.etl.pipeline import ETLPipeline

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='ETL 파이프라인 실행')
    parser.add_argument(
        '--type',
        type=str,
        required=True,
        choices=['stock_list', 'stock_price', 'financial', 'full'],
        help='ETL 타입 선택'
    )
    parser.add_argument(
        '--market',
        type=str,
        default='KRX',
        help='시장 구분 (KRX, KOSPI, KOSDAQ)'
    )
    parser.add_argument(
        '--tickers',
        type=str,
        help='종목 코드 (쉼표로 구분, 예: 005930,000660)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='시작일 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='종료일 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--update-prices',
        action='store_true',
        help='시세 데이터 업데이트 (full 타입에서 사용)'
    )
    parser.add_argument(
        '--update-financials',
        action='store_true',
        help='재무제표 데이터 업데이트 (full 타입에서 사용)'
    )
    
    args = parser.parse_args()
    
    try:
        db = next(get_db())
        pipeline = ETLPipeline(db)
        
        if args.type == 'stock_list':
            logger.info(f"주식 종목 리스트 ETL 실행: {args.market}")
            result = pipeline.run_stock_list_etl(args.market)
            print(f"\n✅ 결과: {result}")
            
        elif args.type == 'stock_price':
            if not args.tickers:
                logger.error("--tickers 옵션이 필요합니다")
                return 1
            
            tickers = [t.strip() for t in args.tickers.split(',')]
            logger.info(f"주식 시세 데이터 ETL 실행: {tickers}")
            result = pipeline.run_stock_price_etl(
                tickers,
                args.start_date,
                args.end_date
            )
            print(f"\n✅ 결과: {result}")
            
        elif args.type == 'financial':
            if not args.tickers:
                logger.error("--tickers 옵션이 필요합니다")
                return 1
            
            tickers = [t.strip() for t in args.tickers.split(',')]
            logger.info(f"재무제표 데이터 ETL 실행: {tickers}")
            result = pipeline.run_financial_data_etl(tickers)
            print(f"\n✅ 결과: {result}")
            
        elif args.type == 'full':
            markets = [args.market] if args.market else ['KRX']
            logger.info(f"전체 ETL 파이프라인 실행: {markets}")
            result = pipeline.run_full_etl(
                markets=markets,
                update_prices=args.update_prices,
                update_financials=args.update_financials
            )
            print(f"\n✅ 결과: {result}")
        
        pipeline.close()
        return 0
        
    except Exception as e:
        logger.error(f"ETL 실행 실패: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

