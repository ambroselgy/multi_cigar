from multiprocessing import Process, Queue, Pool, Manager
import functions as fs
import time



def start_work():
    '''组织抓取过程'''
    processnums = 10
    pool = Pool(processes=10)
    links = Manager().Queue()
    items = Manager().Queue()
    cigars = Manager().Queue()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'}
    filename = "multi.csv"
    firsturl = "https://selected-cigars.com/en/cigars?p="
    startlist = 1
    endlist = 14
#    init()
    fs.makelinks(links, firsturl, startlist, endlist)#调用函数构造list
    for index in range(0, 1):#获取item list
        pool.apply_async(func=fs.getallurl, args=(links, items, header))
    for index in range(0, 8):
        pool.apply_async(func=fs.getinfo, args=(items, cigars, header))
    for index in range(0, 1):
        pool.apply_async(func=fs.save_to_csv, args=(cigars, filename))

    pool.close()
    pool.join()
    # for index in cigars.get():
    #     print(index)

if __name__ == '__main__':
    st = time.time()
    start_work()
    print(time.time()-st)
