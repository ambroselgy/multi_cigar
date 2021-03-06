import functions as fs
import time
import datetime
import os
'''间隔时间运行的selected-cigars爬虫工具，使用multi模块实现多进程抓取，目前运行时间50S'''


def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec


second = sleeptime(1, 0, 0)  # 间隔运行时间 时：分：秒
# filename = "./data/multe_" + str(runtime) + ".csv"  # 存储文件根据时间自动命名
if __name__ == '__main__':
    if not os.path.isdir('./data/'):
        os.mkdir('./data/')
   # while True:
    firsturl = "https://selected-cigars.com/en/cigars?p="  # 网站列表页模板
    startlist = 1  # 商品列表起始
    endlist = 14  # 商品列表终页
    maxurl = 5  # url获取进程数分配
    maxinfo = 15  # 商品信息获取进程数分配
    maxcsv = 1  # csv写入进程数分配
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    runtime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")  # 生成时间
    filename = "./data/multe_" + str(runtime) + ".csv"  # 存储文件根据时间自动命名
    st = time.time()
    fs.start_work(
        filename,
        firsturl,
        startlist,
        endlist,
        maxurl,
        maxinfo,
        maxcsv)
    print(time.time() - st)
    #  time.sleep(second)
