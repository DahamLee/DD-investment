"""
미국 주식 펀더멘털 데이터 추출 모듈

Yahoo Finance를 통한 재무제표 및 펀더멘털 지표 수집
"""
import logging
from typing import Dict, Optional
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class USStockFundamentalFetcher:
    """
    미국 주식 펀더멘털 데이터 추출 클래스
    
    Yahoo Finance를 사용하여 재무제표 및 펀더멘털 지표를 수집합니다.
    """
    
    def fetch_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        재무제표 데이터 추출
        
        Args:
            ticker: 종목 코드
        
        Returns:
            Dict with keys: 'balance_sheet', 'income_statement', 'cash_flow'
        """
        try:
            logger.info(f"재무제표 데이터 추출 시작: {ticker}")
            
            stock = yf.Ticker(ticker)
            
            results = {
                'balance_sheet': pd.DataFrame(),
                'income_statement': pd.DataFrame(),
                'cash_flow': pd.DataFrame()
            }
            
            # 재무제표 조회
            try:
                balance_sheet = stock.balance_sheet
                if balance_sheet is not None and not balance_sheet.empty:
                    results['balance_sheet'] = balance_sheet.T.reset_index()
                    results['balance_sheet'].columns = ['date'] + list(results['balance_sheet'].columns[1:])
            except Exception as e:
                logger.warning(f"재무상태표 조회 실패: {ticker}, {e}")
            
            try:
                income_stmt = stock.financials
                if income_stmt is not None and not income_stmt.empty:
                    results['income_statement'] = income_stmt.T.reset_index()
                    results['income_statement'].columns = ['date'] + list(results['income_statement'].columns[1:])
            except Exception as e:
                logger.warning(f"손익계산서 조회 실패: {ticker}, {e}")
            
            try:
                cash_flow = stock.cashflow
                if cash_flow is not None and not cash_flow.empty:
                    results['cash_flow'] = cash_flow.T.reset_index()
                    results['cash_flow'].columns = ['date'] + list(results['cash_flow'].columns[1:])
            except Exception as e:
                logger.warning(f"현금흐름표 조회 실패: {ticker}, {e}")
            
            logger.info(f"재무제표 데이터 추출 완료: {ticker}")
            return results
            
        except Exception as e:
            logger.error(f"재무제표 데이터 추출 실패: {ticker}, {e}")
            return {
                'balance_sheet': pd.DataFrame(),
                'income_statement': pd.DataFrame(),
                'cash_flow': pd.DataFrame()
            }
    
    def calculate_fundamental_metrics(
        self,
        ticker: str,
        price_data: Optional[pd.DataFrame] = None
    ) -> Dict:
        """
        펀더멘털 지표 계산
        
        Args:
            ticker: 종목 코드
            price_data: 가격 데이터 (시가총액 계산용)
        
        Returns:
            펀더멘털 지표 딕셔너리
        """
        try:
            logger.info(f"펀더멘털 지표 계산 시작: {ticker}")
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 재무제표 데이터
            financials = self.fetch_financial_statements(ticker)
            
            # 기본 지표
            metrics = {
                'ticker': ticker,
                'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'ev_ebitda': info.get('enterpriseToEbitda', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'eps': info.get('trailingEps', info.get('forwardEps')),
                'roe': None,  # 계산 필요
                'roa': None,  # 계산 필요
                'profit_margin': None,  # 계산 필요
                'operating_margin': None,  # 계산 필요
            }
            
            # 재무제표에서 계산 가능한 지표
            if not financials['income_statement'].empty:
                income = financials['income_statement']
                # 최신 연도 데이터 사용
                latest_year = income.iloc[0] if len(income) > 0 else None
                
                if latest_year is not None:
                    # ROE, ROA, 마진 등은 재무제표 데이터로 계산
                    # (실제 계산 로직은 재무제표 컬럼명에 따라 달라짐)
                    pass
            
            logger.info(f"펀더멘털 지표 계산 완료: {ticker}")
            return metrics
            
        except Exception as e:
            logger.error(f"펀더멘털 지표 계산 실패: {ticker}, {e}")
            return {}

