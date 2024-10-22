from ASOS_DAY import ASOS

std = [90, 93, 95, 100, 101, 104, 105, 106, 114, 121, 211, 212, 214, 216, 217]

# encoding key
with open('./Keys/key.txt', 'r') as f:
    keys = f.read().rstrip().split('/n')

asos = ASOS(std,'1990','2020')
for key in keys:
    asos.add_keys(key) # 키 추가하고싶은 만큼 반복
asos.Crwal()
