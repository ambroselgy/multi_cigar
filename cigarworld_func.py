from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Pool, Manager, Value
from pymongo import MongoClient
import datetime


def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec


def init(args):
    global writenums
    writenums = args


def make_page_links(page_links, page_links_queue):
    for index in page_links:
        print(index + "   放入链接池")
        page_links_queue.put(index)
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
            try:
                r = requests.get(tmp_links, headers=header)
                r.encoding = 'utf-8'
                html = r.text
                soup = BeautifulSoup(html, "html.parser")
                product = soup.find_all(
                    'a', attrs={'search-result-item-inner'})
                for i in product:
                    tmp_url = i.get('href')
                    url = 'https://www.cigarworld.de' + tmp_url
                    item_url_queue.put(url)
            except Exception as err:
                print(str(tmp_links) + "    列表页解析报错")
                print(err)


def get_item_info(item_url_queue, item_info_queue, header):

    while True:

        while item_url_queue.empty():
            time.sleep(0.01)

        tmp_links = item_url_queue.get()
        if tmp_links == "#END#":  # 遇到结束标志，推出进程
            print("get_item_info Quit {}".format(item_url_queue.qsize()))
            print("队列剩余" + str(item_info_queue.qsize()))
            break
        else:
            print("开始获取 " + str(tmp_links) + "  数据")
            r = requests.get(tmp_links, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print(r.status_code)
                print("重新获取  " + str(tmp_links) + "   数据")
                r = requests.get(tmp_links, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "lxml")
            try:
                item_list = soup.select("li.ws-g.DetailVariant")
                title = soup.find('h1').string.strip()
                times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                for i in item_list:
                    cigar_name = i.find(
                        'div',
                        attrs={
                            'class': "ws-u-1 DetailVariant-variantName",
                        }).find(
                        text=True).strip()
                    pricelist = i.select(
                        'div.ws-u-1-3.ws-u-lg-1-4.DetailVariant-formPrice > span.preis')
                    numslist = i.find_all(
                        'span', attrs={
                            'class': re.compile(r'einheitlabel')})
                    tmp_itemurl = i.find(
                        'a', attrs={
                            'class': 'ws-u-1 ws-u-lg-4-24 DetailVariant-col DetailVariant-image'})['href']
                    itemurl = 'https://www.cigarworld.de' + tmp_itemurl
                    if len(pricelist) == len(numslist):
                        for i in range(len(pricelist)):
                            tmp_name = str(cigar_name)
                            price = pricelist[i].text.replace("€", "").strip()
                            tmp_nums = numslist[i].text
                            tmp_stock = numslist[i].get('title').strip()
                            if tmp_stock:
                                stock = tmp_stock
                            else:
                                stock = "in stock"
                            #nums = re.sub(r'\D',"",tmp_nums)
                            nums = tmp_nums
                            name = title + " " + tmp_name + '  ' + str(nums)
                            details = '0'
                            detailed = price
                            cigarinfo = {
                                'title': title,
                                'cigar_name': name,
                                'detailed': detailed,
                                'stock': stock,
                                'details': details,
                                'cigar_price': price,
                                'itemurl': itemurl,
                                'times': times}
                            item_info_queue.put(cigarinfo)
                    else:
                        print("比对不通过 " + tmp_links)
            except Exception as err:
                print(str(tmp_links) + "    商品获取报错")
                print(err)


def save_to_mongodb(item_info_queue):
    connect = MongoClient(host='localhost', port=27017)
    db = connect['cigarworld']
    collection = db['test']
    global writenums

    while True:
        while item_info_queue.empty():
            time.sleep(0.02)
        cigarinfo = item_info_queue.get()
        if cigarinfo == "#END#":  # 遇到退出标志，退出进程
            print("save_to_mongodb Quit {}".format(page_links_queue.qsize()))
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


def start_work_mongodb(links, maxurl, maxinfo, maxsave):
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

    make_page_links(links, page_links_queue)  # 调用函数构造list
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
    links = ['https://www.cigarworld.de/en/zigarren/cuba?von=0',
             'https://www.cigarworld.de/en/zigarren/cuba?von=30',
             'https://www.cigarworld.de/en/zigarren/cuba?von=60']  # 网站列表页模板
    maxurl = 3  # 解析列表页，获取商品链接的进程
    maxinfo = 5  # 获取商品信息的进程
    maxsave = 1  # 存储进程
    runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
    st = time.time()
    start_work_mongodb(links, maxurl, maxinfo, maxsave)
    print(time.time() - st)
