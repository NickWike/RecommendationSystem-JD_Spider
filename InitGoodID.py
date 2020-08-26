import os
import re

"""
    @author:zh123
    @date:2020-1-28
    @description:
       title:初始话原商品id与现分配id之间的映射关秀
       1.先读入原来商品ID
       2.再读入上次分配的id的结束值继续分配id
"""

root_path = "./data1"
total_goods_path = "./TotalGood"
good_number = 0
if not os.path.exists(total_goods_path):
    os.mkdir(total_goods_path)
if not os.path.exists(total_goods_path+"/last_good_id.stat"):
    good_number = 1
else:
    with open(total_goods_path+"/last_good_id.stat","r") as f:
        good_number = int(f.read())

dir_list = os.listdir(root_path)
goods_id = {}

for world in dir_list:
    file_path = root_path + "/" + world + "/goods_info_init.csv"
    with open(file_path, "r") as f:
        data_line = f.read().splitlines()
        try:
            for good in data_line:
                good_old_id = re.search("\\d+", good.split("\001")[0]).group(0)
                if not goods_id.get(good_old_id):
                    goods_id[good_old_id] = 1
                else:
                    goods_id[good_old_id] += 1
        except:
            print(good,file_path)

for k in goods_id.keys():
    with open(total_goods_path + "/good_id.csv", "a+") as f:
        f.write(k + "\001" + str(good_number).zfill(11) + "\n")
    good_number += 1

with open(total_goods_path + "/last_good_id.stat", "w+") as f:
    f.write(str(good_number).zfill(11))
