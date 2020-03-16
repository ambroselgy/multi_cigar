#_*_ coding : UTF-8 _*_
#开发人员：Diya
#开发时间：2020/3/16 13:55
#文件名称: mongodb.PY
#开发工具：PyCharm
from pymongo import MongoClient
import datetime

connect = MongoClient(host='localhost', port=27017)
db = connect['select-cigars']
collection = db['stock']
list = collection.find({"cigar_name":"Sancho Panza - Non Plus 25pcs, wooden Box"})
tist = collection.find()
print(list)
print(tist)