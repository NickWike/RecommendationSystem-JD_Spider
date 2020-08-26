import gevent
from gevent import monkey
import requests
import time
import os
"""
    @author:zh123
    @date:2020-1-28
    @description:
        1.根据商品的图片链接将图片下载到本地
        2.首先是将商品图片的url从商品信息中提取出来
        3.然后通过request请求将图片从京东服务器中下载到本地
        4.request请求采用异步的方式进行
"""

monkey.patch_all()  # 设置素所有的耗时操作都异步进行

image_save_path = "./image"     # 下载后的图片保存的目录
data_dir = "./data1"            # 商品原始数据的存放目录

if not os.path.exists(image_save_path):  # 判断存放图片资源的目录是否存在
    os.mkdir(image_save_path)            # 当目录不存在时就创建一个目录

if not os.path.exists(image_save_path+"/logger"):  # 判断保存日志的目录是否存在
    os.mkdir(image_save_path+"/logger")            # 不存在时候创建此目录

header = {  # 模拟请求头
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'}


def download_image(url:str, good_id:int):
    """
    @:param url:需要下载图片的链接地址
    @:param good_id:商品的ID
    @:return None
    """
    status = ""             # 图片下载状态
    message = str(good_id)  # 下载消息初值赋为商品id
    try_cnt = 0             # 当前的尝试次数
    for i in range(3):      # 尝试下载三次
        try:
            res = requests.get(url=url, headers=header, timeout=5)                # 获取图片请求,请求超时时间设置为5秒
            file_suffix = url.split(".")[-1]                                      # 获取文件后缀名(jpg/png/jpeg...)
            with open("./image/{0}.{1}".format(good_id,file_suffix), "wb") as f:  # 创建要保存的图片文件 以二进制的方式
                f.write(res.content)                                              # 写入图片数据
            status = "[ok]"                                                       # 写入成功后将图片的下载状态设为OK
            message += " Save Successful!"                                        # 设置图片下载消息提示保存成功
            break                                                                 # 终止尝试
        except Exception as e:                                                    # 捕获图片在获取和存储过程中的异常
            print(e)                                                              # 打印异常信息
            status = "[error]"                                                    # 图片获取状态设置为错误
            message += " Save Failed!"                                            # 图片获取信息设为保存失败
            continue
        finally:
            current_time_stamp = time.time()  # 获取当前时间戳
            time_local = time.localtime(current_time_stamp)  # 格式化时间戳为本地时间
            time_YmdHMS = time.strftime("%Y-%m-%d_%H:%M:%S", time_local)
            # file_log.write("{0}-{1}-{2}-{3}\n".format(status,message,time_YmdHMS,try_cnt))
            print("{0}-{1}-{2}-{3}".format(status,message,time_YmdHMS,try_cnt))   # 格式化答应日志信息
            message = str(good_id)                                                # 消息再次初始化
            try_cnt += 1                                                          # 尝试次数加一


if __name__ == '__main__':
    dir_list = os.listdir(data_dir)                                                 # 获取所有的搜索类别目录
    dir_list = dir_list[200:]                                                       # 这里通过手动的方式控制需要下载图片目录

    for world in dir_list:                                                          # 遍历每个搜索的词条
        print(world)                                                                # 答应当前的词条
        with open(data_dir + "/" + world + "/good_info_final.csv", "r") as f:       # 打开存放商品信息的文件
            lines = f.read().splitlines()                                           # 读取文件并将将所有行的数据转换成列表的方式存放
            asyn_list = []                                                          # 并发池
            for good in lines:                                                      # 遍历每行数据
                good_data = good.split("\001")                                      # 以"\001"分割符分割每行数据
                good_image = good_data[2]                                           # 获取图片url
                good_id = good_data[6]                                              # 获取商品ID
                asyn_list.append(gevent.spawn(download_image, good_image, good_id)) # 将任务加入并发池当中
            gevent.joinall(asyn_list)                                               # 以协程的方式处理并发任务
