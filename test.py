x = {"cigar_name": 2, 3: 4, 4: 3, 2: 1, 0: 0}
tmp_data = x
tmp_cigar = tmp_data["cigar_name"]
tmp_data.pop(list(filter(lambda k: x[k] == tmp_cigar, tmp_data))[0])
print(tmp_data)