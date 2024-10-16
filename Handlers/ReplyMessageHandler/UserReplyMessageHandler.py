from vkbottle.bot import Bot, Message
from Database.DBManager import DBManager
import re

class UserReplyMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def user_reply_command(self, message: Message):
        if message.reply_message:
            reply_id = message.reply_message.id

            message_type = await self.db.get_message_type(message_id=reply_id, chat_id=message.from_id)

            if message_type == "обратная связь":
                await self.handle_feedback_reply(message)
            elif message_type == "воздушная тревога":
                await self.handle_air_alert_reply(message)
            elif message_type=="зарегистрироваться":
                await  self.handle_registration(message)
            else:
                await message.answer("Неизвестный тип сообщения.")
        else:
            await message.answer("Это не ответ на сообщение.")

    async def handle_feedback_reply(self, message: Message):
        await message.answer("Ответ на обратную связь получен.")

    async def handle_registration(self, message: Message):
        pattern = r'^[а-яё]+/[а-яё]+-\d{2}-\d{1,2}-[а-яё]+$'
        user_group = message.text.lower()
        if re.match(pattern, user_group):
            await self.db.add_user(message.from_id, user_group)
            await message.answer('Ваша заявка отправлена на рассмотрение.')
        else:
            await message.answer('Упс, похоже вы неправильно ввели группу. Повторите попытку.')


    async def handle_air_alert_reply(self, message: Message):
        await message.answer("Ответ на воздушную тревогу получен.")