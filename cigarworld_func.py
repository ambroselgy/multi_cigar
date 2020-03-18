from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime

def getallurl():
        tmp_links = "https://www.cigarworld.de/en/zigarren/cuba/regulares/hoyo-de-monterrey-01004"
        print("开始获取 "+str(tmp_links)+"  数据")
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
        x = requests.session()
        r = x.get(tmp_links)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        item_list = soup.select("li.ws-g.DetailVariant")
        title = soup.find('h1').string
        for i in item_list:
                cigar_name = i.find('span',class_ = "").string
                pricelist = i.select('div.ws-u-1-3.ws-u-lg-1-4.DetailVariant-formPrice > span')
                numslist = i.find_all('span', attrs={'class':re.compile(r'einheitlabel')})
                if len(pricelist) == len(numslist):
                        for i in range(len(pricelist)):
                                name = cigar_name.strip()
                                price = pricelist[i].text.replace("€","").strip()
                                tmp_nums = numslist[i].text
                                tmp_stock = numslist[i].get('title').strip()
                                if tmp_stock:
                                        stock = tmp_stock
                                else:
                                        stock = "in stock"
                                nums = re.sub(r'\D',"",tmp_nums)
                                print("品牌"+title+"雪茄"+str(name)+"价格"+price+"数量"+str(nums)+"库存 "+stock)

getallurl()
