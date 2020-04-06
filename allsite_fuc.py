from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, Value
import re
import json


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

def alpscigar_get_item_url(tmp_links, soup):
    item_url_list = []
    item_list = soup.select("p.name.product-title")
    for i in item_list:
        url = i.find('a')['href']
        item_url_list.append(url+"?wmc-currency=EUR")

    return item_url_list

def cigarmust_get_item_url(tmp_links, soup):
    item_url_list = []
    item_list = soup.select("a.product_img_link")
    for i in item_list:
        item_url_list.append(i['href'])

    return item_url_list

def lacasadeltabaco_get_item_url(tmp_links, soup):
    item_url_list = []
    item_list = soup.select('div.shop_product_metas > h3')
    for i in item_list:
        item_url_list.append(i.find('a')['href'])
    return item_url_list

def amsterdam_get_item_url(tmp_links, soup):
    item_url_list = []
    tmp_item_url = soup.select('div.product-thumb h4 a')
    if tmp_item_url:
        for i in tmp_item_url:
            item_url = i['href']
            item_url_list.append(item_url)
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
                'Brand': brand.lower(),
                'cigar_name': cigar_name.lower(),
                'group': group.lower(),
                'detailed': detailed,
                'stock': stock.lower(),
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
            'Brand': brand.lower(),
            'cigar_name': cigar_name.lower(),
            'group': group.lower(),
            'detailed': detailed,
            'stock': stock.lower(),
            'details': details,
            'cigar_price': price,
            'itemurl': str(itemurl),
            'times': times}
        item_info_list.append(cigarinfo)
    return item_info_list

def cigarworld_get_item_info(tmp_items, soup, item_info_queue,times):
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

    return item_info_list

def alpscigar_get_item_info(tmp_items, soup, item_info_queue,times):
    item_info_list = []
    tmp_brand = soup.find('tr',class_='woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_brand')
    if tmp_brand:
        brand = tmp_brand.find('td', class_='woocommerce-product-attributes-item__value').get_text().strip()
    else:
        brand = 'other'
    group = soup.find('h1',class_='product-title product_title entry-title').get_text()
    cigar_name = re.sub(r'\((\d+)\)$', '', group)
    tmp_pricelist = soup.select('div.product-info.summary.entry-summary.col.col-fit.product-summary.text-left.form-flat')
    tmp_detailed = tmp_pricelist[0].find('del')
    if tmp_detailed:
        cigar_price = tmp_detailed.find('span',class_='woocommerce-Price-amount amount').get_text().replace("€", "").replace("'","").strip()
        detailed = tmp_pricelist[0].find('ins').find('span',class_='woocommerce-Price-amount amount').get_text().replace("€", "").replace("'","").strip()
    else:
        tmp_cigar_price = tmp_pricelist[0].find('span',class_='woocommerce-Price-amount amount')
        if tmp_cigar_price:
            cigar_price = tmp_cigar_price.get_text().replace("€", "").replace("'","").strip()
            detailed = cigar_price
        else:
            cigar_price = '0'
            detailed = cigar_price
    tmp_stock = tmp_pricelist[0].find('p', attrs={'class': re.compile(r'^stock')})
    if tmp_stock:
        stock = tmp_stock.get_text()
    else:
        stock = 'in stock'
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
    item_info_list.append(cigarinfo)

    return item_info_list

def cigarmust_get_item_info(tmp_items, soup, item_info_queue,times):
    item_info_list = []
    tmp_pricelist = soup.find('script', attrs={'type': 'text/javascript'}).get_text()
    cigar_name = soup.find('h1').get_text()
    pattern = re.compile(r"var combinations = (\{.*\})\;")
    priceinfo = json.loads(pattern.search(tmp_pricelist).group(1))
    tmp_brand = soup.find_all('span',attrs={'itemprop':'title'})[-1]
    if tmp_brand:
        brand = list(tmp_brand.parent.stripped_strings)[-1]
    else:
        brand = 'other'
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
                'cigar_name': cigar_name,
                'group': group,
                'detailed': detailed,
                'stock': stock,
                'details': details,
                'cigar_price': cigar_price,
                'itemurl': tmp_items,
                'times': times}
            item_info_list.append(cigarinfo)
    return item_info_list

def lacasadeltabaco_get_item_info(tmp_items, soup, item_info_queue,times):
    item_info_list = []
    brand = soup.find('meta', attrs={'property':'og:brand'})['content']
    group = soup.find('h1',class_="product_title entry-title").get_text().strip()
    cigar_name = re.sub(r"\/(\d*)$","",group).strip()
    cigar_price = soup.find('meta', attrs={'property':'product:price:amount'})['content']
    stock = soup.find('meta', attrs={'property':'product:availability'})['content']
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
    item_info_list.append(cigarinfo)
    return item_info_list

def amsterdam_get_item_info(tmp_items, soup, item_info_queue,times):
    item_info_list = []
    brand_find = soup.find('', text=re.compile(r'Brand: ', re.I))
    if brand_find:
        brand = brand_find.next_sibling.get_text()
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
    return item_info_list

