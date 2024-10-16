from Database.DBManager import DBManager
from vkbottle.bot import Bot, Message

class AdminReplyMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def admin_reply_command(self, message: Message):
        # Проверяем, есть ли reply_message
        if message.reply_message:
            reply_id = message.reply_message.conversation_message_id
            chat_id = message.chat_id

            # Получаем тип сообщения из базы данных
            message_type = await self.db.get_message_type(reply_id, chat_id)

            # В зависимости от типа вызываем нужные методы
            if message_type == "всем":
                await self.handle_reply_to_all(message)
            elif message_type == "курсам":
                await self.handle_reply_to_courses(message)
            elif message_type == "группам":
                await self.handle_reply_to_groups(message)
            elif message_type == "добавление админа":
                await self.handle_add_admin_reply(message)
            elif message_type == "удаление админа":
                await self.handle_remove_admin_reply(message)
            elif message_type == "изменить старосту":
                await self.handle_change_monitor_reply(message)
            elif message_type == "удалить старосту":
                await self.handle_remove_monitor_reply(message)
            else:
                await message.answer("Неизвестный тип сообщения.")
        else:
            await message.answer("Это не ответ на сообщение.")

    # Методы для обработки ответов в зависимости от типа
    async def handle_reply_to_all(self, message: Message):
        await message.answer("Ответ для всех получен.")

    async def handle_reply_to_courses(self, message: Message):
        await message.answer("Ответ для курсов получен.")

    async def handle_reply_to_groups(self, message: Message):
        await message.answer("Ответ для групп получен.")

    async def handle_add_admin_reply(self, message: Message):
        await message.answer("Ответ на запрос о добавлении админа получен.")

    async def handle_remove_admin_reply(self, message: Message):
        await message.answer("Ответ на запрос о удалении админа получен.")

    async def handle_change_monitor_reply(self, message: Message):
        await message.answer("Ответ на запрос о изменении старосты получен.")

    async def handle_remove_monitor_reply(self, message: Message):
        await message.answer("Ответ на запрос о удалении старосты получен.")