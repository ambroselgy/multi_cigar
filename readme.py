from multiprocessing import Process, Queue
for i in range(5):
     locals()['Q%s'%i] = Queue()



print(locals()['Q%s'%1],locals()['Q%s'%2],Q2)