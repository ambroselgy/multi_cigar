# from bs4 import BeautifulSoup
# import requests
# import time
# from multiprocessing import Pool, Manager, Value
# from pymongo import MongoClient
# import datetime
# import csv
# import allsite_fuc as site
# import traceback
#
#
# def sleeptime(hour, min, sec):
#     return hour * 3600 + min * 60 + sec
#
#
# def init(args):
#     global writenums
#     writenums = args
#
#
# def make_page_links(page_links, page_links_queue):
#     for index in page_links:
#         print(index + "   放入链接池")
#         page_links_queue.put(index)
#     page_links_queue.put("#END#")
#
#
# def get_item_url(page_links_queue, item_url_queue, header):
#     while True:
#         tmp_links = page_links_queue.get()
#         print("开始解析 " + str(tmp_links) + "  数据")
#         if tmp_links == "#END#":  # 遇到结束标志，推出进程
#             page_links_queue.put("#END#")
#             print("get_item_url Quit {}".format(page_links_queue.qsize()))
#             break
#         else:
#             r = requests.get(tmp_links, headers=header)
#             while r.status_code != 200:
#                 time.sleep(10)
#                 print("重新解析  " + str(tmp_links) + "   数据")
#                 r = requests.get(tmp_links, headers=header)
#             r.encoding = 'utf-8'
#             html = r.text
#             soup = BeautifulSoup(html, "html.parser")
#             try:
#                 if 'selected-cigars.com' in tmp_links:
#                     item_url_list = site.selectcigars_get_item_url(tmp_links, soup)
#                     for i in item_url_list:
#                         item_url_queue.put(i)
#                 elif 'cigarworld.de' in tmp_links:
#                     item_url_list = site.cigarworld_get_item_url(tmp_links, soup)
#                     for i in item_url_list:
#                         item_url_queue.put(i)
#                 elif 'alpscigar.com' in tmp_links:
#                     item_url_list = site.alpscigar_get_item_url(tmp_links, soup)
#                     for i in item_url_list:
#                         item_url_queue.put(i)
#                 else:
#                     print('网址错误')
#             except Exception as err:
#                 print(str(tmp_links) + "    列表页解析报错")
#                 print(err.args)
#                 print(traceback.format_exc())
#
#
# def get_item_info(item_url_queue, item_info_queue, header):
#     while True:
#
#         while item_url_queue.empty():
#             time.sleep(0.01)
#
#         tmp_items = item_url_queue.get()
#         if tmp_items == "#END#":  # 遇到结束标志，推出进程
#             print("get_item_info Quit {}".format(item_url_queue.qsize()))
#             print("队列剩余" + str(item_info_queue.qsize()))
#             break
#         else:
#             print("开始获取 " + str(tmp_items) + "  数据")
#             r = requests.get(tmp_items, headers=header)
#             times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#             while r.status_code != 200:
#                 time.sleep(10)
#                 print(r.status_code)
#                 print("重新获取  " + str(tmp_items) + "   数据")
#                 r = requests.get(tmp_items, headers=header)
#             r.encoding = 'utf-8'
#             html = r.text
#             soup = BeautifulSoup(html, "lxml")
#             try:
#                 if 'selected-cigars.com' in tmp_items:
#                     item_info_list = site.selectcigars_get_item_info(tmp_items, soup, item_info_queue, times)
#                     for i in item_info_list:
#                         item_info_queue.put(i)
#                 elif 'cigarworld.de' in tmp_items:
#                     item_info_list = site.cigarworld_get_item_info(tmp_items, soup, item_info_queue, times)
#                     for i in item_info_list:
#                         item_info_queue.put(i)
#                 elif 'alpscigar.com' in tmp_items:
#                     item_info_list = site.alpscigar_get_item_info(tmp_items, soup, item_info_queue, times)
#                     for i in item_info_list:
#                         item_info_queue.put(i)
#                 else:
#                     print('网址错误')
#             except Exception as err:
#                 print(str(tmp_items) + "    商品获取报错")
#                 print(err.args)
#                 print(traceback.format_exc())
#
#
# def save_to_mongodb(item_info_queue):
#     connect = MongoClient(host='localhost', port=27017)
#     db = connect['alpscigar']
#     collection = db['stock']
#     global writenums
#
#     while True:
#         while item_info_queue.empty():
#             time.sleep(0.02)
#         cigarinfo = item_info_queue.get()
#         group = cigarinfo["group"]
#         if cigarinfo == "#END#":  # 遇到退出标志，退出进程
#             print("数据存储完成")
#             break
#         else:
#             try:
#                 tmp_data = cigarinfo
#                 tmp_del = ['group', 'Brand', 'cigar_name', 'itemurl']
#                 tmp_filter = {'group': tmp_data['group'], 'Brand': tmp_data['Brand'],
#                               'cigar_name': tmp_data['cigar_name'], 'itemurl': tmp_data['itemurl']}
#                 for i in tmp_del:
#                     del tmp_data[i]
#                 collection.update_one(
#                     filter=tmp_filter, update={
#                         "$set": tmp_data}, upsert=True)
#                 with writenums.get_lock():
#                     writenums.value += 1
#             except Exception as err:
#                 print(group + "    存储报错")
#                 print(err.args)
#                 print(traceback.format_exc())
#
# def start_work_mongodb(links, maxurl, maxinfo, maxsave):
#     '''组织抓取过程'''
#     writenums = Value('i', 0)
#     get_item_url_nums = maxurl
#     get_item_url_pool = Pool(processes=get_item_url_nums)
#     get_item_info_nums = maxinfo
#     get_item_info_pool = Pool(processes=get_item_info_nums)
#     save_to_mongodb_nums = maxsave
#     save_to_mongodb_pool = Pool(
#         processes=save_to_mongodb_nums,
#         initializer=init,
#         initargs=(
#             writenums,
#         ))
#     page_links_queue = Manager().Queue()
#     item_url_queue = Manager().Queue()
#     item_info_queue = Manager().Queue()
#     header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
#                             ' (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
#     make_page_links(links, page_links_queue)  # 调用函数构造list
#     for index in range(0, get_item_url_nums):  # 获取item list
#         get_item_url_pool.apply_async(
#             func=get_item_url, args=(
#                 page_links_queue, item_url_queue, header,))
#     for index in range(0, get_item_info_nums):
#         get_item_info_pool.apply_async(
#             func=get_item_info, args=(
#                 item_url_queue, item_info_queue, header,))
#     for index in range(0, save_to_mongodb_nums):
#         save_to_mongodb_pool.apply_async(
#             func=save_to_mongodb, args=(
#                 item_info_queue,))
#
#     get_item_url_pool.close()
#     get_item_url_pool.join()
#     for i in range(0, get_item_info_nums):
#         item_url_queue.put("#END#")
#     get_item_info_pool.close()
#     get_item_info_pool.join()
#     for i in range(0, save_to_mongodb_nums):
#         item_info_queue.put("#END#")
#     save_to_mongodb_pool.close()
#     save_to_mongodb_pool.join()
#     print("已写入  " + str(writenums.value) + "  条数据")
#
# def make_website_links():
#     links = []
#
#     for index in range(1, 16 + 1):
#         links.append("https://alpscigar.com/product-category/cuban-cigars/page/"+str(index)+"/?wmc-currency=EUR")  # 构造select-cigars links
#     return links
# second = sleeptime(1, 0, 0)  # 间隔运行时间 时：分：秒
# if __name__ == '__main__':
#     links = make_website_links()
#     maxurl = 3  # 解析列表页，获取商品链接的进程
#     maxinfo = 5  # 获取商品信息的进程
#     maxsave = 1  # 存储进程
#     runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
#     st = time.time()
#     start_work_mongodb(links, maxurl, maxinfo, maxsave)
#     print(time.time() - st)
#


