from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os
try:
    import FinanceDataReader as fdr
except Exception:
    fdr = None
import yfinance as yf

# 재무제표 서비스 import
from app.services.financial_statement_service import FinancialStatementService

router = APIRouter()

class StockItem(BaseModel):
    symbol: str
    name: str
    market: str
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None

class StockDetail(BaseModel):
    symbol: str
    name: str
    market: str
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

class CandleData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

class TechnicalIndicator(BaseModel):
    date: str
    ma5: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None

class FinancialStatementItem(BaseModel):
    stock_code: str
    quarter: str
    year: int
    value: Optional[float] = None
    change_pct: Optional[float] = None
    score: Optional[int] = None
    fs_code: Optional[str] = None

@router.get("", response_model=List[StockItem])
def get_stocks(
    market: Optional[str] = Query(None, description="시장 구분 (KOSPI, KOSDAQ, NASDAQ 등)"),
    sector: Optional[str] = Query(None, description="섹터 필터"),
    limit: int = Query(100, ge=1, le=1000, description="결과 제한 수")
):
    """주식 종목 리스트 조회"""
    try:
        if fdr is None:
            raise HTTPException(status_code=500, detail="FinanceDataReader not available")
        
        # KRX 상장 목록 조회
        df = fdr.StockListing("KRX")
        
        # 시장 필터
        if market and 'Market' in df.columns:
            df = df[df['Market'] == market]
        
        # 섹터 필터
        if sector and 'Sector' in df.columns:
            df = df[df['Sector'] == sector]
        
        # 결과 제한
        df = df.head(limit)
        
        stocks = []
        for _, row in df.iterrows():
            stocks.append(StockItem(
                symbol=str(row.get('Code', row.get('Symbol', ''))),
                name=str(row.get('Name', '')),
                market=str(row.get('Market', '')),
                sector=str(row.get('Sector', '')) if 'Sector' in df.columns else None,
                market_cap=float(row.get('Marcap', 0)) if 'Marcap' in df.columns else None
            ))
        
        return stocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stocks: {str(e)}")

@router.get("/financial-statements", response_model=List[FinancialStatementItem])
def get_financial_statements(
    fs_code: str = Query(..., description="재무제표 코드 (예: 당기순이익)"),
    quarter: str = Query(..., description="분기 (예: Q1, Q2, Q3, Q4)"),
    year: int = Query(..., description="연도"),
    comparison_type: int = Query(0, ge=0, le=1, description="비교 기준 (0: 전기대비, 1: 전년동기대비)")
):
    """국내주식 재무제표 정보 조회"""
    import logging
    logger = logging.getLogger(__name__)
    
    fs_service = FinancialStatementService()
    try:
        logger.info(f"재무제표 조회 시작: fs_code={fs_code}, quarter={quarter}, year={year}, comparison_type={comparison_type}")
        
        # 재무제표 서비스에서 함수 호출
        result_df = fs_service.get_fs_score(fs_code, comparison_type, quarter, year)
        
        logger.info(f"조회된 데이터 행 수: {len(result_df)}")
        
        if result_df.empty:
            logger.warning(f"데이터가 없습니다: fs_code={fs_code}, quarter={quarter}, year={year}")
            return []
        
        # DataFrame을 리스트로 변환
        financial_statements = []
        for _, row in result_df.iterrows():
            # 비교 기준에 따라 적절한 컬럼 선택
            change_col = "전기대비" if comparison_type == 0 else "전년동기대비"
            change_pct = float(row[change_col]) if change_col in row and pd.notna(row[change_col]) else None
            
            financial_statements.append(FinancialStatementItem(
                stock_code=str(row.get('stock_code', '')),
                quarter=str(row.get('quarter', '')),
                year=int(row.get('year', 0)),
                value=float(row.get('값', 0)) if '값' in row and pd.notna(row.get('값')) else None,
                change_pct=change_pct,
                score=int(row.get('score', 0)) if 'score' in row and pd.notna(row.get('score')) else None,
                fs_code=str(row.get('fs_code', fs_code))
            ))
        
        # 점수 순으로 정렬
        financial_statements.sort(key=lambda x: x.score if x.score is not None else 0, reverse=True)
        
        logger.info(f"재무제표 조회 완료: {len(financial_statements)}개 항목 반환")
        return financial_statements
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"재무제표 조회 실패: {str(e)}\n{error_detail}")
        raise HTTPException(
            status_code=500, 
            detail=f"재무제표 데이터를 불러오는데 실패했습니다: {str(e)}"
        )
    finally:
        # DB 연결 정리
        try:
            fs_service.close()
        except:
            pass

