import re
import pandas as pd

from Database.DBManager import DBManager
from vkbottle.bot import Bot, Message
from vkbottle import DocMessagesUploader

class AdminReplyMessageHandler:
    def __init__(self, bot: Bot, db: DBManager):
        self.bot = bot
        self.db = db

    async def admin_reply_command(self, message: Message):
        if message.reply_message.id:
            reply_id = message.reply_message.id

            reply_message = await self.db.get_admin_message_by_type(reply_id)

            if not reply_message or len(reply_message) < 3 or reply_message[2] is None:
                await message.answer('🤖На это сообщение нельзя ответить')
                return

            command = reply_message[2]
            print('Команда ' + command)
            command_map = {
                'отправить сообщение': self.handle_reply_send_message,
                'старосты': self.handle_group_leader,
                'подтвердить пользователя': self.handler_confirmed_user,
                'вопрос пользователя': self.handler_user_question,
                'сообщение админа': self.handler_excel,
                'воздушная тревога': self.handler_excel
            }

            if command in command_map:
                await command_map[command](message)
            else:
                await message.answer("🤖Неизвестный тип сообщения.")
        else:
            await message.answer("🤖Что-то пошла не так")

    async def handle_reply_send_message(self, message: Message):
        lines = message.text.split('\n', 1)

        if not message.text.strip():
            await message.answer("🤖Сообщение не должно быть пустым.")
            return
        elif len(lines) == 1 and not message.attachments:
            await message.answer("🤖Для одного текстового блока необходимо приложить вложение.")
            return

        command_line = lines[0].split()
        text = lines[1]

        command = command_line[0].lower()
        command_parameters = [int(command_parameters) for command_parameters in command_line[1:]]

        user_data = []

        '''
        attachments_list = []

        for attachment in message.attachments:
            if attachment.photo:
                owner_id = attachment.photo.owner_id
                media_id = attachment.photo.id
                access_key = attachment.photo.access_key

                attachment_str = f"photo{owner_id}_{media_id}"
                if access_key:
                    attachment_str += f"_{access_key}"
                attachments_list.append(attachment_str)
            elif attachment.doc:
                owner_id = attachment.doc.owner_id
                media_id = attachment.doc.id
                access_key = attachment.doc.access_key

                attachment_str = f"doc{owner_id}_{media_id}"
                if access_key:
                   attachment_str += f"_{access_key}"

                attachments_list.append(attachment_str)

        attachments_str = ','.join(attachments_list)
        '''

        if 'всем' == command:
            users = await self.db.get_all_users_with_confirmed(True)
            print(users)
            for user in users:
                user_feed_id = user[0]

                message_id = await self.bot.api.messages.send(
                    peer_id=user_feed_id,
                    message='📢' + str(text),
                    #attachment = attachments_str,
                    random_id=0
                )

                user_data.append((user_feed_id, message_id))

        elif 'курс' == command:
            if len(command_parameters) == 0:
                await message.answer("🤖Вы не выбрали каким курса отправить сообщение")
                return

            users = await self.db.get_users_by_courses(command_parameters, True)
            for user in users:
                user_feed_id = user[0]
                message_id = await self.bot.api.messages.send(
                    peer_id=user_feed_id,
                    message='📢' + text,
                    #attachment=attachments_str,
                    random_id=0
                )
                user_data.append((user_feed_id, message_id))
        elif 'группа' == command:
            if len(command_parameters) == 0:
                await message.answer("🤖Вы не выбрали каким группам отправить сообщение")
                return

            group_pattern = r'\d+\.\s*(.+)'
            groups = re.findall(group_pattern, message.reply_message.text)

            users = await self.db.get_users_by_group(groups, True)
            for user in users:
                user_feed_id = user[0]
                message_id = await self.bot.api.messages.send(
                    peer_id=user_feed_id,
                    message='📢' + text,
                    #attachment=attachments_str,
                    random_id=0
                )
                user_data.append((user_feed_id, message_id))
        else:
            await message.answer("🤖Команда не распознана")
            return

        await self.db.add_admin_user_message(message.id, "сообщение админа", user_data,
                                             'сообщение админа')
        await message.answer("🤖Ваше сообщение отправлено")

    async def handle_group_leader(self, message: Message):
        lines = message.text.split('\n', 1)

        if len(lines) == 0:
            await message.answer("🤖Вы не написали сообщение")

        command_line = lines[0].split()

        command = command_line[0]
        command_parameters = None
        if len(command_line) > 1:
            try:
                command_parameters = int(command_line[1])
            except ValueError:
                await message.answer('🤖Вы не верно указали id')
                return
        else:
            await message.answer('🤖Вы не указали id')
            return

        if command.lower() == 'удалить':
            if len(lines) != 1:
                await message.answer("🤖Некорректное сообщение")
                return

            await self.db.delete_user(command_parameters)
            await message.answer('🤖Пользователь удален')
            await self.bot.api.messages.send(
                peer_id=command_parameters,
                message='⚠Вы были удалены администратором',
                random_id=0
            )
        elif command.lower() == 'изменить':
            if len(lines) != 2:
                await message.answer("🤖Вы не написали группу")
                return

            pattern = r'^[а-яё]+/[а-яё]+-\d{2}-\d{1,2}-[а-яё]+$'
            user_group = lines[1].lower()
            print('Группа ' + user_group)
            if re.match(pattern, user_group):
                print(f'Группа написана корректно {user_group}, id пользователя {command_parameters}')
                await self.db.update_user_group(command_parameters, user_group)
                await message.answer('🤖Группа пользователя изменена')
            else:
                await message.answer('🤖Не корректный ввод группы')
                return

            await self.bot.api.messages.send(
                peer_id=command_parameters,
                message=f'⚠Администратор изменил вашу группу на {user_group}',
                random_id=0
            )
        elif command.lower() == 'подтвердить':
            await self.db.update_user_confirmed(command_parameters, True)
            await message.answer('🤖Пользователь подтвержден')
            await self.bot.api.messages.send(
                peer_id=command_parameters,
                message='⚠Ваш аккаунт был подтвержден администратором',
                random_id=0
            )

    async def handler_confirmed_user(self, message: Message):
        lines = message.text.split('\n', 1)

        if len(lines) == 0:
            await message.answer("🤖Вы не написали сообщение")

        command_line = lines[0].split()

        command_parameters = None
        if len(command_line) > 1:
            try:
                command_parameters = int(command_line[1])
            except ValueError:
                await message.answer('🤖Вы не верно указали id')
                return
        else:
            await message.answer('🤖Вы не указали id')
            return

        await self.db.update_user_confirmed(command_parameters, True)
        await message.answer('🤖Пользователь подтвержден')
        await self.bot.api.messages.send(
            peer_id=command_parameters,
            message='⚠Ваш аккаунт был подтвержден администратором',
            random_id=0
        )

    async def handler_user_question(self, message: Message):

        message_history = await self.db.get_admin_user_message_by_amdin_message(message.reply_message.id)
        print(message_history)

        user_peer_id = message_history[0][1]
        reply_to_user_message = message_history[0][0]

        print("User_peer_id " + str(user_peer_id))
        print('reply_to_user_message '+ str(reply_to_user_message))

        user_message_id = await self.bot.api.messages.send(
            peer_id=user_peer_id,#узнать пользователя
            message=f'✅Ответ администратора:\n' + message.text,
            random_id=0,
            reply_to=reply_to_user_message
        )

        print('user_message_id ' + str(user_message_id))

        await self.db.add_admin_user_message(message.id,None,
                                             [(user_peer_id, user_message_id)],
                                             'ответ администратора')
        await message.answer('🤖Ваш ответ отправлен')


    async def handler_excel(self, message: Message):
        if not message.text.strip():
            await message.answer("🤖Сообщение не должно быть пустым.")
            return

        command = message.text.lower()

        if command != 'excel':
            await message.answer('Команда не распознана')

        message_historys = await self.db.get_admin_user_message_by_amdin_message(message.reply_message.id)

        print('message_historys '+ str(message_historys))
        data = []
        for message_history in message_historys:
            user_reply_id = message_history[0]
            user_feed_id = message_history[1]
            user_message_reply = await self.db.get_user_message_by_reply_id(user_reply_id, user_feed_id)
            if not user_message_reply:
                continue

            print('user_message_reply ' + str(user_message_reply))
            response = await self.bot.api.messages.get_by_id(message_ids=[user_message_reply[0]])
            user_group = await self.db.get_user_by_id(user_feed_id)
            data.append((user_group, response.items[0].text))

        groups = []
        comments = []

        for ((id_value, group_name, number), comment) in data:
            groups.append(group_name)  # Добавляем названия групп
            comments.append(comment)  # Добавляем комментарии

        # Создаем DataFrame
        df = pd.DataFrame({
            'Группа': groups,
            'Ответ': comments
        })

        excel_file_path = f'{message_historys[0][2].replace(" ", "_")}_{message_historys[0][6].replace(" ", "_").replace(":", "-")}.xlsx'
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Лист1')

        # Создаем uploader для отправки документа
        uploader = DocMessagesUploader(self.bot.api)

        print(excel_file_path)
        doc = await uploader.upload(peer_id=message.peer_id, file_source='./' + excel_file_path)

        await message.answer(attachment=doc)

        import os
        os.remove(excel_file_path)