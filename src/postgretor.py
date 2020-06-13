import psycopg2


class Postgretor:

    def __init__(self, database):
        self.connection = psycopg2.connect(
            host="localhost", database="elimai", user="postgres", password="postgres")
        self.cursor = self.connection.cursor()

    def select_cities(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM cities').fetchall()

    def exist_user(self, phone):
        with self.connection:
            result = self.cursor.execute(
                'SELECT * FROM users WHERE phone_number = ?', (phone,)).fetchall()
            if len(result) != 0:
                return True
            return False

    def add_user(self, user):
        with self.connection:
            return self.cursor.execute('INSERT INTO users (name, city_id, phone_number, language, decision) VALUES (?,?,?,?,?)', user)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
