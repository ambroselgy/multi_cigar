from bs4 import BeautifulSoup
import requests
import re
import time
import datetime
def run():
    tmp_items = 'https://www.cigarworld.de/en/zigarren/cuba/regulares/flor-de-cano-selectos-ccun-dh-januar-1999-01003_18104'
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
    if tmp_list:
        for i in tmp_list:
            tmp_brand = i.find('div', class_='ws-u-1 VariantInfo-itemName').text
            if 'Brand' in tmp_brand:
                brand = i.find('div', class_='ws-u-1 VariantInfo-itemValue').text
            elif 'Item' in tmp_brand:
                cigar_name = i.find('div', class_='ws-u-1 VariantInfo-itemValue').text
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
            item_info_list.append(cigarinfo)
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
            item_info_list.append(cigarinfo)
    for i in item_info_list:
        print(i)

run()