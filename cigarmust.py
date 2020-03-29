from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime
import json

def run():
    tmp_items = 'https://cigarmust.com/en/juan-lopez/1634-juan-lopez-eminentes-regional-edition-switzerland-2016.html'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    r = requests.get(tmp_items, headers=header)
    times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    while r.status_code != 200:
        time.sleep(10)
        print(r.status_code)
        print("重新获取  " + str(tmp_items) + "   数据")
        r = requests.get(tmp_items, headers=header)
    r.encoding = 'utf-8'
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    item_info_list = []
    tmp_pricelist = soup.find('script',attrs={'type':'text/javascript'}).get_text()
    pattern = re.compile(r"var combinations = (\{.*\})\;")
    priceinfo = json.loads(pattern.search(tmp_pricelist).group(1))
    tmp_brand = soup.find('div', attrs={'class':'rte','id':''}).find('strong', text=(re.compile(r'Marca')))
    print(tmp_brand.parent)
    if tmp_brand:
        brand = list(tmp_brand.parent.stripped_strings)[-1]
    cigar_name = soup.find('h1').get_text()
    for num, info in priceinfo.items():
        cigar_price = info['price']
        details = '0'
        detailed = cigar_price
        if info['quantity'] != 0:
            stock = 'in stock'
        else:
            stock = 'sold out'
        for k, v in info['attributes_values'].items():
            group = cigar_name + " " + v
            cigarinfo = {
                'Brand': brand,
                'cigar_name': brand + ' ' + cigar_name,
                'group': group,
                'detailed': detailed,
                'stock': stock,
                'details': details,
                'cigar_price': cigar_price,
                'itemurl': tmp_items,
                'times': times}
            item_info_list.append(cigarinfo)
    for i in item_info_list:
        print(i)

run()