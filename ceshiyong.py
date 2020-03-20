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