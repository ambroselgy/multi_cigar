from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime
def save_to_mongodb(cigars):
    connect = MongoClient(host='localhost', port=27017)
    db = connect['cigarworld']
    collection = db['stock']
    try:
        tmp_data = cigars
        tmp_cigar = cigars["cigar_name"]
        tmp_data.pop(list(filter(lambda k: tmp_data[k] == tmp_cigar, tmp_data))[0])
        collection.update_one(filter={'cigar_name':tmp_cigar},update={
            "$set":tmp_data},upsert=True)
    except Exception as err:
        print(cigarinfo+"    存储报错")
        print(err)

def getinfo():
        tmp_links = "https://www.cigarworld.de/en/zigarren/cuba/regulares/bolivar-01001"
        print("开始获取 "+str(tmp_links)+"  数据")
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
        r = requests.get(tmp_links, headers=header)
        r.encoding = 'utf-8'
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        item_list = soup.select("li.ws-g.DetailVariant")
        title = soup.find('h1').string
        times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for i in item_list:
                cigar_name = i.find('div',attrs={'class':"ws-u-1 DetailVariant-variantName",}).find(text=True).strip()
                print(cigar_name)
                pricelist = i.select('div.ws-u-1-3.ws-u-lg-1-4.DetailVariant-formPrice > span')
                numslist = i.find_all('span', attrs={'class':re.compile(r'einheitlabel')})
                tmp_itemurl = i.find('a',attrs={'class':'ws-u-1 ws-u-lg-4-24 DetailVariant-col DetailVariant-image'})['href']
                itemurl = 'https://www.cigarworld.de'+tmp_itemurl
                if len(pricelist) == len(numslist):
                    for i in range(len(pricelist)):
                        tmp_name = str(cigar_name).replace('\n', '').strip()
                        price = pricelist[i].text.replace("€", "").strip()
                        tmp_nums = numslist[i].text
                        tmp_stock = numslist[i].get('title').strip()
                        if tmp_stock:
                            stock = tmp_stock
                        else:
                            stock = "in stock"
                        nums = re.sub(r'\D', "", tmp_nums)
                        name = title + " " + tmp_name + '  ' + str(nums)
                        details = '0'
                        detailed = price
                        cigarinfo = {'cigar_name': name, 'detailed': detailed, 'stock': stock,
                                     'details': details,
                                     'cigar_price': price, 'itemurl': itemurl, 'times': times}
                        #print(tmp_name)
getinfo()