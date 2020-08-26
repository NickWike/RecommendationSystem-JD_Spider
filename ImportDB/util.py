import pymysql

DB_CONFIG = {"host": "localhost",
             "port": 3306,
             "database": "RECOMMENDATION_SYSTEM_DB",
             "user": "root",
             "password": "123qweQWE"}


class DBOptBase:
    def __init__(self):
        self.db = pymysql.Connect(**DB_CONFIG)
        self.db_cursor = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.commit()
        self.db_cursor.close()
        self.db.close()


if __name__ == '__main__':
    with DBOptBase() as connect:
        connect.db_cursor.execute("SELECT 'Successful' AS ''")
        print(connect.db_cursor.fetchall())
