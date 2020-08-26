import requests
import time
import re
import os
import random
import json

"""
    @author:zh123
    @date:2020-01-24
    @description:
        1.获取商品的一些销售信息
        2.这里主要获取商品的评论数,好/中/差评数量
        3.然后根据上面获取到的数据推测商品的月销售量,和总销售量
        4.主要通过request请求获取json数据
"""


class GetComment:
    url = "https://club.jd.com/comment/productCommentSummaries.action"      # 数据请求的url
    header = {                                                              # 模拟请求头
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}
    good_id = ""                                                            # 商品id

    def __init__(self, n):
        self.good_id = n                                                    # 初始化商品id

    def commit_request(self) -> dict:
        params = {"referenceIds": self.good_id,                             # request请求需要的参数(上坪id,随机数,时间戳)
                  "callback": "jQuery{0}".format(random.randint(10000, 999999)),
                  "_": int(round(time.time() * 1000))}
        response = requests.get(url=self.url,headers=self.header,params=params)  # 进行带参数的request请求
        json_str = re.search("jQuery\\d+\\((.*?)\\);", response.text).group(1)   # 对返回的数据提取json数据部分
        return json.loads(json_str)

    def get_need_data(self, json_data) -> dict:
        comment_data = json_data["CommentsCount"][0]                            # 获取需要部分的数据
        result_data = {
            "CommentCount": comment_data["CommentCount"],                       # 评论总数
            "AverageScore": comment_data["AverageScore"],                       # 商品品均得分
            "GoodCount": comment_data["GoodCount"],                             # 好评数量
            "GeneralCount": comment_data["GeneralCount"],                       # 中评数量
            "PoorCount": comment_data["PoorCount"],                             # 差评数量
            "GoodRate": comment_data["GoodRate"]                                # 好评率
            }
        return result_data


if __name__ == '__main__':
    root_path = "./data1"                                                           # 数据的根目录地址
    dir_list = os.listdir(root_path)                                                # 根地址中所有的目录(也就是所有的搜索词条)
    file_log = open("./get_comment_info.log", "a+")                                 # 新建并打开日志记录文件
    try:
        for world in dir_list:                                                      # 遍历所有的目录
            dir_path = root_path+"/"+world                                          # 构造商品所在目录地址
            with open(dir_path + "/good_info_shop_good_id.csv", "r") as fi:         # 打开商品信息读入的文件
                with open(dir_path+"/original_comment.json", "w+") as f_original:   # 用于存放对应商品销售信息的json文件
                    with open(dir_path + "/good_info_final.csv", "w+") as fo:       # 商品信息更新过后的文件对象
                        good_lines = fi.read().splitlines()                         # 读入以前的商品信息数据并拆分成行
                        for line in good_lines:                                     # 遍历每一行商品数据
                            status = "OK"                                           # 商品信息获取状态初始化为OK
                            message = ""                                            # 商品信息获取时的一些信息
                            try:
                                good_id = re.search("\\d+", line.split("\001")[0]).group()  # 获取商品id
                                G = GetComment(good_id)                                     # 构造一个商品数据获取对象
                                json_data = G.commit_request()                              # 提交request请求(获取数据)
                                f_original.write(json.dumps(json_data) + "\n")              # 写入原始的json数据
                                data = G.get_need_data(json_data)                           # 获取需要的数据
                                create_total_sales = round(data["CommentCount"] * random.uniform(1.0, 1.5))  # 根据随机规则生成商品总销售量
                                create_month_sales = round(create_total_sales // random.randint(12, 24))     # 根据岁间规则随机生成月销售量
                                data["MonthSales"] = create_month_sales                     # 设置数据行的月销售量
                                data["TotalSales"] = create_total_sales                     # 设置数据行的总销售量

                                fo.write("{0}\001{1}\001{2}\001{3}\001{4}\001{5}\001{6}\001{7}\001{8}\n".format(
                                    line, data["CommentCount"],
                                    data["AverageScore"],
                                    data["GoodCount"],
                                    data["GeneralCount"],
                                    data["PoorCount"],
                                    data["GoodRate"],
                                    data["MonthSales"],
                                    data["TotalSales"]
                                ))                                                          # 以\001作为分隔符写入数据行
                                message = "Save {0} {1} Successful!".format(world, good_id) # 商品信息获取状态消息设为保存成功
                            except Exception as e:                                          # 捕获异常
                                print(e)
                                message = "Save {0} {1} Failed {2}".format(world, good_id, str(e))  # 日志消息设置为保存失败(并提供异常信息)
                                status = "ERROR"                                                    # 消息状态设置为ERROR
                            finally:
                                current_time_stamp = time.time()  # 获取当前时间戳
                                time_local = time.localtime(current_time_stamp)  # 格式化时间戳为本地时间
                                time_YmdHMS = time.strftime("%Y-%m-%d_%H:%M:%S", time_local)
                                log = "[{0}]-[{1}]-[{2}]\n".format(status, message, time_YmdHMS)
                                file_log.write(log)                                                 # 写入日志
                                print(log, end="")                                                  # 控制台打印日志
    except Exception as e:
        print(e)                                                                                    # 打印异常信息
    finally:
        file_log.close()                                                                            # 关闭日志文件

""" --sample response data-- """
# j = {
#   "CommentsCount": [
#     {
#       "SkuId": 1868860,
#       "ProductId": 1868860,
#       "ShowCount": 8900,
#       "ShowCountStr": "8900+",
#       "CommentCountStr": "37万+",
#       "CommentCount": 370730,
#       "AverageScore": 5,
#       "DefaultGoodCountStr": "28万+",
#       "DefaultGoodCount": 282281,
#       "GoodCountStr": "23万+",
#       "GoodCount": 232147,
#       "AfterCount": 687,
#       "OneYear": 0,
#       "AfterCountStr": "600+",
#       "VideoCount": 254,
#       "VideoCountStr": "200+",
#       "GoodRate": 0.99,
#       "GoodRateShow": 99,
#       "GoodRateStyle": 148,
#       "GeneralCountStr": "800+",
#       "GeneralCount": 860,
#       "GeneralRate": 0.0080,
#       "GeneralRateShow": 1,
#       "GeneralRateStyle": 2,
#       "PoorCountStr": "500+",
#       "PoorCount": 569,
#       "SensitiveBook": 0,
#       "PoorRate": 0.0020,
#       "PoorRateShow": 0,
#       "PoorRateStyle": 0
#     }
#   ]
# }

# 获取商品的价格
# price_url = "http://p.3.cn/prices/mgets?skuIds=J_ShopID"
#
# res = requests.get(url="https://item.jd.com/100005311440.html",headers=header)
# print(res.text)
