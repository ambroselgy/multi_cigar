from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Pool, Manager, Value
import csv
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
            print("开始获取 " + str(tmp_items) + "  数据")
            r = requests.get(tmp_items, headers=header)
            while r.status_code != 200:
                time.sleep(10)
                print("重新获取  " + str(tmp_items) + "   数据")
                r = requests.get(tmp_items, headers=header)
            r.encoding = 'utf-8'
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            try:
                cigar_name = soup.find('span', class_='base', attrs={'data-ui-id': 'page-title-wrapper'}).text.strip()
                item_list = soup.find_all('td', class_="col item", attrs={"data-th": "Product Name"})
                tmp_brand = soup.find('td', class_="col data", attrs={'data-th': 'Brand'})
                if tmp_brand:
                    brand = tmp_brand.text.strip()
                else:
                    brand = 'other'
                if item_list:
                    for i in item_list:
                        tmp_stock = i.find('div', class_='stockindicator-content')
                        stock = tmp_stock.find('span').string.strip()
                        tmp_group = i.find('strong', class_="product-item-name sc-grouped-title")
                        if tmp_group:
                            group = tmp_group.string.strip()
                        else:
                            group = i.find('span', class_="base").string.strip()
                        cigarprice = i.find('span', attrs={
                            "data-price-type": "finalPrice"}).find('span', class_="price").string.strip()
                        tmp_price = cigarprice[1:]
                        price = tmp_price.replace(",", "")
                        itemurl = tmp_items
                        tmp_details = i.find('span', class_="savingPercent")
                        if tmp_details:
                            details = tmp_details.string.strip().replace(" ", "")
                        else:
                            details = '0'
                        tmp_detailed = float(
                            details.strip('%')) / 100 * float(price) + float(price)
                        detailed = '%.2f' % tmp_detailed
                        cigarinfo = {
                            'Brand': brand,
                            'cigar_name': cigar_name,
                            'group': group,
                            'detailed': detailed,
                            'stock': stock,
                            'details': details,
                            'cigar_price': price,
                            'itemurl': str(itemurl),
                            'times': times}
                        item_info_queue.put(cigarinfo)
                else:
                    group = cigar_name
                    tmp_stock = soup.find('div', class_='stockindicator-content')
                    stock = tmp_stock.find('span').string.strip()
                    cigarprice = soup.find('span', attrs={
                        "data-price-type": "finalPrice"}).find('span', class_="price").string.strip()
                    tmp_price = cigarprice[1:]
                    price = tmp_price.replace(",", "")
                    itemurl = tmp_items
                    tmp_details = soup.find('span', class_="savingPercent")
                    if tmp_details:
                        details = tmp_details.string.strip().replace(" ", "")
                    else:
                        details = '0'
                    tmp_detailed = float(
                        details.strip('%')) / 100 * float(price) + float(price)
                    detailed = '%.2f' % tmp_detailed
                    cigarinfo = {
                        'Brand': brand,
                        'cigar_name': cigar_name,
                        'group': group,
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


def start_work(
        filename,
        firsturl,
        startlist,
        endlist,
        maxurl,
        maxinfo,
        maxcsv):
    '''组织抓取过程'''
    writenums = Value('i', 0)
    getallurl_nums = maxurl
    getallurl_pool = Pool(processes=getallurl_nums)
    getinfo_nums = maxinfo
    getinfo_pool = Pool(processes=getinfo_nums)
    save_to_csv_nums = maxcsv
    save_to_csv_pool = Pool(
        processes=save_to_csv_nums,
        initializer=init,
        initargs=(
            writenums,
        ))
    page_links_queue = Manager().Queue()
    item_url_queue = Manager().Queue()
    item_info_queue = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    make_page_links(page_links_queue, firsturl, startlist, endlist)  # 调用函数构造list
    for index in range(0, getallurl_nums):  # 获取item list
        getallurl_pool.apply_async(func=get_item_url, args=(page_links_queue, item_url_queue, header))
    for index in range(0, getinfo_nums):
        getinfo_pool.apply_async(func=get_item_info, args=(item_url_queue, item_info_queue, header))
    for index in range(0, save_to_csv_nums):
        save_to_csv_pool.apply_async(
            func=save_to_csv, args=(
                item_info_queue, filename,))

    getallurl_pool.close()
    getallurl_pool.join()
    for i in range(0, getinfo_nums):
        item_url_queue.put("#END#")
    getinfo_pool.close()
    getinfo_pool.join()
    for i in range(0, save_to_csv_nums):
        item_info_queue.put("#END#")
    save_to_csv_pool.close()
    save_to_csv_pool.join()
    print("已写入  " + str(writenums) + "  条数据")
