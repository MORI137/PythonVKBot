import sqlite3

# Создание подключения к базе данных
db_path = 'chat_bot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Создание таблицы 'users'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_feed_id INTEGER PRIMARY KEY,
        group_name TEXT,
        is_confirmed BOOLEAN
    )
''')

# Создание таблицы 'admin_message'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_message (
        admin_message_id INTEGER,
        admin_feed_id INTEGER,
        message_type TEXT,
        PRIMARY KEY (admin_message_id, admin_feed_id)
    )
''')

# Создание таблицы 'user_message'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_message (
        user_message_id INTEGER,
        user_feed_id INTEGER,
        message_type TEXT,
        user_message_reply_id INTEGER DEFAULT NULL,
        PRIMARY KEY (user_message_id, user_feed_id),
        FOREIGN KEY (user_feed_id) REFERENCES users(user_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
''')

'''
CREATE TABLE IF NOT EXISTS messages (
    peer_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    message_type TEXT,
    reply_message_id INTEGER DEFAULT NULL,
    PRIMARY KEY (message_id),
    )
'''
#+ создать триггер, который будет удалять все сообщения при удалении пользователя где peer_id совпадает

# Создание таблицы 'admin_user_message'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_user_message (
        user_message_id INTEGER,
        user_feed_id INTEGER,
        admin_message_id INTEGER,
        admin_feed_id INTEGER,
        sent_time TEXT,
        PRIMARY KEY (user_message_id, user_feed_id, admin_message_id, admin_feed_id),
        FOREIGN KEY (user_feed_id) REFERENCES users(user_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (admin_feed_id) REFERENCES admins(admins_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (user_message_id, user_feed_id) REFERENCES user_message(user_message_id, user_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (admin_message_id, admin_feed_id) REFERENCES admin_message(admin_message_id, admin_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
''')

# Создание таблицы 'reminders'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        reminds_id INTEGER PRIMARY KEY,
        reminder_time TEXT,
        is_sent BOOLEAN
    )
''')

# Создание таблицы 'reminders_user'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders_user (
        user_message_id INTEGER,
        user_feed_id INTEGER,
        reminds_id INTEGER,
        is_canceled BOOLEAN,
        PRIMARY KEY (user_message_id, user_feed_id, reminds_id),
        FOREIGN KEY (user_message_id, user_feed_id) REFERENCES user_message(user_message_id, user_feed_id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (reminds_id) REFERENCES reminders(reminds_id)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
''')

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()