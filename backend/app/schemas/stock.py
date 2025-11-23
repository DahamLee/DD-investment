"""
주식 관련 스키마
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StockBase(BaseModel):
    """주식 기본 스키마"""
    ticker: str
    company_name: Optional[str] = None
    isin_code: Optional[str] = None
    industry: Optional[str] = None


class StockCreate(StockBase):
    """주식 생성 스키마"""
    pass


class StockResponse(StockBase):
    """주식 응답 스키마"""
    stock_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinancialDataResponse(BaseModel):
    """재무 데이터 응답 스키마"""
    stock_id: int
    ticker: str
    company_name: str
    industry: str
    부채비율: Optional[float] = None
    유보율: Optional[float] = None
    매출액증가율: Optional[float] = None
    EPS증가율: Optional[float] = None
    ROA: Optional[float] = None
    ROE: Optional[float] = None
    EPS: Optional[float] = None
    BPS: Optional[float] = None
    PER: Optional[float] = None
    PBR: Optional[float] = None
    EV_EBITDA: Optional[float] = None


class StockRankingRequest(BaseModel):
    """주식 랭킹 요청 스키마"""
    metric: str  # 정렬할 지표명
    order: str = "desc"  # asc 또는 desc
    limit: int = 50  # 결과 개수
    industry: Optional[str] = None  # 업종 필터


class StockRankingResponse(BaseModel):
    """주식 랭킹 응답 스키마"""
    stocks: List[FinancialDataResponse]
    total_count: int
    metric: str
    order: str
