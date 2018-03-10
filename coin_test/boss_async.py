
import asyncio
import ccxt.async as ccxt
import time
import random
import requests

class Queue(object):# 定义队列类 为什么加入object
    def __init__(self,size):
       self.size = size #定义队列长度
       self.queue = []#存储队列 列表
    #返回对象的字符串表达式 方便调试
    def __str__(self):
        return str(self.queue)#什么含义
    #入队
    def inQueue(self,n):
        if self.isFull():
            return -1
        self.queue.append(n)#列表末尾添加新的对象
    #出队
    def outQueue(self):
        if self.isEmpty():
            return -1
        firstElement = self.queue[0]  #删除队头元素
        self.queue.remove(firstElement) #删除队操作
        return firstElement
    #插入某元素
    def inPut(self,n,m):#n代表列表当前的第n位元素 m代表传入的值
        self.queue[n] = m
    #获取当前长度
    def getSize(self):
        return len(self.queue)
    #判空
    def isEmpty(self):
        if len(self.queue)==0:
            return True
        return False
    #判满
    def isFull(self):
        if len(self.queue) == self.size:
            return True
        return False

#  获取货币的汇率（美元换其他）
def getCurrencyRate(currency):
    res = requests.get('https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json')
    data = eval(res.text)
    resources = data['list']['resources']
    for i in range(len(resources)):
        if resources[i]['resource']['fields']['name'] == currency:
            rate = float(resources[i]['resource']['fields']['price'])
    return rate


# 获取ticker和depth信息
async def get_exchange_tickerDepth(exchange, symbol):  # 其中exchange为实例化后的市场
    # lastData = {exchange.id: []}  # 初始化最新数据 用于去重
    while 1:
        try:
            print('%s is run %s' % (exchange.id, time.ctime()))

            # 获取ticher信息
            currency = None
            if symbol == 'BTC/KRW':
                currency = 'USD/KRW'
                rate = getCurrencyRate(currency)
            if symbol == 'BTC/JPY':
                currency = 'USD/JPY'
                rate = getCurrencyRate(currency)
            # 获取ticher信息
            tickerInfo = await exchange.fetch_ticker(symbol)
            # 添加最高价 最低价 最新成交价
            ticker = tickerInfo.get('info')
            if type(ticker) == type({}):
                ticker['timestamp'] = tickerInfo.get('timestamp')
                ticker['high'] = tickerInfo.get('high')
                ticker['low'] = tickerInfo.get('low')
                ticker['last'] = tickerInfo.get('last')
            else:
                ticker = tickerInfo
            # 如果货币不是美元 添加汇率
            if currency is not None:
                ticker['rate'] = rate

            # print(ticker)

            # 获取深度信息
            depth = {}
            exchange_depth = await exchange.fetch_order_book(symbol)
            # 获取asks,bids 最低5个，最高5个信息
            asks = exchange_depth.get('asks')[:5]
            bids = exchange_depth.get('bids')[:5]
            depth['asks'] = asks
            depth['bids'] = bids
            # print('depth:{}'.format(depth))
            # data = {
            #     'exchange': exchange.id,
            #     'countries': exchange.countries,
            #     'symbol': symbol,
            #     'ticker': ticker,
            #     'depth': depth
            # }
            data={
                'exchange': exchange.id,
                'last':ticker['last']
            }
            listdata=[data]
            # 生成循环列表
            queueTest = Queue(100)

            queueTest.inQueue(listdata)
            # 保存数据并返回最新数据
            # lastData[exchange.id] = save_exchangeDate(exchangeData, exchange.id, data, lastData)

            print('********* %s is finished, time %s *********' % (exchange.id, time.ctime()))
            await asyncio.sleep(0.5)  # 等待0.5秒
            # coroutine = get_exchange_tickerDepth(exchange, symbol)
            #
            # await asyncio.ensure_future(coroutine)
            print(queueTest)

        except Exception as e:
            print(e)
            if exchange.id in ['bitfinex', 'bitmex']:
                delay = random.randint(10, 60)  # 设置随机等待时间
            else:
                delay = random.randint(0, 10)
            print('$$$$$$$$$ %s is run worried, sleep %s $$$$$$$$$' % (exchange.id, delay))
            await asyncio.sleep(delay)  # 等待后继续添加
            # coroutine = get_exchange_tickerDepth(exchange, symbol)
            # await asyncio.ensure_future(coroutine)

# 存库
# def save_exchangeDate(exchangeData, exchangeName, data, lastData):
#     try:
#         # 连接表
#         exchangeInformation = exchangeData[exchangeName]
#     except:
#         # 连接MongoDB
#         connect = pymongo.MongoClient(host='localhost', port=27017)
#         # 连接数据库
#         exchangeData = connect['exchangeDataAsyncioBoss']
#         # 连接表
#         exchangeInformation = exchangeData[exchangeName]
#     # print(table_name)
#     # 获取最后数据
#     lastData = lastData[exchangeName]
#     # 数据去重后保存
#     if len(lastData) == 0:
#         exchangeInformation.insert_one(data)
#         lastData = data
#     else:
#         if lastData['ticker']['timestamp'] != data['ticker']['timestamp']:
#             exchangeInformation.insert_one(data)
#         lastData = data
#     return lastData


def main():

    exchanges = [ccxt.gdax(),  ccxt.kraken(), ccxt.hitbtc2(),
                  ccxt.huobipro(), ccxt.bitstamp()]
    symbols = ['BTC/USD', 'BTC/USD', 'BTC/USDT',
                'BTC/USDT', 'BTC/USD']
    tasks = []
    for i in range(len(exchanges)):
        task = get_exchange_tickerDepth(exchanges[i], symbols[i])
        tasks.append(asyncio.ensure_future(task))

    loop = asyncio.get_event_loop()

    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    main()



