"""
주식 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.models.stock import Stock, FinancialAccount, FinancialStatementRaw
from app.schemas.stock import StockRankingRequest, FinancialDataResponse


class StockService:
    """주식 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_stock_rankings(self, request: StockRankingRequest) -> List[FinancialDataResponse]:
        """주식 랭킹 조회"""
        
        # SQL 쿼리로 재무 데이터를 피벗하여 조회
        query = text("""
            SELECT 
                s.id as stock_id,
                s.ticker,
                s.company_name,
                s.industry,
                MAX(CASE WHEN fa.account_name = '부채비율' THEN fsr.value END) as 부채비율,
                MAX(CASE WHEN fa.account_name = '유보율' THEN fsr.value END) as 유보율,
                MAX(CASE WHEN fa.account_name = '매출액증가율' THEN fsr.value END) as 매출액증가율,
                MAX(CASE WHEN fa.account_name = 'EPS증가율' THEN fsr.value END) as EPS증가율,
                MAX(CASE WHEN fa.account_name = 'ROA' THEN fsr.value END) as ROA,
                MAX(CASE WHEN fa.account_name = 'ROE' THEN fsr.value END) as ROE,
                MAX(CASE WHEN fa.account_name = 'EPS' THEN fsr.value END) as EPS,
                MAX(CASE WHEN fa.account_name = 'BPS' THEN fsr.value END) as BPS,
                MAX(CASE WHEN fa.account_name = 'PER' THEN fsr.value END) as PER,
                MAX(CASE WHEN fa.account_name = 'PBR' THEN fsr.value END) as PBR,
                MAX(CASE WHEN fa.account_name = 'EV/EBITDA' THEN fsr.value END) as EV_EBITDA
            FROM finance.stock s
            LEFT JOIN finance.financial_statement_raw fsr ON s.id = fsr.stock_id
            LEFT JOIN finance.financial_account fa ON fsr.account_id = fa.id
            WHERE fsr.year = 2024 AND fsr.report_type = 'FY'
        """)
        
        # 업종 필터 추가
        if request.industry:
            query = text(str(query) + " AND s.industry = :industry")
            params = {"industry": request.industry}
        else:
            params = {}
        
        # 정렬 추가
        order_clause = "ASC" if request.order == "asc" else "DESC"
        
        # 지표별 정렬
        metric_mapping = {
            "부채비율": "부채비율",
            "유보율": "유보율", 
            "매출액증가율": "매출액증가율",
            "EPS증가율": "EPS증가율",
            "ROA": "ROA",
            "ROE": "ROE",
            "EPS": "EPS",
            "BPS": "BPS",
            "PER": "PER",
            "PBR": "PBR",
            "EV/EBITDA": "EV_EBITDA"
        }
        
        if request.metric in metric_mapping:
            query = text(str(query) + f" GROUP BY s.id, s.ticker, s.company_name, s.industry ORDER BY {metric_mapping[request.metric]} {order_clause} NULLS LAST LIMIT :limit")
            params["limit"] = request.limit
        else:
            query = text(str(query) + " GROUP BY s.id, s.ticker, s.company_name, s.industry ORDER BY s.company_name LIMIT :limit")
            params["limit"] = request.limit
        
        # 쿼리 실행
        result = self.db.execute(query, params)
        rows = result.fetchall()
        
        # 결과를 스키마로 변환
        stocks = []
        for row in rows:
            stock_data = FinancialDataResponse(
                stock_id=row[0],
                ticker=row[1],
                company_name=row[2],
                industry=row[3],
                부채비율=float(row[4]) if row[4] is not None else None,
                유보율=float(row[5]) if row[5] is not None else None,
                매출액증가율=float(row[6]) if row[6] is not None else None,
                EPS증가율=float(row[7]) if row[7] is not None else None,
                ROA=float(row[8]) if row[8] is not None else None,
                ROE=float(row[9]) if row[9] is not None else None,
                EPS=float(row[10]) if row[10] is not None else None,
                BPS=float(row[11]) if row[11] is not None else None,
                PER=float(row[12]) if row[12] is not None else None,
                PBR=float(row[13]) if row[13] is not None else None,
                EV_EBITDA=float(row[14]) if row[14] is not None else None
            )
            stocks.append(stock_data)
        
        return stocks
    
    def get_industries(self) -> List[str]:
        """업종 목록 조회"""
        result = self.db.execute(text("SELECT DISTINCT industry FROM finance.stock WHERE industry IS NOT NULL ORDER BY industry"))
        return [row[0] for row in result.fetchall()]
