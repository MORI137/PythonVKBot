from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
from Database.DBManager import DBManager


class UserMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def user_command(self, message: Message):
        command_map = {
            "Начать": self.handle_start,
            "Обратная связь": self.handle_feedback,
            "Помощь": self.handle_help,
        }

        command = message.text
        if command in command_map:
            if command == 'Обратная связь':
                user = await self.db.get_user_by_id(message.peer_id)
                if user is None:
                    await message.answer('🤖Прежде чем отправить сообщение вам необходимо зарегистрироваться')
                    return
            await command_map[command](message)
        else:
            await message.answer("🤖Неизвестная команда. Пожалуйста, выберите действие из клавиатуры.", keyboard=self.create_keyboard())

    async def handle_start(self, message: Message):
        sent_message = await message.answer("Добро пожаловать. Введите пожалуйста свою группу.", keyboard=self.create_keyboard())
        await self.db.add_user_message(sent_message.message_id, message.peer_id, 'зарегистрироваться')

    async def handle_feedback(self, message: Message):
        send_message = await message.answer("🤖Напишите ваше сообщение:")
        await self.db.add_user_message(send_message.message_id, message.peer_id, "обратная связь")

    async def handle_help(self, message: Message):
        await message.answer("Помощь")

    def create_keyboard(self):
        keyboard = Keyboard(one_time=False)

        keyboard.add(Text("Обратная связь"), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)

        return keyboard