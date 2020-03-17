from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Process, Queue, Pool, Manager
from pymongo import MongoClient
import datetime
'''间隔时间运行的selected-cigars爬虫工具，使用multi模块实现多进程抓取，目前运行时间50S'''

def sleeptime(hour, min, sec):
    return hour*3600 + min*60 + sec

'''links构造网站pagelist，items构造雪茄库存状态，cigars抓取名称及价格存入csv'''

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
            r.encoding = 'utf-8'
            html = r.text
            itempage = BeautifulSoup(html, "html.parser")
            itemlist = itempage.find_all('td', class_ = "col item", attrs={"data-th":"Product Name"})
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
                    cigarinfo = {'cigar_name':cigarlist,'detailed':detailed,'stock':stock,'details':details,
                                 'cigar_price':price,'itemurl':str(itemurl),'times':times}
                    cigars.put(cigarinfo)
                except Exception as err:
                    cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                    itemurl = tmp_items
                    print(cigarlist+"    报错"+"    "+itemurl)
                    print(err)

def save_to_mongodb(cigars):
    connect = MongoClient(host='localhost', port=27017)
    db = connect['cigars']
    collection = db['stock']
    while True:
        while cigars.empty():
            time.sleep(0.02)
        cigar = cigars.get()
        if cigar == "#END#":  # 遇到退出标志，退出进程
            print("数据存储完成")
            break
        else:
            try:
                tmp_data = cigar
                tmp_cigar = cigar["cigar_name"]
                tmp_data.pop(list(filter(lambda k: tmp_data[k] == tmp_cigar, tmp_data))[0])
                collection.update_one(filter={'cigar_name':tmp_cigar},update={
                    "$set":tmp_data},upsert=True)
            except Exception as err:
                print(cigarinfo+"    存储报错")
                print(err)


def start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxsave ):
    '''组织抓取过程'''
    getallurl_nums = maxurl
    getallurl_pool = Pool(processes=getallurl_nums)
    getinfo_nums = maxinfo
    getinfo_pool = Pool(processes=getinfo_nums)
    save_to_mongodb_nums = maxsave
    save_to_mongodb_pool = Pool(processes=save_to_mongodb_nums)
    links = Manager().Queue()
    items = Manager().Queue()
    cigars = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
#    init()
    makelinks(links, firsturl, startlist, endlist)#调用函数构造list
    for index in range(0, getallurl_nums):#获取item list
        getallurl_pool.apply_async(func=getallurl, args=(links, items, header))
    for index in range(0, getinfo_nums):
        getinfo_pool.apply_async(func=getinfo, args=(items, cigars, header))
    for index in range(0, save_to_mongodb_nums):
        save_to_mongodb_pool.apply_async(func=save_to_mongodb, args=(cigars,))

    getallurl_pool.close()
    getallurl_pool.join()
    for i in range(0,getinfo_nums):
        items.put("#END#")
    getinfo_pool.close()
    getinfo_pool.join()
    for i in range(0,save_to_mongodb_nums):
        cigars.put("#END#")
    save_to_mongodb_pool.close()
    save_to_mongodb_pool.join()


second = sleeptime(1, 0, 0) #间隔运行时间 时：分：秒
if __name__ == '__main__':
#    while True:
        firsturl = "https://selected-cigars.com/en/cigars?p="  #网站列表页模板
        startlist = 1 #商品列表起始
        endlist = 17 #商品列表终页
        maxurl = 5  #解析列表页，获取商品链接的进程
        maxinfo = 10 #获取商品信息的进程
        maxsave = 5  #存储进程
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
        runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
        st = time.time()
        start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxsave)
        print(time.time()-st)
#        time.sleep(second)