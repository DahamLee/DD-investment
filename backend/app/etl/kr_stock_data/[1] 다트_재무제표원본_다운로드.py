#!/usr/bin/env python
# coding: utf-8

# # 필요라이브러리 호출

# In[1]:


import numpy as np
from datetime import datetime,timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta
import requests
import zipfile
import xml.etree.ElementTree as ET
import io
from io import BytesIO
from tqdm import tqdm
import re
import os
import time


# # 종목 고유코드 데이터 불러오기
# 
# ## 다트에서는 종목주식코드가 아닌 고유코드를 사용해서 호출해야 함

# In[2]:


# 내 로컬 저장소
root_directory="E:\\DD Investment\\"
# API키
auth_key="5d09c83e072daf5ba841843927199d76fb7fc200"


# In[3]:


#추가 정보들 제외하고 주요 정보들만 가져오기
Dart_Code=pd.read_csv(root_directory+"종목고유번호(다트).csv",encoding="cp949",index_col=0,usecols=[0,1,5,6],dtype=object)


# In[4]:


def get_financial_statements(고유코드,auth_key):
    results=[]
    year_range=[i for i in range(2015,datetime.today().year+1)] #2015년 이후 데이터만 제공
    quarter_range=["11013","11012","11014","11011"]
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.xml"
    테스트종목=고유코드

    for year in year_range:
        for quarter in quarter_range:
            params = {
            "crtfc_key": auth_key,
            "corp_code": 테스트종목,
            "bsns_year": year,  # date순 정렬
            "reprt_code": quarter, #1분기: 11013, 반기: 11012, 3분기: 11014, 사업보고서: 11011
            "fs_div":"OFS" #증권사 제공 데이터는 연결 우리는 개별데이터 사용    
            }

            resp = requests.get(url, params=params)
            root=ET.fromstring(resp.content) 
            for item in root.findall("list"):
                if item.findtext("sj_div")!="SCE":
                    #계정명 pre 통일
                    계정명=item.findtext("account_nm").replace("(손실)", "").replace(" ", "")
                    if (계정명=="매출채권및기타유동채권") or (계정명=="매출채권및기타유동채권"):
                        계정명="매출채권"
                    data={
                        "등록일":item.findtext("rcept_no")[:8],
                        "당기명":item.findtext("thstrm_nm"),
                        "재무제표구분":item.findtext("sj_div"),
                        "재무제표이름":item.findtext("sj_nm"),
                        "계정코드":item.findtext("account_id").replace("-full", ""),#계정코드 통일을 위해 full부분 제거
                        "계정명":계정명,
                        "당기금액":item.findtext("thstrm_amount")#누적은 thstrm_add_amount
                    }
                    results.append(data)
    return pd.DataFrame(results)



# In[5]:


#개별재무제표 여부 확인
#OFS 개별재무제표가 없는 종목들은 일단 제외하기 위해서

def check_have_OFS(고유코드,auth_key):
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.xml"
    params = {
            "crtfc_key": auth_key,
            "corp_code": 고유코드,
            "bsns_year": datetime.today().year,  # date순 정렬
            "reprt_code": "11013", #1분기: 11013, 반기: 11012, 3분기: 11014, 사업보고서: 11011
            "fs_div":"OFS" #증권사 제공 데이터는 연결 우리는 개별데이터 사용    
            }
    resp = requests.get(url, params=params)
    root=ET.fromstring(resp.content) 
    error_message=root.findtext("status")
    return error_message


# In[7]:


#개별 종목의 재무정보 불러오기 하루 2만건 제한 400종목 대략
#check if directory contians filename
directory = root_directory+"종목_개별재무제표(unrefined)\\"
downloaded_code= [i[-12:-4] for i in os.listdir(directory)]

#개별 종목의 재무정보 불러오기 (1번키 막힌경우)
auth_key2="1ee5c5377c169ffa9b97aab2b5fe422ddc6dbb6a"
auth_key=auth_key2 #1번 코드가 막힌 경우

for 다트코드,종목명,종목코드 in tqdm(zip(Dart_Code["고유코드"],Dart_Code["Name"],Dart_Code.index)):
    if (다트코드 in downloaded_code): 
        continue
    
    elif ("스팩" in 종목명) and re.search('[0-9]', 종목명): #스펙주식 제거
        continue
        
    elif check_have_OFS(다트코드,auth_key)=="013": #013은 조회데이터가 없다는 에러코드
        #나중에 연결제무제표 저장시 따로 구축하면 됨
        continue
    else:
        #종목별 재무제표 불러오기
        stock_fs_df=get_financial_statements(다트코드,auth_key)
        if stock_fs_df.empty:
            print("API 사용한도 초과")
            break
        else:
            stock_fs_df.to_csv(root_directory+"종목_개별재무제표(unrefined)\\{}_{}_{}.csv".format(종목코드,종목명,다트코드),encoding="cp949")
            print("1")
    time.sleep(1)


