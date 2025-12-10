#!/usr/bin/env python
# coding: utf-8

# # 필요라이브러리 호출

# In[ ]:


import numpy as np
import FinanceDataReader as fdr
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


# In[ ]:


# 내 로컬 저장소
root_directory="E:\\DD Investment\\"
# API키
auth_key="5d09c83e072daf5ba841843927199d76fb7fc200"


# # 한국 주식 종목코드 가져오기 - FDR.datareader 라이브러리 사용
# 
# ## 코스피, 코스닥 (코넥스 제외)

# In[ ]:


Kospi_stocks=fdr.StockListing('KOSPI').set_index('Code')
Kosdaq_stocks=fdr.StockListing('KOSDAQ').set_index('Code')
한국주식종목=pd.concat([Kospi_stocks,Kosdaq_stocks])


# # 다트에서 종목코드로 고유코드 찾아 로컬에 저장하기

# In[ ]:


## 다트에서의 종목 고유 번호 가져오기
url_comp_code = "https://opendart.fss.or.kr/api/corpCode.xml"
params_comp_code = {
    "crtfc_key": auth_key,
}
resp_comp_code = requests.get(url_comp_code, params=params_comp_code)
if resp_comp_code.status_code!=200:
    raise Exception(f"[HTTP 오류]: 오류코드 :{resp_comp_code.status_code}")
    
zip_data = BytesIO(resp_comp_code.content)

with zipfile.ZipFile(zip_data, 'r') as zf:
    with zf.open('CORPCODE.xml') as xml_file:
        xml_string = xml_file.read().decode('utf-8') # UTF-8 인코딩으로 읽기

#호출 가능 데이터로 변환
root_comp_code=ET.fromstring(xml_string) 


# In[ ]:


종목코드_dict={}
한국주식종목_종목코드=list(한국주식종목.index)
for item in root_comp_code.findall("list"):
    #상장여부 확인
    stock_code=item.findtext("stock_code")
    if (stock_code!=" ")&(stock_code in 한국주식종목_종목코드):
        고유코드=item.findtext("corp_code") #다트에서 사용하는 종목 별 고유코드
        기업이름=item.findtext("corp_name")
        기업영어이름=item.findtext("corp_eng_name")
        종목코드_dict[stock_code]={"고유코드":고유코드,"기업이름":기업이름, "기업영어이름":기업영어이름}
    else:
        continue
# 종목코드의 length가 코스피+코스닥 종목코드 length보다 작은 이유는 우량주 주식을 배제했기 때문
고유코드_df=pd.DataFrame.from_dict(종목코드_dict,orient='index')   


# In[ ]:


다트고유코드_Final_df=pd.merge(고유코드_df, 한국주식종목,left_index=True, right_index=True, how='left')
if len(다트고유코드_Final_df)==len(고유코드_df):
    print("Error 없이 DataFrame생성 완료")
    다트고유코드_Final_df.to_csv(root_directory+"종목고유번호(다트).csv",encoding="cp949")
else:
    print("Error 발생")

