"""
미국 주식 관련 모델
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Date, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class USStock(BaseModel):
    """미국 주식 종목 모델"""
    __tablename__ = "us_stock"
    __table_args__ = {'schema': 'finance'}
    
    # 기본 정보
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(200))
    cik = Column(String(10), index=True)  # SEC Central Index Key (10자리)
    
    # 거래소 정보
    exchange = Column(String(20))  # NASDAQ, NYSE, AMEX 등
    sector = Column(String(100))
    industry = Column(String(100))
    
    # 기본 지표 (최신 스냅샷)
    market_cap = Column(Numeric(20, 2))  # 시가총액
    currency = Column(String(10), default='USD')
    
    # 활성화 여부
    is_active = Column(Boolean, default=True)
    
    # 관계 설정
    prices = relationship("USPriceDaily", back_populates="stock", cascade="all, delete-orphan")
    fundamentals = relationship("USFundamental", back_populates="stock", cascade="all, delete-orphan")
    filings = relationship("USSecFiling", back_populates="stock", cascade="all, delete-orphan")


class USPriceDaily(BaseModel):
    """미국 주식 일봉 데이터 모델"""
    __tablename__ = "us_price_daily"
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='uq_us_price_daily_stock_date'),
        {'schema': 'finance'}
    )
    
    stock_id = Column(Integer, ForeignKey('finance.us_stock.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # OHLCV
    open = Column(Numeric(12, 4))
    high = Column(Numeric(12, 4))
    low = Column(Numeric(12, 4))
    close = Column(Numeric(12, 4))
    adj_close = Column(Numeric(12, 4))  # 수정 종가
    volume = Column(Numeric(20, 0))  # 거래량
    
    # 추가 지표
    market_cap = Column(Numeric(20, 2))  # 해당 일의 시가총액
    
    # 관계 설정
    stock = relationship("USStock", back_populates="prices")


class USFundamental(BaseModel):
    """미국 주식 펀더멘털 지표 모델"""
    __tablename__ = "us_fundamental"
    __table_args__ = (
        UniqueConstraint('stock_id', 'as_of_date', name='uq_us_fundamental_stock_date'),
        {'schema': 'finance'}
    )
    
    stock_id = Column(Integer, ForeignKey('finance.us_stock.id'), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False, index=True)  # 기준일
    
    # 밸류에이션 지표
    pe_ratio = Column(Numeric(10, 4))  # PER
    pb_ratio = Column(Numeric(10, 4))  # PBR
    ps_ratio = Column(Numeric(10, 4))  # PSR
    ev_ebitda = Column(Numeric(10, 4))  # EV/EBITDA
    
    # 수익성 지표
    roe = Column(Numeric(10, 4))  # ROE (%)
    roa = Column(Numeric(10, 4))  # ROA (%)
    profit_margin = Column(Numeric(10, 4))  # 순이익률 (%)
    operating_margin = Column(Numeric(10, 4))  # 영업이익률 (%)
    
    # 성장성 지표
    eps = Column(Numeric(10, 4))  # EPS
    eps_growth = Column(Numeric(10, 4))  # EPS 성장률 (%)
    revenue_growth = Column(Numeric(10, 4))  # 매출 성장률 (%)
    
    # 배당 지표
    dividend_yield = Column(Numeric(10, 4))  # 배당수익률 (%)
    
    # 리스크 지표
    beta = Column(Numeric(10, 4))  # 베타
    
    # 관계 설정
    stock = relationship("USStock", back_populates="fundamentals")


class USSecFiling(BaseModel):
    """SEC 공시 데이터 모델"""
    __tablename__ = "us_sec_filing"
    __table_args__ = {'schema': 'finance'}
    
    stock_id = Column(Integer, ForeignKey('finance.us_stock.id'), nullable=False, index=True)
    
    # SEC 공시 정보
    form_type = Column(String(20), nullable=False, index=True)  # 10-K, 10-Q, 8-K 등
    filing_date = Column(Date, nullable=False, index=True)  # 공시 접수일
    report_date = Column(Date)  # 보고서 기준일
    accession_number = Column(String(50), unique=True)  # SEC Accession Number
    
    # 공시 내용
    description = Column(Text)  # 공시 설명
    document_url = Column(Text)  # SEC 문서 링크
    
    # 추가 메타데이터
    file_size = Column(Integer)  # 파일 크기 (bytes)
    is_xbrl = Column(Boolean, default=False)  # XBRL 여부
    
    # 관계 설정
    stock = relationship("USStock", back_populates="filings")

