from ImportDB.util import DBOptBase
import os

DATA_PATH = "../data1"


class PutDataToTable(DBOptBase):
    def __init__(self):
        super().__init__()
        self.words = []

    def load_search_words(self):
        self.words = os.listdir(DATA_PATH)

    def put_to_database(self):
        sql = """INSERT INTO 
                 rs_product_keyword_search_info(keyword,status,create_time,update_time) 
                 VALUES(%s,1,NOW(),NOW())"""
        for word in self.words:
            self.db_cursor.execute(sql, word)


if __name__ == '__main__':
    with PutDataToTable() as p:
        p.load_search_words()
        p.put_to_database()
