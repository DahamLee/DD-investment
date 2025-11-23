import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
import pandas as pd
import FinanceDataReader as fdr

# host="34.64.149.167"
host="121.134.7.122"
port="5432"
dbname="finance_db"
user="postgres"
password="ekgkaehddudABC123!"

# DB 연결
conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=dbname,
    user=user,
    password=password
)
cur = conn.cursor()

# 1) 기존 테이블 삭제 후 새로 생성
drop_query = "DROP TABLE IF EXISTS test_table;"
create_query = """
CREATE TABLE test_table (
    code   varchar not null,
    isu_cd varchar not null,
    name   varchar not null,
    market varchar not null
)
"""
cur.execute(drop_query)
cur.execute(create_query)
conn.commit()

# 2) 단일 INSERT 예시
insert_query = """
INSERT INTO test_table (code, isu_cd, name, market) VALUES (%s, %s, %s, %s)
"""
params = (1111, 'aa', 'bb', 'cc')
cur.execute(insert_query, params)
conn.commit()

# 3) 판다스로 bulk insert
df_krx = fdr.StockListing('KRX')
df = df_krx[['Code', 'ISU_CD', 'Name', 'Market']]
df.columns = df.columns.str.lower()

# DataFrame → list of tuples
values = [tuple(x) for x in df.to_numpy()]
columns = ','.join(df.columns)

# bulk insert 쿼리
insert_query = f"INSERT INTO test_table ({columns}) VALUES %s"

# bulk insert 실행
execute_values(cur, insert_query, values)
conn.commit()

print("✅ 데이터 삽입 완료")

# 2) 데이터 조회
df_result = pd.read_sql("SELECT * FROM test_table LIMIT 10;", conn)
print(df_result)

cur.close()
conn.close()