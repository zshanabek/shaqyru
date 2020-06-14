import os
import pdb
import psycopg2
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

PG_HOST = os.getenv("PG_HOST")
PG_DATABASE = os.getenv("PG_DATABASE")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")


class Postgretor:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=PG_HOST, database=PG_DATABASE, user=PG_USER, password=PG_PASSWORD)
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
