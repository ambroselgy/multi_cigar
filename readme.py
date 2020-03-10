#_*_ coding : UTF-8 _*_
#开发人员：Diya
#开发时间：2020/3/10 22:18
#文件名称: readme.PY
#开发工具：PyCharm

#根据页面数量决定进程组数量，根据页面数量计算每个进程组的page起始及结束页
# nums = 14  # 网站总页数，根据页数分配进程数量
# step = nums // 7
# multi_list = []
# for i in range(1, nums, step):
#     multi_list.append(Process(target=fs.run, args=("p" + str(i) + ".csv", i, i + step)))

nums = 90
step = nums//7
startlist = []
for i in range(1, nums, step):
    startlist.append(i)
print(startlist)
for i in range(0, len(startlist)):
    print(startlist[i:i+1])