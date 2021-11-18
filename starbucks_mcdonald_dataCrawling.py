#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings(action='ignore')
import requests
import time
import folium
from pandas.io.json import json_normalize
import pandas as pd
from selenium import webdriver
driver = webdriver.Chrome("./chromedriver.exe")


# 1. 스타벅스 크롤링

# In[2]:


url = 'https://www.starbucks.co.kr/store/getSidoList.do'
request = requests.post(url)
starbucks = request.json()
sido_List = {}
for sido in starbucks['list']:
    sido_List[sido['sido_cd']] =  sido['sido_nm']
print(sido_List)


# In[3]:


sido_cd = input('구군코드를 검색하려는 시도코드를 입력하세요: ')
targetSite = 'https://www.starbucks.co.kr/store/getGugunList.do'
request = requests.post(targetSite, data={
    'sido_cd': sido_cd
})
gugunList = request.json()
gugun_List = {}
for gugun in gugunList['list']:
    gugun_List[gugun['gugun_cd']] = gugun['gugun_nm']
print(gugun_List)


# In[4]:


# 지역별 DT 스타벅스 전 지점
targetSite = 'https://www.starbucks.co.kr/store/getStore.do?r=BF1GQPNI9E'
request = requests.post(targetSite, data={
    'ins_lat': 37.5108295,
    'ins_lng': 127.0292881,
    'p_sido_cd': sido_cd,
    'p_gugun_cd': '',
    'in_biz_cd': '',
    'iend': 1600,
    'set_date': ''
})
starbucks = request.json()
starbucks_df = json_normalize(starbucks, 'list')
starbucks_df_map = starbucks_df[['s_name', 'sido_code', 'sido_name', 'gugun_code', 'gugun_name',  'lat', 'lot']]

starbucks_df_map['lat'] = starbucks_df_map['lat'].astype(float)
starbucks_df_map['lot'] = starbucks_df_map['lot'].astype(float)

starbucks_map = folium.Map(location=[starbucks_df_map['lat'].mean(), starbucks_df_map['lot'].mean()], zoom_start=11)
count = 0 # DT 점 수 구하기
for index, data in starbucks_df_map.iterrows():
    if data['s_name'].find('DT') > 0:
        count += 1
#         pop = folium.Popup(data['s_name'] + '점, 주소: ' + data['doro_address'], max_width=500)
        pop = folium.Popup(data['s_name'] + '점' , max_width=500)
        
        folium.Marker(location=[data['lat'], data['lot']], popup=pop,  icon=folium.Icon(color='green', icon='star')).add_to(starbucks_map)
# starbucks_map.save('./starMap.html')
print(count)
starbucks_map


# 2. 맥도날드 크롤링

# In[5]:


url = "https://www.mcdonalds.co.kr/kor/store/list.do"
driver.get(url)


# In[10]:


# 맥도날드 DT점 데이터
mac_data = []
# 지역의 구군 개수만큼 반복해서 HTML 코드 안에서 DT 점에 관한 정보 찾기
for gu in gugun_List.values(): # 스타벅스 구군 데이터 재활용
    print(gu)
    try:
        driver.find_element_by_css_selector("#searchWord").clear()
    except:
        pass
    driver.find_element_by_css_selector("#searchWord").send_keys(gu) # 검색어 입력
    driver.find_element_by_css_selector("#searchForm > div > div > div > span:nth-child(2) > label").click()  # 맥드라이브 버튼 클릭
    driver.find_element_by_css_selector("#searchForm > div > fieldset > div > button").click() # 검색버튼 클릭
    time.sleep(1)
    
    # 매장 데이터를 담아준다.
    dt_list=driver.find_elements_by_css_selector("#container > div.content > div.contArea > div > div > div.mcStore > table > tbody > tr")
    
    # 가져온 매장 데이터 중에서 필요한 데이터를 추출
    for data in dt_list:
        tmp = data.find_element_by_css_selector("td.tdName > dl > dt > strong > a") # 전체 url
        lat,lng = tmp.get_attribute("href")[19:-2].split(",") # 위도 경도 인덱싱
        title = tmp.text 
        text = data.text # 매장에 관한 모든 내용을 담아둠 '맥드라이브' 키워드 가져오기 위해서 필요
        
        # 구군을 검색한 내용을 바탕으로 시도명도 같고, '맥드라이브'인 자료를 받아온다.
        # sido_List.get(sido_cd) 시도 코드를 key 값으로함(스타벅스 코드 사용)
        if(sido_List.get(sido_cd) in text and "맥드라이브" in text): 
            mac_data.append({
                "title":title,
                "lat":lat,
                "lng":lng
            })
# 찾은 정보를 데이터프레임에 담기
mac_df = pd.DataFrame(mac_data)

# 데이터 가공
mac_df['lat'] = mac_df['lat'].astype(float) # 위도 => float로 변경
mac_df['lng'] = mac_df['lng'].astype(float) # 경도 => float로 변경
mac_map = folium.Map(location=[mac_df['lat'].mean(), mac_df['lng'].mean()], zoom_start=11)
# DT점 수 세는 변수
count = 0;
# 반복을 돌면서 지도에 위치를 표시 => 데이터 시각화
for index, data in mac_df.iterrows():
    count += 1
    pop = folium.Popup(data['title'] + '점', max_width=500)
    folium.Marker(location=[data['lat'], data['lng']], popup=pop, icon=folium.Icon(color='red', icon='star')).add_to(mac_map)
print(count)
mac_map


# In[7]:


mac_df


# In[8]:


starbucks_df_map


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




