from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime
def start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxcsv, processnums):
    '''组织抓取过程'''
    pool = Pool(processes=processnums)
    links = Manager().Queue()
    items = Manager().Queue()
    cigars = Manager().Queue()
    print(links.empty())
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    while cigars.empty():
        print("测试跳出")
        break
if __name__ == '__main__':
#    while True:
        firsturl = "https://selected-cigars.com/en/cigars?p="  #网站列表页模板
        startlist = 1 #商品列表起始
        endlist = 14 #商品列表终页
        maxurl = 5 #url获取进程数分配
        maxinfo = 10 #商品信息获取进程数分配
        maxcsv = 1 #csv写入进程数分配
        processnums = 11 #进程总数
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
        runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
        start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxcsv, processnums)
#        time.sleep(second)