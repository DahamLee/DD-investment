#!/usr/bin/env python
# coding: utf-8

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
import pandas as pd
import FinanceDataReader as fdr
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.cluster import AgglomerativeClustering
from dotenv import load_dotenv

# .env.local 파일 로드 (없으면 .env 파일 사용)
# 현재 파일 위치: backend/app/etl/kr_stock_data/[6] SQLTest.py
# .env.local 위치: backend/.env.local (프로젝트 루트 기준)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
env_local_path = os.path.join(backend_dir, '.env.local')
env_path = os.path.join(backend_dir, '.env')

if os.path.exists(env_local_path):
    load_dotenv(env_local_path)
elif os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 현재 디렉토리에서 찾기
    load_dotenv()

# 환경 변수에서 DB 설정 가져오기
host = os.getenv("DATABASE_HOST", "121.134.7.122")
port = os.getenv("DATABASE_PORT", "5432")
dbname = os.getenv("DATABASE_NAME", "finance_db")
user = os.getenv("DATABASE_USER", "postgres")
password = os.getenv("DATABASE_PASSWORD", "")


def connect_to_sql(host, port, dbname, user, password):
    """PostgreSQL 데이터베이스 연결"""
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    return conn


# 전역 DB 연결 (필요시 사용)
conn = None
cur = None

def get_db_connection():
    """DB 연결 반환 (싱글톤 패턴)"""
    global conn
    if conn is None or conn.closed:
        conn = connect_to_sql(host, port, dbname, user, password)
    return conn


# In[5]:


#query를 통해 모든 데이터가 아닌 특정 항목 데이터 가져오기
def get_fs_pct_change(target_fs_code, 과거기준, db_conn=None):#과거기준은 0일경우 전기 대비, 1일경우 전년 동기 대비
    if db_conn is None:
        db_conn = get_db_connection()
    target_df=pd.read_sql_query("SELECT * FROM test_table where fs_code = '{}'".format(target_fs_code), db_conn)
    pct_change_list=[]
    new_col_name=["전기대비","전년동기대비"][과거기준]
    for stock_code in target_df.stock_code.unique():
        partial_df=target_df[target_df["stock_code"]==stock_code]
        if 과거기준==0: #전기대비
            for prev,now in zip(partial_df["값"].shift(1),partial_df["값"]):
                if (prev==np.nan) or (prev*now==0):
                    append_value=np.nan
                #흑자 전환시 변화율 계산이 어려움
                #100%이상 변화 시 -100%를 적용 그 이하일 경우 절반으로 나누는 우리만의 기준 세움
                elif prev<0 and now>0:
                    append_value=(now/prev*-1)
                    if append_value>1:
                        append_value-=1
                    else:
                        append_value=append_value/2
                else:
                    append_value=(now/prev)-1
                pct_change_list.append(append_value)
                
        elif 과거기준 ==1: #전년동기 대비
            #년도와 분기를 다 통일했기 때문에 shift4를 써서 한번에 계산 가능
            for prev,now in zip(partial_df["값"].shift(4),partial_df["값"]):
                if (prev==np.nan) or (prev*now==0):
                    append_value=np.nan
                #흑자 전환시 변화율 계산이 어려움
                #100%이상 변화 시 -100%를 적용 그 이하일 경우 절반으로 나누는 우리만의 기준 세움
                elif prev<0 and now>0:
                    append_value=(now/prev*-1)
                    if append_value>1:
                        append_value-=1
                    else:
                        append_value=append_value/2
                else:
                    append_value=(now/prev)-1
                pct_change_list.append(append_value)
                 
        else:
            print("올바른 옵션을 선택해주세요")
            break
    target_df[new_col_name]=pct_change_list
    return target_df


# In[30]:


def clustering_score(X, labels, alpha=0.7):
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


# In[32]:


def get_fs_score(target_fs_code, 과거기준, quarter, year, db_conn=None): #quarter는 string, year는 int
    if db_conn is None:
        db_conn = get_db_connection()
    fs_df=get_fs_pct_change(target_fs_code, 과거기준, db_conn)
    partial_nic=fs_df[(fs_df["quarter"]==quarter)&(fs_df["year"]==year)].copy(()).dropna()
    if 과거기준==0:
        nic_test_val=partial_nic.loc[:,["전기대비"]]
    else:
        nic_test_val=partial_nic.loc[:,["전년동기대비"]]
    
    X=np.array(nic_test_val).reshape(-1, 1)
    kmeans = KMeans(n_clusters=10)
    kmeans_results=kmeans.fit_predict(X)
    gmm = GaussianMixture(n_components=10).fit_predict(X)
    agg = AgglomerativeClustering(n_clusters=10, linkage='ward').fit_predict(X)
    
    nic_test_val["kmeans"]=kmeans_results
    nic_test_val["gaussian"]=gmm
    nic_test_val["agllomerative"]=agg
    
    kmeans_score=clustering_score(nic_test_val.iloc[:,0],nic_test_val.iloc[:,1],alpha=0.5)
    gmm_score=clustering_score(nic_test_val.iloc[:,0],nic_test_val.iloc[:,2],alpha=0.5)
    agglo_score=clustering_score(nic_test_val.iloc[:,0],nic_test_val.iloc[:,3],alpha=0.5)
    
    final_clustering_score_dict={"kmeans":kmeans_score[0],"gaussian":gmm_score[0],"agllomerative":agglo_score[0]}
    best_clustering_method=min(final_clustering_score_dict, key=final_clustering_score_dict.get)
    
    #가장 적합한 clustering method 찾아 df완성
    to_be_removed_method=list(final_clustering_score_dict.keys())
    to_be_removed_method.remove(best_clustering_method)
    nic_test_val.drop(to_be_removed_method, axis=1, inplace=True)
    
    #클러스터의 평균값에 따라 점수를 mapping해야함
    mapping_df=nic_test_val.groupby(by=best_clustering_method).mean().sort_values(by="전기대비",ascending=True).reset_index()
    mapping_df.index+=1
    mapping_dict=mapping_df.iloc[:,0].to_dict()
    swapped_dict = {value: key for key, value in mapping_dict.items()}
    nic_test_val["score"]=nic_test_val[best_clustering_method].replace(swapped_dict)
    
    final_score=pd.merge(partial_nic, nic_test_val["score"], left_index=True, right_index=True)
    return final_score


# 테스트 코드 (직접 실행 시에만 실행)
if __name__ == "__main__":
    target_fs_code="당기순이익"
    과거기준=0 #과거기준은 0일경우 전기 대비, 1일경우 전년 동기 대비
    quarter="Q2"
    year=2025
    test=get_fs_score(target_fs_code,과거기준,quarter,year)
    test_sorted = test.sort_values(by='score')
    print(test_sorted)