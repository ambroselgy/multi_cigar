'''

makelinks 构建page list，结束后放入end
geturl get page list，结果放入 url list，get到end后，end放入url list，url list中的end总数是get url的进程数
getinfo get url list，结果放入info，get到end后退出，如果get info 进程数与get url相等，不会存在问题。

makelinks  1 end
geturl


bs4生成对象 <class 'bs4.BeautifulSoup'>
对象find_all 或select后生成结果集 <class 'bs4.element.ResultSet'> 是tag的哦迭代对象
结果集for提取后是 <class 'bs4.element.Tag'> 可以使用属性

（1）find返回的是TAG对象,只有一个值，可以直接使用属性，例如：children

（2）而find_all和select返回的是TAG对象的迭代对象，不能直接用TAG的属性，但是里面每个元素是TAG，可以用属性。