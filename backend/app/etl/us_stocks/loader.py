"""
미국 주식 데이터 로드 (Load) 모듈

전처리된 미국 주식 데이터를 데이터베이스에 저장합니다.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from app.models.us_stock import USStock, USPriceDaily, USFundamental, USSecFiling

logger = logging.getLogger(__name__)


class USStockDataLoader:
    """미국 주식 데이터베이스 로드 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    def load_us_stocks(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        미국 주식 종목 데이터 로드
        
        Args:
            df: DataFrame with columns: ['ticker', 'company_name', 'exchange', 
                                        'sector', 'industry', 'market_cap', 'currency', 'cik']
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"미국 주식 종목 데이터 로드 시작: {len(df)}개")
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for _, row in df.iterrows():
                try:
                    ticker = str(row['ticker']).strip().upper()
                    company_name = str(row.get('company_name', '')).strip() if pd.notna(row.get('company_name')) else None
                    exchange = str(row.get('exchange', '')).strip() if pd.notna(row.get('exchange')) else None
                    sector = str(row.get('sector', '')).strip() if pd.notna(row.get('sector')) else None
                    industry = str(row.get('industry', '')).strip() if pd.notna(row.get('industry')) else None
                    market_cap = row.get('market_cap') if pd.notna(row.get('market_cap')) else None
                    currency = str(row.get('currency', 'USD')).strip() if pd.notna(row.get('currency')) else 'USD'
                    cik = str(row.get('cik', '')).strip() if pd.notna(row.get('cik')) else None
                    
                    if not ticker:
                        stats['skipped'] += 1
                        continue
                    
                    # CIK를 10자리로 패딩
                    if cik:
                        cik = cik.zfill(10)
                    
                    # 기존 종목 확인
                    existing_stock = self.db.query(USStock).filter(USStock.ticker == ticker).first()
                    
                    if existing_stock:
                        # 업데이트
                        if company_name:
                            existing_stock.company_name = company_name
                        if cik:
                            existing_stock.cik = cik
                        if exchange:
                            existing_stock.exchange = exchange
                        if sector:
                            existing_stock.sector = sector
                        if industry:
                            existing_stock.industry = industry
                        if market_cap is not None:
                            existing_stock.market_cap = market_cap
                        if currency:
                            existing_stock.currency = currency
                        existing_stock.updated_at = datetime.utcnow()
                        stats['updated'] += 1
                    else:
                        # 생성
                        new_stock = USStock(
                            ticker=ticker,
                            company_name=company_name,
                            cik=cik,
                            exchange=exchange,
                            sector=sector,
                            industry=industry,
                            market_cap=market_cap,
                            currency=currency,
                            is_active=True
                        )
                        self.db.add(new_stock)
                        stats['created'] += 1
                    
                except IntegrityError as e:
                    logger.warning(f"종목 로드 실패 (중복): {row.get('ticker', 'unknown')}, {e}")
                    self.db.rollback()
                    stats['skipped'] += 1
                    continue
                except Exception as e:
                    logger.warning(f"종목 로드 실패: {row.get('ticker', 'unknown')}, {e}")
                    stats['skipped'] += 1
                    continue
            
            self.db.commit()
            logger.info(f"미국 주식 종목 데이터 로드 완료: {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"미국 주식 종목 데이터 로드 실패: {e}")
            raise
    
    def load_us_stock_prices(
        self,
        ticker: str,
        price_df: pd.DataFrame
    ) -> Dict[str, int]:
        """
        미국 주식 일봉 데이터 로드
        
        Args:
            ticker: 종목 코드
            price_df: DataFrame with columns: ['Date', 'Open', 'High', 'Low', 
                                                'Close', 'Volume', 'Adj Close', 'market_cap']
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"미국 주식 시세 데이터 로드 시작: {ticker}, {len(price_df)}개 행")
            
            # 종목 조회
            stock = self.db.query(USStock).filter(USStock.ticker == ticker.upper()).first()
            if not stock:
                logger.warning(f"종목을 찾을 수 없음: {ticker}")
                return {'created': 0, 'updated': 0, 'skipped': len(price_df)}
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for _, row in price_df.iterrows():
                try:
                    # 날짜 파싱
                    if 'Date' in row:
                        price_date = pd.to_datetime(row['Date']).date()
                    elif 'date' in row:
                        price_date = pd.to_datetime(row['date']).date()
                    else:
                        stats['skipped'] += 1
                        continue
                    
                    # OHLCV 데이터
                    open_price = row.get('Open') if pd.notna(row.get('Open')) else None
                    high_price = row.get('High') if pd.notna(row.get('High')) else None
                    low_price = row.get('Low') if pd.notna(row.get('Low')) else None
                    close_price = row.get('Close') if pd.notna(row.get('Close')) else None
                    adj_close = row.get('Adj Close') if pd.notna(row.get('Adj Close')) else close_price
                    volume = row.get('Volume') if pd.notna(row.get('Volume')) else None
                    market_cap = row.get('market_cap') if pd.notna(row.get('market_cap')) else None
                    
                    # 기존 데이터 확인
                    existing_price = self.db.query(USPriceDaily).filter(
                        and_(
                            USPriceDaily.stock_id == stock.id,
                            USPriceDaily.date == price_date
                        )
                    ).first()
                    
                    if existing_price:
                        # 업데이트
                        if open_price is not None:
                            existing_price.open = open_price
                        if high_price is not None:
                            existing_price.high = high_price
                        if low_price is not None:
                            existing_price.low = low_price
                        if close_price is not None:
                            existing_price.close = close_price
                        if adj_close is not None:
                            existing_price.adj_close = adj_close
                        if volume is not None:
                            existing_price.volume = volume
                        if market_cap is not None:
                            existing_price.market_cap = market_cap
                        existing_price.updated_at = datetime.utcnow()
                        stats['updated'] += 1
                    else:
                        # 생성
                        new_price = USPriceDaily(
                            stock_id=stock.id,
                            date=price_date,
                            open=open_price,
                            high=high_price,
                            low=low_price,
                            close=close_price,
                            adj_close=adj_close,
                            volume=volume,
                            market_cap=market_cap
                        )
                        self.db.add(new_price)
                        stats['created'] += 1
                    
                except IntegrityError as e:
                    logger.warning(f"시세 데이터 로드 실패 (중복): {ticker}, {price_date}, {e}")
                    self.db.rollback()
                    stats['skipped'] += 1
                    continue
                except Exception as e:
                    logger.warning(f"시세 데이터 로드 실패: {ticker}, {price_date}, {e}")
                    stats['skipped'] += 1
                    continue
            
            self.db.commit()
            logger.info(f"미국 주식 시세 데이터 로드 완료: {ticker}, {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"미국 주식 시세 데이터 로드 실패: {ticker}, {e}")
            raise
    
    def load_us_fundamentals(
        self,
        ticker: str,
        metrics: Dict,
        as_of_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        미국 주식 펀더멘털 지표 로드
        
        Args:
            ticker: 종목 코드
            metrics: 펀더멘털 지표 딕셔너리
            as_of_date: 기준일 (None이면 오늘 날짜)
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"미국 주식 펀더멘털 데이터 로드 시작: {ticker}")
            
            # 종목 조회
            stock = self.db.query(USStock).filter(USStock.ticker == ticker.upper()).first()
            if not stock:
                logger.warning(f"종목을 찾을 수 없음: {ticker}")
                return {'created': 0, 'updated': 0, 'skipped': 0}
            
            # 기준일 설정
            if as_of_date is None:
                as_of_date = date.today()
            
            # 기존 데이터 확인
            existing_fundamental = self.db.query(USFundamental).filter(
                and_(
                    USFundamental.stock_id == stock.id,
                    USFundamental.as_of_date == as_of_date
                )
            ).first()
            
            # 펀더멘털 데이터 추출
            pe_ratio = metrics.get('pe_ratio')
            pb_ratio = metrics.get('pb_ratio')
            ps_ratio = metrics.get('ps_ratio')
            ev_ebitda = metrics.get('ev_ebitda')
            roe = metrics.get('roe')
            roa = metrics.get('roa')
            profit_margin = metrics.get('profit_margin')
            operating_margin = metrics.get('operating_margin')
            eps = metrics.get('eps')
            eps_growth = metrics.get('eps_growth')
            revenue_growth = metrics.get('revenue_growth')
            dividend_yield = metrics.get('dividend_yield')
            beta = metrics.get('beta')
            
            if existing_fundamental:
                # 업데이트
                if pe_ratio is not None:
                    existing_fundamental.pe_ratio = pe_ratio
                if pb_ratio is not None:
                    existing_fundamental.pb_ratio = pb_ratio
                if ps_ratio is not None:
                    existing_fundamental.ps_ratio = ps_ratio
                if ev_ebitda is not None:
                    existing_fundamental.ev_ebitda = ev_ebitda
                if roe is not None:
                    existing_fundamental.roe = roe
                if roa is not None:
                    existing_fundamental.roa = roa
                if profit_margin is not None:
                    existing_fundamental.profit_margin = profit_margin
                if operating_margin is not None:
                    existing_fundamental.operating_margin = operating_margin
                if eps is not None:
                    existing_fundamental.eps = eps
                if eps_growth is not None:
                    existing_fundamental.eps_growth = eps_growth
                if revenue_growth is not None:
                    existing_fundamental.revenue_growth = revenue_growth
                if dividend_yield is not None:
                    existing_fundamental.dividend_yield = dividend_yield
                if beta is not None:
                    existing_fundamental.beta = beta
                existing_fundamental.updated_at = datetime.utcnow()
                
                self.db.commit()
                logger.info(f"미국 주식 펀더멘털 데이터 업데이트 완료: {ticker}")
                return {'created': 0, 'updated': 1, 'skipped': 0}
            else:
                # 생성
                new_fundamental = USFundamental(
                    stock_id=stock.id,
                    as_of_date=as_of_date,
                    pe_ratio=pe_ratio,
                    pb_ratio=pb_ratio,
                    ps_ratio=ps_ratio,
                    ev_ebitda=ev_ebitda,
                    roe=roe,
                    roa=roa,
                    profit_margin=profit_margin,
                    operating_margin=operating_margin,
                    eps=eps,
                    eps_growth=eps_growth,
                    revenue_growth=revenue_growth,
                    dividend_yield=dividend_yield,
                    beta=beta
                )
                self.db.add(new_fundamental)
                self.db.commit()
                logger.info(f"미국 주식 펀더멘털 데이터 생성 완료: {ticker}")
                return {'created': 1, 'updated': 0, 'skipped': 0}
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"미국 주식 펀더멘털 데이터 로드 실패 (중복): {ticker}, {e}")
            return {'created': 0, 'updated': 0, 'skipped': 1}
        except Exception as e:
            self.db.rollback()
            logger.error(f"미국 주식 펀더멘털 데이터 로드 실패: {ticker}, {e}")
            raise
    
    def load_us_sec_filings(
        self,
        ticker: str,
        filings: List[Dict]
    ) -> Dict[str, int]:
        """
        SEC 공시 데이터 로드
        
        Args:
            ticker: 종목 코드
            filings: 공시 데이터 리스트 [{'form': '10-K', 'filingDate': '2024-01-01', ...}, ...]
        
        Returns:
            Dict with 'created', 'updated', 'skipped' counts
        """
        try:
            logger.info(f"SEC 공시 데이터 로드 시작: {ticker}, {len(filings)}개")
            
            # 종목 조회
            stock = self.db.query(USStock).filter(USStock.ticker == ticker.upper()).first()
            if not stock:
                logger.warning(f"종목을 찾을 수 없음: {ticker}")
                return {'created': 0, 'updated': 0, 'skipped': len(filings)}
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0}
            
            for filing_data in filings:
                try:
                    form_type = str(filing_data.get('form', '')).strip()
                    filing_date_str = filing_data.get('filingDate', '')
                    report_date_str = filing_data.get('reportDate', '')
                    accession_number = str(filing_data.get('accessionNumber', '')).strip()
                    description = str(filing_data.get('description', '')).strip() if filing_data.get('description') else None
                    document_url = str(filing_data.get('documentUrl', '')).strip() if filing_data.get('documentUrl') else None
                    
                    if not form_type or not filing_date_str:
                        stats['skipped'] += 1
                        continue
                    
                    # 날짜 파싱
                    try:
                        filing_date = pd.to_datetime(filing_date_str).date()
                    except:
                        stats['skipped'] += 1
                        continue
                    
                    report_date = None
                    if report_date_str:
                        try:
                            report_date = pd.to_datetime(report_date_str).date()
                        except:
                            pass
                    
                    # Accession Number로 기존 데이터 확인
                    existing_filing = None
                    if accession_number:
                        existing_filing = self.db.query(USSecFiling).filter(
                            USSecFiling.accession_number == accession_number
                        ).first()
                    
                    if existing_filing:
                        # 업데이트
                        existing_filing.form_type = form_type
                        existing_filing.filing_date = filing_date
                        if report_date:
                            existing_filing.report_date = report_date
                        if description:
                            existing_filing.description = description
                        if document_url:
                            existing_filing.document_url = document_url
                        existing_filing.updated_at = datetime.utcnow()
                        stats['updated'] += 1
                    else:
                        # 생성
                        new_filing = USSecFiling(
                            stock_id=stock.id,
                            form_type=form_type,
                            filing_date=filing_date,
                            report_date=report_date,
                            accession_number=accession_number if accession_number else None,
                            description=description,
                            document_url=document_url,
                            is_xbrl=False  # 기본값
                        )
                        self.db.add(new_filing)
                        stats['created'] += 1
                    
                except IntegrityError as e:
                    logger.warning(f"SEC 공시 데이터 로드 실패 (중복): {ticker}, {filing_data.get('form', 'unknown')}, {e}")
                    self.db.rollback()
                    stats['skipped'] += 1
                    continue
                except Exception as e:
                    logger.warning(f"SEC 공시 데이터 로드 실패: {ticker}, {filing_data.get('form', 'unknown')}, {e}")
                    stats['skipped'] += 1
                    continue
            
            self.db.commit()
            logger.info(f"SEC 공시 데이터 로드 완료: {ticker}, {stats}")
            return stats
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"SEC 공시 데이터 로드 실패: {ticker}, {e}")
            raise
    
    def load_multiple_stocks_prices(
        self,
        prices_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict[str, int]]:
        """
        여러 종목의 시세 데이터 일괄 로드
        
        Args:
            prices_dict: Dict[ticker, DataFrame]
        
        Returns:
            Dict[ticker, stats]
        """
        results = {}
        for ticker, price_df in prices_dict.items():
            try:
                stats = self.load_us_stock_prices(ticker, price_df)
                results[ticker] = stats
            except Exception as e:
                logger.error(f"종목 {ticker} 시세 데이터 로드 실패: {e}")
                results[ticker] = {'created': 0, 'updated': 0, 'skipped': len(price_df)}
        
        return results

