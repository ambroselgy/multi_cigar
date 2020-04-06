from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime

def run():
    tmp_items = 'https://www.cigarworld.de/en/zigarren/cuba/regulares/bolivar-belicosos-finos-01001_6'
    #tmp_items = 'https://www.cigarworld.de/en/zigarren/cuba/raritaeten/la-gloria-cubana-sonderhumidor-haus-15-piramides-amp-15-robusto-extra-90014051_30961'
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
    tmp_list = soup.select('div.ws-g.VariantInfo div.ws-g.ws-c')
    brand_find = soup.find('div',class_='ws-u-1 VariantInfo-itemName', text='Brand')
    if brand_find:
        brand = brand_find.parent.find('div', class_='ws-u-1 VariantInfo-itemValue').get_text().strip()
    else:
        brand = 'other'
    cigar_name_find = soup.find('div',class_='ws-u-1 VariantInfo-itemName', text='Item')
    if cigar_name_find:
        cigar_name = brand + ' ' + cigar_name_find.parent.find('div', class_='ws-u-1 VariantInfo-itemValue').get_text().strip()
    else:
        cigar_name = brand + ' ' + soup.find('h1').string.strip()
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
        group = cigar_name + ' ' + nums
        if tmp_details:
            details = re.sub(r'\*', '', tmp_details.text.strip())
        else:
            details = 0

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
        item_info_list.append(cigarinfo)
        print(cigarinfo)


run()
