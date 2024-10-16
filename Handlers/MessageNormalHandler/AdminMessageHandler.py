from Database.DBManager import DBManager
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor


class AdminMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db
        self.main_admin = None

    async def init(self):
        self.main_admin = await self.db.get_main_admin()

    async def admin_command(self, message: Message):
        command_map = {
            "Начать": self.handle_start,
            "Воздушная тревога": self.handle_emergency_alert,
            "Отправить сообщение": self.handle_send_message,
            "Помощь": self.handle_help,
            "Старосты": self.handle_stars,
        }

        command = message.text
        if command in command_map:
            await command_map[command](message)
        else:
            await message.answer("Неизвестная команда. Пожалуйста, выберите действие из клавиатуры.",
                                 keyboard=self.create_keyboard())

    async def handle_start(self, message):
        await message.answer("Старт", keyboard=self.create_keyboard())

    async def handle_emergency_alert(self, message):
        users = await self.db.get_all_users()

        await message.answer("Сообщение о воздушной тревоге отправлено")



    async def handle_send_message(self, message):
        await message.answer("Введите сообщение для отправки всем:")
        # Здесь можно добавить логику для отправки сообщения всем

    async def handle_help(self, message):
        await message.answer("Помощь")
        # Здесь можно добавить дополнительную информацию о помощи

    async def handle_stars(self, message):
        await message.answer("Информация о старостах...")

    async def add_admin_command(self, message: Message):
        if message.from_id != self.main_admin:
            await message.answer("У вас нет прав для добавления администраторов.")
            return

        user_id = message.text.split()[1]
        try:
            user_id = int(user_id)
            await self.db.add_admin(user_id)
            await message.answer(f"Пользователь {user_id} добавлен как администратор.")
        except (ValueError, IndexError):
            await message.answer("Пожалуйста, укажите корректный ID пользователя.")

    async def remove_admin_command(self, message: Message):
        if message.from_id != self.main_admin:
            await message.answer("У вас нет прав для удаления администраторов.")
            return

        user_id = message.text.split()[1]
        try:
            user_id = int(user_id)
            await self.db.remove_admin(user_id)
            await message.answer(f"Пользователь {user_id} удален из администраторов.")
        except (ValueError, IndexError):
            await message.answer("Пожалуйста, укажите корректный ID пользователя.")

    def create_keyboard(self):
        keyboard = Keyboard(one_time=False)

        keyboard.add(Text("Воздушная тревога"), color=KeyboardButtonColor.NEGATIVE)
        keyboard.row()
        keyboard.add(Text("Отправить сообщение"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Старосты"), color=KeyboardButtonColor.POSITIVE)
        #keyboard.row()
        keyboard.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)

        return keyboard