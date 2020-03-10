from multiprocessing import Process, Queue
import functions as fs


if __name__ == '__main__':
    nums = 6 #网站总页数，根据页数分配进程数量
    step = nums//2
    multi_list = []
    quelist = Queue()
    quelist.empty()
    infolist = []
    for i in range(1, nums, step):
        multi_list.append(Process(target=fs.run, args=("m"+str(i)+".csv", i, i + step, quelist)))
    for multi in multi_list:
        multi.start()
    print(multi_list)
    # while not quelist.empty():
    #     print(quelist.get())
