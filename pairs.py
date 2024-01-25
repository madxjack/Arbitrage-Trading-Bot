import ccxt
import csv
import requests


class Pairs:
    def __init__(self):
        self.binance = ccxt.binance()
        self.bitfinex = ccxt.bitfinex()
        self.kraken = ccxt.kraken()
        self.coinbasepro = ccxt.coinbasepro()
        self.kukoin = ccxt.kucoin()
        self.pairsBinance = []
        self.pairsBitfinex = []
        self.pairsKraken = []
        self.pairsCoinbasepro = []
        self.pairsKukoin = []
        self.pairsBinanceBitfinex = []
        self.pairsBinanceKraken = []
        self.pairsBitfinexKraken = []
        self.pairsBinanceKrakenBitfinex = []
        self.pairsBinanceKrakenCoinbasepro = []
        self.pairsBinanceKrakenKukoin = []

    def getPairsBinance(self):
        symbols = list(self.binance.load_markets().keys())
        for symbol in symbols:
            self.pairsBinance.append(symbol)
        return self.pairsBinance

    def getPairsKraken(self):
        symbols = list(self.kraken.load_markets().keys())
        for symbol in symbols:
            self.pairsKraken.append(symbol)
        return self.pairsKraken

    def getPairsBitfinex(self):
        symbols = list(self.bitfinex.load_markets().keys())
        for symbol in symbols:
            self.pairsBitfinex.append(symbol)
        return self.pairsBitfinex

    def getPairsCoinbasepro(self):
        symbols = list(self.coinbasepro.load_markets().keys())
        for symbol in symbols:
            self.pairsCoinbasepro.append(symbol)
        return self.pairsCoinbasepro

    def getPairsKukoin(self):
        symbols = list(self.kukoin.load_markets().keys())
        for symbol in symbols:
            self.pairsKukoin.append(symbol)
        return self.pairsKukoin

    def getPairsBitfinexRequest(self):
        url = "https://api-pub.bitfinex.com/v2/conf/pub:list:pair:exchange"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        pairs = response.json()
        for pair in pairs:
            for pair1 in pair:
                self.pairsBitfinex.append(pair1)
        return self.pairsBitfinex

    def getPairsCommonBinanceKraken(self):
        for pair in self.pairsKraken:
            pair1 = pair.split('/')[0]
            pair2 = pair.split('/')[1]
            for pairB in self.pairsBinance:
                pairB1 = pairB.split('/')[0]
                pairB2 = pairB.split('/')[1]
                if pairB not in self.pairsBinanceKraken:
                    if pair == pairB:
                        self.pairsBinanceKraken.append(pair)
                    elif pair1 == pairB1 and pair2 == 'USD' and pairB2 == 'USDT':
                        self.pairsBinanceKraken.append(pair)
                    elif pair1 == pairB1 and (pairB2 == 'BUSD' or pairB2 == 'USDC'):
                        self.pairsBinanceKraken.append(pairB)
        return self.pairsBinanceKraken

    def getPairsCommonBinanceKrakenBitfinex(self):
        # Delete xrp(delisted)
        self.pairsBinanceKraken = self.getPairList('pairsBinanceKraken.csv')
        self.pairsBitfinex = self.getPairsBitfinex()
        for pair in self.pairsBitfinex:
            pair1 = pair.split('/')[0]
            pair2 = pair.split('/')[1]
            for pairB in self.pairsBinanceKraken:
                pairB1 = pairB.split('/')[0]
                pairB2 = pairB.split('/')[1]
                if pair not in self.pairsBinanceKrakenBitfinex:
                    if pair == pairB:
                        self.pairsBinanceKrakenBitfinex.append(pair)
                    elif pair1 == pairB1 and pair2 == 'USDT' and pairB2 == 'USD':
                        self.pairsBinanceKrakenBitfinex.append(pair)

        return self.pairsBinanceKrakenBitfinex

    def getPairsCommonBinanceKrakenCoinbasepro(self):
        self.pairsBinanceKraken = self.getPairList('pairsBinanceKraken.csv')
        self.pairsCoinbasepro = self.getPairsCoinbasepro()
        for pair in self.pairsCoinbasepro:
            pair1 = pair.split('/')[0]
            pair2 = pair.split('/')[1]
            if not pair2 == 'GBP' and not pair2 == 'USD':
                for pairB in self.pairsBinanceKraken:
                    pairB1 = pairB.split('/')[0]
                    pairB2 = pairB.split('/')[1]
                    if pairB not in self.pairsBinanceKrakenCoinbasepro and pair not in self.pairsBinanceKrakenCoinbasepro:
                        if pair == pairB:
                            self.pairsBinanceKrakenCoinbasepro.append(pair)
        return self.pairsBinanceKrakenCoinbasepro

    def getPairsCommonBinanceKrakenKukoin(self):
        self.pairsBinanceKraken = self.getPairList('pairsBinanceKraken.csv')
        self.pairsKukoin = self.getPairsKukoin()
        for pair in self.pairsKukoin:
            if pair == 'MC/USDT':
                return
            pair1 = pair.split('/')[0]
            pair2 = pair.split('/')[1]
            for pairB in self.pairsBinanceKraken:
                pairB1 = pairB.split('/')[0]
                pairB2 = pairB.split('/')[1]
                if pairB not in self.pairsBinanceKrakenKukoin and pair not in self.pairsBinanceKrakenKukoin:
                    if pair == pairB:
                        self.pairsBinanceKrakenKukoin.append(pair)
                    elif pair1 == pairB1 and pair2 == 'USDT' and pairB2 == 'USD' and pair not in self.pairsBinanceKrakenKukoin:
                        self.pairsBinanceKrakenKukoin.append(pair)
        return self.pairsBinanceKrakenKukoin

    def csvPairsKraken(self):
        pairs = Pairs()
        pairs.getPairsKraken()
        pairs.pairsKraken.sort()
        pairs.pairsToCSV(pairs.pairsKraken, 'pairsKraken.csv')

    def csvPairsBinance(self):
        pairs = Pairs()
        pairs.getPairsBinance()
        pairs.pairsBinance.sort()
        pairs.pairsToCSV(pairs.pairsBinance, 'pairsBinance.csv')

    def csvPairsCoinbasepro(self):
        pairs = Pairs()
        pairs.getPairsCoinbasepro()
        pairs.pairsCoinbasepro.sort()
        pairs.pairsToCSV(pairs.pairsCoinbasepro, 'pairsCoinbasepro.csv')

    def csvPairsBitfinex(self):
        pairs = Pairs()
        pairs.getPairsBitfinexRequest()
        pairs.pairsToCSV(pairs.pairsBitfinex, 'pairsBitfinexRequest.csv')

    def csvPairsBinanceKraken(self):
        pairs = Pairs()
        pairs.getPairsBinance()
        pairs.getPairsKraken()
        pairs.getPairsCommonBinanceKraken()
        pairs.pairsBinanceKraken.sort()
        pairs.pairsToCSV(pairs.pairsBinanceKraken, 'pairsBinanceKraken.csv')

    def csvPairsBinanceKrakenCoinbasepro(self):
        pairs = Pairs()
        pairs.getPairsCommonBinanceKrakenCoinbasepro()
        pairs.pairsBinanceKrakenCoinbasepro.sort()
        pairs.pairsToCSV(pairs.pairsBinanceKrakenCoinbasepro,
                         'pairsBinanceKrakenCoinbasepro.csv')

    def csvPairsBinanceKrakenBitfinex(self):
        pairs = Pairs()
        pairs.getPairsCommonBinanceKrakenBitfinex()
        pairs.pairsBinanceKrakenBitfinex.sort()
        pairs.pairsToCSV(pairs.pairsBinanceKrakenBitfinex,
                         'pairsBinanceKrakenBitfinex.csv')

    def csvPairsBinanceKrakenKukoin(self):
        pairs = Pairs()
        pairs.getPairsCommonBinanceKrakenKukoin()
        pairs.pairsBinanceKrakenKukoin.sort()
        pairs.pairsToCSV(pairs.pairsBinanceKrakenKukoin,
                         'pairsBinanceKrakenKukoin.csv')

    # def getPairsCommonBinanceKrakenCoinbase(self):
    #     binanceKrakenPairs = self.getPairList('pairsBinanceKraken.csv')
    #     coinbasePairs = self.getPairsCoinbase()
    #     self.pairsBinanceKrakenCoinbase =  list(set(binanceKrakenPairs).intersection(set(coinbasePairs)))
    #     return self.pairsBinanceKrakenCoinbase

    def getPairList(self, file):
        listPairs = []
        with open(file, 'r') as file:
            reader = csv.reader(file, delimiter=' ')
            for pair in reader:
                newSymbol = str(pair)[2:-2]
                listPairs.append(newSymbol)
        return listPairs

    def pairsToCSV(self, pairs, filename):
        with open(filename, 'w', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_NONE, delimiter='\n')
            wr.writerow(pairs)


pairs = Pairs()
pairs.csvPairsBinanceKrakenCoinbasepro()
