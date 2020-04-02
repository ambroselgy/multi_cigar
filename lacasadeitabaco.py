from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime
import json
import traceback

def run():
    tmp_items=("https://www.lacasadeltabaco.com/zh-hans/product/romeo-y-julieta-mille-fleur-25/")
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
    brand = soup.find('meta', attrs={'property':'og:brand'})['content']
    cigar_price = soup.find('meta', attrs={'property':'product:price:amount'})['content']
    stock = soup.find('meta', attrs={'property':'product:availability'})['content']
    group = soup.find('h1', class_="product_title entry-title").get_text().strip()
    details = '0'
    detailed = cigar_price
    cigar_name = re.sub(r"\/(\d*)$", "", group).strip()
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