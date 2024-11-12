import aiosqlite
from datetime import datetime
from config import db_path
from config import admin

class DBManager:

    def is_admin(self, feed_id):
        return feed_id == admin

    async def get_users_by_courses(self, courses, is_confirmed = None):
        if not courses:
            return []

        current_year = datetime.now().year
        year_map = {5: current_year - 4, 4: current_year - 3, 3: current_year - 2, 2: current_year - 1}

        like_conditions = []
        for course in courses:
            if course in year_map:
                year_admitted = year_map[course] - 2000
                like_conditions.append(f"group_name LIKE '%-{year_admitted}-%'")

        where_clause = " OR ".join(like_conditions)
        query = f"SELECT * FROM users WHERE ({where_clause})"#СКОБКИ МОГУТ ПОЛОМАТЬ

        if is_confirmed is not None:
            query += f' AND is_confirmed = {is_confirmed}'

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            users = await cursor.fetchall()

        return users

    async def get_users_by_group(self, group: list, is_confirmed = None):
        if not group:
            return []

        placeholders = ', '.join('?' for _ in group)
        query = f"SELECT * FROM users WHERE group_name IN ({placeholders})"

        if is_confirmed is not None:
            query += f' AND is_confirmed = {is_confirmed}'

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query, group)
            return await cursor.fetchall()

    async def update_user_group(self, user_id, group):
        query = f"UPDATE users SET group_name = '{group}' WHERE user_feed_id = {user_id}"

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query)
            await db.commit()

    async def update_user_confirmed(self, user_id, is_confirmed):
        async with aiosqlite.connect(db_path) as db:
            query_update = "UPDATE users SET is_confirmed = ? WHERE user_feed_id = ?"
            await db.execute(query_update, (is_confirmed, user_id))
            await db.commit()

    async def get_user_by_id(self, user_id, is_confirmed = None):
        query = f"SELECT * FROM users WHERE user_feed_id = {user_id}"
        if is_confirmed is not None:
            query += f' AND is_confirmed = {is_confirmed}'

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchone()

    async def get_all_users(self, is_confirmed = None):
        query = "SELECT * FROM users"
        if is_confirmed is not None:
            query += f' WHERE is_confirmed = {is_confirmed}'

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchall()

    async def get_all_users_with_confirmed(self, is_confirmed):
        query = f"SELECT * FROM users WHERE is_confirmed = {is_confirmed}"

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchall()

    async def get_admin_message_by_type(self, message_id):
        query = f"SELECT * FROM admin_message WHERE admin_feed_id = {admin} AND admin_message_id = {message_id}"

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchone()

    async def get_user_message_by_message_id(self, message_id, feed_id):
        query = f"SELECT * FROM user_message WHERE user_feed_id = {feed_id} AND user_message_id = {message_id}"
        print(query)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchone()

    async def get_user_message_by_reply_id(self, reply_id, feed_id):
        query = f"SELECT * FROM user_message WHERE user_feed_id = {feed_id} AND user_message_reply_id = {reply_id}"
        print(query)
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query)
            return await cursor.fetchone()

    async def add_user(self, user_id, group):
        query_insert = "INSERT INTO users (user_feed_id, group_name, is_confirmed) VALUES (?, ?, ?)"

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query_insert, (user_id, group, False))
            await db.commit()

    async def add_user_message(self, message_id, feed_id, message_type, user_message_reply_id = None):
        query = "INSERT INTO user_message(user_message_id, user_feed_id, message_type, user_message_reply_id) VALUES (?, ?, ?, ?)"

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query, (message_id, feed_id, message_type, user_message_reply_id,))
            await db.commit()

    async def add_admin_message(self, message_id, message_type):
        query = "INSERT INTO admin_message(admin_message_id, admin_feed_id, message_type) VALUES (?, ?, ?) "

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query, (message_id, admin, message_type))
            await db.commit()

    async def add_admin_user_message(self, message_admin_id, admin_type_message, users_data, user_type_message):
        await self.add_admin_message(message_admin_id, admin_type_message)

        sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('add_admin_user_message users_data: ' + str(users_data))

        # Открываем соединение с базой данных
        async with aiosqlite.connect(db_path) as db:
            await db.execute("PRAGMA busy_timeout = 30000")  # Устанавливаем таймаут

            # Подготовка данных для вставки в admin_user_message
            admin_user_message_data = []

            for user_feed_id, user_message_id in users_data:
                print('user_feed_id: ' + str(user_feed_id))
                print('user_message_id: ' + str(user_message_id))
                await self.add_user_message(user_message_id, user_feed_id, user_type_message)

                # Собираем данные для пакетной вставки
                admin_user_message_data.append((user_message_id, user_feed_id, message_admin_id, admin, sent_time))

            # Выполняем пакетную вставку в admin_user_message
            await db.executemany(""" 
                    INSERT INTO admin_user_message (user_message_id, user_feed_id, admin_message_id, admin_feed_id, sent_time)
                    VALUES (?, ?, ?, ?, ?)
                """, admin_user_message_data)

            # Коммит изменений
            await db.commit()
        '''
        await self.add_admin_message(message_admin_id, admin_type_message)

        sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('add_admin_user_message users_data' + str(users_data))
        for user_feed_id, user_message_id  in users_data:
            print('user_feed_id' + str(user_feed_id))
            print('user_message_id' + str(user_message_id))
            await self.add_user_message(user_message_id, user_feed_id, user_type_message)
            async with aiosqlite.connect(db_path) as db:
                await db.execute("""
                    INSERT INTO admin_user_message (user_message_id, user_feed_id, admin_message_id, admin_feed_id, sent_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_message_id, user_feed_id, message_admin_id, admin, sent_time))

        await db.commit()
        '''

    async def delete_user(self, user_id):
        query = f"DELETE FROM users WHERE user_feed_id = {user_id}"

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query)
            await db.commit()

    async def delete_user_message(self, user_feed_id, user_message_id):
        query = f"DELETE FROM user_message WHERE user_message_id = {user_message_id} AND user_feed_id = user_feed_id"

        async with aiosqlite.connect(db_path) as db:
            await db.execute(query)
            await db.commit()

    async def get_admin_user_message_by_amdin_message(self, admin_message_id):
        query = '''
                SELECT aum.user_message_id, aum.user_feed_id, um.message_type AS user_message_type,
                       aum.admin_message_id, aum.admin_feed_id, am.message_type AS admin_message_type,
                       aum.sent_time
                FROM admin_user_message aum
                INNER JOIN user_message um
                    ON aum.user_message_id = um.user_message_id
                    AND aum.user_feed_id = um.user_feed_id
                INNER JOIN admin_message am
                    ON aum.admin_message_id = am.admin_message_id
                    AND aum.admin_feed_id = am.admin_feed_id
                WHERE aum.admin_message_id = ? AND aum.admin_feed_id = ?
            '''

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query, (admin_message_id, admin,))
            return await cursor.fetchall()


    async def get_admin_user_message_by_user_message(self, user_message_id, user_feed_id):
        query = '''
                SELECT aum.user_message_id, aum.user_feed_id, um.message_type AS user_message_type,
                       aum.admin_message_id, aum.admin_feed_id, am.message_type AS admin_message_type,
                       aum.sent_time
                FROM admin_user_message aum
                INNER JOIN user_message um
                    ON aum.user_message_id = um.user_message_id
                    AND aum.user_feed_id = um.user_feed_id
                INNER JOIN admin_message am
                    ON aum.admin_message_id = am.admin_message_id
                    AND aum.admin_feed_id = am.admin_feed_id
                WHERE aum.user_message_id = ? AND aum.user_feed_id = ?
            '''

        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(query, (user_message_id, user_feed_id,))
            return await cursor.fetchall()


    async def add_admin_user_message_without_admin(self, admin_message_id, users_data, user_type_message):
        async with aiosqlite.connect(db_path) as db:
            sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for user_feed_id, user_message_id  in users_data:
                await self.add_user_message(user_message_id, user_feed_id, user_type_message)

                await db.execute("""
                    INSERT INTO admin_user_message (user_message_id, user_feed_id, admin_message_id, admin_feed_id, sent_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_message_id, user_feed_id, admin_message_id, admin, sent_time))

            await db.commit()