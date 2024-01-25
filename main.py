import bot
import csv
import numpy as np
from threading import Thread
import telegram as tg
import config


def getPairList(file):
    listPairs = []
    with open(file, 'r') as file:
        reader = csv.reader(file, delimiter=' ')
        for pair in reader:
            newSymbol = str(pair)[2:-2]
            listPairs.append(newSymbol)

    return listPairs


def splitPairList():
    pairList = getPairList('pairsBinanceKraken.csv')
    lists = np.array_split(pairList, 12)
    return lists


if __name__ == '__main__':
    lists = splitPairList()
    tg.sendTelegramArbitrageBotOk(config.BOT_MESSAGE_START)

    threads = []

    for i, lst in enumerate(lists):
        t = Thread(target=bot.Bot().start, args=(lst,), name=f't{i+1}')
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    tg.sendTelegramArbitrageBotOk(config.BOT_MESSAGE_STOP)
