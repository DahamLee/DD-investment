"""
주식 관련 모델
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel


class Stock(BaseModel):
    """주식 종목 모델"""
    __tablename__ = "stock"
    __table_args__ = {'schema': 'finance'}
    
    # id는 BaseModel에서 상속 (자동 생성)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(100))
    isin_code = Column(String(20))
    industry = Column(String(100))
    
    # 관계 설정
    financial_data = relationship("FinancialStatementRaw", back_populates="stock")


class FinancialAccount(BaseModel):
    """재무 계정 모델"""
    __tablename__ = "financial_account"
    __table_args__ = {'schema': 'finance'}
    
    # id는 BaseModel에서 상속 (자동 생성)
    account_name = Column(String(100), unique=True, nullable=False)
    account_type = Column(String(50))  # BS, IS, CF, VALUATION
    
    # 관계 설정
    financial_data = relationship("FinancialStatementRaw", back_populates="account")


class FinancialStatementRaw(BaseModel):
    """재무제표 원시 데이터 모델"""
    __tablename__ = "financial_statement_raw"
    __table_args__ = {'schema': 'finance'}
    
    # id는 BaseModel에서 상속 (자동 생성)
    stock_id = Column(Integer, ForeignKey('finance.stock.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('finance.financial_account.id'), nullable=False)
    year = Column(Integer, nullable=False)
    report_type = Column(String(10), nullable=False)  # Q1, Q2, Q3, FY
    value = Column(Numeric(20, 4))
    unit = Column(String(20), default='KRW')
    
    # 관계 설정
    stock = relationship("Stock", back_populates="financial_data")
    account = relationship("FinancialAccount", back_populates="financial_data")
