from fastapi import APIRouter
from .endpoints import markets, news, health, stocks, lotto, crud, auth, stock_ranking

api_router = APIRouter()

# 각 엔드포인트 라우터 포함
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(stock_ranking.router, prefix="/stock-ranking", tags=["stock-ranking"])
api_router.include_router(lotto.router, prefix="/lotto", tags=["lotto"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(crud.router, prefix="/crud", tags=["crud"])
