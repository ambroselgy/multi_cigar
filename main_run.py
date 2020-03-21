import time
import datetime
from cigar_class import Scigars

if __name__ == '__main__':
    #    while True:
    firsturl = "https://selected-cigars.com/en/cigars?p="  # 网站列表页模板
    startlist = 1  # 商品列表起始
    endlist = 14  # 商品列表终页
    maxurl = 5  # 解析列表页，获取商品链接的进程
    maxinfo = 15  # 获取商品信息的进程
    maxsave = 3  # 存储进程
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
    st = time.time()
    scigars = Scigars()
    scigars.run()
    print(time.time() - st)