#_*_ coding : UTF-8 _*_
#开发人员：Diya
#开发时间：2020/3/19 13:51
#文件名称: mogodb_find.PY
#开发工具：PyCharm
#$lt和<，$lte和<=，$gt和>，gte和>=，ne和!=   $in和$nin  $not 和 $and $or

#{"$and": [{"cigar_name": {"$regex":"Cohiba"}}, {"stock": {"$regex": "available"}}]}
#{"stock":{$not: {"$regex":"sold",'$options':'i'}}}
#{"cigar_name":{"$regex":"bolivar",'$options':'i'}}
#{"cigar_name":{"$regex":"Bolívar",'$options':'i'}}
#{$and:[{"cigar_name":{"$regex":"cohiba",'$options':'i'}},{"stock":{$not:{"$regex":"sold",'$options':'i'}}}]}
#{$or:[{"cigar_name":{"$regex":"bolivar",'$options':'i'}},{"cigar_name":{"$regex":"Bolívar",'$options':'i'}}]}
#{$and:[{$or:[{"cigar_name":{"$regex":"bolivar",'$options':'i'}},{"cigar_name":{"$regex":"Bolívar",'$options':'i'}}]},{"group":{"$regex":"petit",'$options':'i'}}]}