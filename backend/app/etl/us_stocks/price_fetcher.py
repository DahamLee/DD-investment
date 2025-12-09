"""
미국 주식 가격 데이터 추출 모듈

Yahoo Finance, Polygon.io 등을 통한
미국 주식 시세 데이터 수집
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

from app.core.config import settings

logger = logging.getLogger(__name__)


class USStockPriceFetcher:
    """
    미국 주식 가격 데이터 추출 클래스
    
    Yahoo Finance API를 사용하여 일봉 데이터를 수집합니다.
    """
    
    def __init__(self):
        self.polygon_api_key = getattr(settings, 'polygon_api_key', None)
    
    def fetch_stock_list(self, exchange: str = "NASDAQ") -> pd.DataFrame:
        """
        거래소별 주식 종목 리스트 추출
        
        Args:
            exchange: 거래소 (NASDAQ, NYSE, AMEX 등)
        
        Returns:
            DataFrame with columns: ['ticker', 'company_name', 'exchange', 'sector', 'industry']
        """
        try:
            logger.info(f"미국 주식 종목 리스트 추출 시작: {exchange}")
            
            # yfinance로는 종목 리스트를 직접 가져올 수 없으므로
            # S&P 500, NASDAQ 100 등 주요 지수 구성종목 사용
            if exchange == "NASDAQ":
                # NASDAQ 100 티커 리스트 (예시)
                # 실제로는 외부 API나 파일에서 가져와야 함
                tickers = self._get_nasdaq_tickers()
            elif exchange == "NYSE":
                tickers = self._get_nyse_tickers()
            else:
                tickers = []
            
            # 각 티커의 정보 조회
            results = []
            for ticker in tickers[:100]:  # 테스트용 100개만
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    results.append({
                        'ticker': ticker,
                        'company_name': info.get('longName', info.get('shortName', ticker)),
                        'exchange': info.get('exchange', exchange),
                        'sector': info.get('sector', ''),
                        'industry': info.get('industry', ''),
                        'market_cap': info.get('marketCap', 0),
                        'currency': info.get('currency', 'USD')
                    })
                except Exception as e:
                    logger.warning(f"티커 {ticker} 정보 조회 실패: {e}")
                    continue
            
            df = pd.DataFrame(results)
            logger.info(f"미국 주식 종목 리스트 추출 완료: {len(df)}개")
            return df
            
        except Exception as e:
            logger.error(f"미국 주식 종목 리스트 추출 실패: {e}")
            return pd.DataFrame()
    
    def _get_nasdaq_tickers(self) -> List[str]:
        """NASDAQ 주요 티커 리스트 (예시)"""
        # 실제로는 외부 API나 파일에서 가져와야 함
        # 여기서는 주요 종목만 예시로 제공
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'NFLX', 'AMD', 'INTC', 'CSCO', 'CMCSA', 'ADBE', 'COST',
            'AVGO', 'PEP', 'TXN', 'QCOM', 'AMGN', 'HON'
        ]
    
    def _get_nyse_tickers(self) -> List[str]:
        """NYSE 주요 티커 리스트 (예시)"""
        return [
            'JPM', 'JNJ', 'V', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'DIS',
            'BAC', 'ABBV', 'KO', 'MRK', 'PFE', 'TMO', 'CVX', 'XOM'
        ]
    
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
            ticker: 종목 코드 (예: "AAPL")
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with columns: ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
        """
        try:
            logger.info(f"미국 주식 시세 데이터 추출 시작: {ticker}")
            
            stock = yf.Ticker(ticker)
            
            if start_date and end_date:
                df = stock.history(start=start_date, end=end_date)
            else:
                df = stock.history(period=period)
            
            if df.empty:
                logger.warning(f"티커 {ticker} 데이터 없음")
                return pd.DataFrame()
            
            # 컬럼명 정규화
            df = df.reset_index()
            if 'Date' not in df.columns and 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'Date'})
            
            # 필요한 컬럼만 선택
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if 'Adj Close' in df.columns:
                required_cols.append('Adj Close')
            
            available_cols = [col for col in required_cols if col in df.columns]
            df = df[available_cols].copy()
            
            # Date를 datetime으로 변환
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            
            # 티커 컬럼 추가
            df['ticker'] = ticker
            
            logger.info(f"미국 주식 시세 데이터 추출 완료: {ticker}, {len(df)}개 행")
            return df
            
        except Exception as e:
            logger.error(f"미국 주식 시세 데이터 추출 실패: {ticker}, {e}")
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
    
    def fetch_stock_info(self, ticker: str) -> Dict:
        """
        주식 기본 정보 추출 (시가총액, PER, PBR 등)
        
        Args:
            ticker: 종목 코드
        
        Returns:
            주식 정보 딕셔너리
        """
        try:
            logger.info(f"주식 기본 정보 추출 시작: {ticker}")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 필요한 정보만 추출
            result = {
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'eps': info.get('trailingEps', info.get('forwardEps')),
                'beta': info.get('beta', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'quote_type': info.get('quoteType', 'EQUITY')
            }
            
            logger.info(f"주식 기본 정보 추출 완료: {ticker}")
            return result
            
        except Exception as e:
            logger.error(f"주식 기본 정보 추출 실패: {ticker}, {e}")
            return {}

