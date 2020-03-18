from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime


def getallurl():
        tmp_links = "https://www.cigarworld.de/en/zigarren/cuba/regulares/cohiba-zigarren-01002"
        print("开始获取 "+str(tmp_links)+"  数据")
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
        x = requests.session()
        r = x.get(tmp_links)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        item_list = soup.select("li.ws-g.DetailVariant")
        title = soup.find('h1').string
        #namelist = soup.select("a.ws-u-1.ws-u-lg-11-24.ws-u-xl-13-24.DetailVariant-col.DetailVariant-data > div.ws-g > div.ws-u-1.DetailVariant-dataName > span:first-of-type")
        #itemlist = soup.find_all('li', class_="ws-g DetailVariant")
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

