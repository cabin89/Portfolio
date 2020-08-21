from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re


#로그인, 탐색계정
usr_ID = ''
usr_PWD = ''
baseUrl = 'https://www.instagram.com/'
plusUrl = '' #크롤링할 계정명
url = baseUrl + plusUrl

driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get('https://www.instagram.com/')
time.sleep(2)
assert "Instagram" in driver.title
driver.find_element_by_name('username').send_keys(usr_ID)
driver.find_element_by_name('password').send_keys(usr_PWD)
driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div[4]/button').click()
time.sleep(2)


#헤더에 유저정보 바꿔서 사람인 척 하기
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
html = requests.get(url, headers = headers).text

driver.get(url)
time.sleep(2)

body = driver.find_element_by_tag_name("body")

result_posting_adress = []
list_hashtag = []
html = driver.page_source
soup = BeautifulSoup(html, features="lxml")


#스크롤다운, result_posting_adress에 URL추가
for i in range(1): #( )안에 스크롤 반복횟수 입력
    insta = soup.select(".v1Nh3.kIKUG._bz0w")
    body.send_keys(Keys.END)
    time.sleep(0.5)
    for i in insta:
        result_posting_adress.append('https://www.instagram.com/' +i.a['href'])
        # list(set(map(tuple,result_posting_adress)))#중복제거


for i in result_posting_adress:
    driver.get(i)
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    time.sleep(2)
    hashtag = soup.select('.xil3i')
    for i in hashtag:
        hashtag_final = i.text
        list_hashtag.append(hashtag_final)

# print(list_hashtag)

with open("insta_hashtag.csv", "w") as f:
    for i in range(len(list_hashtag)):
        hashtag_info = list_hashtag[i] + "\n"
        f.write(hashtag_info)

driver.close()
