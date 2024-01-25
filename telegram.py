import requests
import config


def sendTelegram(message, listChatId):
    for chatId in listChatId:
        requests.post(
            f'https://api.telegram.org/bot{config.TG_BOT_TOKEN}/sendMessage?chat_id={chatId}&text={message}')


def sendTelegramArbitrageBotOk(message):
    requests.post(
        f'https://api.telegram.org/bot{config.TG_BOT_TOKEN}/sendMessage?chat_id={config.TG_CHAT_ID_DEV}&text={message}')


def getChatIdByGroupName(groupName):
    url = f'https://api.telegram.org/bot{config.TG_BOT_TOKEN}/getChat?chat_id=@{groupName}'


class Telegram:
    def __init__(self, listChatID, chat_dev, token):
        self.token = token
        self.listChatID = listChatID
        self.chat_dev = chat_dev

    def sendMessage(self, message):
        for chatId in self.listChatID:
            url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chatId}&text={message}'
            requests.post(url)

    def sendMessageDev(self, message):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={self.chat_dev}&text={message}'
        requests.post(url)


# Check updates bot
url = f"https://api.telegram.org/bot{config.TG_BOT_TOKEN}/getUpdates"
print(requests.get(url).json())
