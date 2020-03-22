from bs4 import BeautifulSoup
import requests
import re
import time
from multiprocessing import Pool, Manager, Value
import datetime

def cigarworld_get_item_info():
    tmp_links = 'https://www.cigarworld.de/en/zigarren/cuba/limitadas/bolivar-edicion-limitada-soberanos-el-2018-90007188_36872'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    r = requests.get(tmp_links, headers=header)
    r.encoding = 'utf-8'
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    item_list = soup.select("li.ws-g.DetailVariant")
    brand = soup.find('h1').string.strip()
    times = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cigarinfo_list = []
    if item_list:
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
                    tmp_name = brand + " " + str(cigar_name)
                    price = pricelist[i].text.replace("€", "").strip()
                    tmp_nums = numslist[i].text
                    tmp_stock = numslist[i].get('title').strip()
                    if tmp_stock:
                        stock = tmp_stock
                    else:
                        stock = "in stock"
                    # nums = re.sub(r'\D',"",tmp_nums)
                    nums = tmp_nums
                    group = tmp_name + '  ' + str(nums)
                    details = '0'
                    detailed = price
                    cigarinfo = {
                        'Brand': brand,
                        'cigar_name': tmp_name,
                        'group': group,
                        'detailed': detailed,
                        'stock': stock,
                        'details': details,
                        'cigar_price': price,
                        'itemurl': itemurl,
                        'times': times}
                    cigarinfo_list.append(cigarinfo)
            else:
                print("比对不通过 " + tmp_links)
    else:
        cigar_name = soup.find('h4',class_='h-alt h-alt-nm').string.strip()
        numslist = soup.find_all(
            'span', attrs={
                'class': re.compile(r'einheitlabel')})
        pricelist = soup.find_all('span',class_='preis')
        if len(numslist) == len(pricelist):
            for i in range(len(pricelist)):
                tmp_name = brand + " " + str(cigar_name)
                price = pricelist[i].text.replace("€", "").strip()
                tmp_nums = numslist[i].text
                tmp_stock = numslist[i].get('title').strip()
                if tmp_stock:
                    stock = tmp_stock
                else:
                    stock = "in stock"
                nums = tmp_nums
                group = tmp_name + '  ' + str(nums)
                details = '0'
                detailed = price
                itemurl = tmp_links
                cigarinfo = {
                    'Brand': brand,
                    'cigar_name': tmp_name,
                    'group': group,
                    'detailed': detailed,
                    'stock': stock,
                    'details': details,
                    'cigar_price': price,
                    'itemurl': itemurl,
                    'times': times}
                cigarinfo_list.append(cigarinfo)

    return cigarinfo_list



cigarinfo_list=cigarworld_get_item_info()
print(cigarinfo_list)

