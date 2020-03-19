import multiprocessing as mp
from multiprocessing import Value, Array
import threading
import time
import pdb

def init(args):
    ''' store the counter for later use '''
    global counter
    counter = args

def run():
    global counter
    for i in range(0, 3):
        time.sleep(1);
        with counter.get_lock():
            counter.value += 1
        print(counter.value)

if __name__ == "__main__":
    counter = Value('i', 0)
    pool = mp.Pool(processes=5, initializer=init, initargs=(counter,))
    print("I am set counter:%s" % (counter.value))
    for i in range(0, 10):
        # pdb.set_trace()
        pool.apply_async(run, ())
    pool.close()
    pool.join()
    print("I am set counter:%s" % (counter.value))