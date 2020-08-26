import oss2
import os
import time
import gevent
from gevent import monkey
from gevent.lock import BoundedSemaphore

"""
    @author: zh123
    @date: 2020-2-12
    @description: 1.将获取的到的图片资源上传到阿里云的oss中进行存储,
            2.这里使用阿里云的oss对象存储用作图床
            3.使用阿里云的oss接口进行上传文件
            4.程序使用协程的操作来加快文件上传速率
"""

monkey.patch_all()          # 设置所有耗时操作均已异步进行

SEM = BoundedSemaphore(1)   # 设置可使用资源数量,这里指的是log_file对象 因为这里只写入一个日志文件所以设为1

IMAGE_DIR = "./image"   # 需要上传资源的父目录路径
IMAGE_LIST = []         # 所有图片的名称列表

for root, dirs, files in os.walk(IMAGE_DIR):
    IMAGE_LIST = files  # 获取图片文件名名称

AUTH = oss2.Auth("xxxxxxxxxxx", "xxxxxxxxxxxxxxxxxx")              # 配置oss用户
BUCKET = oss2.Bucket(AUTH, "https://oss-cn-xxxxxx.aliyuncs.com", "xxxxxxxxxxxxxxxxxxxxxxxxx")  # 构建一个Bucket对象
LOG_FILE = open("./put_image_to_oss.log", "a+")   # 打开需要写入的日志文件


def put_file(file_name, try_num):
    status_code = ""    # 上传状态码
    status_text = ""    # 上传状态文本
    log_message = ""    # 日志消息
    image_id = file_name.split(".")[0]  # 图片ID
    for i in range(try_num):    # 对上传请求进行 try_num 次尝试
        try:
            BUCKET.put_object_from_file("image_res/000" + file_name, IMAGE_DIR + "/" + file_name)  # 上传文件
            status_code = "1"   # 上传成功状态码赋值为1
            status_text = "OK"  # 上传状态文本设为 OK
            log_message = "Put to OSS successful!"  # 上传日志消息设为上传成功
            break
        except Exception as e:     # 捕获上传时遇到的错误
            status_code = "0"      # 上传失败状态码设为0
            status_text = "ERROR"  # 上传失败状态文本设为错误
            log_message = "Put to OSS failed!({0})".format(str(e))   # 日志消息设为上传失败并贴上 错误信息
        finally:
            current_time_stamp = time.time()  # 获取当前时间戳
            time_local = time.localtime(current_time_stamp)  # 格式化时间戳为本地时间
            time_YmdHMS = time.strftime("%Y-%m-%d_%H:%M:%S", time_local)
            log_text = "{0}-[{1}]-{2}-{3}-[{4}]-{5}\n".format(status_code,
                                                              status_text,
                                                              log_message,
                                                              image_id,
                                                              time_YmdHMS,
                                                              str(i + 1))  # 根据上上面状态信息构建一行日志信息
            # start -日志写入时候 日志文件对象写入同步操作-
            SEM.acquire()               # 获取日志写入资源锁
            LOG_FILE.write(log_text)    # 写入日志
            print(log_text, end="")     # 向控制台打印日志
            SEM.release()               # 释放日志写入资源锁
            # end


if __name__ == '__main__':
    total_cnt = len(IMAGE_LIST)     # 获取总的文件个数
    concurrent_num = 1000           # 并发数
    cnt = 0                         # 上传文件个数
    for index in range(0, len(IMAGE_LIST), concurrent_num):     # 根据并发数量进行切割文件列表
        asyn_list = []                                          # 异步操作列表
        image_list = IMAGE_LIST[index:index + concurrent_num]   # 马上要进行上传文件的列表
        for f in image_list:                                    # 遍历列表文件名
            asyn_list.append(gevent.spawn(put_file, f, 3))      # 将上传操作加入到协程池
            cnt += 1                                            # 上传文件数量值加一
        gevent.joinall(asyn_list)                               # 将所有协程加入并运行
    LOG_FILE.close()                                            # 关闭日志文件
    print(total_cnt, cnt)                                       # 打印上传文件总数和记录的上传数量
