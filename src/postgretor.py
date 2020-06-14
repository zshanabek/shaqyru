import psycopg2


class Postgretor:

    def __init__(self, database):
        self.connection = psycopg2.connect(
            host="localhost", database="elimai", user="batyr", password="qupiasoz")
        self.cursor = self.connection.cursor()

    def select_cities(self):
        with self.connection:
            self.cursor.execute('SELECT * FROM cities')
            return self.cursor.fetchall()

    def exist_phone(self, phone):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM users WHERE phone_number = %s', (phone,))
            result = self.cursor.fetchall()
            if len(result) != 0:
                return True
            return False

    def exist_user(self, telegram_id):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
            result = self.cursor.fetchall()
            if len(result) != 0:
                return True
            return False

    def select_user(self, telegram_id):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
            return self.cursor.fetchall()[0]

    def add_user(self, user):
        with self.connection:
            self.cursor.execute(
                'INSERT INTO users (name, city_id, phone_number, language, telegram_id, telegram_username, decision) VALUES (%s,%s,%s,%s,%s,%s,%s)', user)

    def update_user(self, user):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET name = %s, city_id = %s, phone_number = %s, language = %s, decision = %s WHERE telegram_id=%s', user)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
