f = open('/Users/xukai/Downloads/learn/智慧园区/System/data/all_laser_company_triples_new.txt','r')

relations = []
for i in f:
    i = i.replace('\n', '').split()
    if len(i) == 3 and i[1] == 'scope':
        relations.append([i[0], i[2]])

for j in relations:
