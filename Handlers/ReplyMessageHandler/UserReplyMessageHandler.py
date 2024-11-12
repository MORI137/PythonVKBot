from vkbottle.bot import Bot, Message
from vkbottle_types.codegen.objects import UsersFields

from Database.DBManager import DBManager
import re

from config import admin


class UserReplyMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def user_reply_command(self, message: Message):
        if message.reply_message.id is not None:
            reply_id = message.reply_message.id
            user_message = await self.db.get_user_message_by_message_id(reply_id, message.peer_id)

            if user_message is None or len(user_message) < 3 or user_message[2] is None:
                await message.answer('🤖На это сообщение нельзя ответить')
                return

            message_type = user_message[2]

            command_map = {
                "обратная связь": self.handle_feedback_reply,
                "воздушная тревога": self.handle_air_alert_reply,
                "зарегистрироваться": self.handle_registration,
                "сообщение админа": self.handle_reply_to_admin_message,
                'ответ администратора': self.handle_reply_to_admin_message_feedback
            }

            if message_type in command_map:
                await command_map[message_type](message)
            else:
                await message.answer("🤖Неизвестный тип сообщения.")
        else:
            await message.answer("🤖Это не ответ на сообщение.")

    async def handle_feedback_reply(self, message: Message):
        user = await self.db.get_user_by_id(message.peer_id)

        response = await self.bot.api.users.get(user_ids=message.peer_id,
                                                fields=[UsersFields.FIRST_NAME_NOM, UsersFields.LAST_NAME_NOM])
        if response is None:
            await message.answer('🤖Не получилось отправить сообщение.')

        admin_message_id = await self.bot.api.messages.send(
            peer_id=admin,
            message=f'❓Вам написал староста группы {user[1]}:\n' + message.text,
            random_id=0
        )

        await self.db.add_admin_user_message(admin_message_id, 'вопрос пользователя',
                                             [(message.peer_id, message.id)],
                                             None)

        await message.answer('🤖Сообщение отправлено')

    async def handle_registration(self, message: Message):
        user = await self.db.get_user_by_id(message.peer_id)
        if user is not None:
            await message.answer('Вы уже зарегистрированы.')
            return

        pattern = r'^[а-яё]+/[а-яё]+-\d{2}-\d{1,2}-[а-яё]+$'
        user_group = message.text.lower()
        if re.match(pattern, user_group):
            response = await self.bot.api.users.get(user_ids=message.peer_id,
                                                    fields=[UsersFields.FIRST_NAME_NOM, UsersFields.LAST_NAME_NOM])
            if response is None:
                await message.answer('Не удалось отправить заявку')
                return

            await self.db.add_user(message.peer_id, user_group)
            sent_message = await self.bot.api.messages.send(
                    peer_id=admin,
                    message=f'Пользователь {message.peer_id} {response[0].first_name} {response[0].last_name} из группы {user_group} хочет добавиться',
                    random_id=0
                    )
            await self.db.add_admin_message(sent_message, 'подтвердить пользователя')
            await message.answer('Ваша заявка отправлена на рассмотрение.')
        else:
            await message.answer('Упс, похоже вы неправильно ввели группу. Повторите попытку.')


    async def handle_air_alert_reply(self, message: Message):
        user_message = await self.db.get_user_message_by_reply_id(message.reply_message.id,
                                                                               message.peer_id)
        print('handle_air_alert_reply User_message ' + str(user_message))
        if user_message is not None:
            print('Старое удалилось')
            await self.db.delete_user_message(message.peer_id, user_message[0])

        await self.db.add_user_message(message.id, message.peer_id,
                                       'ответ воздушная тревога', message.reply_message.id)
        await message.answer(f'🤖Ваш ответ отправлен')


    async def handle_reply_to_admin_message(self, message: Message):
        user_message = await self.db.get_user_message_by_reply_id(message.reply_message.id,
                                                                  message.peer_id)

        if user_message is not None:
            await self.db.delete_user_message(message.peer_id, user_message[0])

        await self.db.add_user_message(message.id, message.peer_id,
                                       'ответ сообщение администратора', message.reply_message.id)
        await message.answer(f'🤖Ваш ответ отправлен')

    async def handle_reply_to_admin_message_feedback(self, message: Message):

        response = await self.bot.api.users.get(user_ids=message.peer_id,
                                                fields=[UsersFields.FIRST_NAME_NOM, UsersFields.LAST_NAME_NOM])
        if response is None:
            await message.answer('🤖Не получилось отправить сообщение.')

        message_history = await self.db.get_admin_user_message_by_user_message(message.reply_message.id, message.peer_id)

        admin_peer_id = message_history[0][4]
        reply_to_admin_message = message_history[0][3]

        print("User_peer_id " + str(admin_peer_id))
        print('reply_to_user_message ' + str(reply_to_admin_message))

        user = await self.db.get_user_by_id(message.peer_id)

        admin_message_id = await self.bot.api.messages.send(
            peer_id=admin_peer_id,
            message=f'❓Вам написал староста группы {user[1]}:\n' + message.text,
            random_id=0,
            reply_to=reply_to_admin_message
        )

        print('user_message_id ' + str(admin_message_id))

        await self.db.add_admin_user_message(admin_message_id, 'вопрос пользователя',
                                             [(message.peer_id, message.id)],
                                             None)
        await message.answer(f'🤖Ваш ответ отправлен')