#_*_ coding : UTF-8 _*_
#开发人员：Diya
#开发时间：2020/3/16 13:55
#文件名称: mongodb.PY
#开发工具：PyCharm
from pymongo import MongoClient
import datetime

connect = MongoClient(host='localhost', port=27017)
db = connect['test']
collection = db['stock']
# collection.insert_one({"name":"user1", "age":12, "sex":"male"})
# collection.insert_one({"name":"user2", "age":13, "sex":"male"})
# collection.insert_one({"name":"user3", "age":14, "sex":"male"})
collection.find()
collection.update_one(filter={"name":"user99"}, update={"$set":{"age":99}}, upsert=True)
