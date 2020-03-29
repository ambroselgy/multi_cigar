'''
bs4生成对象 <class 'bs4.BeautifulSoup'>
对象find_all 或select后生成结果集 <class 'bs4.element.ResultSet'> 是tag的迭代对象
结果集for提取后是 <class 'bs4.element.Tag'> 可以使用属性(class,href,string等)

（1）find返回的是TAG对象,只有一个值，可以直接使用属性，例如：children,string,class等

（2）而find_all和select返回的是TAG对象的迭代对象，不能直接用TAG的属性，但是里面每个元素是TAG，可以用属性。
string和get_text的区别是string返回所有字符内容（包含注释等），而get_text返回正式的text内容

html_doc = """
<html><head><title>The Dormouse's story</title></head>

<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1"><!--Elsie--></a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc,'lxml')
head_tag = soup.find_all('a')
for i in head_tag:
    print(i.text)

print("-------------------")
for i in head_tag:
    print(i.get_text())
print("-------------------")
for i in head_tag:
    print(i.string)

print("-------------------")
print("soup的类型是对象",type(soup))
print("head_tag的类型是.Tag",type(head_tag))


string：用来获取目标路径下第一个非标签字符串，得到的是个字符串
strings：用来获取目标路径下所有的子孙非标签字符串，返回的是个生成器
stripped_strings：用来获取目标路径下所有的子孙非标签字符串，会自动去掉空白字符串，返回的是一个生成器
get_text：用来获取目标路径下的子孙字符串，返回的是字符串（包含HTML的格式内容）
text：用来获取目标路径下的子孙非标签字符串，返回的是字符串

with open("cigarworld.txt", 'r') as f:
tmp_links = f.readlines()
links = [i.strip() for i in tmp_links]
print(l)
'''
dc = {'8': {'attributes_values': {'1': 'Box 25 Pcs.'}, 'attributes': [4], 'price': 408.542247, 'specific_price': False, 'ecotax': 0, 'weight': 1, 'quantity': 4, 'reference': 'IN6001', 'unit_impact': '0.000000', 'minimal_quantity': '1', 'date_formatted': '', 'available_date': '', 'id_image': 410, 'list': "'4'"}, '192': {'attributes_values': {'1': 'SLB 25 Pcs.'}, 'attributes': [15], 'price': 408.542247, 'specific_price': False, 'ecotax': 0, 'weight': 1, 'quantity': 4, 'reference': 'IN6005', 'unit_impact': '0.000000', 'minimal_quantity': '1', 'date_formatted': '', 'available_date': '', 'id_image': 410, 'list': "'15'"}}
for num, info in dc.items():
    for k, v in info['attributes_values'].items():
        print(v)
        print(info['price'])


