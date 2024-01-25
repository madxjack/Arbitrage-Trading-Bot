import time
from datetime import datetime, timedelta
import telegram as tg
import csv
import numpy as np
import ccxt
import config
import traceback


class Snitch:
    def __init__(self, pair, pairsBanned, pairsBannedInitialDate, binance, kraken, kukoin, coinbasepro, timeSleep) -> None:
        self.pair = pair
        self.minProfit = config.BOT_MIN_PROFIT
        self.minRentability = config.BOT_MIN_RENTABILIDAD
        self.minPercentageDiffPrices = config.BOT_MIN_DIFFERENCE_PRICES
        self.pairsBanned = pairsBanned
        self.pairsBannedInitialDate = pairsBannedInitialDate
        self.binance = binance
        self.kraken = kraken
        self.kukoin = kukoin
        self.coinbasepro = coinbasepro
        self.binanceAskPrice = 0
        self.krakenAskPrice = 0
        self.kukoinAskPrice = 0
        self.coinbaseproAskPrice = 0
        self.binanceBidPrice = 0
        self.krakenBidPrice = 0
        self.kukoinBidPrice = 0
        self.coinbaseproBidPrice = 0
        self.timeSleep = timeSleep
        self.orderbook = None
        self.telegram = tg.Telegram(
            config.TG_CHAT_ID_TRIAL, config.TG_CHAT_ID_DEV, config.TG_BOT_TOKEN)
        self.BinanceActive = config.EX_BINANCE
        self.KukoinActive = config.EX_KUKOIN
        self.KrakenActive = config.EX_KRAKEN
        self.CoinbaseActive = config.EX_COINBASE

    def start(self):
        try:
            if self.timeSleep > 0:
                time.sleep(self.timeSleep)
            # Cleaning sleeping time to prevent ban
            if self.timeSleep - 0.2 >= 0:
                self.timeSleep -= 0.2
            else:
                self.timeSleep = 0

            if (self.timeSleep > 10):
                self.telegram.sendMessageDev(
                    'AB bot relentizandose ' + str(self.timeSleep) + 'seg para prevenir el baneo...')

            # Check if pair singnal was thrown in the las 15 min
            if self.checkPairBanned():
                return

            exchanges = ['binance', 'kraken', 'kukoin', 'coinbasepro']
            exchange_pairs = {
                ex: self.checkExchangePairName(ex) for ex in exchanges}

            # Check if pair exists in kukoin
            if self.checkPairInKukoin(exchange_pairs['kukoin']) and self.KukoinActive == True:
                # Check if pair exists in coinbasepro
                if self.checkPairInCoinbasepro(exchange_pairs['coinbasepro']):
                    # print('Pair ' + self.pair +
                    #       ' exists in kukoin and coinbasepro')
                    # Get ask and bid prices from all exchanges
                    exchangePrices = self.getPairsPrices(binance=exchange_pairs['binance'], kraken=exchange_pairs['kraken'],
                                                         kukoin=exchange_pairs['kukoin'], coinbasepro=exchange_pairs['coinbasepro'])
                    # Get all min ask price
                    self.binanceAskPrice = exchangePrices['binance'][1]
                    self.krakenAskPrice = exchangePrices['kraken'][1]
                    self.kukoinAskPrice = exchangePrices['kukoin'][1]
                    self.coinbaseproAskPrice = exchangePrices['coinbasepro'][1]
                    askExchangePrices = {'binance': self.binanceAskPrice, 'kraken': self.krakenAskPrice,
                                         'kukoin': self.kukoinAskPrice, 'coinbasepro': self.coinbaseproAskPrice}
                    # Get all max bid price
                    self.binanceBidPrice = exchangePrices['binance'][0]
                    self.krakenBidPrice = exchangePrices['kraken'][0]
                    self.kukoinBidPrice = exchangePrices['kukoin'][0]
                    self.coinbaseproBidPrice = exchangePrices['coinbasepro'][0]
                    bidExchangePrices = {'binance': self.binanceBidPrice, 'kraken': self.krakenBidPrice,
                                         'kukoin': self.kukoinBidPrice, 'coinbasepro': self.coinbaseproBidPrice}
                    # Get min ask price and min bid price
                    exchangeMinPrice, minPrice = self.checkMinExchangePrice(
                        binance=self.binanceAskPrice, kraken=self.krakenAskPrice, kukoin=self.kukoinAskPrice, coinbasepro=self.coinbaseproAskPrice)
                    exchangeMaxPrice, maxPrice = self.checkMaxExchangePrice(
                        binance=self.binanceBidPrice, kraken=self.krakenBidPrice, kukoin=self.kukoinBidPrice, coinbasepro=self.coinbaseproBidPrice)
                    # time.sleep(1)
                else:
                    # print('Pair ' + self.pair + ' exists in kukoin')
                    # Get ask and bid prices from all exchanges
                    exchangePrices = self.getPairsPrices(
                        binance=exchange_pairs['binance'], kraken=exchange_pairs['kraken'], kukoin=exchange_pairs['kukoin'])
                    # Get all min ask price
                    self.binanceAskPrice = exchangePrices['binance'][1]
                    self.krakenAskPrice = exchangePrices['kraken'][1]
                    self.kukoinAskPrice = exchangePrices['kukoin'][1]
                    askExchangePrices = {'binance': self.binanceAskPrice,
                                         'kraken': self.krakenAskPrice, 'kukoin': self.kukoinAskPrice}
                    # Get all max bid price
                    self.binanceBidPrice = exchangePrices['binance'][0]
                    self.krakenBidPrice = exchangePrices['kraken'][0]
                    self.kukoinBidPrice = exchangePrices['kukoin'][0]
                    bidExchangePrices = {'binance': self.binanceBidPrice,
                                         'kraken': self.krakenBidPrice, 'kukoin': self.kukoinBidPrice}
                    # Get min ask price and min bid price
                    exchangeMinPrice, minPrice = self.checkMinExchangePrice(
                        binance=self.binanceAskPrice, kraken=self.krakenAskPrice, kukoin=self.kukoinAskPrice)
                    exchangeMaxPrice, maxPrice = self.checkMaxExchangePrice(
                        binance=self.binanceBidPrice, kraken=self.krakenBidPrice, kukoin=self.kukoinBidPrice)
                    # time.sleep(1)

                # Check if kukoin bans us
                if self.binanceAskPrice == 0 and self.kukoinBidPrice == 0:
                    print('kukoin bans us')
                    self.timeSleep = + 5
            else:
                if self.checkPairInCoinbasepro(exchange_pairs['coinbasepro'] and self.CoinbaseActive == True):
                    print('Pair ' + self.pair + ' exists in coinbasepro')
                    # Get ask and bid prices from all exchanges
                    exchangePrices = self.getPairsPrices(
                        binance=exchange_pairs['binance'], kraken=exchange_pairs['kraken'], coinbasepro=exchange_pairs['coinbasepro'])
                    # Get all min ask price
                    self.binanceAskPrice = exchangePrices['binance'][1]
                    self.krakenAskPrice = exchangePrices['kraken'][1]
                    self.coinbaseproAskPrice = exchangePrices['coinbasepro'][1]
                    askExchangePrices = {'binance': self.binanceAskPrice,
                                         'kraken': self.krakenAskPrice, 'coinbasepro': self.coinbaseproAskPrice}
                    # Get all max bid price
                    self.binanceBidPrice = exchangePrices['binance'][0]
                    self.krakenBidPrice = exchangePrices['kraken'][0]
                    self.coinbaseproBidPrice = exchangePrices['coinbasepro'][0]
                    bidExchangePrices = {'binance': self.binanceBidPrice,
                                         'kraken': self.krakenBidPrice, 'coinbasepro': self.coinbaseproBidPrice}
                    # Get min ask price and min bid price
                    exchangeMinPrice, minPrice = self.checkMinExchangePrice(
                        binance=self.binanceAskPrice, kraken=self.krakenAskPrice, coinbasepro=self.coinbaseproAskPrice)
                    exchangeMaxPrice, maxPrice = self.checkMaxExchangePrice(
                        binance=self.binanceBidPrice, kraken=self.krakenBidPrice, coinbasepro=self.coinbaseproBidPrice)

                else:
                    exchangePrices = self.getPairsPrices(
                        binance=exchange_pairs['binance'], kraken=exchange_pairs['kraken'])
                    self.binanceAskPrice = exchangePrices['binance'][1]
                    self.krakenAskPrice = exchangePrices['kraken'][1]
                    askExchangePrices = {
                        'binance': self.binanceAskPrice, 'kraken': self.krakenAskPrice}
                    # Get all max bid price
                    self.binanceBidPrice = exchangePrices['binance'][0]
                    self.krakenBidPrice = exchangePrices['kraken'][0]
                    bidExchangePrices = {
                        'binance': self.binanceBidPrice, 'kraken': self.krakenBidPrice}
                    # Get min ask price and min bid price

                    exchangeMinPrice, minPrice = self.checkMinExchangePrice(
                        binance=self.binanceAskPrice, kraken=self.krakenAskPrice)
                    exchangeMaxPrice, maxPrice = self.checkMaxExchangePrice(
                        binance=self.binanceBidPrice, kraken=self.krakenBidPrice)

            for askExchange in askExchangePrices:
                minPrice = askExchangePrices[askExchange]
                exchangeMinPrice = askExchange
                bidExchanges = {}
                askExchanges = {}
                for bidExchange in bidExchangePrices:
                    exchangeMaxPrice = bidExchange
                    maxPrice = bidExchangePrices[bidExchange]
                    if maxPrice > minPrice and minPrice > 0 and maxPrice > 0:
                        percentageDiffPrices = round(
                            self.percentageDiffPrices(maxPrice, minPrice), 2)
                        if percentageDiffPrices > self.minPercentageDiffPrices:
                            try:
                                # Get ask order between min and max price
                                exchangeMinPriceObj = getattr(
                                    self, exchangeMinPrice)
                                pairExchangeAsks = self.checkExchangePairName(
                                    exchangeMinPrice)
                                if exchangeMinPrice in askExchanges:
                                    obExchangeBuy = askExchanges[exchangeMinPrice]
                                else:
                                    obExchangeBuy = exchangeMinPriceObj.getOrderbook(
                                        pairExchangeAsks)
                                    askExchanges[exchangeMinPrice] = obExchangeBuy
                                avgAskRange, askOrders = exchangeMinPriceObj.getOrdersAskBetweenPrices(
                                    minPrice, maxPrice)

                                # Get bid order between min and max price
                                exchangeMaxPriceObj = getattr(
                                    self, exchangeMaxPrice)
                                pairExchangeBids = self.checkExchangePairName(
                                    exchangeMaxPrice)
                                if exchangeMaxPrice in bidExchanges:
                                    obExchangeSell = bidExchanges[exchangeMaxPrice]
                                else:
                                    obExchangeSell = exchangeMaxPriceObj.getOrderbook(
                                        pairExchangeBids)
                                    bidExchanges[exchangeMaxPrice] = obExchangeSell
                                avgBidRange, bidOrders = exchangeMaxPriceObj.getOrdersBidBetweenPrices(
                                    minPrice, maxPrice)

                            except ccxt.BaseError as e:
                                self.timeSleep += 3
                                print(
                                    'Error getting ask bid orders in range: ' + str(e))
                                return

                            # Get avg price ask and bid
                            avgAskPrice = avgAskRange[0]
                            avgBidPrice = avgBidRange[0]

                            # Get ask and bid volume between min and max price
                            askVolume = avgAskRange[1]
                            bidVolume = avgBidRange[1]

                            # Check which volume is bigger
                            if askVolume >= bidVolume:
                                # Get effective price and volume for ask and bid orderbook with bid volume
                                avgBidPriceEffective, bidVolumeEffective = self.getBidPriceVolumeEffective(
                                    obExchangeSell, bidVolume, minPrice)
                                # Catch error with some pairs that pair2 is mixed (usdt/usd/busd)
                                try:
                                    avgAskPriceEffective, askVolumeEffective = self.getAskPriceVolumeEffective(
                                        obExchangeBuy, bidVolume, maxPrice)
                                except:
                                    obExchangeBuy = exchangeMinPriceObj.getOrderbook(
                                        pairExchangeAsks)
                                    askVolumeEffective = 0
                                    avgAskPriceEffective = 0
                                volumenEffective = bidVolumeEffective
                            else:
                                # Get effective price and volume for ask and bid orderbook with ask volume
                                avgBidPriceEffective, bidVolumeEffective = self.getBidPriceVolumeEffective(
                                    obExchangeSell, askVolume, minPrice)
                                # Catch error with some pairs that pair2 is mixed (usdt/usd/busd)
                                try:
                                    avgAskPriceEffective, askVolumeEffective = self.getAskPriceVolumeEffective(
                                        obExchangeBuy, askVolume, maxPrice)
                                except:
                                    obExchangeBuy = exchangeMinPriceObj.getOrderbook(
                                        pairExchangeAsks)
                                    askVolumeEffective = 0
                                    avgAskPriceEffective = 0

                                volumenEffective = askVolumeEffective

                            # Get some variables to send
                            # Check if pair base is USD
                            if self.checkPairBaseIsUSD(self.pair):
                                profit = self.getProfit(
                                    avgAskPriceEffective, avgBidPriceEffective, volumenEffective)
                                askVolumeUSD = askVolume * avgAskPrice
                                bidVolumeUSD = bidVolume * avgBidPrice
                                askVolumeEffectiveUSD = askVolumeEffective * avgAskPriceEffective
                                bidVolumeEffectiveUSD = bidVolumeEffective * avgBidPriceEffective

                            else:  # If pair base is not USD, get USD price and calculate USD volume
                                priceUSD = self.binance.getCoinInUSD(
                                    self.pair.split('/')[1])
                                askVolumeUSD = askVolume * avgAskPrice * priceUSD
                                bidVolumeUSD = bidVolume * avgBidPrice * priceUSD
                                volumenEffectiveUSD = volumenEffective * priceUSD
                                askVolumeEffectiveUSD = askVolumeEffective * avgAskPriceEffective * priceUSD
                                bidVolumeEffectiveUSD = bidVolumeEffective * avgBidPriceEffective * priceUSD
                                profit = self.getProfit(
                                    avgAskPriceEffective, avgBidPriceEffective, volumenEffective)

                            if profit > self.minProfit and askVolume > 0:
                                rentability = round(
                                    (profit / askVolumeEffectiveUSD) * 100, 2)
                            else:
                                rentability = 0
                            self.timeSleep += 0.8
                            # MESSAGE TO SEND
                            if volumenEffective > 0 and profit > self.minProfit and rentability > self.minRentability:
                                pair1 = self.pair.split('/')[0]
                                pair2 = self.pair.split('/')[1]
                                pairStr = f'Pairs: {pairExchangeAsks} - {pairExchangeBids}'
                                netStr = self.find_PairNet(
                                    'pairsRed.csv', self.pair)
                                if (netStr != None):
                                    netStr = 'Red: ' + netStr
                                buyStr = exchangeMinPrice.capitalize() + ' - Valor: ' + str(minPrice)
                                sellStr = exchangeMaxPrice.capitalize() + ' - Valor: ' + str(maxPrice)
                                percentageStr = 'Porcentaje: ' + \
                                    str(percentageDiffPrices) + '%'
                                gapStr1 = 'Gap(Asks): ' + str(round(askVolume, 2)) + ' ' + \
                                    pair1 + \
                                    ' (' + str(round(askVolumeUSD, 2)) + ' USD)'
                                gapStr2 = 'Gap(Bids): ' + str(round(bidVolume, 2)) + ' ' + \
                                    pair1 + \
                                    ' (' + str(round(bidVolumeUSD, 2)) + ' USD)'
                                effectiveVolGapStr = 'Volumen efectivo: ' + \
                                    str(round(volumenEffective, 6)) + \
                                    ' ' + pair1
                                rentabilityStr = 'Rentabilidad: ' + \
                                    str(rentability) + '%'
                                profitStr = 'Beneficio: ' + \
                                    str(round(profit, 2)) + ' ' + 'USD'
                                message = 'Bot v2.5-040323\n' + pairStr + '\n' + buyStr + '\n' + sellStr + '\n'
                                if (netStr != None):
                                    message = message + netStr + '\n'
                                message = message + percentageStr + '\n' + gapStr1 + '\n' + gapStr2 \
                                    + '\n' + effectiveVolGapStr + '\n' + rentabilityStr + '\n' + profitStr
                                print(message)
                                # If profit > minProfit, pair banned for 20 minutes
                                if profit > self.minProfit:
                                    # datetimeBinance = self.binance.getTimeExchange()
                                    # dateBum = datetime.strftime(
                                    #     datetimeBinance, '%Y-%m-%d %H:%M:%S')
                                    dateBum = datetime.now()
                                    bum = self.banPair(self.pair, dateBum)
                                    print(f'Pair baneado: {bum}')
                                    self.banPairsUntradeable(bum)

                                self.telegram.sendMessage(message)
                                self.timeSleep += 0.2

                            # print(message)
        except ccxt.BaseError as e:
            print(f'{self.pair} - ERROR SNITCH CCXT: {e}')
            self.telegram.sendMessageDev(f'{self.pair} - ERROR SNITCH: {e}')
            self.timeSleep += 3
        except Exception as e:
            print(f'{self.pair} - ERROR SNITCH: {e}')
            traceback.print_exc()
            self.telegram.sendMessageDev(f'{self.pair} - ERROR SNITCH: {e}')

    def checkPairBanned(self):
        nowDate = datetime.now()
        for dictPair in self.pairsBanned:
            if self.pair == dictPair['name'] and self.pair != "":
                # dictDate = datetime.strptime(
                #     dictPair['date'], '%Y-%m-%d %H:%M:%S')
                dictDate = dictPair['date']
                dateBan = dictDate + \
                    timedelta(minutes=config.BOT_BAN_PAIR_TIME)
                print(f'Date Pair banned: {dictDate}')
                print(f'Date finish ban: {dateBan}')
                if nowDate < dateBan:
                    # add mod para eliminar pair de la lista de baneados
                    return True
                else:
                    self.pairsBanned.remove(dictPair)
                    return False
        return False

    def banPairsUntradeable(self, pairBanned):
        timeBannedSoft = datetime.now() + timedelta(minutes=50)
        timeBannedHard = datetime.now() + timedelta(minutes=200)
        # Check if pair is in pairsBannedInitialDate (first time bannedInitialDate)
        if not any(pair['name'] == pairBanned['name'] for pair in self.pairsBannedInitialDate):
            newParBanned = {
                'name': pairBanned['name'],
                'count': 1,
                'bannedInitialDate': pairBanned['date']
            }
            self.pairsBannedInitialDate.append(newParBanned)
            return

        for pair in self.pairsBannedInitialDate:
            if pairBanned['name'] == pair['name']:
                if pair['bannedInitialDate'] + timedelta(minutes=config.BOT_BAN_PAIR_TIME * 2) < pairBanned['date']:
                    self.pairsBannedInitialDate.remove(pair)
                else:
                    if pair['count'] > 2 and pair['count'] < 4:
                        pair['count'] += 1
                        if self.checkPairNameInDict(pair, self.pairsBanned):
                            for pairBanned in self.pairsBanned:
                                if pairBanned['name'] == pair['name']:
                                    pairBanned['date'] = timeBannedSoft
                                    print(
                                        f'Pair {pairBanned["name"]} banned for 50 min until {timeBannedSoft}')
                        else:
                            self.banPair(pair['name'], timeBannedSoft)

                    elif pair['count'] <= 2:
                        pair['count'] += 1
                        pair['bannedInitialDate'] = datetime.now()
                        print(f'Pair count: {pair["count"]}')
                    else:
                        self.banPair(pair['name'], timeBannedHard)
                        print(f'Pair reseted: {pair["name"]}')
                        print(
                            f'Pair {pairBanned["name"]} banned for {timeBannedHard} min until {timeBannedHard}')
                return

    def checkPairNameInDict(self, pair, dict):
        if any(pair['name'] == pairDict['name'] for pairDict in dict):
            return True
        return False

    def banPair(self, pair, date):
        pairBannedObj = {
            'name': pair,
            'date': date
        }
        self.pairsBanned.append(pairBannedObj)
        return pairBannedObj

    def checkExchangePairName(self, name):
        if name == 'binance':
            return self.checkBinancePairName()
        elif name == 'kraken':
            return self.checkKrakenPairName()
        elif name == 'kukoin':
            return self.checkKukoinPairName()
        elif name == 'coinbasepro':
            return self.checkCoinbaseproPairName()

    def checkBinancePairName(self):
        pair = self.pair
        firstPair = pair.split('/')[0]
        sec_pair = pair.split('/')[1]

        if firstPair == 'NANO':
            firstPair = 'XNO'

        if sec_pair == 'USD':
            b_pair = firstPair + '/' + 'USDT'
        else:
            b_pair = firstPair + '/' + sec_pair

        return b_pair

    def checkKrakenPairName(self):
        pair = self.pair
        firstPair = pair.split('/')[0]
        sec_pair = pair.split('/')[1]

        if sec_pair == 'BUSD' or sec_pair == 'USDC':
            k_pair = firstPair + '/' + 'USD'
        else:
            k_pair = firstPair + '/' + sec_pair

        return k_pair

    def checkKukoinPairName(self):
        pair = self.pair
        firstPair = pair.split('/')[0]
        sec_pair = pair.split('/')[1]

        if sec_pair == 'BUSD' or sec_pair == 'USDC':
            pair = firstPair + '/' + 'USDT'
        else:
            pair = firstPair + '/' + sec_pair

        return pair

    def checkBitfinexPairNameRequest(self, pair):
        firstPair = pair.split('/')[0]
        sec_pair = pair.split('/')[1]

        pairName = self.getPairNameInBitfinexRequest(firstPair, sec_pair)

        return pairName

    def checkCoinbaseproPairName(self):
        pair = self.pair
        firstPair = pair.split('/')[0]
        sec_pair = pair.split('/')[1]

        if sec_pair == 'BUSD' or sec_pair == 'USDC' or sec_pair == 'USD':
            pair = firstPair + '/' + 'USDT'
        else:
            pair = firstPair + '/' + sec_pair

        return pair

    def checkPairInKrakenCSV(self, pair):
        with open('pairsKraken.csv', newline='') as csvfile:
            exists = False
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                pairCheck = row[0]
                if pairCheck == pair:
                    exists = True
        return exists

    def checkPairInBitfinex(self, pair):
        with open('pairsBinanceKrakenBitfinex.csv', newline='') as csvfile:
            exists = False
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                pairCheck = row[0]
                if pairCheck == pair:
                    exists = True
        return exists

    def checkPairInKukoin(self, pair):
        with open('pairsBinanceKrakenKukoin.csv', newline='') as csvfile:
            exists = False
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                pairCheck = row[0]
                if pairCheck == pair:
                    exists = True
        return exists

    def getPairNameInBitfinexRequest(self, pair1, pair2):
        with open('pairsBitfinexRequest.csv', newline='') as csvfile:
            pair = pair1 + pair2
            print(pair)
            reader = csv.reader(csvfile, delimiter=',')

            for row in reader:
                pairCheck = row[0]

                if ':' in pairCheck:
                    pairCheck1 = pairCheck.split(':')[0]
                    pairCheck2 = pairCheck.split(':')[1]
                    if pairCheck1 == pair1 and pairCheck2 == pair2:
                        pair = pairCheck1 + ':' + pairCheck2
                        return pair
                    elif pairCheck1 == pair1 and pair2 == 'USDT':
                        pair = pairCheck1 + ':' + 'UST'
                        return pair
                else:
                    if pairCheck == pair:
                        pair = pairCheck
                        return pair
                    else:
                        if pair1 in pairCheck:
                            pairSplit = pairCheck.split(pair1)[1]
                            if pair2 == 'USDT' and pairSplit == 'UST':
                                pair2 = 'UST'
                                pair = pair1 + pair2
                                return pair
                            elif pair2 == pairSplit:
                                pair = pair1 + pair2
                                return pair
                            elif pair2 == 'BUSD' or pairSplit == 'USDC':
                                pair = pair1 + 'USD'
                                return pair

            return pair

    def checkPairInCoinbasepro(self, pair):
        with open('pairsBinanceKrakenCoinbasepro.csv', newline='') as csvfile:
            exists = False
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                pairCheck = row[0]
                if pairCheck == pair:
                    exists = True
        return exists

    def checkMaxExchangePrice(self, **kwargs):
        maxPrice = 0
        exchange = ''
        for key, value in kwargs.items():
            if value is None:
                value = 0
            if value > maxPrice and value > 0:
                maxPrice = value
                exchange = key
        return exchange, maxPrice

    def checkMinExchangePrice(self, **kwargs):
        maxPrice = 0
        exchange = ''
        i = 0
        for key, value in kwargs.items():
            if value is None:
                value = 0
            if i == 0:
                maxPrice = value
                exchange = key
            else:

                if value < maxPrice and value > 0:
                    maxPrice = value
                    exchange = key
            i += 1
        return exchange, maxPrice

    def getPairsPrices(self, **kwargs):
        # Get the prices of the pairs in the exchanges
        exchangePrices = {}
        for key, value in kwargs.items():
            try:
                exchange = getattr(self, key.lower())
                price = exchange.getPrices(value)
                exchangePrices[key] = price
            except Exception as e:
                self.telegram.sendMessageDev(
                    f'Error getting price {key} - {value} - {e}')
                exchangePrices[key] = [0, 0]
                self.timeSleep += 3
        return exchangePrices

    def percentageDiffPrices(self, maxPrice, minPrice):
        percentage = ((maxPrice - minPrice) / minPrice) * 100
        return percentage

    def getAskPriceVolumeEffective(self, orderBook, volume, highPrice):
        highPrice = float(highPrice)
        priceList = []
        volumeList = []
        sumVol = 0
        orderCounter = 0

        for book in orderBook['asks']:
            if float(book[0]) < highPrice and float(book[0] != 0 and sumVol < volume):
                if sumVol + book[1] < volume:
                    if book[1] > (volume - sumVol):
                        volumeLeft = volume - sumVol
                        sumVol = volume
                        priceList.append(book[0])
                        volumeList.append(volumeLeft)
                    else:
                        sumVol += book[1]
                        priceList.append(book[0])
                        volumeList.append(book[1])
                else:
                    sumVol += book[1]
                    priceList.append(book[0])
                    volumeList.append(book[1])
            orderCounter += 1
        try:
            weigthed_avg = np.average(priceList, weights=volumeList)
        except:
            weigthed_avg = 0

        avgPriceEffective = weigthed_avg
        volumenEffective = sumVol
        return avgPriceEffective, volumenEffective

    def getBidPriceVolumeEffective(self, orderBook, volume, lowPrice):
        lowPrice = float(lowPrice)
        priceList = []
        volumeList = []
        sumVol = 0
        orderCounter = 0

        for book in orderBook['bids']:
            if float(book[0]) > lowPrice and float(book[0] != 0) and sumVol < volume:
                if sumVol + book[1] < volume:
                    if book[1] > (volume - sumVol):
                        volumeLeft = volume - sumVol
                        sumVol = volume
                        priceList.append(book[0])
                        volumeList.append(volumeLeft)
                    else:
                        sumVol += book[1]
                        priceList.append(book[0])
                        volumeList.append(book[1])
                else:
                    sumVol += book[1]
                    priceList.append(book[0])
                    volumeList.append(book[1])
            orderCounter += 1
        try:
            weigthed_avg = np.average(priceList, weights=volumeList)
        except:
            weigthed_avg = 0

        avgPriceEffective = weigthed_avg
        volumenEffective = sumVol
        return avgPriceEffective, volumenEffective

    def getPricesVolumeEffective(self, orderBook, volumen, lowPrice, highPrice):
        lowPrice = float(lowPrice)
        highPrice = float(highPrice)

        avgBidPriceEffective, bidVolumeEffective = self.getBidPriceVolumeEffective(
            orderBook, volumen, lowPrice)
        avgAskPriceEffective, askVolumeEffective = self.getAskPriceVolumeEffective(
            orderBook, volumen, highPrice)

        return avgBidPriceEffective, bidVolumeEffective, avgAskPriceEffective, askVolumeEffective

    def getProfit(self, avgAskPriceEffective, avgBidPriceEffective, volumenEffective):
        profit = round(
            (avgBidPriceEffective - avgAskPriceEffective) * volumenEffective, 2)
        return profit

    def checkPairBaseIsUSD(self, pair):
        if pair.split('/')[1] == 'USD' or pair.split('/')[1] == 'USDT' or pair.split('/')[1] == 'USDC' or pair.split('/')[1] == 'BUSD':
            return True
        else:
            return False

    def find_PairNet(self, data, search_string):
        with open(data, 'r') as file:
            for line in file:
                if search_string in line:
                    return line.split(";")[1].strip()
        return None
