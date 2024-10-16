from vkbottle.bot import Bot
from Handlers.MessageNormalHandler.MessageHandler import MessageHandler

class VKBot:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.message_handler = MessageHandler(self.bot)
        self.bot.run_forever()

