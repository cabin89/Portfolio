from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

baseUrl = 'https://www.instagram.com/explore/tags/'
plusUrl = input('검색할 태그를 입력하세요 : ')
url = baseUrl + quote_plus(plusUrl)

driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get(url)

time.sleep(3) #3초 기다리게 하는 것 / 나중에 페이지 버튼 눌러서 매크로하거나 그럴 때 누르고 로딩시간 같은 텀을 주는 것

body = driver.find_element_by_tag_name("body")

result_posting_adress = []
result = []
html = driver.page_source
soup = BeautifulSoup(html, features="lxml")

#인스타 스크롤다운 result에 저장, 중복제거
for i in range(5):#( )안에 스크롤 반복횟수 입력
    insta = soup.select('.v1Nh3.kIKUG._bz0w')
    body.send_keys(Keys.END)
    time.sleep(0.5)
    for i in insta:
        result.append(i.select_one('.KL4Bh').img['src'])
        result_posting_adress.append('https://www.instagram.com' + i.a['href'])
        list(set(map(tuple,result)))#중복제거

print(insta)
#result 스크롤다운 누적 저장된 이미지를 반복해서 파일로 저장
n=1
for i in result:
    replace_i = i.replace("''","")
    with urlopen(replace_i) as f:
        with open('./img/' + plusUrl + str(n) + '.jpg', 'wb') as h:
            img = f.read()
            h.write(img)
    n += 1

#다운받은 이미지 주소와 경로를 csv 파일로
with open("./img/insta_img_url.csv", "w") as f:
    for i in range(len(result)):
        imginfo = result_posting_adress[i] + "\n" + result[i] + "\n"
        f.write(imginfo)



driver.close()
print('완료!')
