# -*- coding: utf-8 -*-
from urllib import parse
from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common import actions
# from selenium.webdriver.common.action_chains import ActionChains
from decimal import Decimal, DecimalException, BasicContext
# from multiprocessing import Manager, Pool, freeze_support, Lock
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import date
from datetime import datetime as dt
from datetime import timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import itertools
import functools
import socket
import browser_cookie3
import pandas as pd
import numpy as np
import urllib.request
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import requests
import re
import os
import json
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

start_time = time.time()

# KRX 정보데이터시스템 - 업종분류 현황(변수에 날짜 전달)
def krx_industy_fluctuation_rate(date):
    with requests.Session() as s:
        print('{}{}'.format(date.strftime('%Y-%m-%d'), '    KRX 정보데이터시스템 - 업종분류 현황'))
        headers = {
            'Referer' : 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020506',
            'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            }
        s.headers.update(headers)
        
        # menu_id = 'MDC0201020505'       # [12024] 업종별 분포 MDCSTAT038
        # menu_id = 'MDC0201020506'       # [12024] 업종분류 현황 MDCSTAT039
        df_list = []
        kospi_kosdaq = ['STK', 'KSQ']   # 코스피, 코스닥 차례로..     
        for i in kospi_kosdaq:
            data = {
                'bld': 'dbms/MDC/STAT/standard/MDCSTAT03901',
                'mktId': i,     # STK : 코스피, KSQ : 코스닥 
                'trdDd': date.strftime('%Y-%m-%d').replace('-', ''),
                'money': '1',   #원
                'csvxls_isNo': 'false',
            }
            res = s.post('http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd', data=data)
            time.sleep(1)
            html = res.text
            json_load = json.loads(html)['block1']
            json_load = json.dumps(json_load)
            df = pd.read_json(json_load, orient='records')
            df['날짜'] = date.strftime('%Y-%m-%d')
            df = df.rename(columns = {'ISU_SRT_CD': '종목코드', 'ISU_ABBRV': '종목명', 'MKT_TP_NM': '시장구분', 'IDX_IND_NM': '업종명', 'TDD_CLSPRC': '종가', 'CMPPREVDD_PRC': '대비', 'FLUC_RT': '등락률', 'MKTCAP': '시가총액', 'FLUC_TP_CD': 'FLUC_TP_CD'}, inplace = False)
            # df['시가총액'].apply(lambda x: round(int(x.replace(',', '')) * 1000000))
            #----용량절약을 위한 필요한 정보만을 담은 데이터프레임(활성화 / 비활성화)---------------------------------------------------------
            df = df.drop('시장구분', axis=1)
            df = df.drop('종가', axis=1)
            df = df.drop('대비', axis=1)
            df = df.drop('시가총액', axis=1)
            df = df.drop('FLUC_TP_CD', axis=1)
            #------------------------------------------------------------------------------------------------------
            for r in range(df.shape[0]):
                if df.loc[(r), '등락률'] == '-':
                    df.loc[(r), '등락률'] = None
            df = df.dropna(how='any', axis=0)
            # print(df)
            df_list.append(df)
        df_concated = pd.concat(df_list)
        return df_concated


# 엑셀로 저장
def make_excel(krx_df):
    today = round(time.time()*1000)          # 오늘
    file_name ='{}{}{}{}{}'.format('KRX_업종분류현황(', dt.fromtimestamp(round(today,-4)/1000).strftime('%Y-%m-%d'), ')', num, '.xlsx')
    save_path = '{}{}{}'.format(os.path.dirname(os.path.abspath(__file__)), '\\', file_name)
    with pd.ExcelWriter(save_path, mode='w', engine='openpyxl') as writer:
        krx_df.to_excel(writer, index=False, encoding='utf-8-sig')


#Plotly Line-chart
def plotly_line_chart(df_group):
    fig = go.FigureWidget(px.line(df_group, x="날짜", y="등락률", color='업종명', title='업종별 등락률'))
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
    )    
    fig.update_traces(mode='markers+lines')
    fig.update_layout(
        clickmode='event+select',
        # xaxis_type="log", 
        # yaxis_type="log",
    )
    # fig.show()
    return fig


