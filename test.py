from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime
'''间隔时间运行的selected-cigars爬虫工具，使用multi模块实现多进程抓取，目前运行时间50S'''

def make_links(nums,links):
    for i in range(nums):
        print(str(i) + "   放入links池")
        links.put(str(i))
    links.put("#END#")

def make_urls(links, urllist):
    while True:
        while links.empty():
            time.sleep(0.01)
        url = links.get()
        print("make_urls 取出  "+url+"   links剩余"+str(links.qsize()))
        if url == "#END#":
            links.put("#END#")
            #urllist.put("#END#")
            print("make_urls 放入 #END#  ")
            break
        else:
            time.sleep(1)
            print("make_urls 放入   "+"m"+str(url))
            urllist.put("m"+str(url))

def get_info(urllist, itemlist):
    while True:
        while urllist.empty():
            time.sleep(0.01)
        item = urllist.get()
        print("get_info 取出   "+item+"   urllist剩余"+str(urllist.qsize()))
        if item == "#END#":
            #urllist.put("#END#")
            #itemlist.put("#END#")
            print("get_info 放入 #END#")
            break
        else:
            time.sleep(1)
            print("get_info 放入  "+"g"+str(item))
            itemlist.put("g"+str(item))

def save_info(itemlist):
    while True:
        while itemlist.empty():
            time.sleep(0.01)

        info = itemlist.get()
        print("save_info 取出  "+info+"   itemlist剩余"+str(itemlist.qsize()))
        if info == "#END#":
            #itemlist.put("#END#")
            #print("save_info 放入 #END#")
            break
        else:
            print("save_info 打印  "+info+"   itemlist剩余   "+str(itemlist.qsize()))


def start_work_mongodb():
    '''组织抓取过程'''
    make_urls_nums = 5
    make_urls_pool = Pool(processes=make_urls_nums)
    get_info_nums = 5
    get_info_pool = Pool(processes=get_info_nums)
    save_info_nums = 5
    save_info_pool = Pool(processes=save_info_nums)
    links = Manager().Queue()
    urllist = Manager().Queue()
    itemlist = Manager().Queue()
    nums = 10
    make_links(nums, links)
    for index in range(0, make_urls_nums):#
        make_urls_pool.apply_async(func=make_urls, args=(links, urllist,))
    for index in range(0, get_info_nums):
        get_info_pool.apply_async(func=get_info, args=(urllist, itemlist, ))
    for index in range(0, save_info_nums):
        save_info_pool.apply_async(func=save_info, args=(itemlist,))

    make_urls_pool.close()
    make_urls_pool.join()
    for i in range(0,get_info_nums):
        urllist.put("#END#")
    get_info_pool.close()
    get_info_pool.join()
    for i in range(0,save_info_nums):
        itemlist.put("#END#")
    save_info_pool.close()
    save_info_pool.join()

if __name__ == '__main__':
    start_work_mongodb()