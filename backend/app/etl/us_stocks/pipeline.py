"""
미국 주식 ETL 파이프라인 오케스트레이션

SEC EDGAR, 가격 데이터, 펀더멘털 데이터를 통합하여
미국 주식 데이터를 수집하고 저장합니다.
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from .sec_fetcher import SECDataFetcher
from .price_fetcher import USStockPriceFetcher
from .fundamental_fetcher import USStockFundamentalFetcher
from .loader import USStockDataLoader

logger = logging.getLogger(__name__)


class USStockETLPipeline:
    """
    미국 주식 ETL 파이프라인 클래스
    
    SEC EDGAR API, Yahoo Finance 등을 통합하여
    미국 주식 데이터를 수집하고 저장합니다.
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or next(get_db())
        self.sec_fetcher = SECDataFetcher()
        self.price_fetcher = USStockPriceFetcher()
        self.fundamental_fetcher = USStockFundamentalFetcher()
        self.loader = USStockDataLoader(self.db)
        self.logger = logger
    
    def run_stock_list_etl(self, exchange: str = "NASDAQ") -> Dict:
        """
        주식 종목 리스트 ETL 실행
        
        Args:
            exchange: 거래소 (NASDAQ, NYSE 등)
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"미국 주식 종목 리스트 ETL 시작: {exchange}")
            
            # Extract
            logger.info("1. 데이터 추출 중...")
            raw_df = self.price_fetcher.fetch_stock_list(exchange)
            
            if raw_df.empty:
                logger.warning("추출된 데이터가 없습니다")
                return {'status': 'failed', 'reason': 'no_data'}
            
            # Transform & Load
            logger.info("2. 데이터베이스 로드 중...")
            load_stats = self.loader.load_us_stocks(raw_df)
            
            result = {
                'status': 'success',
                'exchange': exchange,
                'extracted': len(raw_df),
                'loaded': load_stats
            }
            
            logger.info(f"미국 주식 종목 리스트 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"미국 주식 종목 리스트 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_price_etl(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        주식 시세 데이터 ETL 실행
        
        Args:
            tickers: 종목 코드 리스트
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"미국 주식 시세 데이터 ETL 시작: {len(tickers)}개 종목")
            
            results = {}
            total_extracted = 0
            
            for ticker in tickers:
                try:
                    logger.info(f"종목 처리 중: {ticker}")
                    
                    # Extract
                    raw_df = self.price_fetcher.fetch_stock_price(
                        ticker, start_date, end_date
                    )
                    if raw_df.empty:
                        logger.warning(f"종목 {ticker} 데이터 없음")
                        results[ticker] = {'status': 'no_data'}
                        continue
                    
                    total_extracted += len(raw_df)
                    
                    # Transform & Load
                    load_stats = self.loader.load_us_stock_prices(ticker, raw_df)
                    
                    results[ticker] = {
                        'status': 'success',
                        'extracted': len(raw_df),
                        'loaded': load_stats
                    }
                    
                except Exception as e:
                    logger.error(f"종목 {ticker} 처리 실패: {e}")
                    results[ticker] = {'status': 'failed', 'error': str(e)}
                    continue
            
            result = {
                'status': 'completed',
                'total_tickers': len(tickers),
                'successful': sum(1 for r in results.values() if r.get('status') == 'success'),
                'total_extracted': total_extracted,
                'details': results
            }
            
            logger.info(f"미국 주식 시세 데이터 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"미국 주식 시세 데이터 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_sec_filings_etl(
        self,
        tickers: List[str],
        form_types: Optional[List[str]] = None,
        days_back: int = 90
    ) -> Dict:
        """
        SEC 공시 데이터 ETL 실행
        
        Args:
            tickers: 종목 코드 리스트
            form_types: 공시 유형 리스트 (10-K, 10-Q, 8-K 등)
            days_back: 최근 N일 데이터만 조회
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"SEC 공시 데이터 ETL 시작: {len(tickers)}개 종목")
            
            # Extract
            logger.info("1. SEC 공시 데이터 추출 중...")
            filings_data = self.sec_fetcher.fetch_multiple_companies_filings(
                tickers, form_types, days_back
            )
            
            results = {}
            total_filings = 0
            
            for ticker, filings in filings_data.items():
                total_filings += len(filings)
                results[ticker] = {
                    'status': 'success',
                    'filings_count': len(filings)
                }
            
            # Transform & Load
            logger.info("2. 데이터베이스 로드 중...")
            total_loaded = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for ticker, filings in filings_data.items():
                load_stats = self.loader.load_us_sec_filings(ticker, filings)
                total_loaded['created'] += load_stats.get('created', 0)
                total_loaded['updated'] += load_stats.get('updated', 0)
                total_loaded['skipped'] += load_stats.get('skipped', 0)
            
            result = {
                'status': 'completed',
                'total_tickers': len(tickers),
                'successful': len(results),
                'total_filings': total_filings,
                'total_loaded': total_loaded,
                'details': results
            }
            
            logger.info(f"SEC 공시 데이터 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SEC 공시 데이터 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_fundamental_etl(self, tickers: List[str]) -> Dict:
        """
        펀더멘털 데이터 ETL 실행
        
        Args:
            tickers: 종목 코드 리스트
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"펀더멘털 데이터 ETL 시작: {len(tickers)}개 종목")
            
            results = {}
            
            for ticker in tickers:
                try:
                    logger.info(f"종목 처리 중: {ticker}")
                    
                    # Extract
                    metrics = self.fundamental_fetcher.calculate_fundamental_metrics(ticker)
                    
                    if not metrics:
                        results[ticker] = {'status': 'no_data'}
                        continue
                    
                    # Transform & Load
                    load_stats = self.loader.load_us_fundamentals(ticker, metrics)
                    
                    results[ticker] = {
                        'status': 'success',
                        'loaded': load_stats
                    }
                    
                except Exception as e:
                    logger.error(f"종목 {ticker} 처리 실패: {e}")
                    results[ticker] = {'status': 'failed', 'error': str(e)}
                    continue
            
            result = {
                'status': 'completed',
                'total_tickers': len(tickers),
                'successful': sum(1 for r in results.values() if r.get('status') == 'success'),
                'details': results
            }
            
            logger.info(f"펀더멘털 데이터 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"펀더멘털 데이터 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_full_etl(
        self,
        tickers: List[str],
        update_prices: bool = True,
        update_filings: bool = True,
        update_fundamentals: bool = False
    ) -> Dict:
        """
        전체 ETL 파이프라인 실행
        
        Args:
            tickers: 종목 코드 리스트
            update_prices: 시세 데이터 업데이트 여부
            update_filings: SEC 공시 데이터 업데이트 여부
            update_fundamentals: 펀더멘털 데이터 업데이트 여부
        
        Returns:
            전체 실행 결과
        """
        try:
            logger.info("미국 주식 전체 ETL 파이프라인 시작")
            
            results = {
                'started_at': datetime.utcnow().isoformat(),
                'stock_prices': {},
                'sec_filings': {},
                'fundamentals': {}
            }
            
            # 1. 주식 시세 데이터 ETL
            if update_prices:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                
                results['stock_prices'] = self.run_price_etl(
                    tickers, start_date, end_date
                )
            
            # 2. SEC 공시 데이터 ETL
            if update_filings:
                results['sec_filings'] = self.run_sec_filings_etl(
                    tickers, days_back=90
                )
            
            # 3. 펀더멘털 데이터 ETL
            if update_fundamentals:
                results['fundamentals'] = self.run_fundamental_etl(tickers)
            
            results['completed_at'] = datetime.utcnow().isoformat()
            results['status'] = 'completed'
            
            logger.info("미국 주식 전체 ETL 파이프라인 완료")
            return results
            
        except Exception as e:
            logger.error(f"미국 주식 전체 ETL 파이프라인 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def close(self):
        """리소스 정리"""
        if self.db:
            self.db.close()

