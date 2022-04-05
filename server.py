from flask import Flask, render_template, request, jsonify

from server_mid import server_mid

mid = server_mid()

app = Flask(__name__)

testInfo = {}


def achieve_company_person(company, company_arrt_content):  # 获取公司高管列表
    l = []
    person_set = set()
    attr_list = ['董事长', '总经理', '董事', '监事', '股东', '自然人股东', '执行董事']
    for i in company_arrt_content:
        if i[0] == company and i[1] in attr_list:
            l.append(i)
            person_set.add(i[2])
    return list(set(person_set))


def ahieve_comany():  # 获取已有公司名列表
    f = open('/named_entity_recognition-master/entities.txt',
             'r')
    company_list = []
    for i in f:
        company_list.append(i.replace('\n', ''))
    return company_list


def achieve_company_addr(addr):  # 获取公司所在城市
    f = open('data/company_addr.txt', 'r')
    company_arrt_content = []
    for i in f:
        i = i.replace('\n', '').split()
        if len(i) == 3 and i[2].find(addr) != -1 and i[2].find(addr + '路') == -1:
            company_arrt_content.append([i[0], addr, i[1]])
    f.close()
    return company_arrt_content


def achieve_tripple_list():  # 获取三元组（公司，属性，属性值）
    f = open('data/all_laser_company_triples_new.txt', 'r')
    company_arrt_content = []
    for i in f:
        i = i.replace('\n', '').split()
        if len(i) == 3:
            company_arrt_content.append([i[0], i[1], i[2]])
    return company_arrt_content


def achieve_work_info():
    f = open('data/company_gaoguan.txt', 'r')
    company_arrt_content = []
    for i in f:
        i = i.replace('\n', '').split()
        if len(i) == 3:
            company_arrt_content.append([i[0], i[1], i[2]])
    f.close()
    return company_arrt_content


def achieve_gaoguan_work(company_arrt_content, gaoguan):  # 获取高管的职位
    l = []
    for i in company_arrt_content:
        if gaoguan == i[1]:
            l.append(i)
    return l


# a = achieve_tripple_list()
# print(achieve_gaoguan_content(a,'邓家科'))

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


def res_kw_json(l):
    res = []
    for item in l:
        res.append({"name": item, "group": 1})
    return res


@app.route('/select_process', methods=['GET', 'POST'])  # 路由
def select_process():
    if request.method == 'POST':
        n, total = mid.select_process()
        response = {"n": n, "total": total}
        return jsonify(response)
    else:
        return "None"

@app.route('/entityfilesend', methods=['GET', 'POST'])  # 路由
def entity_file_sentence():
    if request.method == 'POST':
        f = request.files['file_upload']
        f.save("upload_data/"+f.filename)
        sentence = []
        with open("upload_data/"+f.filename,"r",encoding='utf-8') as f:
            for line in f:
                sentence.append(line.replace("\n",""))
        temp_result = mid.entity_file_extraction((sentence))
        res_data = {"text": sentence, "entity_list": temp_result}
        return jsonify(res_data)
    else:
        return request.args.get("sentence")

@app.route('/entityfiletest', methods=['GET', 'POST'])  # 路由
def entity_file_test():
    if request.method == 'POST':
        sentence = []
        with open("upload_data/test_1.txt","r",encoding='utf-8') as f:
            for line in f:
                sentence.append(line.replace("\n",""))
        temp_result = mid.entity_file_extraction((sentence))
        res_data = {"text": sentence, "entity_list": temp_result}
        return jsonify(res_data)
    else:
        sentence = []
        with open("upload_data/test_1.txt","r",encoding='utf-8') as f:
            for line in f:
                sentence.append(line.replace(",",""))
        res_data = {"text": sentence}
        return jsonify(res_data)

@app.route('/entitysend', methods=['GET', 'POST'])  # 路由
def entity_sentence():
    if request.method == 'POST':
        sentence = request.form.get("sentence")
        temp_result = mid.entity_extraction(sentence)
        res_data = {"text": sentence, "entity_list": temp_result}
        return jsonify(res_data)
    else:
        return request.args.get("sentence")