from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime
def run():

    tmp_items = 'https://alpscigar.com/shop/humidors/limited-edition/cubatabaco-1492-humidor-1992/?wmc-currency=EUR'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    tmp_post = 'https://alpscigar.com/mod_pagespeed_beacon?url=https%3A%2F%2Falpscigar.com%2Fproduct-category%2Fcuban-cigars%2Fpage%2F7%2F'
    r = requests.post(tmp_post,headers=header)
    r.encoding='utf-8'
    html = r.text
    print(html)
    # r = requests.get(tmp_items, headers=header)
    # times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # while r.status_code != 200:
    #     time.sleep(10)
    #     print(r.status_code)
    #     print("重新获取  " + str(tmp_items) + "   数据")
    #     r = requests.get(tmp_items, headers=header)
    # r.encoding = 'utf-8'
    # html = r.text
    # soup = BeautifulSoup(html, "lxml")
    # tmp_brand = soup.find('tr',class_='woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_brand')
    # if tmp_brand:
    #     brand = tmp_brand.find('td', class_='woocommerce-product-attributes-item__value').get_text().strip()
    # else:
    #     brand = 'other'
    # group = soup.find('h1',class_='product-title product_title entry-title').get_text()
    # cigar_name = re.sub(r'\((\d+)\)$', '', group)
    # tmp_pricelist = soup.select('div.product-info.summary.entry-summary.col.col-fit.product-summary.text-left.form-flat')
    # tmp_detailed = tmp_pricelist[0].find('del')
    # if tmp_detailed:
    #     cigar_price = tmp_detailed.find('span',class_='woocommerce-Price-amount amount').get_text().replace("€", "").replace("'","").strip()
    #     detailed = tmp_pricelist[0].find('ins').find('span',class_='woocommerce-Price-amount amount').get_text().replace("€", "").replace("'","").strip()
    # else:
    #     tmp_cigar_price = tmp_pricelist[0].find('span',class_='woocommerce-Price-amount amount')
    #     if tmp_cigar_price:
    #         cigar_price = tmp_cigar_price.get_text().replace("€", "").replace("'","").strip()
    #         detailed = cigar_price
    #     else:
    #         cigar_price = '0'
    #         detailed = cigar_price
    # tmp_stock = tmp_pricelist[0].find('p', attrs={'class': re.compile(r'^stock')})
    # if tmp_stock:
    #     stock = tmp_stock.get_text()
    # else:
    #     stock = 'in stock'
    # print(brand)
    # print(cigar_name)
    # print(group)
    # print(cigar_price)
    # print(detailed)
    # print(stock)

run()
