from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, Value
import re


def selectcigars_get_item_url(soup):
    item_url_list = []
    product = soup.find_all(
        'li', class_="item product product-item")
    for i in product:
        x = i.find(
            'strong', class_="product name product-item-name")
        url = x.find('a')['href']
        item_url_list.append(url)
    return item_url_list


def cigarworld_get_item_url(soup):
    item_url_list = []
    product = soup.find_all(
        'a', attrs={'search-result-item-inner'})
    for i in product:
        tmp_url = i.get('href')
        url = 'https://www.cigarworld.de' + tmp_url
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
    item_list = soup.select("li.ws-g.DetailVariant")
    brand = soup.find('h1').string.strip()
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
                    item_info_list.append(cigarinfo)
            else:
                print("比对不通过 " + tmp_items)
    else:
        cigar_name = brand
        numslist = soup.find_all(
            'span', attrs={
                'class': re.compile(r'einheitlabel')})
        pricelist = soup.find_all('span', class_='preis')
        if len(numslist) == len(pricelist):
            for i in range(len(pricelist)):
                tmp_name = brand
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
                itemurl = tmp_items
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
                item_info_list.append(cigarinfo)
    return item_info_list