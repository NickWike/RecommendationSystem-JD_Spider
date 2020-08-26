import os

"""
    @author:zh123
    @date:2020-1-28
    @description:
       title:为原有的商品信息初始化本地分配的商店ID
       1.先读入原来商店名称和现在商店ID之间的映射表
       2.再读入原有的商品信息存放文件,通过映射关系添加分配的商家ID字段
"""

root_dir = "./data1"                                                                    # 商品数据存放的根目录
list_dir = os.listdir(root_dir)                                                         # 根目录包含的目录列表
shop_name_to_ID = {}                                                                    # 商家名称和ID之间的映射表
with open("./TotalShop/shop_id.csv", "r") as f:                                         # 读入映射关系文件
    shop_list = f.read().splitlines()                                                   # 将数据拆分成行
    for l in shop_list:                                                                 # 遍历每行数据
        shop_info = l.split("\001")                                                     # 分割成列表([商家名称,商家id])
        shop_name_to_ID[shop_info[0]] = shop_info[1]                                    # 加入到映射表中

# print(shop_name_to_ID)
cnt = 0                                                                                 # 商品总数
for world in list_dir:                                                                  # 遍历列表
    path = root_dir + "/" + world                                                       # 构造商品数据文件存放的目录地址
    with open(path + "/goods_info_init.csv", "r") as fi:                                # 打开原商品信息的存放文件
        good_list = fi.read().splitlines()                                              # 将数据拆分成行
        with open(path + "/good_info_have_id.csv", "w") as fo:                          # 增加商家ID字段后的文件
            for good in good_list:                                                      # 遍历商品数据行
                cnt += 1                                                                # 商品数据加一
                fo.write(good + "\001" + shop_name_to_ID[good.split("\001")[-1]] + "\n")  # 写入数据
print(cnt)
