'''

makelinks 构建page list，结束后放入end
geturl get page list，结果放入 url list，get到end后，end放入url list，url list中的end总数是get url的进程数
getinfo get url list，结果放入info，get到end后退出，如果get info 进程数与get url相等，不会存在问题。

makelinks  1 end
geturl