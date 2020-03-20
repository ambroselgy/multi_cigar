def save_to_csv(item_info_queue, filename):
    global writenums
    while True:
        while item_info_queue.empty():
            time.sleep(0.02)
        cigarinfo = item_info_queue.get()
        if cigarinfo == "#END#":  # 遇到退出标志，退出进程
            print("数据存储完成")
            break
        else:
            filename = filename
            with open(filename, "a", encoding='utf-8-sig', newline='') as csvfile:
                headers = [
                    'title',
                    'cigar_name',
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
                            ['品牌', '雪茄', '税前价格', '库存', '折扣', '原价', '链接', '更新时间'])
                        csvwriter.writerow(cigarinfo)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1
                    else:
                        csvwriter.writerow(cigarinfo)
                        csvfile.close()
                        with writenums.get_lock():
                            writenums.value += 1