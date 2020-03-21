from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Pool, Manager, Value
from pymongo import MongoClient
import datetime


def get_item_info():
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    html = 'https://selected-cigars.com/en/cohiba-50-short-1'
    tmp_items = html
    if tmp_items == "#END#":  # 遇到结束标记，退出进程
        print("end")
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
                print('item_list 不空')
                for i in item_list:
                    tmp_stock = i.find('div', class_='stockindicator-content')
                    stock = tmp_stock.find('span').string.strip()
                    if i.find('strong', class_="product-item-name sc-grouped-title"):
                        group = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                    else:
                        group = i.find('span', class_="base").string.strip()
                    cigarprice = i.find('span', attrs={
                        "data-price-type": "finalPrice"}).find('span', class_="price").string.strip()
                    tmp_price = cigarprice[1:]
                    price = tmp_price.replace(",", "")
                    itemurl = tmp_items
                    details = i.find('span', class_="savingPercent").string.strip().replace(" ", "")
                    if details:
                        pass
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
                    print(cigarinfo)
            else:
                print('item_list为空')
                group = cigar_name
                tmp_stock = soup.find('div', class_='stockindicator-content')
                stock = tmp_stock.find('span').string.strip()
                cigarprice = soup.find('span', attrs={
                    "data-price-type": "finalPrice"}).find('span', class_="price").string.strip()
                tmp_price = cigarprice[1:]
                price = tmp_price.replace(",", "")
                itemurl = tmp_items
                if soup.find('span', class_="savingPercent"):
                    details = soup.find(
                        'span', class_="savingPercent").string.strip().replace(
                        " ", "")
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
                print(cigarinfo)
        except Exception as err:
            print(str(tmp_items) + "    商品获取报错")
            print(err)

get_item_info()