@app.route('/event_prediction', methods=['GET', 'POST'])  # 路由
def event_prediction():
    if request.method == 'POST':
        event = request.form.get("event")
        temp_result = mid.event_prediction(event)
        res_data = {"event_result": temp_result}
        return jsonify(res_data)
    else:
        return request.args.get("event")

def res_rel_json(r):
    # r = [("实体1", "实体2"),
    #              ("实体2", "实体3"),
    #              ("实体4", "实体5")]

    entities = []
    relation_set = set()
    text_pairs = []
    link_label = dict()
    for item in r:
        relation_set.add(item[0] + "-.-" + item[1])

        entities.append(item[0])
        entities.append(item[1])

        text_pairs.append("<" + item[0] + "," + item[1].replace("\n","") + ">")
        if len(item) > 2:
            link_label[item[0] + "-.-" + item[1]] = item[2]
        else:
            link_label[item[0] + "-.-" + item[1]] = " "

    entities = list(set(entities))
    en_dict = dict((j, i) for i, j in enumerate(entities))

    nodes = res_kw_json(entities)
    edges = []

    for item in r:
        temp_res = {'source': en_dict[item[0]], 'target': en_dict[item[1]],
                    'correlation': link_label[item[0] + "-.-" + item[1]]}
        edges.append(temp_res)

    return nodes, edges, "\t".join(text_pairs)


@app.route('/relationsend', methods=['GET', 'POST'])  # 路由
def relation_sentence():
    if request.method == 'POST':

        sentence = request.form.get("sentence")

        relations = mid.relation_extraction(sentence)

        # relations = [("实体1", "实体2"),
        #              ("实体2", "实体3"),
        #              ("实体4", "实体5")]

        # res_data = {"text":"\t".join(text_area),"kw_json":res_kw_json(text_area)}

        nodes, edges, text_pair = res_rel_json(relations)

        return jsonify({'text': text_pair, 'node': nodes, 'edge': edges})

        # return request.form.get("sentence")
    else:
        return request.args.get("sentence")
    # return json.dumps(testInfo)

@app.route('/casualitysend', methods=['GET', 'POST'])  # 路由
def casuality_sentence():
    if request.method == 'POST':
        sentence = request.form.get("sentence")
        relations = mid.casuality_extraction(sentence)
        #
        # relations = [("实体1", "实体2"),
        #              ("实体2", "实体3"),
        #              ("实体4", "实体5")]

        # res_data = {"text":"\t".join(text_area),"kw_json":res_kw_json(text_area)}

        cau_nodes, cau_edges, cau_text_pair = res_rel_json(relations[0])
        eff_nodes, eff_edges, eff_text_pair = res_rel_json(relations[1])


        return jsonify({'text': cau_text_pair, 'cau_nodes': cau_nodes,
                        'cau_edges': cau_edges,'eff_nodes':eff_nodes,'eff_edges':eff_edges,
                        'cau_fre': relations[2],'eff_fre':relations[3]
                        })

        # return request.form.get("sentence")
    else:
        return request.args.get("sentence")

@app.route('/gaoguansend', methods=['GET', 'POST'])  # 路由
def gaoguan_sentence():
    if request.method == 'POST':
        tripple_list = achieve_tripple_list()
        work_list = achieve_work_info()
        sentence = request.form.get("sentence")
        # print(sentence)
        fangshi = request.form.get('xingshi')
        # print(fangshi)
        if fangshi == 'gaoguanname':
            relations = achieve_gaoguan_work(work_list, sentence)
            # relations = [("马云", "阿里巴巴", "董事长"),
            #              ("马云", "蚂蚁金服", "总经理"), ]
        elif fangshi == 'companyname':
            name_list = achieve_company_person(sentence, tripple_list)
            # print('name_list',name_list)
            relations = []
            for name in name_list:
                realtions_pre = achieve_gaoguan_work(work_list, name)
                relations.extend(realtions_pre)
        else:
            relations = []
        # print(relations)

        nodes, edges, text_pair = res_rel_json(relations)

        return jsonify({'text': text_pair, 'node': nodes, 'edge': edges})
    else:
        return request.args.get("sentence")


