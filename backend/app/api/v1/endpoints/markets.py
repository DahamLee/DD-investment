from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
try:
    import FinanceDataReader as fdr
except Exception:
    fdr = None
import yfinance as yf
import pandas as pd

router = APIRouter()

class OhlcRow(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

class TickerItem(BaseModel):
    code: str
    name: str
    market: Optional[str] = None

@router.get("/ohlc", response_model=List[OhlcRow])
def get_ohlc(
    ticker: str = Query(..., description="종목 코드 (예: 005930)"),
    start: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    prev_only: bool = Query(True, description="전일자만 반환 여부"),
):
    """종목 OHLC 데이터 조회"""
    # 1) Try FinanceDataReader (KRX 지원)
    if fdr is not None:
        try:
            df = fdr.DataReader(ticker, start, end)
        except Exception:
            df = None
    else:
        df = None

    # 2) Fallback to yfinance (KRX는 .KS/.KQ 접미사 필요할 수 있음)
    if df is None or len(df) == 0:
        yf_tickers = [ticker, f"{ticker}.KS", f"{ticker}.KQ"]
        df = None
        for yt in yf_tickers:
            try:
                df_try = yf.download(yt, start=start, end=end, progress=False)
                if df_try is not None and len(df_try) > 0:
                    df = df_try
                    break
            except Exception:
                continue
        if df is None or len(df) == 0:
            raise HTTPException(status_code=404, detail="No data found for ticker")

    if df is None or len(df) == 0:
        return []

    # 보편 컬럼 이름 대응: FinanceDataReader는 Date index, [Open, High, Low, Close, Volume] 제공
    df = df.reset_index()
    # 컬럼명 표준화
    rename_map = {
        'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'close', 'Volume': 'volume'
    }
    df = df.rename(columns=rename_map)
    # 날짜 문자열로 변환
    if isinstance(df.loc[0, 'date'], pd.Timestamp):
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # prev_only: 전일자 1건만 반환
    if prev_only:
        # 최근 데이터 2개 중 전일자 선택 (오늘이 포함되면 2번째, 아니면 1번째)
        recent = df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(2)
        if len(recent) == 1:
            return [recent.iloc[0].to_dict()]
        # len == 2 인 경우: 전일자 = 마지막 전 행
        return [recent.iloc[-2].to_dict()]

    rows = df[['date', 'open', 'high', 'low', 'close', 'volume']].to_dict(orient='records')
    return rows

@router.get("/tickers", response_model=List[TickerItem])
def get_tickers(market: Optional[str] = Query(None, description="시장 구분 (KOSPI, KOSDAQ 등)")):
    """KRX 상장 종목 목록 조회"""
    if fdr is None:
        raise HTTPException(status_code=500, detail="FinanceDataReader not available")
    try:
        # KRX 전체 상장 목록
        df = fdr.StockListing("KRX")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load tickers: {e}")

    # 표준 컬럼 대응 (코드/이름/시장)
    candidates = [
        ("Code", "Name", "Market"),
        ("Symbol", "Name", "Market"),
        ("code", "name", "market"),
    ]
    code_col = name_col = market_col = None
    for c, n, m in candidates:
        if c in df.columns and n in df.columns:
            code_col, name_col = c, n
            market_col = m if m in df.columns else None
            break
    if code_col is None:
        raise HTTPException(status_code=500, detail="Unexpected listing schema")

    if market and market_col and market_col in df.columns:
        df = df[df[market_col] == market]

    out = []
    for _, row in df.iterrows():
        out.append(TickerItem(
            code=str(row[code_col]),
            name=str(row[name_col]),
            market=str(row[market_col]) if (market_col and market_col in df.columns) else None,
        ))
    return out
