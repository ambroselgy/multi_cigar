from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Pool, Manager, Value
from pymongo import MongoClient
import datetime


def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec


def init(args):
    global writenums
    writenums = args


def make_page_links(page_links_queue, firsturl, startlist, endlist):
    for index in range(startlist, endlist + 1):
        print(firsturl + str(index) + "   放入链接池")
        page_links_queue.put(firsturl + str(index))
    page_links_queue.put("#END#")


def get_item_url(page_links_queue, item_url_queue, header):

    while True:
        tmp_links = page_links_queue.get()
        print("开始解析 " + str(tmp_links) + "  数据")
        if tmp_links == "#END#":  # 遇到结束标志，推出进程
            page_links_queue.put("#END#")
            print("get_item_url Quit {}".format(page_links_queue.qsize()))
            break
        else:
            r = requests.get(tmp_links, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print("重新解析  " + str(tmp_links) + "   数据")
                r = requests.get(tmp_links, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            try:
                product = soup.find_all(
                    'li', class_="item product product-item")
                for i in product:
                    x = i.find(
                        'strong', class_="product name product-item-name")
                    url = x.find('a')['href']
                    item_url_queue.put(url)
            except Exception as err:
                print(str(tmp_links) + "    列表页解析报错")
                print(err)


def get_item_info(item_url_queue, item_info_queue, header):

    while True:

        while item_url_queue.empty():
            time.sleep(0.01)

        tmp_items = item_url_queue.get()
        if tmp_items == "#END#":  # 遇到结束标记，退出进程
            print("get_item_info Quit {}".format(item_url_queue.qsize()))
            print("队列剩余" + str(item_info_queue.qsize()))
            break
        else:
            print("开始获取 " + str(tmp_links) + "  数据")
            r = requests.get(tmp_items, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print("重新获取  " + str(tmp_items) + "   数据")
                r = requests.get(tmp_items, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            try:
                item_list = soup.find_all(
                    'td', class_="col item", attrs={
                        "data-th": "Product Name"})
                title = soup.find(
                    'td', class_="col data", attrs={
                        'data-th': 'Brand'}).string.strip()
                times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                for i in item_list:
                        tmp_stock = i.find('div', class_='stockindicator-content')
                        stock = tmp_stock.find('span').string.strip()
                        cigarlist = i.find(
                            'strong', class_="product-item-name sc-grouped-title").string.strip()
                        cigarprice = i.find('span', attrs={
                                            "data-price-type": "finalPrice"}).find('span', class_="price").string.strip()
                        tmp_price = cigarprice[1:]
                        price = tmp_price.replace(",", "")
                        itemurl = tmp_items
                        if i.find('span', class_="savingPercent"):
                            details = i.find(
                                'span', class_="savingPercent").string.strip().replace(
                                " ", "")
                        else:
                            details = '0'
                        tmp_detailed = float(
                            details.strip('%')) / 100 * float(price) + float(price)
                        detailed = '%.2f' % tmp_detailed
                        cigarinfo = {
                            'title': title,
                            'cigar_name': cigarlist,
                            'detailed': detailed,
                            'stock': stock,
                            'details': details,
                            'cigar_price': price,
                            'itemurl': str(itemurl),
                            'times': times}
                        item_info_queue.put(cigarinfo)
            except Exception as err:
            print(str(tmp_items) + "    商品获取报错")
            print(err)


def save_to_mongodb(item_info_queue):
    connect = MongoClient(host='localhost', port=27017)
    db = connect['cigars']
    collection = db['stock']
    global writenums

    while True:
        while item_info_queue.empty():
            time.sleep(0.02)
        cigarinfo = item_info_queue.get()
        if cigarinfo == "#END#":  # 遇到退出标志，退出进程
            print("数据存储完成")
            break
        else:
            try:
                tmp_data = cigarinfo
                tmp_cigar = cigarinfo["cigar_name"]
                tmp_data.pop(
                    list(
                        filter(
                            lambda k: tmp_data[k] == tmp_cigar,
                            tmp_data))[0])
                collection.update_one(
                    filter={
                        'cigar_name': tmp_cigar}, update={
                        "$set": tmp_data}, upsert=True)
                with writenums.get_lock():
                    writenums.value += 1
            except Exception as err:
                print(tmp_cigar + "    存储报错")
                print(err)


def start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxsave):
    '''组织抓取过程'''
    writenums = Value('i', 0)
    get_item_url_nums = maxurl
    get_item_url_pool = Pool(processes=get_item_url_nums)
    get_item_info_nums = maxinfo
    get_item_info_pool = Pool(processes=get_item_info_nums)
    save_to_mongodb_nums = maxsave
    save_to_mongodb_pool = Pool(
        processes=save_to_mongodb_nums,
        initializer=init,
        initargs=(
            writenums,
        ))
    page_links_queue = Manager().Queue()
    item_url_queue = Manager().Queue()
    item_info_queue = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    make_page_links(
        page_links_queue,
        firsturl,
        startlist,
        endlist)  # 调用函数构造list
    for index in range(0, get_item_url_nums):  # 获取item list
        get_item_url_pool.apply_async(
            func=get_item_url, args=(
                page_links_queue, item_url_queue, header))
    for index in range(0, get_item_info_nums):
        get_item_info_pool.apply_async(
            func=get_item_info, args=(
                item_url_queue, item_info_queue, header))
    for index in range(0, save_to_mongodb_nums):
        save_to_mongodb_pool.apply_async(
            func=save_to_mongodb, args=(
                item_info_queue,))

    get_item_url_pool.close()
    get_item_url_pool.join()
    for i in range(0, get_item_info_nums):
        item_url_queue.put("#END#")
    get_item_info_pool.close()
    get_item_info_pool.join()
    for i in range(0, save_to_mongodb_nums):
        item_info_queue.put("#END#")
    save_to_mongodb_pool.close()
    save_to_mongodb_pool.join()
    print("已写入  " + str(writenums) + "  条数据")


second = sleeptime(1, 0, 0)  # 间隔运行时间 时：分：秒
if __name__ == '__main__':
    #    while True:
    firsturl = "https://selected-cigars.com/en/cigars?p="  # 网站列表页模板
    startlist = 1  # 商品列表起始
    endlist = 14  # 商品列表终页
    maxurl = 5  # 解析列表页，获取商品链接的进程
    maxinfo = 15  # 获取商品信息的进程
    maxsave = 3  # 存储进程
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
    st = time.time()
    start_work_mongodb(firsturl, startlist, endlist, maxurl, maxinfo, maxsave)
    print(time.time() - st)
#        time.sleep(second)
