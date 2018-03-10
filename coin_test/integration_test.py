import numpy as np
import pandas as pd
from influxdb import InfluxDBClient
import statsmodels
from statsmodels.tsa.stattools import coint
from pandas.core.frame import DataFrame
import seaborn as sns


def findData(exchange,starttime,endtime,skiptime):
    # 连接到指定数据库
    client = InfluxDBClient('localhost', '8086', 'root', '', 'exchangeData1111')
    #查询语句
    findsql=" SELECT first(\"last\") AS \"first_last\" FROM " +exchange+ \
            " WHERE time >= \'" + starttime +"\' AND time <= \'" +endtime+ "\' GROUP BY time(" + skiptime+ "s) FILL(previous)"
    # print('the result is : %s' % findsql)
    # 查询数据
    result = client.query(findsql)
    dataList=[]
    for data in result:
        get_result = data
        for i in get_result:
            dataList.append(i['first_last'])
    index = 0
    if dataList[0] is None:
        for j in range(len(dataList)):
            if dataList[j] is not None:
                index = j
                break
        for j in range(index):
            dataList[j] = dataList[index]
    return dataList

# 找出协整关系
def find_cointegrated_pairs(dataframe):
    # 得到DataFrame长度
    n = dataframe.shape[1]
    # 初始化p值矩阵
    pvalue_matrix = np.ones((n, n))
    # 抽取列的名称
    keys = dataframe.keys()
    # 初始化强协整组
    pairs = []
    # 对于每一个i
    for i in range(n):
        # 对于大于i的j
        for j in range(i+1, n):
            # 获取相应的两只交易所的Series
            stock1 = dataframe[keys[i]]
            stock2 = dataframe[keys[j]]
            # 分析它们的协整关系
            result1 = coint(stock1, stock2)
            result2 = coint(stock2, stock1)
            # 取出并记录p值
            pvalue1 = result1[1]
            pvalue2 = result2[1]
            pvalue_matrix[i, j] = pvalue1
            pvalue_matrix[j, i] = pvalue2
            # print(pvalue_matrix)
            # 如果p值小于0.05
            # if pvalue < 1:
            #     # 记录股票对和相应的p值
            #     pairs.append((keys[i], keys[j], pvalue))
    # 返回结果
    return pvalue_matrix, pairs
def main():
    starttime='2018-03-05 11:00:00' #开始时间
    endtime='2018-03-05 12:00:00'   #结束时间
    skiptime= '2'  # 间隔时间（秒）
    # 选择交易所
    exchanges = ['binance','bitfinex','bitmex', 'bitstamp','gdax', 'hitbtc2', 'huobipro','kraken']
    # 获取所有数据
    allLastList={}
    for exchange in exchanges:
        result=findData(exchange,starttime,endtime,skiptime)
        allLastList[exchange]=result
    #将总数据转为dataframe结构
    df=DataFrame(allLastList)
    # 作协整检验
    pvalues, pairs = find_cointegrated_pairs(df)
    #矩阵结构
    df_pvalues = DataFrame(pvalues, index=exchanges, columns=exchanges)
    print('协整检验值：')
    print( df_pvalues)
    #保存为csv文件
    df_pvalues.to_csv(r'C:\Users\XSY\Desktop\P值.csv',encoding='utf-8',index=True,header=True)
if __name__ == '__main__':
    main()