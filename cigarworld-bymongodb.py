from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Pool, Manager, Value
from pymongo import MongoClient
import datetime
import csv


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
            r = requests.get(tmp_links, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print("重新解析  " + str(tmp_links) + "   数据")
                r = requests.get(tmp_links, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            try:
                item_list = soup.select("li.ws-g.DetailVariant")
                if item_list:
                    for i in item_list:
                        tmp_itemurl = i.find(
                            'a', attrs={
                                'class': 'ws-u-1 ws-u-lg-4-24 DetailVariant-col DetailVariant-image'})['href']
                        url = 'https://www.cigarworld.de' + tmp_itemurl
                        item_url_queue.put(url)
                else:
                    url = tmp_links
                    item_url_queue.put(url)
            except Exception as err:
                print(str(tmp_links) + "    列表页解析报错")
                print(err)


def get_item_info(item_url_queue, item_info_queue, header):

    while True:

        while item_url_queue.empty():
            time.sleep(0.01)

        tmp_items = item_url_queue.get()
        if tmp_items == "#END#":  # 遇到结束标志，推出进程
            print("get_item_info Quit {}".format(item_url_queue.qsize()))
            print("队列剩余" + str(item_info_queue.qsize()))
            break
        else:
            print("开始获取 " + str(tmp_items) + "  数据")
            r = requests.get(tmp_items, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print(r.status_code)
                print("重新获取  " + str(tmp_items) + "   数据")
                r = requests.get(tmp_items, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "lxml")
            times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            try:
                tmp_list = soup.select('div.ws-g.VariantInfo div.ws-g.ws-c')
                if tmp_list:
                    for i in tmp_list:
                        tmp_brand = i.find('div',class_='ws-u-1 VariantInfo-itemName').text
                        if 'Brand' in tmp_brand:
                            brand = i.find('div',class_='ws-u-1 VariantInfo-itemValue').text
                        elif 'Item' in tmp_brand:
                            cigar_name = i.find('div',class_='ws-u-1 VariantInfo-itemValue').text
                    itemlist = soup.find_all('div',class_='ws-g DetailOrderbox-row')
                    for i in itemlist:
                        tmp_price = i.find('span',class_='preis').contents
                        if len(tmp_price) > 1:
                            detailed = tmp_price[0].replace("€", "").strip()
                            cigar_price = tmp_price[1].text.strip()
                        else:
                            detailed = tmp_price[0].replace("€", "").strip()
                            cigar_price = detailed
                        nums = i.find('span', attrs={'class': re.compile(r'einheitlabel')}).text.strip()
                        stock = i.find('label',attrs={'for':re.compile(r'wk_anzahl')}).get('title').strip()
                        tmp_details = i.find('small',attrs={'style':re.compile('color')})
                        if tmp_details:
                            details = re.sub(r'\*','',tmp_details.text.strip())
                        else:
                            details = 0
                        cigarinfo = {
                            'Brand': brand,
                            'cigar_name': brand+' '+cigar_name,
                            'group': brand+' '+cigar_name+' '+nums,
                            'detailed': detailed,
                            'stock': stock,
                            'details': details,
                            'cigar_price': cigar_price,
                            'itemurl': tmp_items,
                            'times': times}
                        item_info_queue.put(cigarinfo)
                else:
                    brand = 'other'
                    cigar_name = soup.find('h1').string.strip()
                    itemlist = soup.find_all('div', class_='ws-g DetailOrderbox-row')
                    for i in itemlist:
                        tmp_price = i.find('span', class_='preis').contents
                        if len(tmp_price) > 1:
                            detailed = tmp_price[0].replace("€", "").strip()
                            cigar_price = tmp_price[1].text.strip()
                        else:
                            detailed = tmp_price[0].replace("€", "").strip()
                            cigar_price = detailed
                        nums = i.find('span', attrs={'class': re.compile(r'einheitlabel')}).text.strip()
                        stock = i.find('label', attrs={'for': re.compile(r'wk_anzahl')}).get('title').strip()
                        tmp_details = i.find('small', attrs={'style': re.compile('color')})
                        if tmp_details:
                            details = re.sub(r'\*', '', tmp_details.text.strip())
                        else:
                            details = 0
                        cigarinfo = {
                            'Brand': brand,
                            'cigar_name': brand + ' ' + cigar_name,
                            'group': brand + ' ' + cigar_name + ' ' + nums,
                            'detailed': detailed,
                            'stock': stock,
                            'details': details,
                            'cigar_price': cigar_price,
                            'itemurl': tmp_items,
                            'times': times}
                        item_info_queue.put(cigarinfo)

            except Exception as err:
                print(str(tmp_items) + "    商品获取报错")
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
                group = cigarinfo["group"]
                tmp_del = ['group', 'Brand', 'cigar_name', 'itemurl']
                tmp_filter = {'group': tmp_data['group'], 'Brand': tmp_data['Brand'],
                              'cigar_name': tmp_data['cigar_name'], 'itemurl': tmp_data['itemurl']}
                for i in tmp_del:
                    del tmp_data[i]
                collection.update_one(
                    filter=tmp_filter, update={
                        "$set": tmp_data}, upsert=True)
                with writenums.get_lock():
                    writenums.value += 1
            except Exception as err:
                print(group + "    存储报错")
                print(err)

def save_to_csv(item_info_queue, filename):
    global writenums
    while True:
        while item_info_queue.empty():
            time.sleep(0.02)
        cigar = item_info_queue.get()
        if cigar == "#END#":  # 遇到退出标志，退出进程
            print("数据存储完成")
            break
        else:
            filename = filename
            with open(filename, "a", encoding='utf-8-sig', newline='') as csvfile:
                headers = [
                    'Brand',
                    'cigar_name',
                    'group',
                    'detailed',
                    'stock',
                    'details',
                    'cigar_price',
                    'itemurl',
                    'times']
                csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
                rowwriter = csv.writer(csvfile)
                with open(filename, 'r', encoding='utf-8-sig') as rowfile:
                    rowreader = csv.reader(rowfile)
                    if not [row for row in rowreader]:
                        rowwriter.writerow(
                            ['品牌', '型号','雪茄', '税前价格', '库存', '折扣', '原价', '链接', '更新时间'])
                        csvwriter.writerow(cigar)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1
                    else:
                        csvwriter.writerow(cigar)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1

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
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    make_page_links(links, page_links_queue)  # 调用函数构造list
    for index in range(0, get_item_url_nums):  # 获取item list
        get_item_url_pool.apply_async(
            func=get_item_url, args=(
                page_links_queue, item_url_queue, header,))
    for index in range(0, get_item_info_nums):
        get_item_info_pool.apply_async(
            func=get_item_info, args=(
                item_url_queue, item_info_queue, header,))
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
    print("已写入  " + str(writenums.value) + "  条数据")
def start_work_csv(links, maxurl, maxinfo, maxsave):
    '''组织抓取过程'''
    filename = "./data/multe_" + str(runtime) + ".csv"
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
                page_links_queue, item_url_queue, header,))
    for index in range(0, get_item_info_nums):
        get_item_info_pool.apply_async(
            func=get_item_info, args=(
                item_url_queue, item_info_queue, header,))
    for index in range(0, save_to_mongodb_nums):
        save_to_mongodb_pool.apply_async(
            func=save_to_csv, args=(
                item_info_queue,filename,))

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
    print("已写入  " + str(writenums.value) + "  条数据")

second = sleeptime(1, 0, 0)  # 间隔运行时间 时：分：秒
if __name__ == '__main__':
    with open("cigarworld.txt", 'r') as f:
        tmp_links = f.readlines()
    links = [i.strip() for i in tmp_links]

    # 网站列表页模板
    maxurl = 3  # 解析列表页，获取商品链接的进程
    maxinfo = 5  # 获取商品信息的进程
    maxsave = 1  # 存储进程
    runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
    st = time.time()
    start_work_mongodb(links, maxurl, maxinfo, maxsave)
    print(time.time() - st)

