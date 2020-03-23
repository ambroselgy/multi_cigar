from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, Value
import re


def selectcigars_get_item_url(tmp_links, soup):
    item_url_list = []
    product = soup.find_all(
        'li', class_="item product product-item")
    for i in product:
        x = i.find(
            'strong', class_="product name product-item-name")
        url = x.find('a')['href']
        item_url_list.append(url)
    return item_url_list


def cigarworld_get_item_url(tmp_links, soup):
    item_url_list = []
    item_list = soup.select("li.ws-g.DetailVariant")
    if item_list:
        for i in item_list:
            tmp_itemurl = i.find(
                'a', attrs={
                    'class': 'ws-u-1 ws-u-lg-4-24 DetailVariant-col DetailVariant-image'})['href']
            url = 'https://www.cigarworld.de' + tmp_itemurl
            item_url_list.append(url)
    else:
        url = tmp_links
        item_url_list.append(url)
    return item_url_list

def selectcigars_get_item_info(tmp_items, soup, item_info_queue,times):
    item_info_list = []
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
            item_info_list.append(cigarinfo)
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
        item_info_list.append(cigarinfo)
    return item_info_list

def cigarworld_get_item_info(tmp_items, soup, item_info_queue,times):
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

    return item_info_list