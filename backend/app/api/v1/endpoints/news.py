from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class NewsItem(BaseModel):
    id: str
    title: str
    summary: str
    published_at: str
    source: str
    category: str
    url: str
    image_url: Optional[str] = None

class NewsResponse(BaseModel):
    data: List[NewsItem]
    total: int
    page: int
    page_size: int

@router.get("/news", response_model=NewsResponse)
def get_news(
    category: Optional[str] = Query(None, description="뉴스 카테고리 (market, tech, etf, options)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    search: Optional[str] = Query(None, description="검색 키워드")
):
    """뉴스 목록 조회"""
    # TODO: 실제 뉴스 API 연동
    # 현재는 모킹 데이터 반환
    mock_news = [
        NewsItem(
            id="1",
            title="연준 금리 동결, 시장 반응은?",
            summary="미국 연방준비제도가 기준금리를 동결하기로 결정했다.",
            published_at="2024-01-15T09:00:00Z",
            source="Reuters",
            category="market",
            url="https://example.com/news/1",
            image_url="https://example.com/images/news1.jpg"
        ),
        NewsItem(
            id="2", 
            title="테크 실적 시즌 프리뷰",
            summary="주요 테크 기업들의 4분기 실적 발표가 시작된다.",
            published_at="2024-01-15T08:30:00Z",
            source="Bloomberg",
            category="tech",
            url="https://example.com/news/2"
        )
    ]
    
    return NewsResponse(
        data=mock_news,
        total=len(mock_news),
        page=page,
        page_size=page_size
    )

@router.get("/news/{news_id}")
def get_news_detail(news_id: str):
    """뉴스 상세 조회"""
    # TODO: 실제 뉴스 상세 API 연동
    return {"id": news_id, "content": "뉴스 상세 내용..."}

