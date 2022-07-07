import sqlite3


class Database:

    __instance = None

    def __new__(cls, *args, **kwargs):

        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __del__(self):
        Database.__instance = None

    def __init__(self, name):
        self._conn = sqlite3.connect(name, check_same_thread=False)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def create(self):
        with self.connection:
            #self.cursor.execute("""DROP TABLE IF EXISTS money""")
            self.execute("""CREATE TABLE IF NOT EXISTS money(
                        value_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        created DATE NOT NULL
                        )""")

    def commit(self):
        self.connection.commit()

    def insert(self, package: tuple):
        self.execute("""INSERT INTO money(
                    value_id, type, amount, category, created) VALUES(NULL, ?, ?, ?, ?)""", package)
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def select_10_values(self) -> list:
        self.execute('''SELECT value_id, type, amount, category, created FROM money ORDER BY value_id DESC LIMIT 10''')
        result = self.fetchall()
        return result

    def delete_value(self, value_id: str):
        self.execute(f'''DELETE from money WHERE value_id = {value_id}''')
        self.commit()

    def get_current_month_statistic(self) -> list:
        self.execute('''SELECT type, amount, category, created FROM money 
                    WHERE DATE(created) >= DATE('NOW', 'START OF MONTH')''')
        result = self.fetchall()
        return result

    def get_range_statistic(self, start: str, end: str) -> list:
        self.execute(f'''SELECT type, amount, category, created FROM money 
                            WHERE DATE(created) BETWEEN "{start}" AND "{end}"''')
        result = self.fetchall()
        return result
