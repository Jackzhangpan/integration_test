import pymongo
import time

#  时间戳转化为日期
def stampToTime(timestamp):
    timeArray = time.localtime(timestamp/1000)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

#  时间转时间戳
def timeToStamp(gettime):
    timeArray = time.strptime(gettime, "%Y-%m-%d %H:%M:%S")
    gettime = int(time.mktime(timeArray)) * 1000
    return gettime

# 从集合中查询
def getDataInCollection(collection, starttime, endtime):
    startTime = timeToStamp(starttime)
    endTime = timeToStamp(endtime)
    dataCollection = collection.find({"ticker.timestamp": {'$gte': startTime, '$lte': endTime}})
    dataCount = dataCollection.count()
    # 用于存储数据
    dataList = []
    if dataCount > 0:
        for data in dataCollection:
            dataList.append(data)
        return dataList
    else:
        dataList.append(0)
        return dataList

# 获取时间戳队列
def getStampList(dataList):
    timestampList = []
    # 将时间戳存入队列
    for i in range(len(dataList)):
        data = dataList[i]
        # print(type(data['ticker']['timestamp']))
        timestampList.append(data['ticker']['timestamp'])

    return timestampList

# 处理数据
def dealWithData(dataList,timestampList, timestamp):
    difftimestampList = []
    # 将时间戳的相差值存入队列
    for i in range(len(dataList)):
        difftimestampList.append(abs(timestampList[i] - timestamp))
    minIndex = difftimestampList.index(min(difftimestampList))  # 返回最小时间差的索引
    resultdata = dataList[minIndex]
    if resultdata['ticker']['last'] != None:
        lastprice = float(resultdata['ticker']['last'])
    else:
        lastprice = float(resultdata['ticker']['close'])  # 如果没有last 用close替代
    return lastprice


#  获取数据库中全部集合
def getAllCollection():
    # 链接MongoDB
    connect = pymongo.MongoClient(host='localhost', port=27017)
    # 连接数据库
    db = connect.exchangeDataTest
    # 数据库所有的集合
    collections = {'binance': db.binance, 'okex': db.okex,
                   'bitfinex': db.bitfinex2, 'bitmex': db.bitmex,
                   'bitstamp': db.bitstamp1, 'gdax': db.gdax, 'huobi': db.huobipro}

    return collections

#  获取所有数据
def getAllDate(starttime, endtime, skipTime):
    # 获取所有集合
    collections = getAllCollection()

    # 查询开始时间戳
    startStamp = timeToStamp(starttime)
    # 用于存储所有数据
    allDate = {}

    #  初始化allData
    while startStamp <= timeToStamp(endtime):
        # allDate[startStamp] = []
        currentTime = stampToTime(startStamp)
        allDate[currentTime] = []
        # 时间加步长
        startStamp += skipTime

    for key in collections.keys():
        # 获取对应的数据集合
        collection = collections[key]
        # 获取数据队列
        dataList = getDataInCollection(collection, starttime, endtime)
        # 获取时间戳队列
        stampList = getStampList(dataList)
        # 重置开始时间
        startStamp = timeToStamp(starttime)

        while startStamp <= timeToStamp(endtime):
            currentTime = stampToTime(startStamp)
            # 获取最后成交价格
            lastPrice = dealWithData(dataList, stampList, startStamp)
            allDate[currentTime].append(lastPrice)
            # 时间加步长
            startStamp += skipTime

    return allDate

if __name__ == '__main__':
    # 查询时间
    starttime = "2018-01-26 18:00:00"
    endtime = "2018-01-26 19:00:00"

    # 间隔时间
    skipTime = 6000  # 毫秒

    allDate = getAllDate(starttime, endtime, skipTime)
    print(allDate)



