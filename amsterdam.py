from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import MongoClient
import datetime
def run():

    tmp_items = 'https://lcdh-amsterdam.com/index.php?route=product/product&path=59_144&product_id=723'
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
    brand_find = soup.find('', text=re.compile(r'Brand: ', re.I)).next_sibling
    if brand_find:
        brand = brand_find.get_text()
    else:
        brand = 'other'
    stock_find = soup.find('li', text=re.compile(r'Availa.*\:'))
    if stock_find:
        stock = re.sub(r'.*\:', '', stock_find.get_text()).strip()
    else:
        stock = 'sold out'
    price_find = soup.find('h2', class_='productprice')
    if price_find:
        single_price = price_find.get_text().replace("€", "").replace(",", "").strip()
    details = '0'
    cigar_name_find = soup.find('h1')
    if cigar_name_find:
        cigar_name = cigar_name_find.get_text()
    else:
        cigar_name = 'other'
    group_find = soup.find_all('option', attrs={'value':re.compile(r'\d')})
    for i in group_find:
        tmp_group = i.get_text().strip()
        if tmp_group == 'Singles':
            cigar_price = single_price
            group = cigar_name + " " + tmp_group
        else:
            cigar_price = str(round(int(re.findall(r"\d+\.?\d*", tmp_group)[0]) * float(single_price),2))
            group = cigar_name + " " + tmp_group
        detailed = cigar_price
        print(brand)
        print(cigar_name)
        print(group)
        print(cigar_price)
        print(detailed)
        print(stock)

run()

def make_links():
    links = []
    tmp_page_links = soup.select('a.list-group-item')
    if tmp_page_links:
        for i in tmp_page_links:
            if not len(i.get('class')) > 1:
                url = i['href']+'&page=1'
                url_t = i['href']+'&page=2'
                links.extend([url, url_t])

def get_url():
    tmp_item_url = soup.select('div.product-thumb h4 a')
    if tmp_item_url:
        for i in tmp_item_url:
            item_url = i['href']
            print(item_url)


# tmp_brand = soup.find('tr',
#                       class_='woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_brand')
# if tmp_brand:
#     brand = tmp_brand.find('td', class_='woocommerce-product-attributes-item__value').get_text().strip()
# else:
#     brand = 'other'
# group = soup.find('h1', class_='product-title product_title entry-title').get_text()
# cigar_name = re.sub(r'\((\d+)\)$', '', group)
# tmp_pricelist = soup.select('div.product-info.summary.entry-summary.col.col-fit.product-summary.text-left.form-flat')
# tmp_detailed = tmp_pricelist[0].find('del')
# if tmp_detailed:
#     cigar_price = tmp_detailed.find('span', class_='woocommerce-Price-amount amount').get_text().replace("€",
#                                                                                                          "").replace(
#         "'", "").strip()
#     detailed = tmp_pricelist[0].find('ins').find('span', class_='woocommerce-Price-amount amount').get_text().replace(
#         "€", "").replace("'", "").strip()
# else:
#     tmp_cigar_price = tmp_pricelist[0].find('span', class_='woocommerce-Price-amount amount')
#     if tmp_cigar_price:
#         cigar_price = tmp_cigar_price.get_text().replace("€", "").replace("'", "").strip()
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