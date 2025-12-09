"""
데이터 로드 (Load) 모듈

전처리된 데이터를 데이터베이스에 저장합니다.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.stock import Stock, FinancialAccount, FinancialStatementRaw

logger = logging.getLogger(__name__)


class DataLoader:
    """데이터베이스 로드 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def load_stocks(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        주식 종목 데이터 로드
        
        Args:
            df: Stock DataFrame with columns: ['ticker', 'company_name', 'isin_code', 'industry']
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"주식 종목 데이터 로드 시작: {len(df)}개")
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for _, row in df.iterrows():
                try:
                    ticker = str(row['ticker']).strip()
                    company_name = str(row.get('company_name', '')).strip()
                    isin_code = str(row.get('isin_code', '')).strip() if pd.notna(row.get('isin_code')) else None
                    industry = str(row.get('industry', '')).strip() if pd.notna(row.get('industry')) else None
                    
                    if not ticker or not company_name:
                        stats['skipped'] += 1
                        continue
                    
                    # 기존 종목 확인
                    existing_stock = self.db.query(Stock).filter(Stock.ticker == ticker).first()
                    
                    if existing_stock:
                        # 업데이트
                        existing_stock.company_name = company_name
                        if isin_code:
                            existing_stock.isin_code = isin_code
                        if industry:
                            existing_stock.industry = industry
                        existing_stock.updated_at = datetime.utcnow()
                        stats['updated'] += 1
                    else:
                        # 생성
                        new_stock = Stock(
                            ticker=ticker,
                            company_name=company_name,
                            isin_code=isin_code,
                            industry=industry
                        )
                        self.db.add(new_stock)
                        stats['created'] += 1
                    
                except Exception as e:
                    logger.warning(f"종목 로드 실패: {row.get('ticker', 'unknown')}, {e}")
                    stats['skipped'] += 1
                    continue
            
            self.db.commit()
            logger.info(f"주식 종목 데이터 로드 완료: {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"주식 종목 데이터 로드 실패: {e}")
            raise
    
    def load_financial_accounts(self, account_names: List[Dict[str, str]]) -> Dict[str, int]:
        """
        재무 계정 데이터 로드
        
        Args:
            account_names: [{'name': '매출액', 'type': 'IS'}, ...]
        
        Returns:
            Dict with 'created', 'updated' counts
        """
        try:
            logger.info(f"재무 계정 데이터 로드 시작: {len(account_names)}개")
            
            stats = {'created': 0, 'updated': 0}
            
            for account_info in account_names:
                try:
                    account_name = account_info['name']
                    account_type = account_info.get('type', 'UNKNOWN')
                    
                    existing = self.db.query(FinancialAccount).filter(
                        FinancialAccount.account_name == account_name
                    ).first()
                    
                    if existing:
                        existing.account_type = account_type
                        existing.updated_at = datetime.utcnow()
                        stats['updated'] += 1
                    else:
                        new_account = FinancialAccount(
                            account_name=account_name,
                            account_type=account_type
                        )
                        self.db.add(new_account)
                        stats['created'] += 1
                    
                except Exception as e:
                    logger.warning(f"재무 계정 로드 실패: {account_info}, {e}")
                    continue
            
            self.db.commit()
            logger.info(f"재무 계정 데이터 로드 완료: {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"재무 계정 데이터 로드 실패: {e}")
            raise
    
    def load_financial_statements(
        self,
        ticker: str,
        financial_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, int]:
        """
        재무제표 원시 데이터 로드
        
        Args:
            ticker: 종목 코드
            financial_data: {'balance_sheet': df, 'income_statement': df, 'cash_flow': df}
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"재무제표 데이터 로드 시작: {ticker}")
            
            # 종목 조회
            stock = self.db.query(Stock).filter(Stock.ticker == ticker).first()
            if not stock:
                logger.warning(f"종목을 찾을 수 없음: {ticker}")
                return {'created': 0, 'updated': 0, 'skipped': 0}
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0}
            
            # TODO: 실제 재무제표 데이터 구조에 맞게 구현 필요
            # 현재는 구조만 제공
            
            logger.info(f"재무제표 데이터 로드 완료: {ticker}, {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"재무제표 데이터 로드 실패: {ticker}, {e}")
            raise
    
    def load_stock_prices(
        self,
        ticker: str,
        price_df: pd.DataFrame
    ) -> Dict[str, int]:
        """
        주식 시세 데이터 로드
        
        주의: 현재 모델에 시세 테이블이 없으므로, 필요시 모델 추가 필요
        
        Args:
            ticker: 종목 코드
            price_df: 시세 DataFrame
        
        Returns:
            Dict with stats
        """
        try:
            logger.info(f"주식 시세 데이터 로드 시작: {ticker}")
            
            # TODO: 시세 데이터 모델이 없으므로, 필요시 추가 필요
            # 예: StockPrice 모델 생성 후 구현
            
            logger.warning("시세 데이터 모델이 없어 로드 스킵")
            return {'created': 0, 'updated': 0, 'skipped': len(price_df)}
            
        except Exception as e:
            logger.error(f"주식 시세 데이터 로드 실패: {ticker}, {e}")
            raise

