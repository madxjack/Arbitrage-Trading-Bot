import numpy as np
from datetime import datetime
import time
import telegram as tg

class Exchange():
    def __init__(self, exchange):
        self.exchange = exchange
        self.deep = 100
        self.orderbook = None
    
    def getOrderbook(self, pair):
        self.orderbook = self.exchange.fetch_order_book(pair, self.deep)
        return self.orderbook
    
    def getOrdersBidBetweenPrices(self, lowPrice, highPrice):
        sumVol = 0
        lowPrice = float(lowPrice)
        highPrice = float(highPrice)
        priceList = []
        volumeList = []
        pvAvg = []

        bids = self.orderbook['bids']
        for bid in bids:
            if float(bid[0]) <= highPrice and float(bid[0]) >= lowPrice:
                sumVol = sumVol + bid[1]
                priceList.append(bid[0])
                volumeList.append(bid[1])
        try:
            weigthed_avg = np.average(priceList, weights=volumeList)    
        except:
            weigthed_avg = 0

        precio_avg = weigthed_avg
        pvAvg.append(precio_avg)
        pvAvg.append(sumVol)
        return pvAvg, bids
    
    def getOrdersAskBetweenPrices(self, lowPrice, highPrice):
        sumVol = 0
        priceList = []
        volumeList = []
        pvAvg = []
        lowPrice = float(lowPrice)
        highPrice = float(highPrice)

        asks = self.orderbook['asks']
        for ask in asks:
            if float(ask[0]) <= highPrice and float(ask[0]) >= lowPrice:
                sumVol = sumVol + ask[1]
                priceList.append(ask[0])
                volumeList.append(ask[1])
        try:
            weigthed_avg = np.average(priceList, weights=volumeList)    
        except:
            weigthed_avg = 0

        precio_avg = weigthed_avg
        pvAvg.append(precio_avg)
        pvAvg.append(sumVol)
        return pvAvg, asks

    def getPrices(self, pair):
        ticker = self.exchange.fetch_ticker(pair)
        bid = ticker['bid']
        ask = ticker['ask']
        price = [bid, ask]

        return price

    def getCoinInUSD(self, coin):
        pair = coin + '/USDT'
        ticker = self.exchange.fetch_ticker(pair)
        bid = ticker['bid']
        ask = ticker['ask']
        price = ask
        return price
    
    def getTimeExchange(self):
        time = self.exchange.fetch_time()   
        time = time / 1000
        dt = datetime.fromtimestamp(time).replace(microsecond=0)
        return dt
    
    def loadMarkets(self):
        self.exchange.load_markets()