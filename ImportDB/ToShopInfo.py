from ImportDB.util import DBOptBase
import random


class LoadShopInfo(DBOptBase):
    def __init__(self):
        super().__init__()
        self.area_info = []
        self.shop_sales = {}

    def run(self):
        self.init_area_code()
        self.init_shop_sales()
        with open('../TotalShop/shop_id.csv') as f:
            data_lines = f.read().splitlines()
            for line in data_lines:
                data = line.split("\001")
                shop_data = self.create_shop_data(data)
                self.insert_data_to_tb(shop_data)
                print(shop_data)

    def insert_data_to_tb(self, data):
        sql = "INSERT INTO rs_shop_info VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())"
        try:
            self.db_cursor.execute(sql,data)
        except Exception as e:
            print(e)

    def create_shop_data(self, data):
        shop_data = [
            data[1],    # 0 id
            data[0],    # 1 name
            0,          # 2 average_score
            0,          # 3 total_sales
            0,          # 4 month_sales
            None,       # 5 area_code
            1           # 6 status
        ]
        shop_data[5] = self.area_info[random.randint(0, len(self.area_info)-1)]
        shop_sales_info = self.shop_sales[int(data[1])]
        shop_data[2] = shop_sales_info[0]
        shop_data[3] = shop_sales_info[1]
        shop_data[4] = shop_sales_info[2]
        return shop_data

    def init_area_code(self):
        sql = "SELECT area_code FROM rs_area_info WHERE area_code % 100 = 0"
        try:
            self.db_cursor.execute(sql)
            self.area_info = list(map(lambda x: x[0], self.db_cursor.fetchall()))
        except Exception as e:
            print(e)

    def init_shop_sales(self):
        sql = """
            SELECT shop_id,AVG(average_score),SUM(total_sales),SUM(month_sales) 
            FROM rs_product_sales_info as rpsi,rs_product_base_info as rpbi 
            WHERE rpsi.product_id = rpbi.id 
            GROUP BY shop_id
        """
        self.db_cursor.execute(sql)
        query_data = list(map(lambda x:(x[0],x[1:]),self.db_cursor.fetchall()))
        self.shop_sales = dict(query_data)


if __name__ == '__main__':
    with LoadShopInfo() as l:
        l.run()