@app.route('/konggusend', methods=['GET', 'POST'])  # 路由
def konggu_sentence():
    if request.method == 'POST':
        company_list = ahieve_comany()
        sentence = request.form.get("sentence")
        tripple_list = achieve_tripple_list()
        relations = achieve_konggu_content(tripple_list, sentence, company_list)
        # f = open('/Users/xukai/Desktop/实体关系.txt', 'r')
        # relations = []
        # for i in f:
        #     i = i.replace('\n', '').split()
        #     if len(i) == 3:
        #         relations.append([i[0], i[2], i[1]])

        # relations = [("阿里巴巴", "饿了么", "amount percent"),
        #              ("阿里巴巴", "蚂蚁金服", "amount percent"), ]

        nodes, edges, text_pair = res_rel_json(relations)

        return jsonify({'text': text_pair, 'node': nodes, 'edge': edges})
    else:
        return request.args.get("sentence")


@app.route('/locationsend', methods=['GET', 'POST'])  # 路由
def location_sentence():
    if request.method == 'POST':
        addr = request.form.get("sentence")
        # 新加的部分
        # entity_attrs, entity_summaries, entity_chain, entity_text = mid.summary_extraction(kw)
        # 新加的部分结束

        relations = achieve_company_addr(addr)

        if len(relations) > 100:
            relations1 = relations[:400]
        else:
            relations1 = relations
        # relations = [("阿里巴巴", "杭州", "location"),
        #              ("蚂蚁金服", "杭州", "location"), ]

        nodes, edges, text_pair = res_rel_json(relations1)

        return jsonify({'text': text_pair, 'node': nodes, 'edge': edges})
    else:
        return request.args.get("sentence")


@app.route('/informationsend', methods=['POST'])  # 路由
def information_sentence():
    if request.method == 'POST':
        companyname = request.form.get("companyname")
        money = request.form.get("money")
        farenname = request.form.get("farenname")
        gudongname = request.form.get("gudongname")
        address1 = request.form.get("address1")
        entType = request.form.get("entType")
        openStatus = request.form.get("openStatus")
        scope = request.form.get("scope")
        print('post')
        print(companyname, money, farenname, gudongname, address1, entType, openStatus, scope)
        a = {'success': 'success'}
        return jsonify(a)


@app.route('/summarysend', methods=['GET', 'POST'])
def summary_sentence():
    if request.method == 'POST':

        kw = request.form.get("sentence")

        entity_attrs, entity_summaries, entity_chain, entity_text = mid.summary_extraction(kw)

        # relations1 = [("实体1", "实体2"),
        #               ("实体1", "实体3"),
        #               ("实体1", "实体4"),
        #               ("实体1", "实体5"),
        #               ("实体1", "实体6"),
        #               ("实体1", "实体7"),
        #               ("实体1", "实体8"),
        #               ("实体1", "实体9"),
        #               ("实体1", "实体10"),
        #               ]
        #
        # relations2 = [
        #     ("实体1", "实体3"),
        #     ("实体1", "实体6"),
        #     ("实体1", "实体8"),
        #     ("实体1", "实体10"),
        # ]
        #
        # relation_chain = [("实体1", "实体2"),
        #                   ("实体2", "实体3"),
        #                   ("实体4", "实体5")]

        # res_data = {"text":"\t".join(text_area),"kw_json":res_kw_json(text_area)}

        # entity_texts = "1111111"

        rnodes, redges, rtext_pair = res_rel_json(entity_attrs)
        snodes, sedges, stext_pair = res_rel_json(entity_summaries)
        cnodes, cedges, ctext_pair = res_rel_json(entity_chain)
        import_nodes = mid.get_import_nodes(entity_chain)

        res = {'rnode': rnodes, 'redge': redges,
               'snode': snodes, 'sedge': sedges,
               'cnode': cnodes, 'cedge': cedges,
               'otext': "<br>".join(entity_text),
               'inodechain': "<br><br>".join(import_nodes)}
        # print(res)
        return jsonify(res)

        # return request.form.get("sentence")
    else:
        return request.args.get("sentence")
    # return json.dumps(testInfo)


@app.route('/')
def hello_world():
    # return 'Hello World!'
    return render_template('index2.html')


@app.route('/index')
def index():
    return render_template('index2.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