#Dash App
def dash_app(fig):
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div([
        dcc.Graph(
            id='line_chart',
            figure=fig,
            style={
                'height': '100vh'
            },
            clear_on_unhover=True,
        ),    
    ])
    
    # @app.callback(
    #     dash.dependencies.Output("line_chart", "figure"),
    #     [dash.dependencies.Input("line_chart", "hoverData")]
    # )
    # def highlight_trace(hover_data):
    #     # here you set the default settings
    #     for trace in fig.data:
    #         trace["line"]["width"] = 1
    #         trace["opacity"] = 0.3
    #     if hover_data:
    #         trace_index = hover_data["points"][0]["curveNumber"]
    #         fig.data[trace_index]["line"]["width"] = 5
    #         fig.data[trace_index]["opacity"] = 1
    #     return fig

    @app.callback(
        [Output('line_chart', 'figure')],
        [Input('line_chart', 'clickData')],
    )
    # {'points': [{'curveNumber': 23, 'pointNumber': 160, 'pointIndex': 160, 'x': '2012-08-23', 'y': 5.7}]}
    def display_hover_data(clickData):
        for trace in fig.data:
            trace["line"]["width"] = 1
            trace["opacity"] = 0.3
        if clickData:
            trace_index = clickData["points"][0]["curveNumber"]
            fig.data[trace_index]["line"]["width"] = 5
            fig.data[trace_index]["opacity"] = 1
        return fig

    return app



if __name__ == '__main__':
    date = [
        # ('2010-01-01', '2010-12-31'),
        # ('2011-01-01', '2011-12-31'),
        # ('2012-01-01', '2012-12-31'),
        # ('2013-01-01', '2013-12-31'),
        # ('2014-01-01', '2014-12-31'),
        # ('2015-01-01', '2015-12-31'),
        # ('2016-01-01', '2016-12-31'),
        # ('2017-01-01', '2017-12-31'),
        # ('2018-01-01', '2018-12-31'),
        # ('2019-01-01', '2019-12-31'),
        # ('2020-01-01', '2020-12-31'),
        ('2021-01-01', '2021-05-18'),
    ]
    # start_date = '2020-01-01'
    # finish_date = '2020-12-31'
    # finish_date = dt.now().strftime('%Y-%m-%d')
    
    # num = 0
    # for i in date:
    #     num += 1
    #     date = pd.bdate_range(i[0], i[1]).tolist()  # business date range (weekday)
    #     # 날짜 주말제외한 리스트 만들고 업종분류 현황 완료 후 업종별 분포 진행
    #     krx_df = list(map(krx_industy_fluctuation_rate, date))
    #     krx_df = pd.concat(krx_df)
    #     make_excel(krx_df)
    #     time.sleep(10)
    
    #----데이터 시각화---------------------------------------------------------------------------------------------------
    # df_1 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황12.xlsx')
    # df_2 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황11.xlsx')
    # df_3 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황10.xlsx')
    # df_4 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황9.xlsx')
    # df_5 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황8.xlsx')
    # df_6 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황7.xlsx')
    # df_7 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황6.xlsx')
    # df_8 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황5.xlsx')
    # df_9 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황4.xlsx')
    df_10 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황3.xlsx')
    # df_11 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황2.xlsx')
    # df_12 = pd.read_excel('/Users/macintoshhd/Desktop/Coding/Python/업종/KRX_업종분류현황1.xlsx')

    df = pd.concat([df_10])
    df_group = df.groupby(['날짜', '업종명'], as_index=False).mean()
    df_group['등락률'] = df_group['등락률'].apply(lambda x : round(x, 1))
    # df.groupby(['날짜', '업종명'], as_index=False).apply(lambda x : x['업종명'])
    fig = plotly_line_chart(df_group)
    
    app = dash_app(fig)             #Dash 앱으로 구현
    
    app.run_server()                #App 실행
    

    print('Working time : {} sec'.format(time.time() - start_time))
    print('------Finish------')

