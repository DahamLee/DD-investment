"""
데이터 추출 (Extract) 모듈

외부 API에서 주식 데이터를 추출합니다.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr
import yfinance as yf
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """주식 기본 정보 및 시세 데이터 추출"""
    
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
    
    def fetch_stock_list(self, market: str = "KRX") -> pd.DataFrame:
        """
        주식 종목 리스트 추출
        
        Args:
            market: 시장 구분 (KRX, KOSPI, KOSDAQ 등)
        
        Returns:
            DataFrame with columns: ['ticker', 'company_name', 'market', 'isin_code', 'industry']
        """
        try:
            logger.info(f"주식 종목 리스트 추출 시작: {market}")
            
            if market == "KRX":
                # 한국 전체 시장
                df_kospi = fdr.StockListing("KOSPI")
                df_kosdaq = fdr.StockListing("KOSDAQ")
                df = pd.concat([df_kospi, df_kosdaq], ignore_index=True)
            else:
                df = fdr.StockListing(market)
            
            # 컬럼명 정규화
            df = df.rename(columns={
                'Symbol': 'ticker',
                'Name': 'company_name',
                'Market': 'market',
                'ISIN': 'isin_code',
                'Sector': 'industry'
            })
            
            # 필요한 컬럼만 선택
            if 'industry' not in df.columns:
                df['industry'] = None
            
            df = df[['ticker', 'company_name', 'market', 'isin_code', 'industry']].copy()
            df = df.dropna(subset=['ticker', 'company_name'])
            
            logger.info(f"주식 종목 리스트 추출 완료: {len(df)}개")
            return df
            
        except Exception as e:
            logger.error(f"주식 종목 리스트 추출 실패: {e}")
            raise
    
    def fetch_stock_price(
        self, 
        ticker: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y"
    ) -> pd.DataFrame:
        """
        주식 시세 데이터 추출
        
        Args:
            ticker: 종목 코드 (예: "005930" for 삼성전자)
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with columns: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        try:
            logger.info(f"주식 시세 데이터 추출 시작: {ticker}")
            
            # 한국 주식은 FinanceDataReader 사용
            if ticker.isdigit() and len(ticker) == 6:
                # 한국 주식 (6자리 숫자)
                if start_date and end_date:
                    df = fdr.DataReader(ticker, start_date, end_date)
                else:
                    # 기본값: 최근 1년
                    end = datetime.now()
                    start = end - timedelta(days=365)
                    df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            else:
                # 해외 주식은 yfinance 사용
                stock = yf.Ticker(ticker)
                if start_date and end_date:
                    df = stock.history(start=start_date, end=end_date)
                else:
                    df = stock.history(period=period)
            
            # 컬럼명 정규화
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'Date'})
            
            # 필요한 컬럼만 선택 및 정규화
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            available_cols = [col for col in required_cols if col in df.columns]
            df = df[available_cols].copy()
            
            # Date를 datetime으로 변환
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            
            logger.info(f"주식 시세 데이터 추출 완료: {ticker}, {len(df)}개 행")
            return df
            
        except Exception as e:
            logger.error(f"주식 시세 데이터 추출 실패: {ticker}, {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        여러 종목의 시세 데이터 일괄 추출
        
        Args:
            tickers: 종목 코드 리스트
            start_date: 시작일
            end_date: 종료일
        
        Returns:
            Dict[ticker, DataFrame]
        """
        results = {}
        for ticker in tickers:
            try:
                df = self.fetch_stock_price(ticker, start_date, end_date)
                if not df.empty:
                    results[ticker] = df
            except Exception as e:
                logger.warning(f"종목 {ticker} 추출 실패: {e}")
                continue
        
        return results


class FinancialDataFetcher:
    """재무제표 데이터 추출"""
    
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
    
    def fetch_financial_statements(
        self,
        ticker: str,
        years: Optional[List[int]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        재무제표 데이터 추출
        
        Args:
            ticker: 종목 코드
            years: 연도 리스트 (None이면 최근 5년)
        
        Returns:
            Dict with keys: 'balance_sheet', 'income_statement', 'cash_flow'
        """
        try:
            logger.info(f"재무제표 데이터 추출 시작: {ticker}")
            
            if years is None:
                current_year = datetime.now().year
                years = list(range(current_year - 4, current_year + 1))
            
            # FinanceDataReader로 재무제표 추출
            # 주의: 실제 API에 따라 구현이 달라질 수 있음
            results = {
                'balance_sheet': pd.DataFrame(),
                'income_statement': pd.DataFrame(),
                'cash_flow': pd.DataFrame()
            }
            
            # TODO: 실제 재무제표 API 연동
            # 현재는 구조만 제공
            logger.warning(f"재무제표 API 연동 필요: {ticker}")
            
            return results
            
        except Exception as e:
            logger.error(f"재무제표 데이터 추출 실패: {ticker}, {e}")
            return {
                'balance_sheet': pd.DataFrame(),
                'income_statement': pd.DataFrame(),
                'cash_flow': pd.DataFrame()
            }


class SECDataFetcher:
    """SEC 데이터 추출 (미국 주식 공시 데이터)"""
    
    def __init__(self):
        self.sec_api_key = getattr(settings, 'sec_api_key', None)
        self.edgar_base_url = "https://data.sec.gov"
    
    def fetch_sec_filings(
        self,
        ticker: str,
        form_type: str = "10-K",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        SEC 공시 데이터 추출
        
        Args:
            ticker: 종목 코드 (예: "AAPL")
            form_type: 공시 유형 (10-K, 10-Q, 8-K, etc.)
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            List of filing dictionaries
        """
        try:
            logger.info(f"SEC 공시 데이터 추출 시작: {ticker}, {form_type}")
            
            # SEC EDGAR API 사용
            # 주의: SEC API는 rate limiting이 있으므로 주의 필요
            
            # 방법 1: SEC EDGAR 직접 API
            # https://www.sec.gov/edgar/sec-api-documentation
            
            # 방법 2: sec-api.io 같은 서비스 사용 (유료)
            # if self.sec_api_key:
            #     url = f"https://api.sec-api.io/full-text-search"
            #     ...
            
            # TODO: 실제 SEC API 연동 구현
            logger.warning(f"SEC API 연동 필요: {ticker}")
            
            return []
            
        except Exception as e:
            logger.error(f"SEC 공시 데이터 추출 실패: {ticker}, {e}")
            return []
    
    def fetch_company_facts(self, ticker: str) -> Dict:
        """
        SEC Company Facts 데이터 추출
        
        Args:
            ticker: 종목 코드
        
        Returns:
            Company facts dictionary
        """
        try:
            logger.info(f"SEC Company Facts 추출 시작: {ticker}")
            
            # SEC Company Facts API
            # https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
            
            # TODO: 실제 API 연동
            logger.warning(f"SEC Company Facts API 연동 필요: {ticker}")
            
            return {}
            
        except Exception as e:
            logger.error(f"SEC Company Facts 추출 실패: {ticker}, {e}")
            return {}
