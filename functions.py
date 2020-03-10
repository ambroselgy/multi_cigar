from bs4 import BeautifulSoup
import requests
import csv
import os

def getallurl(baseurl, header, page):
    r = requests.get(baseurl,headers = header)
    r.encoding = 'utf-8'
    html = r.text
    #print(html)
    soup = BeautifulSoup(html,"html.parser")
    #print(soup)
    product = soup.find_all('li', class_ ="item product product-item")
    urllist = []
    try:
        for i in product:
            if not i.find_all('span', text = "Out of stock"):
                x = i.find('strong', class_="product name product-item-name")
                url = x.find('a')['href']
                urllist.append(url)
        print("进程 "+str(os.getpid())+" "+str(baseurl)+" 链接获取完成，返回urllist")
        return urllist
    except:
        return print("链接无效")

def getinfo(url, header):
    print('开始获取商品数据', url)
    r = requests.get(url, headers=header)
    r.encoding = 'utf-8'
    html = r.text
    itempage = BeautifulSoup(html, "html.parser")
    itemlist = itempage.find_all('td', class_ = "col item", attrs={"data-th":"Product Name"})
    try:
        for i in itemlist:
            if not i.find_all('span', text = "Sold Out"):
                cigarlist = i.find('strong', class_="product-item-name sc-grouped-title").string.strip()
                cigarprice = i.find('span', attrs={"data-price-type":"finalPrice"}).find('span',class_="price").string.strip()
                price = cigarprice[1:]
        itemurl = url
        return{
            'cigar_name':cigarlist,
            'cigar_price':price,
            'itemurl':str(itemurl)
        }
    except:
        cigarlist = "数据错误"
        price = "数据错误"
        itemurl = url
        return {
            'cigar_name': cigarlist,
            'cigar_price': price,
            'itemurl': str(itemurl)
        }

def save_to_csv(filename, result={}):
    filename = filename
    with open(filename, "a", encoding='utf-8-sig', newline='') as csvfile:
        headers = ['cigar_name', 'cigar_price','itemurl']
        csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
        csvwriter.writerow(result)
        csvfile.close()
def run(filename, startpage, endpage, quelist):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    filename = filename
    firsturl = "https://selected-cigars.com/en/cigars?p="
    txtlist = []
    for x in range(startpage, endpage):
        page = x
        baseurl = firsturl + str(page)
        print("进程： "+str(os.getpid())+" 正在打开 "+baseurl)
        for url in getallurl(baseurl, header, page):
            if not quelist.full():
                quelist.put(url)
            else:
                print("无法写入queue")
        print(quelist.qsize())
