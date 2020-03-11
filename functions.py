from bs4 import BeautifulSoup
import requests
import csv
import os
import time
from multiprocessing import Process, Queue, Pool, Manager
'''links构造网站pagelist，items构造雪茄库存状态，cigars抓取名称及价格存入csv'''

def makelinks(links, firsturl, startlist, endlist):
    for index in range(startlist, endlist+1):
        links.put(firsturl + str(index))
    links.put("#END#")

def getallurl(links, items, header):

    while True:
        tmp_links = links.get()
        if tmp_links == "#END#" : #遇到结束标志，推出进程
            links.put("#END#")
            items.put("#END#")
            print("Pages Quit {}". format(links.qsize()))
            break
        else:
            r = requests.get(tmp_links, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            product = soup.find_all('li', class_="item product product-item")
            for i in product:
                if not i.find_all('span', text = "Out of stock"):
                    x = i.find('strong', class_="product name product-item-name")
                    url = x.find('a')['href']
                    #print(url)
                    items.put(url)

def getinfo(items, cigars, header):

    while True:

        while items.empty():
            time.sleep(0.01)

        tmp_items = items.get()
        if tmp_items == "#END#": #遇到结束标记，退出进程
            items.put("#END#")
            cigars.put("#END")
            print("数据抓取完成 {}".format(items.qsize()))
            break
        else:
            print('开始获取商品数据', tmp_items)
            r = requests.get(tmp_items, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            itempage = BeautifulSoup(html, "html.parser")
            itemlist = itempage.find_all('td', class_ = "col item", attrs={"data-th":"Product Name"})
            #获取到雪茄商品页面中的商品列表，通常为1支，1盒及价格等。
            for i in itemlist:
                if not i.find_all('span', text = "Sold Out"):
                        cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                        cigarprice = i.find('span', attrs={"data-price-type":"finalPrice"}).find('span',class_="price").string.strip()
                        price = cigarprice[1:]
                        itemurl = tmp_items
                        cigarinfo = {'cigar_name':cigarlist,'cigar_price':price,'itemurl':str(itemurl)}
                        cigars.put(cigarinfo)
                # else:
                #     cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                #     price = 'Sold out'
                #     itemurl = tmp_items
                #     cigarinfo = {'cigar_name': cigarlist, 'cigar_price': price, 'itemurl': str(itemurl)}
                #     cigars.put(cigarinfo)
            # except:
            #     cigarlist = "error"
            #     price = "error"
            #     itemurl = url
            #     cigarinfo = {
            #         'cigar_name': cigarlist,
            #         'cigar_price': price,
            #         'itemurl': str(itemurl)
            #     }
            #     print(cigarinfo)
            #     cigars.put(cigarinfo)

def save_to_csv(cigars, filename):
    while True:
        while cigars.empty():
            time.sleep(0.02)
        cigar = cigars.get()
        if cigar == "#END#":   #遇到退出标志，退出进程
            print("数据存储完成")
            break
        else:
            filename = filename
            with open(filename, "a", encoding='utf-8-sig', newline='') as csvfile:
                headers = ['cigar_name', 'cigar_price','itemurl']
                csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
                csvwriter.writerow(cigar)
                csvfile.close()
def start_work(filename, firsturl, startlist, endlist, maxurl, maxinfo, maxcsv, processnums):
    '''组织抓取过程'''
    pool = Pool(processes=processnums)
    links = Manager().Queue()
    items = Manager().Queue()
    cigars = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
#    init()
    makelinks(links, firsturl, startlist, endlist)#调用函数构造list
    for index in range(0, maxurl):#获取item list
        pool.apply_async(func=getallurl, args=(links, items, header))
    for index in range(0, maxinfo):
        pool.apply_async(func=getinfo, args=(items, cigars, header))
    for index in range(0, maxcsv):
        pool.apply_async(func=save_to_csv, args=(cigars, filename))

    pool.close()
    pool.join()
