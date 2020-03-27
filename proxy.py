import requests
from bs4 import BeautifulSoup
proxyHost = "58.218.200.229"
proxyPort = "2662"
proxyMeta = "https://%(host)s:%(port)s" % {

    "host" : proxyHost,
    "port" : proxyPort,
}

proxies = {
    "https"  : proxyMeta,
}

# r = requests.get(targetUrl, proxies=proxies)
#
#
#
# import random
# proxy = [
#     {
#         'http': 'http://61.135.217.7:80',
#         'https': 'http://61.135.217.7:80',
#     },
# {
#         'http': 'http://118.114.77.47:8080',
#         'https': 'http://118.114.77.47:8080',
#     },
# {
#         'http': 'http://112.114.31.177:808',
#         'https': 'http://112.114.31.177:808',
#     },
# {
#         'http': 'http://183.159.92.117:18118',
#         'https': 'http://183.159.92.117:18118',
#     },
# {
#         'http': 'http://110.73.10.186:8123',
#         'https': 'http://110.73.10.186:8123',
#     },
# ]
# url = '爬取链接地址'
# response = requests.get('url',proxies=random.choice(proxy))

api = 'http://http.tiqu.alicdns.com/getip3?num=20&type=2&pro=&city=0&yys=100026&port=11&pack=89501&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
r = requests.get(api)
r.encoding = 'utf-8'
html = r.text
soup = BeautifulSoup(html, "html.parser")
print(soup)