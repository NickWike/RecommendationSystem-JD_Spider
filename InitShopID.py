import os

"""
    @author:zh123
    @date:2020-1-28
    @description:
       title:初始化商店名称与分配的商家ID的映射文件
       1.通过将所有的商家名读入后
       2.从上次ID的结束值进行依次递增分配id
"""

path = "./data1"
total_shop_path = "./TotalShop"
dir_list = os.listdir("./data1")
shop_ID = -1
if not os.path.exists(total_shop_path+"/last_shop_id.stat"):
    shop_ID = 1
else:
    with open(total_shop_path+"/last_shop_id.stat", "r") as f:
        shop_ID = int(f.read())

shop_list = {}
cnt = 0
for d in dir_list:
    file_path = path+"/" + d + "/goods_info_init.csv"
    with open(file_path, "r") as f:
        good_info_list = f.read().splitlines()
        for l in good_info_list:
            cnt +=1
            shop_name = l.split("\001")[-1]
            if not shop_list.get(shop_name):
                shop_list[shop_name] = 1
            else:
                shop_list[shop_name] += 1

if not os.path.exists(total_shop_path):
    os.mkdir(total_shop_path)

with open(total_shop_path+"/shop_id.csv","a+") as f:
    for k in shop_list.keys():
        f.write(k + "\001" + str(shop_ID).zfill(11)+"\n")
        shop_ID += 1
with open(total_shop_path+"/last_shop_id.stat","a") as f:
    f.write(str(shop_ID).zfill(11))
print(cnt)

