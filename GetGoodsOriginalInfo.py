from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import re
import time

"""
    @author:zh123
    @date:2020-1-21
    @description:
        1.采用selenium的方式爬去商品的基本信息
        2.首先是获取所有需要搜索的商品(需要进行搜索的词条保存在search_worlds.txt当中)
        3.然后在京东商城中搜索这些商品
        4.爬取搜索出的商品基本信息
    @note:当要绕过某些网站的监测时可以找单ChromeDriver所在目录
          打开chromedriver修改  var key = '$cdc_mhjhghuummzhhhzffhzmmm_'; 
          key的值可以乱输入但长度要和修改前一样
"""


class JDGoodInfoGet:
    search_world = ""               # 当前需要搜索的商品名称
    browser = None                  # 浏览器对象
    url = "https://search.jd.com/"  # 京东商城的搜索主页

    def __init__(self):
        option = webdriver.ChromeOptions()                                          # 初始化一个chrome浏览器的网页驱动器设置
        option.add_experimental_option('excludeSwitches', ['enable-automation'])    # 设置实验参数,规避网站的监测
        self.browser = webdriver.Chrome(chrome_options=option)                      # 初始化浏览器对象,配置设置
        self.browser.delete_all_cookies()                                           # 删除所有的cookies信息

    def set_search_word(self, w):                                                   # 设置搜索的商品名称
        self.search_world = w

    def start_search(self):                                                         # 开始搜索工作
        self.browser.get(self.url)                                                  # 浏览器获取搜索网页
        self.browser.find_element(By.ID, "keyword").send_keys(self.search_world)    # 寻找搜索框并在其内填入搜索商品名称
        self.browser.find_element(By.CLASS_NAME, "input_submit").click()            # 寻找开始搜索按钮并点击搜索
        time.sleep(5)                                                               # 等待五秒
        path = "./data1/{0}".format(self.search_world)                              # 当前搜索商品的存放目录地址
        if not os.path.exists(path):                                                # 判断目录是否存在
            os.mkdir(path)                                                          # 不存在时新建此目录
        file = open(path + "/goods_info_init.csv", "a+")                            # 新建并打开商品信息需要存放的文件
        try:
            self.start_get_data(file, 10)                                           # 开始获取数据,传入参数10获取10页的数据
        except Exception as e:                                                      # 捕获异常
            print(e)                                                                # 打印异常
        finally:
            file.close()                                                            # 关闭文件

    def start_get_data(self, file, need_page):                                      # 获取商品的数据
        for i in range(need_page):                                                  # 需要爬去的页面数量
            soup = BeautifulSoup(self.browser.page_source, "html.parser")           # 解析当前页面的html
            total_page = int(soup.find("div", id="J_topPage",class_="f-pager").find("i").string)  # 获取总页数
            if i+1 > total_page:                                                    # 如果当前的页数大于总页树是跳出函数
                return
            s_list = soup.find_all("li", class_="gl-item")                          # 寻找所有class="gl-item"的li标签
            for item in s_list:                                                     # 遍历标签列表
                try:
                    g_name_div = item.find('div', class_="p-name-type-2") # 在当前的标签下寻找class="p-name-type-2"的div标签
                    good_url = g_name_div.find('a')["href"]               # 在div标签下寻找 a 标签并获取商品的url
                    good_name = g_name_div.find("em").get_text()          # 在div标签下寻找 em 标签并获取文本内容即为商品名
                    good_image_url = re.search("//.*?\\.((jpg)|(png)|(jpeg))",
                                               str(item.find("div", class_="p-img").find("img"))).group()  # 获取商品图片url
                    good_price = item.find("div", class_="p-price").find('i').string  # 获取商品的价格
                    shop_name = item.find("div", class_="p-shop").find("a").string    # 获取商品所属商家的名称
                    good_url = "https:" + good_url if good_url[:2] == "//" else good_url  # 格式化商品的url
                    good_image_url = "https:" + good_image_url if good_image_url[:2] == "//" else good_image_url  # 格式化商品图片的url
                    print(good_url, good_name, good_image_url, good_price, shop_name)     # 打印商品的基本信息
                    data_line = {"good_url": good_url,
                                 "good_name": good_name,
                                 "good_image_url": good_image_url,
                                 "good_price": good_price,
                                 "shop_name": shop_name}                                  # 构建数据行
                    status = self.save_data(file, data_line)                              # 保存数据行,并获取保存状态
                    good_id = re.search("\\d+", good_url).group()
                    mes = "{0}-[page{1}]-[{2}]".format("Successful to save!" if status[0] else "Failed to save!", str(i+1), good_id)  # 保存的日志行
                    self.save_log(mes)  # 保存日志

                except Exception as e:                                # 商品数据获取过程中的异常
                    mes = "Error: {0}-[page{1}]".format(e, str(i+1))  # 构造日志行
                    self.save_log(message=mes)                        # 保存日志
            try:
                self.browser.find_element(By.CLASS_NAME, "pn-next").click()            # 寻找下一页按钮并点击下一页
            except Exception as e:
                self.save_log("Failed to click next page-[page{0}]".format(str(i+1)))  # 当下一页按钮不存在时记录错误信息
            time.sleep(10)                                                             # 等待10秒防止监测

    def save_data(self, file, data_line: dict) -> (bool, Exception):
        try:
            file.write(data_line["good_url"] + "\001" +
                       data_line["good_name"] + "\001" +
                       data_line["good_image_url"] + "\001" +
                       data_line["good_price"] + "\001" +
                       data_line["shop_name"] + "\n")       # 商品数据,并以"\001"作为分隔
        except Exception as e:
            return False, e                                 # 返回保存失败的状态码和错误信息
        return True, None                                   # 返回保存成功

    def save_log(self,message: str):
        with open("get_shop_info.log","a+") as f:
            current_time_stamp = time.time()  # 获取当前时间戳
            time_local = time.localtime(current_time_stamp)  # 格式化时间戳为本地时间
            time_YmdHMS = time.strftime("%Y-%m-%d_%H:%M:%S", time_local)
            f.write("{0}-[{1}]-[{2}]\n".format(message, time_YmdHMS, self.search_world))  # 写入日志数据

    def close(self):
        self.browser.close()    # 关闭浏览器驱动


if __name__ == '__main__':
    J = JDGoodInfoGet()                             # 初始胡京东商品信息获取类
    with open("search_worlds.txt","r") as f:        # 打开需要搜索词条的文件
        search_worlds = f.read().split()
    # search_worlds = search_worlds[300:]
    try:
        for w in search_worlds:                     # 遍历每个词条
            J.set_search_word(w)                    # 设置搜索的词条
            J.start_search()                        # 开始搜索并获取数据
            time.sleep(20)                          # 等待20秒防止监测
    except Exception as e:
        print(e)                                    # 打印异常信息
    finally:
        J.close()                                   # 关闭驱动
