"""
ETL 파이프라인 오케스트레이션

전체 ETL 프로세스를 관리합니다.
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.etl.fetch_api import StockDataFetcher, FinancialDataFetcher
from app.etl.preprocess import DataPreprocessor
from app.etl.load import DataLoader

logger = logging.getLogger(__name__)


class ETLPipeline:
    """ETL 파이프라인 클래스"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db or next(get_db())
        self.fetcher = StockDataFetcher()
        self.financial_fetcher = FinancialDataFetcher()
        self.preprocessor = DataPreprocessor()
        self.loader = DataLoader(self.db)
        self.logger = logger
    
    def run_stock_list_etl(self, market: str = "KRX") -> Dict:
        """
        주식 종목 리스트 ETL 실행
        
        Args:
            market: 시장 구분
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"주식 종목 리스트 ETL 시작: {market}")
            
            # Extract
            logger.info("1. 데이터 추출 중...")
            raw_df = self.fetcher.fetch_stock_list(market)
            
            if raw_df.empty:
                logger.warning("추출된 데이터가 없습니다")
                return {'status': 'failed', 'reason': 'no_data'}
            
            # Transform
            logger.info("2. 데이터 전처리 중...")
            clean_df = self.preprocessor.clean_stock_list(raw_df)
            
            if clean_df.empty:
                logger.warning("전처리 후 데이터가 없습니다")
                return {'status': 'failed', 'reason': 'preprocessing_failed'}
            
            # Load
            logger.info("3. 데이터베이스 로드 중...")
            load_stats = self.loader.load_stocks(clean_df)
            
            result = {
                'status': 'success',
                'market': market,
                'extracted': len(raw_df),
                'cleaned': len(clean_df),
                'loaded': load_stats
            }
            
            logger.info(f"주식 종목 리스트 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"주식 종목 리스트 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_stock_price_etl(
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
            logger.info(f"주식 시세 데이터 ETL 시작: {len(tickers)}개 종목")
            
            results = {}
            total_extracted = 0
            total_cleaned = 0
            total_loaded = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for ticker in tickers:
                try:
                    logger.info(f"종목 처리 중: {ticker}")
                    
                    # Extract
                    raw_df = self.fetcher.fetch_stock_price(ticker, start_date, end_date)
                    if raw_df.empty:
                        logger.warning(f"종목 {ticker} 데이터 없음")
                        results[ticker] = {'status': 'no_data'}
                        continue
                    
                    total_extracted += len(raw_df)
                    
                    # Transform
                    clean_df = self.preprocessor.clean_stock_price(raw_df)
                    if clean_df.empty:
                        logger.warning(f"종목 {ticker} 전처리 실패")
                        results[ticker] = {'status': 'preprocessing_failed'}
                        continue
                    
                    # 기술적 지표 계산
                    clean_df = self.preprocessor.calculate_technical_indicators(clean_df)
                    total_cleaned += len(clean_df)
                    
                    # Load
                    # TODO: 시세 데이터 모델 추가 후 활성화
                    # load_stats = self.loader.load_stock_prices(ticker, clean_df)
                    # total_loaded['created'] += load_stats.get('created', 0)
                    # total_loaded['updated'] += load_stats.get('updated', 0)
                    # total_loaded['skipped'] += load_stats.get('skipped', 0)
                    
                    results[ticker] = {
                        'status': 'success',
                        'extracted': len(raw_df),
                        'cleaned': len(clean_df)
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
                'total_cleaned': total_cleaned,
                'total_loaded': total_loaded,
                'details': results
            }
            
            logger.info(f"주식 시세 데이터 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"주식 시세 데이터 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_financial_data_etl(
        self,
        tickers: List[str],
        years: Optional[List[int]] = None
    ) -> Dict:
        """
        재무제표 데이터 ETL 실행
        
        Args:
            tickers: 종목 코드 리스트
            years: 연도 리스트
        
        Returns:
            실행 결과 통계
        """
        try:
            logger.info(f"재무제표 데이터 ETL 시작: {len(tickers)}개 종목")
            
            results = {}
            
            for ticker in tickers:
                try:
                    logger.info(f"종목 처리 중: {ticker}")
                    
                    # Extract
                    financial_data = self.financial_fetcher.fetch_financial_statements(ticker, years)
                    
                    # Transform
                    normalized_data = self.preprocessor.normalize_financial_data(financial_data)
                    
                    # Load
                    load_stats = self.loader.load_financial_statements(ticker, normalized_data)
                    
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
            
            logger.info(f"재무제표 데이터 ETL 완료: {result}")
            return result
            
        except Exception as e:
            logger.error(f"재무제표 데이터 ETL 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_full_etl(
        self,
        markets: List[str] = ["KRX"],
        update_prices: bool = True,
        update_financials: bool = False
    ) -> Dict:
        """
        전체 ETL 파이프라인 실행
        
        Args:
            markets: 시장 리스트
            update_prices: 시세 데이터 업데이트 여부
            update_financials: 재무제표 데이터 업데이트 여부
        
        Returns:
            전체 실행 결과
        """
        try:
            logger.info("전체 ETL 파이프라인 시작")
            
            results = {
                'started_at': datetime.utcnow().isoformat(),
                'stock_list': {},
                'stock_prices': {},
                'financial_data': {}
            }
            
            # 1. 주식 종목 리스트 ETL
            for market in markets:
                results['stock_list'][market] = self.run_stock_list_etl(market)
            
            # 2. 주식 시세 데이터 ETL (선택적)
            if update_prices:
                # 최근 1년 데이터 업데이트
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                
                # DB에서 종목 리스트 가져오기
                stocks = self.db.query(Stock).limit(100).all()  # 테스트용 100개만
                tickers = [stock.ticker for stock in stocks]
                
                if tickers:
                    results['stock_prices'] = self.run_stock_price_etl(
                        tickers, start_date, end_date
                    )
            
            # 3. 재무제표 데이터 ETL (선택적)
            if update_financials:
                stocks = self.db.query(Stock).limit(50).all()  # 테스트용 50개만
                tickers = [stock.ticker for stock in stocks]
                
                if tickers:
                    results['financial_data'] = self.run_financial_data_etl(tickers)
            
            results['completed_at'] = datetime.utcnow().isoformat()
            results['status'] = 'completed'
            
            logger.info("전체 ETL 파이프라인 완료")
            return results
            
        except Exception as e:
            logger.error(f"전체 ETL 파이프라인 실패: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def close(self):
        """리소스 정리"""
        if self.db:
            self.db.close()



