from collections import Counter
from wordcloud import WordCloud
from matplotlib import font_manager, rc
#import matplotlib as mpl
import matplotlib.pylab as plt
import numpy as np
import pandas as pd

def get_noun():

    f = open('cleaned_comment.txt', 'r')
    cleaned_comment = f.read()

    from konlpy.tag import Twitter

    twitter = Twitter()
    noun = twitter.nouns(cleaned_comment)

    return noun

#counting and bar chart
counts = Counter(get_noun())
tags = counts.most_common(50)

chart = pd.DataFrame({'word':[],
                    'count':[]})

for i in range(len(tags)):
    word = tags[i][0]
    count = tags[i][1]

    insert_data = pd.DataFrame({'word':[word],
                                'count':[count]})
    chart = chart.append(insert_data)

chart.index = range(len(chart))
# np.arrange에 대한 설명 https://codepractice.tistory.com/88
index = np.arange(len(chart))
# matplotlib 폰트설정

rc('font', family='AppleGothic')
#한글 사용시 마이너스 폰트 깨짐 문제 해결
plt.rcParams['axes.unicode_minus'] = False
plt.bar(index,chart['count'].tolist())
plt.xticks(index, chart['word'].tolist(), fontsize=10, rotation=30)
plt.xlabel('word', fontsize=15)
plt.ylabel('count', fontsize=15)
plt.title('단어 빈도수 시각화')
plt.show()


#wordcloud
wc = WordCloud(font_path='font/NanumGothic.ttf',background_color='white', width=800, height=600)

print(dict(tags))
cloud = wc.generate_from_frequencies(dict(tags))
plt.figure(figsize=(10, 8))
plt.axis('off')
plt.imshow(cloud)
plt.show()
