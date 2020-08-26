from ImportDB.util import DBOptBase
import os
import re
import numpy as np
import random

DATA_PATH = "../data1"
IMAGE_HOST = "http://recommendation-system.oss-cn-chengdu.aliyuncs.com/image_res/"
POSTAGE_LIST = ["0.00"] + ["%.2f" % i for i in range(6, 20, 2)]
PROBABILITY = [0.4, 0.175, 0.15, 0.1, 0.075, 0.05, 0.025, 0.025]


class LoadProductInfo(DBOptBase):
    def __init__(self):
        super().__init__()

    def run(self):
        word_list = os.listdir(DATA_PATH)
        for word in word_list:
            data_file_path = DATA_PATH + "/" + word + "/good_info_final.csv"
            with open(data_file_path,"r") as f:
                data_lines = f.read().splitlines()
                for line in data_lines:
                    data_line = line.split("\001")
                    product_existed, base_info_data = self.create_base_info_data(word, data_line)
                    if product_existed:
                        self.update_data_from_base_info(base_info_data[0],base_info_data[2])
                    else:
                        self.insert_data_to_base_info(base_info_data)
                        sales_info_data = self.create_sales_info_data(data_line)
                        self.insert_data_to_sales_info(sales_info_data)
            print(data_file_path)
            self.db.commit()

    def create_base_info_data(self, word, data_line):
        product_existed = False
        result_data = [data_line[6],  # 0 id
                       data_line[5],  # 1 shop_id
                       None,          # 2 keyword_search_id
                       data_line[1],  # 3 name
                       None,          # 4 image_url
                       data_line[3],  # 5 price
                       None,          # 6 postage
                       1]             # 7 status
        keywords_list = self.find_original_keywords(data_line[6])
        if keywords_list:
            product_existed = True
        keywords_list.append(self.find_search_word_id(word))
        keywords_str = ";".join(list(set(keywords_list)))
        result_data[2] = keywords_str
        jd_image_url = data_line[2]
        image_suffix = re.search(r"\.((png)|(jpg)|(jpeg))", jd_image_url).group(0)
        my_image_url = IMAGE_HOST + data_line[6].zfill(11) + image_suffix
        result_data[4] = my_image_url
        result_data[6] = np.random.choice(POSTAGE_LIST, p=PROBABILITY)
        return product_existed, result_data

    @staticmethod
    def create_sales_info_data(data_line):
        result_data = [data_line[6],    # 0 product_id
                       data_line[7],    # 1 comment_count
                       data_line[8],    # 2 average_score
                       data_line[9],    # 3 good_count
                       data_line[10],   # 4 general_count
                       data_line[11],   # 5 poor_count
                       data_line[12],   # 6 good_rate
                       data_line[13],   # 7 month_sales
                       data_line[14],   # 8 total_sales
                       int((int(data_line[14])+random.randint(0, 10000))*random.random()*1.5)]  # 9 inventory
        return result_data

    def find_original_keywords(self, product_id):
        sql = "SELECT keyword_search_id FROM rs_product_base_info WHERE id = %s"
        try:
            self.db_cursor.execute(sql, product_id)
            keywords_str = self.db_cursor.fetchall()
            if keywords_str:
                keywords_list = keywords_str[0][0].split(";")
                return keywords_list
        except Exception as e:
            print(e)
        return []

    def find_search_word_id(self, word):
        sql = "SELECT id from rs_product_keyword_search_info WHERE keyword = %s"
        try:
            self.db_cursor.execute(sql, word)
            return str(self.db_cursor.fetchall()[0][0]).zfill(11)
        except Exception as e:
            print(e)
            return 0

    def insert_data_to_base_info(self, data):
        sql = """
                INSERT INTO rs_product_base_info
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())   
              """
        try:
            self.db_cursor.execute(sql, data)
        except Exception as e:
            raise e

    def update_data_from_base_info(self, product_id, keyword_search_id):
        sql = "UPDATE rs_product_base_info SET keyword_search_id=%s,update_time=NOW() WHERE id = %s"
        try:
            self.db_cursor.execute(sql, [keyword_search_id, product_id])
        except Exception as e:
            print(e)
            raise e

    def insert_data_to_sales_info(self, data):
        sql = """
                        INSERT INTO rs_product_sales_info
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())   
              """
        try:
            self.db_cursor.execute(sql, data)
        except Exception as e:
            raise e


if __name__ == '__main__':
    with LoadProductInfo() as l:
        l.run()
        # l.find_search_word_id("电动充电式飞利浦剃须刀")
        # print(l.find_original_keywords("00000003310"))
