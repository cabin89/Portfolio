from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pandas as pd
import numpy as np
import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re


#타겟채널 (이곳에 채널명을 입력하시오)
Target_channel ='https://www.youtube.com/c/321RelaxingMeditationRelaxClips/featured'


url = Target_channel
driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get(Target_channel)
time.sleep(2)
assert "YouTube" in driver.title

driver.find_element_by_xpath('//*[@id="tabsContent"]/paper-tab[2]/div').click()

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
html = requests.get(url, headers = headers).text

body = driver.find_element_by_tag_name("body")

html = driver.page_source
soup = BeautifulSoup(html, features='lxml')




# 끝까지 스크롤
last_height = driver.execute_script("return document.documentElement.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
    # Wait to load page
    time.sleep(1)
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
       break
    last_height = new_height


#지정 횟수 스크롤
# for i in range(1): #( )안에 스크롤 반복횟수 입력
#     body.send_keys(Keys.END)
#     time.sleep(0.5)
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    #파싱 목록
    thumbnail = []
    all_thumbnail = soup.select('#thumbnail')
    for i in all_thumbnail:
        id = i.get('href')
        #replace 쓸때 바꾸려는 리스트에 None이 있으면 작동 안하므로 밑에 if문으로 정의해줘야 한다.
        if id == None:
            id = id
        else:
            id = id.replace('/watch?v=','')
        plus_id = ('https://i.ytimg.com/vi/{}/hqdefault.jpg'.format(id))
        thumbnail.append(plus_id)

    all_title = soup.find_all('a','yt-simple-endpoint style-scope ytd-grid-video-renderer')
    title = [soup.find_all('a','yt-simple-endpoint style-scope ytd-grid-video-renderer')[n].string for n in range(0,len(all_title))]

    video_url = []
    all_video_url = soup.select('#thumbnail')
    for i in all_video_url:
        url = i.get('href')
        #위의 경우처럼 url 리스트에 None 이 포함되어 if문으로 정의해준다.
        if url == None:
            url = url
        else:
            plus_url = 'https://www.youtube.com'
            url = (plus_url + url)
        video_url.append(url)

    all_running_time = soup.find_all('span', 'style-scope ytd-thumbnail-overlay-time-status-renderer')
    running_time = [soup.find_all('span', 'style-scope ytd-thumbnail-overlay-time-status-renderer')[n].string for n in range(0,len(all_running_time))]
    all_view = soup.find_all('a', {'id' : 'video-title'})
    view = [soup.find_all('a', {'id' : 'video-title'})[n].get('aria-label').split()[-2] for n in range(0,len(all_view))]
    all_upload_date = soup.select('#metadata-line > span:last-of-type')
    upload_date = [soup.select('#metadata-line > span:last-of-type')[n].string for n in range(0,len(all_upload_date))]

    #pandas DataFrame으로 전달
    insert_data = {'Thumbnail':thumbnail,
                 'Title':title,
                 'Video_url':video_url,
                 'Running_time':running_time,
                 'View':view,
                 'Upload_date':upload_date
                 }

    Youtube_Data = pd.DataFrame.from_dict(insert_data, orient='index')
    Youtube_Data.index.name = 'Num'
    Youtube_Data.columns.name = 'Info'
    Youtube_Data.transpose()



print(Youtube_Data.transpose())
#csv로 저장
Youtube_Data.transpose().to_csv('Youtube_Data.csv', mode='w', encoding='utf-8-sig')

#실시간 스트리밍이 중간에 있을 경우 직접 조정해줘야 한다.
driver.close()
