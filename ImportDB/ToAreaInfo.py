from ImportDB.util import DBOptBase


class LoadAreaInfo(DBOptBase):
    def __init__(self):
        super().__init__()

    def run(self):
        with open("./area_info.csv", 'r') as f:
            data_lines = f.read().splitlines()
            for line in data_lines:
                data = line.split("\001")
                self.insert_data_to_table(data)

    def insert_data_to_table(self, data):
        sql = "INSERT INTO rs_area_info VALUES (%s,%s,%s,NOW(),NOW())"
        try:
            self.db_cursor.execute(sql, data)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    with LoadAreaInfo() as l:
        l.run()