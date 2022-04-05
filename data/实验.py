f = open('all_laser_company_triples_new.txt', 'r')
company_arrt_content = []
for i in f:
    i = i.replace('\n', '').split()
    if len(i) == 3:
        company_arrt_content.append([i[0], i[1], i[2]])

attr_list = ['董事长', '总经理', '董事', '监事', '股东', '自然人股东', '执行董事']

f2 = open('company_gaoguan.txt', 'w')
for i in company_arrt_content:
    if i[1] in attr_list and len(i[2]) <= 4:
        print(i)
        i.insert(1, i.pop())
        f2.write(' '.join(i) + '\n')
    if i[2] in attr_list and len(i[1]) <= 4:
        f2.write(' '.join(i) + '\n')


#
# # print(company_arrt_content[:10])


def achieve_gaoguan_content(company_arrt_content, gaoguan):
    l = []
    attr_list = ['董事长', '总经理', '董事', '监事', '股东', '自然人股东', '执行董事']
    for i in company_arrt_content:
        if gaoguan in i and i[1] in attr_list:
            i.insert(1, i.pop())
            l.append(i)
        if gaoguan in i and i[2] in attr_list:
            l.append(i)
    return l


def ahieve_comany():
    f = open('/Users/xukai/Downloads/learn/智慧园区/后台模型/1命名实体识别/Pbilstm_crf/named_entity_recognition-master/entities.txt',
             'r')
    company_list = []
    for i in f:
        company_list.append(i.replace('\n', ''))
    return company_list


def achieve_konggu_content(company_arrt_content, company, company_list):
    l = []
    for i in company_arrt_content:
        i.insert(0, i.pop())
        if i[0] == company and i[1] in company_list and i[2] != 'None':
            l.append(i)
        elif i[1] == company and i[0] in company_list and i[2] != 'None':
            l.append(i)
        else:
            continue
    return l


def achieve_company_addr(addr):
    f = open('/Users/xukai/Downloads/learn/智慧园区/System/data/company_addr.txt', 'r')
    company_arrt_content = []
    for i in f:
        i = i.replace('\n', '').split()
        if len(i) == 3 and i[2].find(addr) != -1:
            company_arrt_content.append([i[0], addr, i[1]])
    f.close()
    return company_arrt_content


def achieve_company_person(company, company_arrt_content):
    l = []
    person_set = set()
    attr_list = ['董事长', '总经理', '董事', '监事', '股东', '自然人股东', '执行董事']
    for i in company_arrt_content:
        if i[0] == company and i[1] in attr_list:
            l.append(i)
            person_set.add(i[2])
    return list(set(person_set))

# a= achieve_company_person('东莞市雷宇激光设备有限公司', company_arrt_content)
# print(a)


# a = ahieve_comany()
# print(achieve_konggu_content(company_arrt_content, '华工科技产业股份有限公司', a))
# print(achieve_gaoguan_content(company_arrt_content,'邓家科'))
