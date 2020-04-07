import time
from pymongo import MongoClient
import csv
import os

def run():
    connect = MongoClient(host='localhost', port=27017)
    db = connect['cigarstock']
    collection = db['stock']
    find_brand = ''
    find_cigar_name = ''
    find_stock = ''
    if not os.path.isdir('./data/'):
        os.mkdir('./data/')
    filename = './data/cigarstock.csv'
    find_list = collection.find({"$and": [{"Brand": {"$regex":find_brand,'$options':'i'}}, {"cigar_name": {"$regex":find_cigar_name,'$options':'i'}}]})
    for i in find_list:
        del i['_id']
        with open(filename, "a", encoding='utf-8-sig', newline='') as csvfile:
            headers = [
                'Brand',
                'cigar_name',
                'group',
                'detailed',
                'stock',
                'details',
                'cigar_price',
                'itemurl',
                'times']
            csvwriter = csv.DictWriter(csvfile, fieldnames=headers)
            rowwriter = csv.writer(csvfile)
            with open(filename, 'r', encoding='utf-8-sig') as rowfile:
                rowreader = csv.reader(rowfile)
                if not [row for row in rowreader]:
                    rowwriter.writerow(
                        ['品牌', '型号', '雪茄', '税前价格', '库存', '折扣', '原价', '链接', '更新时间'])
                    csvwriter.writerow(i)
                    csvfile.close()
                else:
                    csvwriter.writerow(i)
                    csvfile.close()


run()