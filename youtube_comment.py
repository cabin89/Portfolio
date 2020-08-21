from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from openpyxl.workbook import Workbook
from konlpy.tag import Twitter

import pandas as pd
import numpy as np
import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re

# 명사추출함수
def get_noun(self):

    f = open('cleaned_comment.txt', 'r')
    cleaned_comment = f.read()

    from konlpy.tag import Twitter

    twitter = Twitter()
    noun = twitter.nouns(cleaned_comment)

    return noun




#타겟채널 (이곳에 채널명을 입력하시오)
Target_video ='https://www.youtube.com/watch?v=0M0xVtbZDcs'


url = Target_video
driver = webdriver.Chrome(executable_path='/Users/macintoshhd/Desktop/Coding/Python/chromedriver')
driver.get(Target_video)
time.sleep(2)

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
html = requests.get(url, headers = headers).text

body = driver.find_element_by_tag_name("body")

body.send_keys(Keys.PAGE_DOWN)
time.sleep(1)

# 스크롤 횟수 '()' 안에 횟수 지정
for i in range(1):
    body.send_keys(Keys.END)
    time.sleep(5)

html = driver.page_source
soup = BeautifulSoup(html, features='lxml')
# 데이터 크롤링
Channel_name = soup.select_one('#text > a').string
Sub_count = soup.find('yt-formatted-string', {'id' : 'owner-sub-count'}).string.replace('subscribers', '')
Title = soup.find('yt-formatted-string', 'style-scope ytd-video-primary-info-renderer').string
Click = soup.find('span', 'view-count style-scope yt-view-count-renderer').string.replace('views', '')
Upload_date = soup.select_one('#date > yt-formatted-string').string
Like_count = soup.select('yt-formatted-string[aria-label]')[0].get('aria-label').replace('likes','')
Dislike_count = soup.select('yt-formatted-string[aria-label]')[1].get('aria-label').replace('dislikes','')
Comment_count = soup.find('yt-formatted-string', {'class' : 'count-text style-scope ytd-comments-header-renderer'}).string.replace('Comments','')

all_user_id = soup.select('#author-text > span')
User_id = [soup.select('#author-text > span')[n].string.strip() for n in range(0, len(all_user_id))]
all_comments = soup.select('#content-text')
Comments = [soup.select('#content-text')[n].get_text().replace('\n', '') for n in range(0, len(all_comments))]
all_comments_likes = soup.find_all('span', {'id' : 'vote-count-middle'})
Comments_likes = [soup.find_all('span', {'id' : 'vote-count-middle'})[n].string.strip() for n in range(0, len(all_comments_likes))]

# 데이터프레임 생성
insert_video_data = {'Channel_name' : Channel_name,
                    'Sub_count' : Sub_count,
                    'Title' : Title,
                    'Click' : Click,
                    'Upload_date' : Upload_date,
                    'Like_count' : Like_count,
                    'Dislike_count' : Dislike_count,
                    'Comment_count' : Comment_count,
}
insert_Comments_data = {'User_id' : User_id,
                        'Comments' : Comments,
                        'Likes' : Comments_likes,
}

Video_data = pd.DataFrame.from_dict(insert_video_data, orient='index')
Video_data.index.name = 'Info'
Comments_data = pd.DataFrame.from_dict(insert_Comments_data, orient='index')
Comments_data.index.name = 'Num'
Comments_data.columns.name = 'Info'
# 엑셀저장
Video_data.to_excel('Video_data.xlsx', encoding='utf-8-sig')
Comments_data.transpose().to_excel('Comments_data.xlsx', encoding='utf-8-sig')

# Text Mining, 불용어구 제거
#이모티콘 제거
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

#분석에 어긋나는 불용어구 제외 (특수문자, 의성어)---전처리 과정
han = re.compile(r'[ㄱ-ㅎㅏ-ㅣ!?~,".\n\r#\ufeff\u200d]')

cleaned_comment = []
for i in Comments:
    tokens = re.sub(emoji_pattern, '', i)
    tokens = re.sub(han, '', tokens)
    cleaned_comment.append(tokens)
#불용어구 제외한 댓글 데이타프레임 생성
cleaned_comment = pd.DataFrame(cleaned_comment, columns=['comment'])
cleaned_comment.to_csv('cleaned_comment.txt', index=True, sep=' ', header=None,encoding='utf-8-sig')

# cleaned_comment['token'] = cleaned_comment['comment'].apply(lambda x: get_noun(x))

# print(Video_data)
# print(Comments_data.transpose())
# print('Finish')

driver.close()