@router.get("/{symbol}", response_model=StockDetail)
def get_stock_detail(symbol: str = Path(..., description="종목 코드")):
    """특정 종목 상세 정보 조회"""
    try:
        # 기본 정보 조회
        if fdr is None:
            raise HTTPException(status_code=500, detail="FinanceDataReader not available")
        
        df = fdr.StockListing("KRX")
        stock_info = df[df['Code'] == symbol].iloc[0] if len(df[df['Code'] == symbol]) > 0 else None
        
        if stock_info is None:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # 최신 가격 정보 조회
        try:
            price_data = fdr.DataReader(symbol, end=datetime.now().strftime('%Y-%m-%d'))
            latest_price = price_data.iloc[-1] if len(price_data) > 0 else None
        except:
            latest_price = None
        
        return StockDetail(
            symbol=symbol,
            name=str(stock_info.get('Name', '')),
            market=str(stock_info.get('Market', '')),
            sector=str(stock_info.get('Sector', '')) if 'Sector' in stock_info else None,
            market_cap=float(stock_info.get('Marcap', 0)) if 'Marcap' in stock_info else None,
            price=float(latest_price['Close']) if latest_price is not None else None,
            volume=float(latest_price['Volume']) if latest_price is not None else None,
            high_52w=float(stock_info.get('High', 0)) if 'High' in stock_info else None,
            low_52w=float(stock_info.get('Low', 0)) if 'Low' in stock_info else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load stock detail: {str(e)}")

@router.get("/{symbol}/candles", response_model=List[CandleData])
def get_stock_candles(
    symbol: str = Path(..., description="종목 코드"),
    start: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    interval: str = Query("1d", description="간격 (1d, 1h, 5m 등)")
):
    """종목 캔들차트 데이터 조회"""
    try:
        if fdr is None:
            raise HTTPException(status_code=500, detail="FinanceDataReader not available")
        
        # 기본 날짜 설정
        if not end:
            end = datetime.now().strftime('%Y-%m-%d')
        if not start:
            start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 데이터 조회
        df = fdr.DataReader(symbol, start, end)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail="No data found for symbol")
        
        # 데이터 변환
        df = df.reset_index()
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d') if 'Date' in df.columns else df.index.strftime('%Y-%m-%d')
        
        candles = []
        for _, row in df.iterrows():
            candles.append(CandleData(
                date=row['date'],
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=float(row['Volume']) if 'Volume' in row else None
            ))
        
        return candles
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candles: {str(e)}")

@router.get("/{symbol}/indicators", response_model=List[TechnicalIndicator])
def get_stock_indicators(
    symbol: str = Path(..., description="종목 코드"),
    start: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    indicators: str = Query("ma,rsi,macd,bollinger", description="지표 종류 (ma,rsi,macd,bollinger)")
):
    """종목 기술지표 데이터 조회"""
    try:
        if fdr is None:
            raise HTTPException(status_code=500, detail="FinanceDataReader not available")
        
        # 기본 날짜 설정
        if not end:
            end = datetime.now().strftime('%Y-%m-%d')
        if not start:
            start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 데이터 조회
        df = fdr.DataReader(symbol, start, end)
        
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail="No data found for symbol")
        
        # 기술지표 계산
        df = df.reset_index()
        df['date'] = df['Date'].dt.strftime('%Y-%m-%d') if 'Date' in df.columns else df.index.strftime('%Y-%m-%d')
        
        # 이동평균
        if 'ma' in indicators:
            df['ma5'] = df['Close'].rolling(window=5).mean()
            df['ma20'] = df['Close'].rolling(window=20).mean()
            df['ma60'] = df['Close'].rolling(window=60).mean()
        
        # RSI
        if 'rsi' in indicators:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        if 'macd' in indicators:
            exp1 = df['Close'].ewm(span=12).mean()
            exp2 = df['Close'].ewm(span=26).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # 볼린저 밴드
        if 'bollinger' in indicators:
            df['ma20'] = df['Close'].rolling(window=20).mean()
            std = df['Close'].rolling(window=20).std()
            df['bollinger_upper'] = df['ma20'] + (std * 2)
            df['bollinger_lower'] = df['ma20'] - (std * 2)
        
        # 결과 변환
        indicators_list = []
        for _, row in df.iterrows():
            indicators_list.append(TechnicalIndicator(
                date=row['date'],
                ma5=float(row['ma5']) if 'ma5' in row and pd.notna(row['ma5']) else None,
                ma20=float(row['ma20']) if 'ma20' in row and pd.notna(row['ma20']) else None,
                ma60=float(row['ma60']) if 'ma60' in row and pd.notna(row['ma60']) else None,
                rsi=float(row['rsi']) if 'rsi' in row and pd.notna(row['rsi']) else None,
                macd=float(row['macd']) if 'macd' in row and pd.notna(row['macd']) else None,
                macd_signal=float(row['macd_signal']) if 'macd_signal' in row and pd.notna(row['macd_signal']) else None,
                bollinger_upper=float(row['bollinger_upper']) if 'bollinger_upper' in row and pd.notna(row['bollinger_upper']) else None,
                bollinger_lower=float(row['bollinger_lower']) if 'bollinger_lower' in row and pd.notna(row['bollinger_lower']) else None
            ))
        
        return indicators_list
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load indicators: {str(e)}")
