import os
import re

"""
    @author:zh123
    @date:2020-1-28
    @description:
       title:为原有的商品信息初始化本地分配的商品ID
       1.先读入原来商品ID和现在商品ID之间的映射表
       2.再读入原有的商品信息存放文件,通过映射关系添加分配的商品ID字段
"""

root_dir = "./data1"                                                        # 商品数据的根目录
list_dir = os.listdir(root_dir)                                             # 获取根目录里的目录列表(也就是所有搜索词条)
old_id_to_new_id = {}                                                       # 原id与新id的映射表
with open("./TotalGood/good_id.csv", "r") as f:                             # 读入映射关系文件
    good_id_lines = f.read().splitlines()                                   # 将所有的数据拆分成行
    for line in good_id_lines:                                              # 遍历所有的数据行
        good_id_map = line.split("\001")                                    # 行数据拆分成列表([原id,新id])
        old_id_to_new_id[good_id_map[0]] = good_id_map[1]                   # 赋值给映射表
for world in list_dir:                                                      # 遍历每个目录
    path = root_dir+"/"+world                                               # 构造商品信息文件的根目录地址
    with open(path+"/good_info_have_id.csv", "r") as fi:                    # 原来商品信息的文件
        good_list = fi.read().splitlines()                                  # 数据拆分成行
        with open(path + "/good_info_shop_good_id.csv", "w+") as fo:        # 增加商品ID后的文件对象
            for good in good_list:                                          # 遍历所有的数据行
                old_id = re.search("\\d+", good.split("\001")[0]).group(0)  # 提取旧的商品id
                fo.write(good + "\001" + old_id_to_new_id[old_id] + "\n")   # 根据映射表增加字段(本地分配的id)
