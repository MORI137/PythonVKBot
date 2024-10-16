import aiosqlite
from datetime import datetime
from config import db_path
from config import admin

class DBManager:

    def is_admin(self, user_id):
        return user_id in admin

    async def get_groups_by_courses(self, courses):
        results = []

        current_year = datetime.now().year

        year_map = {4: current_year - 3, 3: current_year - 2, 2: current_year - 1}

        # Получаем все группы для заданных курсов
        async with aiosqlite.connect(db_path) as db:
            for course in courses:
                if course in year_map:
                    year_admitted = year_map[course]

                    query = "SELECT * FROM users WHERE group LIKE ?"
                    cursor = await db.execute(query, (f'%/[A-Za-z]+-{year_admitted}-%',))
                    users = await cursor.fetchall()
                    results.extend(users)

        return results

    async def add_user(self, user_id, group):
        async with aiosqlite.connect(db_path) as db:
            # Проверяем, существует ли пользователь с таким user_id
            query_check = "SELECT * FROM users WHERE user_feed_id = ?"
            cursor = await db.execute(query_check, (user_id,))
            exists = await cursor.fetchone()

            if exists != None and exists:
                query_update = "UPDATE users SET group_name = ?, is_confirmed = ? WHERE user_feed_id = ?"
                await db.execute(query_update, (group, False, user_id))
            else:
                query_insert = """
                        INSERT INTO user (user_feed_id, group_name, is_confirmed)
                        VALUES (?, ?, ?)
                        """
                await db.execute(query_insert, (user_id, group, False))

            await db.commit()

    async def get_all_users(self):
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT * FROM users")
            result = await cursor.fetchall()
            return result

    async def get_users_by_course(self, courses):
        current_date = datetime.now()
        results = []

        async with aiosqlite.connect(db_path) as db:
            for course in courses:
                year_admitted = int(course.split('-')[1].split('б')[1])
                # Рассчитываем курс: (текущий год - год поступления)
                start_date = datetime(year_admitted + 1, 9, 1)
                if current_date >= start_date:
                    calculated_course = (current_date.year - year_admitted) + 1  # Курс
                else:
                    calculated_course = current_date.year - year_admitted

                query = "SELECT * FROM user WHERE course = ? AND role = 'user'"
                cursor = await db.execute(query, (calculated_course,))
                users = await cursor.fetchall()
                results.extend(users)

        return results

    async def get_all_admins(self):
        async with aiosqlite.connect(db_path) as db:
            cursor = db.cursor()
            cursor = await db.execute("SELECT user_id FROM user WHERE role = 'admin' OR role = 'super_admin'")
            admins = await cursor.fetchall()
            return [admin[0] for admin in admins]

    async def get_main_admin(self):
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT user_id FROM user WHERE role = 'super_admin'")
            result = await cursor.fetchall()
            return result[0]

    async def add_message(self, message_id, chat_id, message_type):
        async with aiosqlite.connect(db_path) as db:
            await db.execute("""
                INSERT INTO message(message_id, chat_id, timestamp, message_type)
                VALUES (?, ?, ?, ?) 
            """, (message_id, chat_id, datetime.now().strftime("%d/%m/%Y %H:%M:%S") ,message_type))
            await db.commit()

