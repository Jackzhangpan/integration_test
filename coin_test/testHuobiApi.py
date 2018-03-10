# -*- coding: utf-8 -*-
# @Date    : 2018-1-14 15:40:03
# @Author  : zhangpan
# @QQ      : 771761672
# @github  : https://github.com/Jackzhangpan

import base64
import datetime
import hashlib
import hmac
import time
import json
import urllib
import urllib.parse
import urllib.request
import requests

# API 请求地址
MARKET_URL = "https://api.huobi.pro"
TRADE_URL = "https://api.huobi.pro"

# 首次运行可通过get_accounts()获取acct_id,然后直接赋值,减少重复获取。
ACCOUNT_ID = None


def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)

    try:
        response = requests.get(url, postdata, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpGet failed, detail is:%s,%s" %(response.text,e))
        return
# 获取KLine
def get_kline(symbol, period, size=1):
    """
    :param symbol
    :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
    :param size: 可选值： [1,2000]
    :return:
    """
    params = {'symbol': symbol,
              'period': period,
              'size': size}

    url = MARKET_URL + '/market/history/kline'
    return http_get_request(url, params)


# 获取marketdepth
def get_depth(symbol, type):
    """
    :param symbol
    :param type: 可选值：{ percent10, step0, step1, step2, step3, step4, step5 }
    :return:
    """
    params = {'symbol': symbol,
              'type': type}

    url = MARKET_URL + '/market/depth'
    return http_get_request(url, params)

#获取ticker信息
def get_huobi_ticker():
    # 定义ticker字典
    ticker={}
    huobi_ticker=get_kline('btcusdt','1min')
    ch=huobi_ticker.get('ch')
    ts=huobi_ticker.get('ts')
    data=huobi_ticker.get('data')
    # 信息放到ticker字典中
    ticker['ch']=ch
    ticker['ts']=ts
    ticker['data']=data
    print('ticker:{}'.format(ticker))
    return ticker
    # print (huobi_ticker)
# 获取深度信息
def get_huobi_depth():
    depth={}
    #获取symbol为btcusdt,type为step0的深度信息
    huobi_depth=get_depth('btcusdt','step0')
    #获取symbol为btcusdt,type为step0的深度信息
    huobi_ch=huobi_depth.get('ch')
    # 获取asks,bids 最低5个，最高5个信息,以及ts时间戳
    asks=huobi_depth.get('tick').get('asks')[:5]
    bids=huobi_depth.get('tick').get('bids')[:5]
    ts=huobi_depth.get('tick').get('ts')
    # 放到字典depth中
    depth['ch'] = huobi_ch
    depth['ts'] = ts
    depth['asks'] = asks
    depth['bids'] = bids

	
    print('depth:{}'.format(depth))
    return depth

if __name__ == '__main__':
    while True:
        get_huobi_ticker()
        get_huobi_depth()
        time.sleep(1)


