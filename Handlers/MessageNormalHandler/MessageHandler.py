from vkbottle.bot import Bot, Message
from Handlers.MessageNormalHandler.AdminMessageHandler import AdminMessageHandler
from Database.DBManager import DBManager
from Handlers.ReplyMessageHandler.AdminReplyMessageHandler import AdminReplyMessageHandler
from Handlers.ReplyMessageHandler.UserReplyMessageHandler import UserReplyMessageHandler
from Handlers.MessageNormalHandler.UserMessageHandler import UserMessageHandler

class MessageHandler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = DBManager()
        self.admin_message_handler = AdminMessageHandler(bot, self.db)
        self.admin_message_handler.init()
        self.admin_reply_message_handler = AdminReplyMessageHandler(bot, self.db)

        self.user_message_handler = UserMessageHandler(bot, self.db)
        self.user_reply_message_handler = UserReplyMessageHandler(bot, self.db)

        self._register_handlers()


    def _register_handlers(self):
        @self.bot.on.message()
        async def handle_message(message: Message):
            if message.reply_message:
                await self._handle_reply_message(message)
            else:
                await self._handle_normal_message(message)

    async def _handle_normal_message(self, message: Message):
        if self.db.is_admin(message.from_id):
            await self.admin_message_handler.admin_command(message)
        else:
            await self.user_message_handler.user_command(message)

    async def _handle_reply_message(self, message: Message):
        if self.db.is_admin(message.from_id):
            await self.admin_reply_message_handler.admin_reply_command(message)
        else:
            await self.user_reply_message_handler.user_reply_command(message)
