"""
SEC EDGAR API 데이터 추출 모듈

SEC EDGAR API를 사용하여 미국 주식 공시 데이터를 수집합니다.
- Company Facts (CIK, 티커 매핑)
- Filings (10-K, 10-Q, 8-K 등)
- XBRL 데이터
"""
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import settings

logger = logging.getLogger(__name__)


class SECDataFetcher:
    """
    SEC EDGAR API 데이터 추출 클래스
    
    SEC API는 rate limiting이 있으므로:
    - User-Agent 헤더 필수
    - 요청 간 딜레이 권장 (0.1초)
    - 공식 문서: https://www.sec.gov/edgar/sec-api-documentation
    """
    
    def __init__(self, user_agent: Optional[str] = None):
        """
        Args:
            user_agent: SEC API 요청 시 필수 User-Agent
                       형식: "CompanyName AdminContact@example.com"
        """
        self.base_url = "https://data.sec.gov"
        self.submissions_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        
        # User-Agent 필수 (없으면 403 에러)
        self.user_agent = user_agent or getattr(
            settings, 'sec_user_agent', 
            'DD Investment admin@ddinvestment.com'
        )
        
        # 세션 설정 (재시도 로직 포함)
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        })
        
        # Rate limiting을 위한 딜레이
        self.request_delay = 0.1  # 초
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        SEC API 요청 (rate limiting 고려)
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
        
        Returns:
            JSON 응답 또는 None
        """
        try:
            time.sleep(self.request_delay)  # Rate limiting
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SEC API 요청 실패: {url}, {e}")
            return None
    
    def fetch_company_tickers(self) -> Dict[str, Dict]:
        """
        SEC에서 제공하는 전체 회사 티커-CIK 매핑 조회
        
        Returns:
            Dict[ticker, {'cik': str, 'name': str, 'exchange': str}]
        
        참고: 이 엔드포인트는 매우 큰 파일이므로 주의 필요
        """
        try:
            logger.info("SEC Company Tickers 조회 시작")
            
            url = f"{self.base_url}/files/company_tickers.json"
            data = self._make_request(url)
            
            if not data:
                return {}
            
            # SEC 응답 형식: {"0": {"cik_str": ..., "ticker": ..., "title": ...}, ...}
            result = {}
            for key, value in data.items():
                if isinstance(value, dict) and 'ticker' in value:
                    ticker = value['ticker']
                    result[ticker] = {
                        'cik': str(value.get('cik_str', '')).zfill(10),  # CIK는 10자리
                        'name': value.get('title', ''),
                        'exchange': value.get('exchange', '')
                    }
            
            logger.info(f"SEC Company Tickers 조회 완료: {len(result)}개")
            return result
            
        except Exception as e:
            logger.error(f"SEC Company Tickers 조회 실패: {e}")
            return {}
    
    def fetch_company_facts(self, cik: str) -> Optional[Dict]:
        """
        SEC Company Facts 데이터 조회
        
        Args:
            cik: Central Index Key (10자리, 앞에 0 패딩)
        
        Returns:
            Company Facts JSON 데이터
        """
        try:
            logger.info(f"SEC Company Facts 조회 시작: CIK={cik}")
            
            # CIK를 10자리로 패딩
            cik_padded = str(cik).zfill(10)
            url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik_padded}.json"
            
            data = self._make_request(url)
            
            if data:
                logger.info(f"SEC Company Facts 조회 완료: CIK={cik}")
            
            return data
            
        except Exception as e:
            logger.error(f"SEC Company Facts 조회 실패: CIK={cik}, {e}")
            return None
    
    def fetch_company_submissions(self, cik: str) -> Optional[Dict]:
        """
        회사의 제출물(Submissions) 목록 조회
        
        Args:
            cik: Central Index Key
        
        Returns:
            Submissions JSON 데이터 (filings 리스트 포함)
        """
        try:
            logger.info(f"SEC Company Submissions 조회 시작: CIK={cik}")
            
            cik_padded = str(cik).zfill(10)
            url = f"{self.base_url}/submissions/CIK{cik_padded}.json"
            
            data = self._make_request(url)
            
            if data:
                logger.info(f"SEC Company Submissions 조회 완료: CIK={cik}")
            
            return data
            
        except Exception as e:
            logger.error(f"SEC Company Submissions 조회 실패: CIK={cik}, {e}")
            return None
    
    def fetch_filings(
        self,
        cik: str,
        form_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        특정 회사의 공시(Filings) 목록 조회
        
        Args:
            cik: Central Index Key
            form_type: 공시 유형 (10-K, 10-Q, 8-K 등, None이면 전체)
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        
        Returns:
            Filings 리스트
        """
        try:
            logger.info(f"SEC Filings 조회 시작: CIK={cik}, form={form_type}")
            
            # Submissions에서 filings 추출
            submissions = self.fetch_company_submissions(cik)
            if not submissions or 'filings' not in submissions:
                return []
            
            filings = submissions['filings']['recent']
            
            # 필터링
            result = []
            for i in range(len(filings.get('form', []))):
                form = filings['form'][i]
                
                # Form 타입 필터
                if form_type and form != form_type:
                    continue
                
                # 날짜 필터
                filing_date = filings.get('filingDate', [])[i] if 'filingDate' in filings else None
                if filing_date:
                    if start_date and filing_date < start_date:
                        continue
                    if end_date and filing_date > end_date:
                        continue
                
                # 결과 구성
                filing_data = {
                    'form': form,
                    'filingDate': filing_date,
                    'reportDate': filings.get('reportDate', [])[i] if 'reportDate' in filings else None,
                    'accessionNumber': filings.get('accessionNumber', [])[i] if 'accessionNumber' in filings else None,
                    'description': filings.get('description', [])[i] if 'description' in filings else None,
                }
                
                # 문서 링크 생성
                if filing_data['accessionNumber']:
                    acc_no = filing_data['accessionNumber'].replace('-', '')
                    filing_data['documentUrl'] = (
                        f"https://www.sec.gov/cgi-bin/viewer?action=view"
                        f"&cik={cik}&accession_number={filing_data['accessionNumber']}"
                        f"&xbrl_type=v"
                    )
                
                result.append(filing_data)
            
            logger.info(f"SEC Filings 조회 완료: CIK={cik}, {len(result)}개")
            return result
            
        except Exception as e:
            logger.error(f"SEC Filings 조회 실패: CIK={cik}, {e}")
            return []
    
    def fetch_ticker_to_cik(self, ticker: str) -> Optional[str]:
        """
        티커로 CIK 조회
        
        Args:
            ticker: 주식 티커 (예: "AAPL")
        
        Returns:
            CIK (10자리 문자열) 또는 None
        """
        try:
            # Company Tickers에서 조회
            tickers_map = self.fetch_company_tickers()
            
            ticker_upper = ticker.upper()
            if ticker_upper in tickers_map:
                return tickers_map[ticker_upper]['cik']
            
            logger.warning(f"티커에 해당하는 CIK를 찾을 수 없음: {ticker}")
            return None
            
        except Exception as e:
            logger.error(f"티커-CIK 조회 실패: {ticker}, {e}")
            return None
    
    def fetch_multiple_companies_filings(
        self,
        tickers: List[str],
        form_types: Optional[List[str]] = None,
        days_back: int = 90
    ) -> Dict[str, List[Dict]]:
        """
        여러 회사의 공시 데이터 일괄 조회
        
        Args:
            tickers: 티커 리스트
            form_types: 공시 유형 리스트 (None이면 10-K, 10-Q, 8-K)
            days_back: 최근 N일 데이터만 조회
        
        Returns:
            Dict[ticker, List[filings]]
        """
        if form_types is None:
            form_types = ['10-K', '10-Q', '8-K']
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        results = {}
        
        for ticker in tickers:
            try:
                cik = self.fetch_ticker_to_cik(ticker)
                if not cik:
                    logger.warning(f"티커 {ticker}의 CIK를 찾을 수 없음")
                    continue
                
                filings = []
                for form_type in form_types:
                    ticker_filings = self.fetch_filings(
                        cik, form_type, start_date, end_date
                    )
                    filings.extend(ticker_filings)
                
                results[ticker] = filings
                
            except Exception as e:
                logger.error(f"티커 {ticker} 공시 조회 실패: {e}")
                continue
        
        return results

