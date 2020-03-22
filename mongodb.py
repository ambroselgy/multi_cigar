# _*_ coding : UTF-8 _*_
# 开发人员：Diya
# 开发时间：2020/3/16 13:55
#文件名称: mongodb.PY
# 开发工具：PyCharm
from pymongo import MongoClient
import datetime

connect = MongoClient(host='localhost', port=27017)
db = connect['test']
collection = db['test']
# collection.insert_one({
#   "Brand" : "Ramón Allones",
#   "cigar_name" : "Ramón Allones - Small Club Coronas",
#   "group" : "Ramón Allones - Small Club Coronas 1 piece",
#   "cigar_price" : "6.30",
#   "detailed" : "6.30",
#   "details" : "0",
#   "itemurl" : "https://selected-cigars.com/en/ramon-allones-small-club-coronas",
#   "stock" : "available",
#   "times" : "2020-03-22 14:35"
# })
# collection.insert_one({
#   "Brand" : "other",
#   "cigar_name" : "Ramón Allones - Small Club Coronas",
#   "group" : "Ramón Allones - Small Club Coronas 1 piece",
#   "cigar_price" : "6.30",
#   "detailed" : "6.30",
#   "details" : "0",
#   "itemurl" : "https://selected-cigars.com/en/ramon-allones-small-club-coronas",
#   "stock" : "available",
#   "times" : "2020-03-22 14:35"
# })
# collection.insert_one({
#   "Brand" : "cohiba",
#   "cigar_name" : "Ramón Allones - Small Club Coronas",
#   "group" : "Ramón Allones - Small Club Coronas 1 piece",
#   "cigar_price" : "6.30",
#   "detailed" : "6.30",
#   "details" : "0",
#   "itemurl" : "https://selected-cigars.com/en/ramon-allones-small-club-coronas",
#   "stock" : "available",
#   "times" : "2020-03-22 14:35"
# })


#cigarinfo = {'Brand': brand,'cigar_name': cigar_name,'group': group,'detailed': detailed,'stock': stock,
#             'details': details,'cigar_price': price,'itemurl': str(itemurl),'times': times}
tmp_filter = {'group':'Ramón Allones - Small Club Coronas 1 piece',
              'Brand':'cohiba',
              'cigar_name':'Ramón Allones - Small Club Coronas',
              'itemurl':'https://selected-cigars.com/en/ramon-allones-small-club-coronas'}
tmp_data = {
  "cigar_price" : "666",
  "detailed" : "666",
  "details" : "0",
  "stock" : "available",
  "times" : "2020-03-22 14:35"
}

collection.update_one(
    filter=tmp_filter, update={
        "$set": tmp_data}, upsert=True)