"""
재무제표 서비스
[6] SQLTest.py의 로직을 서비스 레이어로 분리
"""
import os
import logging
import psycopg2
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import AgglomerativeClustering
from dotenv import load_dotenv
from typing import Optional

logger = logging.getLogger(__name__)

# .env.local 파일 로드 (없으면 .env 파일 사용)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))  # backend/ 디렉토리
env_local_path = os.path.join(backend_dir, '.env.local')
env_path = os.path.join(backend_dir, '.env')

if os.path.exists(env_local_path):
    load_dotenv(env_local_path, override=True)
elif os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

# 환경 변수에서 DB 설정 가져오기
DATABASE_HOST = os.getenv("DATABASE_HOST", "121.134.7.122")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "finance_db")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")


class FinancialStatementService:
    """재무제표 서비스"""
    
    def __init__(self):
        self.conn = None
    
    def _get_db_connection(self):
        """DB 연결 반환 (싱글톤 패턴)"""
        try:
            if self.conn is None or self.conn.closed:
                logger.info(f"DB 연결 시도: host={DATABASE_HOST}, port={DATABASE_PORT}, dbname={DATABASE_NAME}, user={DATABASE_USER}")
                self.conn = psycopg2.connect(
                    host=DATABASE_HOST,
                    port=DATABASE_PORT,
                    dbname=DATABASE_NAME,
                    user=DATABASE_USER,
                    password=DATABASE_PASSWORD
                )
                logger.info("DB 연결 성공")
            return self.conn
        except Exception as e:
            logger.error(f"DB 연결 실패: {str(e)}")
            raise
    
    def close(self):
        """DB 연결 종료"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            self.conn = None
    
    def get_fs_pct_change(self, target_fs_code: str, 과거기준: int, db_conn: Optional[psycopg2.extensions.connection] = None):
        """
        재무제표 변화율 계산
        
        Args:
            target_fs_code: 재무제표 코드 (예: "당기순이익")
            과거기준: 0일 경우 전기 대비, 1일 경우 전년 동기 대비
            db_conn: DB 연결 (None이면 자동으로 연결)
        
        Returns:
            DataFrame: 변화율이 추가된 재무제표 데이터
        """
        if db_conn is None:
            db_conn = self._get_db_connection()
        
        query = "SELECT * FROM test_table where fs_code = '{}'".format(target_fs_code)
        logger.info(f"SQL 쿼리 실행: {query}")
        
        try:
            target_df = pd.read_sql_query(query, db_conn)
            logger.info(f"조회된 데이터 행 수: {len(target_df)}")
            
            if len(target_df) == 0:
                logger.warning(f"데이터가 없습니다: fs_code={target_fs_code}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"SQL 쿼리 실행 실패: {str(e)}")
            raise
        pct_change_list = []
        new_col_name = ["전기대비", "전년동기대비"][과거기준]
        
        for stock_code in target_df.stock_code.unique():
            partial_df = target_df[target_df["stock_code"] == stock_code]
            
            if 과거기준 == 0:  # 전기대비
                for prev, now in zip(partial_df["값"].shift(1), partial_df["값"]):
                    if (prev == np.nan) or (prev * now == 0):
                        append_value = np.nan
                    # 흑자 전환시 변화율 계산이 어려움
                    # 100%이상 변화 시 -100%를 적용 그 이하일 경우 절반으로 나누는 우리만의 기준 세움
                    elif prev < 0 and now > 0:
                        append_value = (now / prev * -1)
                        if append_value > 1:
                            append_value -= 1
                        else:
                            append_value = append_value / 2
                    else:
                        append_value = (now / prev) - 1
                    pct_change_list.append(append_value)
                    
            elif 과거기준 == 1:  # 전년동기 대비
                # 년도와 분기를 다 통일했기 때문에 shift4를 써서 한번에 계산 가능
                for prev, now in zip(partial_df["값"].shift(4), partial_df["값"]):
                    if (prev == np.nan) or (prev * now == 0):
                        append_value = np.nan
                    # 흑자 전환시 변화율 계산이 어려움
                    # 100%이상 변화 시 -100%를 적용 그 이하일 경우 절반으로 나누는 우리만의 기준 세움
                    elif prev < 0 and now > 0:
                        append_value = (now / prev * -1)
                        if append_value > 1:
                            append_value -= 1
                        else:
                            append_value = append_value / 2
                    else:
                        append_value = (now / prev) - 1
                    pct_change_list.append(append_value)
            else:
                raise ValueError("올바른 옵션을 선택해주세요 (0: 전기대비, 1: 전년동기대비)")
        
        target_df[new_col_name] = pct_change_list
        return target_df
    
    def clustering_score(self, X, labels, alpha=0.7):
        """
        클러스터링 점수 계산
        
        Args:
            X: 데이터 포인트
            labels: 클러스터 레이블
            alpha: 응집도 가중치 (기본값 0.7)
        
        Returns:
            tuple: (통합 점수, 응집도, 균형도)
        """
        X = np.array(X)
        labels = np.array(labels)
        unique_labels = np.unique(labels)
        
        # noise (-1) 제거 (DBSCAN 대응)
        unique_labels = unique_labels[unique_labels >= 0]
        if len(unique_labels) <= 1:
            return np.nan, np.nan, np.nan  # 클러스터가 1개 이하이면 평가 불가
        
        overall_var = np.var(X)
        
        # 1. 응집도 (WCSS / Var)
        wcss = 0
        for k in unique_labels:
            cluster_points = X[labels == k]
            wcss += np.mean((cluster_points - cluster_points.mean())**2)
        cohesion = wcss / overall_var
        
        # 2. 균형도 (클러스터 크기 편차)
        sizes = np.array([np.sum(labels == k) for k in unique_labels])
        mean_size = sizes.mean()
        balance = np.mean(((sizes - mean_size)/mean_size)**2)/len(unique_labels)
        
        # 3. 통합 점수
        score = alpha * cohesion + (1 - alpha) * balance
        return score, cohesion, balance
    
    def get_fs_score(self, target_fs_code: str, 과거기준: int, quarter: str, year: int, db_conn: Optional[psycopg2.extensions.connection] = None):
        """
        재무제표 점수 계산 (클러스터링 기반)
        
        Args:
            target_fs_code: 재무제표 코드 (예: "당기순이익")
            과거기준: 0일 경우 전기 대비, 1일 경우 전년 동기 대비
            quarter: 분기 (예: "Q1", "Q2", "Q3", "Q4")
            year: 연도 (예: 2025)
            db_conn: DB 연결 (None이면 자동으로 연결)
        
        Returns:
            DataFrame: 점수가 추가된 재무제표 데이터
        """
        if db_conn is None:
            db_conn = self._get_db_connection()
        
        try:
            fs_df = self.get_fs_pct_change(target_fs_code, 과거기준, db_conn)
            
            if fs_df.empty:
                logger.warning(f"재무제표 변화율 데이터가 없습니다: fs_code={target_fs_code}")
                return pd.DataFrame()
            
            partial_nic = fs_df[(fs_df["quarter"] == quarter) & (fs_df["year"] == year)].copy().dropna()
            logger.info(f"필터링 후 데이터 행 수: quarter={quarter}, year={year}, rows={len(partial_nic)}")
            
            if len(partial_nic) == 0:
                logger.warning(f"해당 분기/연도 데이터가 없습니다: quarter={quarter}, year={year}")
                return pd.DataFrame()  # 데이터가 없으면 빈 DataFrame 반환
        except Exception as e:
            logger.error(f"재무제표 변화율 계산 실패: {str(e)}")
            raise
        
        if 과거기준 == 0:
            nic_test_val = partial_nic.loc[:, ["전기대비"]]
        else:
            nic_test_val = partial_nic.loc[:, ["전년동기대비"]]
        
        X = np.array(nic_test_val).reshape(-1, 1)
        kmeans = KMeans(n_clusters=10)
        kmeans_results = kmeans.fit_predict(X)
        gmm = GaussianMixture(n_components=10).fit_predict(X)
        agg = AgglomerativeClustering(n_clusters=10, linkage='ward').fit_predict(X)
        
        nic_test_val["kmeans"] = kmeans_results
        nic_test_val["gaussian"] = gmm
        nic_test_val["agllomerative"] = agg
        
        kmeans_score = self.clustering_score(nic_test_val.iloc[:, 0], nic_test_val.iloc[:, 1], alpha=0.5)
        gmm_score = self.clustering_score(nic_test_val.iloc[:, 0], nic_test_val.iloc[:, 2], alpha=0.5)
        agglo_score = self.clustering_score(nic_test_val.iloc[:, 0], nic_test_val.iloc[:, 3], alpha=0.5)
        
        final_clustering_score_dict = {
            "kmeans": kmeans_score[0],
            "gaussian": gmm_score[0],
            "agllomerative": agglo_score[0]
        }
        best_clustering_method = min(final_clustering_score_dict, key=final_clustering_score_dict.get)
        
        # 가장 적합한 clustering method 찾아 df완성
        to_be_removed_method = list(final_clustering_score_dict.keys())
        to_be_removed_method.remove(best_clustering_method)
        nic_test_val.drop(to_be_removed_method, axis=1, inplace=True)
        
        # 클러스터의 평균값에 따라 점수를 mapping해야함
        change_col = "전기대비" if 과거기준 == 0 else "전년동기대비"
        mapping_df = nic_test_val.groupby(by=best_clustering_method).mean().sort_values(by=change_col, ascending=True).reset_index()
        mapping_df.index += 1
        mapping_dict = mapping_df.iloc[:, 0].to_dict()
        swapped_dict = {value: key for key, value in mapping_dict.items()}
        nic_test_val["score"] = nic_test_val[best_clustering_method].replace(swapped_dict)
        
        final_score = pd.merge(partial_nic, nic_test_val["score"], left_index=True, right_index=True)
        return final_score

