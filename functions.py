from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Pool, Manager, Value
from pymongo import MongoClient
import datetime
import csv


def init(args):
    ''' store the counter for later use '''
    global writenums
    writenums = args

def makelinks(links, firsturl, startlist, endlist):
    for index in range(startlist, endlist+1):
        print(firsturl + str(index)+"   放入链接池")
        links.put(firsturl + str(index))
    links.put("#END#")

def getallurl(links, items, header):

    while True:
        tmp_links = links.get()
        print("开始获取 "+str(tmp_links)+"  数据")
        if tmp_links == "#END#" : #遇到结束标志，推出进程
            links.put("#END#")
            print("Pages Quit {}". format(links.qsize()))
            break
        else:
            try:
                r = requests.get(tmp_links, headers=header)
                while r.status_code != 200:
                    time.sleep(10)
                    print("重新获取  "+str(tmp_links)+"   数据")
                    r = requests.get(tmp_links, headers=header)
                r.encoding = 'utf-8'
                html = r.text
                soup = BeautifulSoup(html, "html.parser")
                product = soup.find_all('li', class_="item product product-item")
                for i in product:
                    x = i.find('strong', class_="product name product-item-name")
                    url = x.find('a')['href']
                    items.put(url)
            except Exception as err:
                print(str(tmp_links)+"    列表页解析报错")
                print(err)

def getinfo(items, cigars, header):

    while True:

        while items.empty():
            time.sleep(0.01)

        tmp_items = items.get()
        if tmp_items == "#END#": #遇到结束标记，退出进程
            print("数据抓取完成 {}".format(items.qsize()))
            break
        else:
            r = requests.get(tmp_items, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print("重新获取  " + str(tmp_items) + "   数据")
                r = requests.get(tmp_items, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            itempage = BeautifulSoup(html, "html.parser")
            itemlist = itempage.find_all('td', class_ = "col item", attrs={"data-th":"Product Name"})
            title = itempage.find('td', class_="col data",attrs={'data-th':'Brand'}).string.strip()
            times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            print('开始获取商品数据', tmp_items)
            #获取到雪茄商品页面中的商品列表，通常为1支，1盒及价格等。
            for i in itemlist:
                try:
                    tmp_stock = i.find('div', class_='stockindicator-content')
                    stock = tmp_stock.find('span').string.strip()
                    cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                    cigarprice = i.find('span', attrs={"data-price-type":"finalPrice"}).find('span',class_="price").string.strip()
                    tmp_price = cigarprice[1:]
                    price = tmp_price.replace(",","")
                    itemurl = tmp_items
                    if i.find('span', class_ = "savingPercent"):
                        details = i.find('span', class_ ="savingPercent").string.strip().replace(" ","")
                    else:
                        details = '0'
                    tmp_detailed = float(details.strip('%')) / 100 * float(price) + float(price)
                    detailed = '%.2f' % tmp_detailed
                    cigarinfo = {'title':title, 'cigar_name':cigarlist, 'detailed':detailed, 'stock':stock,
                                 'details':details, 'cigar_price':price, 'itemurl':str(itemurl), 'times':times}
                    cigars.put(cigarinfo)
                except Exception as err:
                    cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                    itemurl = tmp_items
                    print(cigarlist+"    报错"+"    "+itemurl)
                    print(err)

def save_to_csv(cigars, filename):
    global writenums
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
                headers = ['title', 'cigar_name', 'detailed', 'stock', 'details', 'cigar_price', 'itemurl', 'times']
                csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
                rowwriter = csv.writer(csvfile)
                with open(filename, 'r', encoding='utf-8-sig') as rowfile:
                    rowreader = csv.reader(rowfile)
                    if not [row for row in rowreader]:
                        rowwriter.writerow(['品牌', '雪茄', '税前价格', '库存', '折扣', '原价', '链接', '更新时间'])
                        csvwriter.writerow(cigar)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1
                    else:
                        csvwriter.writerow(cigar)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1


def start_work(filename, firsturl, startlist, endlist, maxurl, maxinfo, maxcsv):
    '''组织抓取过程'''
    writenums = Value('i', 0)
    getallurl_nums = maxurl
    getallurl_pool = Pool(processes=getallurl_nums)
    getinfo_nums = maxinfo
    getinfo_pool = Pool(processes=getinfo_nums)
    save_to_csv_nums = maxcsv
    save_to_csv_pool = Pool(processes=save_to_csv_nums, initializer=init, initargs=(writenums,))
    links = Manager().Queue()
    items = Manager().Queue()
    cigars = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    makelinks(links, firsturl, startlist, endlist)#调用函数构造list
    for index in range(0, getallurl_nums):#获取item list
        getallurl_pool.apply_async(func=getallurl, args=(links, items, header))
    for index in range(0, getinfo_nums):
        getinfo_pool.apply_async(func=getinfo, args=(items, cigars, header))
    for index in range(0, save_to_csv_nums):
        save_to_csv_pool.apply_async(func=save_to_csv, args=(cigars, filename,))

    getallurl_pool.close()
    getallurl_pool.join()
    for i in range(0, getinfo_nums):
        items.put("#END#")
    getinfo_pool.close()
    getinfo_pool.join()
    for i in range(0, save_to_csv_nums):
        cigars.put("#END#")
    save_to_csv_pool.close()
    save_to_csv_pool.join()
    print("已写入  " + str(writenums) + "  条数据")

