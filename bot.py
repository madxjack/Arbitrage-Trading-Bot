import exchange as ex
import snitch
import telegram as tg
from datetime import datetime, timedelta
import ccxt
import threading
import config


class Bot:
    def __init__(self):
        self.binance = ex.Exchange(ccxt.binance(
            {'enableRateLimit': True,
                'rateLimit': 2000,
             }
        ))
        self.kukoin = ex.Exchange(ccxt.kucoin(
            {'enableRateLimit': True,
                'rateLimit': 2000,
             }
        ))
        self.kraken = ex.Exchange(ccxt.kraken(
            {'enableRateLimit': True,
                'rateLimit': 2000,
             }
        ))
        self.coinbasepro = ex.Exchange(ccxt.coinbasepro(
            {'enableRateLimit': True,
                'rateLimit': 2000,
             }
        ))
        self.pairsBanned = []
        self.pairsBannedInitialDate = []
        self.telegram = tg.Telegram(
            config.TG_CHAT_ID_TRIAL, config.TG_CHAT_ID_DEV, config.TG_BOT_TOKEN)
        self.timeSleep = 0

    def start(self, pairs):
        thread = threading.current_thread()
        startDate = datetime.now()
        while True:
            for pair in pairs:
                try:
                    # print(pair)
                    nowDate = datetime.now()
                    if (startDate + timedelta(minutes=60) < nowDate) and (pair == '1INCH/USD' and thread.name == 't1'):
                        startDate = nowDate
                        self.telegram.sendMessageDev(
                            config.BOT_MESSAGE_RUNNING)

                    snitchInstance = snitch.Snitch(pair, self.pairsBanned, self.pairsBannedInitialDate,
                                                   self.binance, self.kraken, self.kukoin, self.coinbasepro, self.timeSleep)
                    snitchInstance.start()
                    self.pairsBanned = snitchInstance.pairsBanned
                    self.timeSleep = snitchInstance.timeSleep

                except Exception as e:
                    # Si salta una excepcion en el la funcion main chivato(), y es un error de no existir
                    # el pair en binance, lo elimina del csv pairs.csv y lo añade a errBinance.csv
                    errMessage = 'Error Arbitrage Bot main: ' + str(e)
                    self.telegram.sendMessageDev(errMessage)
