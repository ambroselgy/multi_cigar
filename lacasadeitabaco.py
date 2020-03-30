from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime
import json
import traceback

def run():
    tmp_items=("https://www.lacasadeltabaco.com/zh-hans/product/flor-de-cano-preferidos-loc-mar02-vintage-03-02-5/")
    # for i in links:
    #     tmp_items = i
    #     print("开始解析  "+str(i))
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    r = requests.get(tmp_items, headers=header, timeout=50)
    times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    while r.status_code != 200:
        time.sleep(10)
        print(r.status_code)
        print("重新获取  " + str(tmp_items) + "   数据")
        r = requests.get(tmp_items, headers=header)
    r.encoding = 'utf-8'
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    try:
        item_list = soup.select('div.shop_product_metas > h3')
        for i in item_list:
            print(i.find('a')['href'])
    except Exception as err:
        print(err.args)
        print(traceback.format_exc())
    tmp_brand = soup.find('p',attrs={"itemprop":"brand"})
    if tmp_brand:
        brand = tmp_brand.get_text()
    else:
        brand = 'other'
    group = soup.find('h1',class_="product_title entry-title").get_text()
    cigar_name = re.sub(r"\/(\d*)$","",group).strip()
    tmp_cigar_price = soup.select("div.product_price > p.price > span.woocommerce-Price-amount.amount")
    cigar_price = tmp_cigar_price[0].get_text().replace("€", "").replace(",",".").strip()
    stock = 'in stock'
    detailed = cigar_price
    details = '0'
    cigarinfo = {
        'Brand': brand,
        'cigar_name': cigar_name,
        'group': group,
        'detailed': detailed,
        'stock': stock,
        'details': details,
        'cigar_price': cigar_price,
        'itemurl': tmp_items,
        'times': times}
    print(cigarinfo)

run()