"""
데이터 전처리 (Transform) 모듈

추출된 데이터를 정제하고 변환합니다.
"""
import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """데이터 전처리 클래스"""
    
    def __init__(self):
        self.logger = logger
    
    def clean_stock_list(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        주식 종목 리스트 정제
        
        Args:
            df: 원본 DataFrame
        
        Returns:
            정제된 DataFrame
        """
        try:
            logger.info("주식 종목 리스트 정제 시작")
            
            # 복사본 생성
            df_clean = df.copy()
            
            # 중복 제거
            df_clean = df_clean.drop_duplicates(subset=['ticker'], keep='first')
            
            # 필수 컬럼 검증
            required_cols = ['ticker', 'company_name']
            missing_cols = [col for col in required_cols if col not in df_clean.columns]
            if missing_cols:
                raise ValueError(f"필수 컬럼 누락: {missing_cols}")
            
            # 빈 값 처리
            df_clean['company_name'] = df_clean['company_name'].fillna('')
            df_clean['industry'] = df_clean.get('industry', pd.Series()).fillna('')
            df_clean['isin_code'] = df_clean.get('isin_code', pd.Series()).fillna('')
            
            # ticker 형식 정규화 (앞뒤 공백 제거, 대문자 변환)
            df_clean['ticker'] = df_clean['ticker'].astype(str).str.strip().str.upper()
            
            # 유효하지 않은 ticker 제거 (6자리 숫자 또는 알파벳+숫자)
            df_clean = df_clean[
                df_clean['ticker'].str.match(r'^[A-Z0-9]{1,10}$', na=False)
            ]
            
            logger.info(f"주식 종목 리스트 정제 완료: {len(df_clean)}개")
            return df_clean
            
        except Exception as e:
            logger.error(f"주식 종목 리스트 정제 실패: {e}")
            raise
    
    def clean_stock_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        주식 시세 데이터 정제
        
        Args:
            df: 원본 DataFrame
        
        Returns:
            정제된 DataFrame
        """
        try:
            if df.empty:
                return df
            
            logger.info("주식 시세 데이터 정제 시작")
            
            df_clean = df.copy()
            
            # Date 컬럼 확인 및 변환
            if 'Date' in df_clean.columns:
                df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')
            elif df_clean.index.name == 'Date' or isinstance(df_clean.index, pd.DatetimeIndex):
                df_clean = df_clean.reset_index()
                if 'Date' not in df_clean.columns:
                    df_clean['Date'] = df_clean.index
            
            # Date가 없으면 에러
            if 'Date' not in df_clean.columns:
                raise ValueError("Date 컬럼이 없습니다")
            
            # 날짜순 정렬
            df_clean = df_clean.sort_values('Date').reset_index(drop=True)
            
            # 가격 데이터 정제
            price_cols = ['Open', 'High', 'Low', 'Close']
            for col in price_cols:
                if col in df_clean.columns:
                    # 음수나 0인 가격 제거
                    df_clean = df_clean[df_clean[col] > 0]
                    # 이상치 제거 (평균의 10배 이상)
                    if len(df_clean) > 0:
                        mean_price = df_clean[col].mean()
                        df_clean = df_clean[df_clean[col] <= mean_price * 10]
            
            # Volume 정제
            if 'Volume' in df_clean.columns:
                df_clean['Volume'] = df_clean['Volume'].fillna(0)
                df_clean['Volume'] = df_clean['Volume'].clip(lower=0)
            
            # 중복 날짜 제거 (최신 데이터 유지)
            df_clean = df_clean.drop_duplicates(subset=['Date'], keep='last')
            
            # 결측치가 너무 많은 행 제거 (50% 이상)
            threshold = len(df_clean.columns) * 0.5
            df_clean = df_clean.dropna(thresh=threshold)
            
            logger.info(f"주식 시세 데이터 정제 완료: {len(df_clean)}개 행")
            return df_clean
            
        except Exception as e:
            logger.error(f"주식 시세 데이터 정제 실패: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        기술적 지표 계산
        
        Args:
            df: 시세 DataFrame
        
        Returns:
            기술적 지표가 추가된 DataFrame
        """
        try:
            if df.empty or 'Close' not in df.columns:
                return df
            
            logger.info("기술적 지표 계산 시작")
            
            df_ind = df.copy()
            
            # 이동평균
            df_ind['MA5'] = df_ind['Close'].rolling(window=5).mean()
            df_ind['MA20'] = df_ind['Close'].rolling(window=20).mean()
            df_ind['MA60'] = df_ind['Close'].rolling(window=60).mean()
            
            # RSI (Relative Strength Index)
            delta = df_ind['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_ind['RSI'] = 100 - (100 / (1 + rs))
            
            # 볼린저 밴드
            df_ind['BB_Middle'] = df_ind['Close'].rolling(window=20).mean()
            bb_std = df_ind['Close'].rolling(window=20).std()
            df_ind['BB_Upper'] = df_ind['BB_Middle'] + (bb_std * 2)
            df_ind['BB_Lower'] = df_ind['BB_Middle'] - (bb_std * 2)
            
            # MACD
            exp1 = df_ind['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df_ind['Close'].ewm(span=26, adjust=False).mean()
            df_ind['MACD'] = exp1 - exp2
            df_ind['MACD_Signal'] = df_ind['MACD'].ewm(span=9, adjust=False).mean()
            df_ind['MACD_Hist'] = df_ind['MACD'] - df_ind['MACD_Signal']
            
            logger.info("기술적 지표 계산 완료")
            return df_ind
            
        except Exception as e:
            logger.error(f"기술적 지표 계산 실패: {e}")
            return df
    
    def normalize_financial_data(
        self,
        financial_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        재무제표 데이터 정규화
        
        Args:
            financial_data: 재무제표 딕셔너리
        
        Returns:
            정규화된 재무제표 딕셔너리
        """
        try:
            logger.info("재무제표 데이터 정규화 시작")
            
            normalized = {}
            
            for key, df in financial_data.items():
                if df.empty:
                    normalized[key] = df
                    continue
                
                df_norm = df.copy()
                
                # 숫자형 컬럼만 정규화
                numeric_cols = df_norm.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    # 무한대 값 처리
                    df_norm[col] = df_norm[col].replace([np.inf, -np.inf], np.nan)
                    # 0으로 나누기 방지
                    df_norm[col] = df_norm[col].fillna(0)
                
                normalized[key] = df_norm
            
            logger.info("재무제표 데이터 정규화 완료")
            return normalized
            
        except Exception as e:
            logger.error(f"재무제표 데이터 정규화 실패: {e}")
            return financial_data



