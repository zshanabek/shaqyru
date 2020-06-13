import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_cities(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM cities').fetchall()

    def add_user(self, user):
        with self.connection:
            return self.cursor.execute('INSERT INTO users (name, city_id, phone_number, language, decision) VALUES (?,?,?,?,?)', user)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
