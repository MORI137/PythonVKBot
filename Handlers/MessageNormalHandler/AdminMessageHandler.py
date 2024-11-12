from datetime import datetime
from vkbottle_types.codegen.objects import UsersFields
from Database.DBManager import DBManager
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor


class AdminMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def admin_command(self, message: Message):
        command_map = {
            "Начать": self.handle_start,
            "Воздушная тревога": self.handle_emergency_alert,
            "Отправить сообщение": self.handle_send_message,
            "Помощь": self.handle_help,
            "Старосты": self.handle_group_leader,
        }

        command = message.text
        if command in command_map:
            await command_map[command](message)
        else:
            await message.answer("🤖Неизвестная команда. Пожалуйста, выберите действие из клавиатуры.",
                                 keyboard=self.create_keyboard())

    async def handle_start(self, message):
        await message.answer("Старт", keyboard=self.create_keyboard())

    async def handle_emergency_alert(self, message: Message):
        users = await self.db.get_all_users(True)
        user_data = []

        for user in users:
            user_feed_id = user[0]

            message_id = await self.bot.api.messages.send(
                peer_id=user_feed_id,
                message="🚨🚨🚨Внимание всем. Воздушная тревога.",
                random_id=0
            )
            print((user_feed_id, message_id))
            user_data.append((user_feed_id, message_id))
            print(user_data)

        admin_message_id = await message.answer("🤖Сообщение о воздушной тревоге отправлено")
        await self.db.add_admin_user_message(admin_message_id.message_id,
                                             "воздушная тревога",
                                             user_data,
                                             'воздушная тревога')


    async def handle_send_message(self, message: Message):
        users = await self.db.get_all_users(True)

        message_text = '🤖Выберите группы/курсы\n' + self.group_by_course(users)

        sent_message = await message.answer(message_text)
        await self.db.add_admin_message(sent_message.message_id, 'отправить сообщение')

    async def handle_help(self, message):
        await message.answer("Помощь")

    async def handle_group_leader(self, message: Message):
        users = await self.db.get_all_users()
        user_ids = [user[0] for user in users]

        response = await self.bot.api.users.get(user_ids=user_ids, fields=[UsersFields.FIRST_NAME_NOM, UsersFields.LAST_NAME_NOM])
        user_details = {user.id: f"{user.last_name} {user.first_name}" for user in response}
        merged_data = []

        for index, user in enumerate(users, start=0):
            user_id = user[0]
            group_name = user[1]
            is_confirmed = user[2]

            full_name = user_details.get(user_id, "Неизвестный пользователь")

            if is_confirmed:
                merged_data.append(f"{index+1}. {group_name} {full_name} {user_id}")  # Без статуса
            else:
                merged_data.append(f"{index+1}. {group_name} {full_name} {user_id} Не подтвержден")

        merged_data_string = "\n".join(merged_data)
        sent_message = await message.answer('🤖\n'+ merged_data_string)
        await self.db.add_admin_message(sent_message.message_id, 'старосты')


    def create_keyboard(self):
        keyboard = Keyboard(one_time=False)

        keyboard.add(Text("Воздушная тревога"), color=KeyboardButtonColor.NEGATIVE)
        keyboard.row()
        keyboard.add(Text("Отправить сообщение"), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        keyboard.add(Text("Старосты"), color=KeyboardButtonColor.POSITIVE)
        keyboard.add(Text("Помощь"), color=KeyboardButtonColor.SECONDARY)

        return keyboard

    def group_by_course(self, users):
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Функция для вычисления курса
        def calculate_course(group_year):
            if current_month <= 8:
                return current_year - group_year
            else:
                return current_year - group_year + 1

        groups = sorted(set([user[1] for user in users]))

        groups_by_course = {}
        for group in groups:
            # Извлекаем курс: последние две цифры до "о"
            group_year = 2000 + int(group.split('-')[1])
            course = calculate_course(group_year)
            if course not in groups_by_course:
                groups_by_course[course] = []
            groups_by_course[course].append(group)

        # Формируем текст вывода
        message_text = ""
        counter = 1
        for course in sorted(groups_by_course.keys()):
            message_text += f"{course} курс\n"
            course_groups = groups_by_course[course]

            for i in range(0, len(course_groups), 2):
                if i + 1 < len(course_groups):
                    message_text += f"{counter}. {course_groups[i]}  {counter + 1}. {course_groups[i + 1]}\n"
                    counter += 2
                else:
                    message_text += f"{counter}. {course_groups[i]}\n"
                    counter += 1

        return message_text.strip()