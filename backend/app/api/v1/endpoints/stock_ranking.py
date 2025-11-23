"""
주식 랭킹 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.stock_service import StockService
from app.schemas.stock import StockRankingRequest, StockRankingResponse, FinancialDataResponse

router = APIRouter()


def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    """주식 서비스 의존성"""
    return StockService(db)


@router.get("/rankings", response_model=StockRankingResponse)
async def get_stock_rankings(
    metric: str = Query(..., description="정렬할 지표명"),
    order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    limit: int = Query(50, description="결과 개수"),
    industry: Optional[str] = Query(None, description="업종 필터"),
    stock_service: StockService = Depends(get_stock_service)
):
    """
    주식 랭킹 조회
    
    - **metric**: 정렬할 지표명 (부채비율, 유보율, 매출액증가율, EPS증가율, ROA, ROE, EPS, BPS, PER, PBR, EV/EBITDA)
    - **order**: 정렬 순서 (asc: 오름차순, desc: 내림차순)
    - **limit**: 결과 개수 (기본값: 50)
    - **industry**: 업종 필터 (선택사항)
    """
    try:
        request = StockRankingRequest(
            metric=metric,
            order=order,
            limit=limit,
            industry=industry
        )
        
        stocks = stock_service.get_stock_rankings(request)
        
        return StockRankingResponse(
            stocks=stocks,
            total_count=len(stocks),
            metric=metric,
            order=order
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"주식 랭킹 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/industries", response_model=List[str])
async def get_industries(
    stock_service: StockService = Depends(get_stock_service)
):
    """
    업종 목록 조회
    """
    try:
        industries = stock_service.get_industries()
        return industries
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"업종 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/metrics", response_model=List[str])
async def get_available_metrics():
    """
    사용 가능한 지표 목록 조회
    """
    return [
        "부채비율",
        "유보율", 
        "매출액증가율",
        "EPS증가율",
        "ROA",
        "ROE",
        "EPS",
        "BPS",
        "PER",
        "PBR",
        "EV/EBITDA"
    ]
