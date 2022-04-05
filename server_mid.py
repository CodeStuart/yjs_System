import json
import random
import networkx as nx
import os
import pickle

import tensorflow as tf
from deep_model.utils import create_model, get_logger
from deep_model.model import Model

from deep_model.loader import input_from_line
from deep_model.predict import extraction_result
from deep_model.train import FLAGS, load_config


cmp_radio = 0.98

class server_mid:
    def __init__(self):

        self.all_data = []
        self.all_entity = []

        self.entity_data = []
        self.casuality_data = []
        self.event_prediction_data = []
        self.process1_n = 0
        self.process1_total = 0.1


        with open("data/出具虚假证明.txt", "r", encoding="utf-8") as f:
            for item in f.readlines():
                self.entity_data.append(item)

        with open("data/casuality.txt", "r", encoding="utf-8") as f:
            for item in f.readlines():
                self.casuality_data.append(item)

        with open("data/event_prediction.txt","r", encoding="utf-8") as f:
            for line in f:
                self.event_prediction_data.append(eval(line.replace("\n","")))

        with open("data/all_data.json", "r", encoding="utf-8") as f:
            for item in f.readlines():
                temp_data = json.loads(item.strip())
                self.all_data.append(temp_data)

                for item_entity in temp_data['entities'].split("-.-"):
                    self.all_entity.append(item_entity)


        self.all_data.sort(key=lambda x: len(x), reverse=False)

        self.all_triples = []

        # with open("/Users/xukai/Downloads/learn/智慧园区/knowledge_System/data/triples_simplify", "r", encoding="utf-8") as f:
        with open("data/all_laser_company_triples_new.txt", "r", encoding="utf-8") as f:
        # with open('/Users/xukai/Desktop/fj_test.txt') as f:
            for item in f.readlines():
                temp_data2 = item.strip().split("\t")
                if len(temp_data2) == 3:
                    self.all_triples.append(temp_data2)

    def event_prediction(self,evnet):
        """
        [[('同比下降', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('亏损', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('亏损', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('原材料价格上涨', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('整改', 'None', '发生', '经营异常', '西泵股份', '客体公司'),
  ('同比下降', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('低于', 'None', '发生', '经营异常', '西泵股份', '客体公司'),
  ('低于', 'None', '发生', '经营异常', '西泵股份', '客体公司')],
 [('下架', 'None', '发生', '经营异常', '人人乐', '客体公司'),
  ('没收', 'None', '发生', '违法违规', '西泵股份', '客体公司'),
  ('下架', 'None', '发生', '违法违规', '网宿科技', '客体公司'),
  ('同比下降', 'None', '发生', '业务异常', '西泵股份', '客体公司'),
  ('利润下降', 'None', '发生', '经营异常', '西泵股份', '客体公司')],
 3]
        :param evnet:
        :return:
        """
        for line in self.event_prediction_data:
            if str(evnet.strip()) == str(line[0][0][4].strip()):
                return line

    def select_process(self):
        return self.process1_n,self.process1_total

    def company_extract(self, text_list):
        config = load_config(FLAGS.config_file)
        logger = get_logger(FLAGS.log_file)
            # limit GPU memory
        tf_config = tf.ConfigProto()
        tf_config.gpu_options.allow_growth = True
        with open(FLAGS.map_file, "rb") as f:
            tag_to_id, id_to_tag = pickle.load(f)

        com_list = []
        tri_list = []
        print("0")
        with tf.Session(config=tf_config) as sess:
            model = create_model(sess, Model, FLAGS.ckpt_path, config, logger)
            for i in range(len(text_list)):
                print(i)
                self.process1_n = i + 1
                s = text_list[i]
                result = model.evaluate_line(sess, input_from_line(s, FLAGS.max_seq_len, tag_to_id), id_to_tag)
                res = result['entities']
                com = []
                tri = []
                #print(result)
                for di in res:
                    if di['type'] == 'C':
                        if di['word'] not in com:
                            com.append(di['word'])
                    if di['type'] == 'T':
                        if di['word'] not in tri:
                            tri.append(di['word'])
                s = ' '.join(com)
                com_list.append(s)
                s = ' '.join(tri)
                tri_list.append(s)
        result = []
        for i in range(len(text_list)):
                c_list = com_list[i].split()
                t_list = tri_list[i].split()
                count = len(c_list)
                dex = 0
                for t in range(count):
                    if ',' in c_list[t] or '，' in c_list[t]:
                        continue
                    if len(str(c_list[t])) > 1:
                        if len(t_list) > 0:
                            s = c_list[t]+"-"+t_list[0]+"_"+text_list[i] + "\n"
                        else:
                            s = c_list[t]+"_"+text_list[i] + "\n"
                        dex += 1
                        result.append(s+"\n")
                        break
                        #print(s)
                if dex == 0:
                    N = "None_"+text_list[i]
                    result.append(N)

        tf.reset_default_graph()
        return result



    def entity_file_extraction(self, sentence):
        self.process1_total= len(sentence)
        res = self.company_extract(sentence)
        print("end")
        return res



    def entity_extraction(self, sentence):
        self.process1_total = 1
        res = self.company_extract([sentence])
        return res

    def casuality_extraction(self, sentence):
        cau_res = []
        eff_res = []
        # res = [("实体1", "实体2"),
        #              ("实体2", "实体3"),
        #              ("实体4", "实体5")]
        for item in self.casuality_data:
            tmp = item.split("###")
            if str(sentence.strip()) == str(tmp[0]).replace("\n",""):
                    cau_res.append((tmp[0].replace("\n",""),tmp[1].replace("\n","")))
            if str(sentence.strip()) == str(tmp[1]).replace("\n",""):
                    eff_res.append((tmp[1].replace("\n",""),tmp[0].replace("\n","")))

        cau_fre = self.static_casuality(cau_res,0)
        cau_fre = sorted(cau_fre.items(), key=lambda x: x[1], reverse=True)

        eff_fre = self.static_casuality(eff_res,0)
        eff_fre = sorted(eff_fre.items(), key=lambda x: x[1], reverse=True)

        return [cau_res,eff_res,cau_fre,eff_fre]


    def static_casuality(self,res,flag):
        l = len(res)
        fre_dict = {}
        for line in res:
            if flag == 0:
                fre_dict[line[1]] = fre_dict.get(line[1], 1) + 1
            else:
                fre_dict[line[0]] = fre_dict.get(line[0], 1) + 1
            # if line[1] not in fre_dict:
            #     fre_dict[line[1]] = 0
            # else:
            #     fre_dict[line[1]] += 1
        for key,item in fre_dict.items():
            fre_dict[key] = str(item/l)[0:4]
        return fre_dict

    def relation_extraction(self, sentence):
        res = []

        for item in self.all_data:
            if sentence.strip() == item["news_sentence"].strip():
                for item_entity in item["ent_pairs"].split("-..-"):
                    if item_entity not in res:
                        res.append(item_entity.split("-.-"))
                break

        return res

    def get_summary(self,entity_attr: list) -> list:
        entity_pairs = {}
        for item_entity in entity_attr:
            if item_entity[0] not in entity_pairs.keys():
                entity_pairs[item_entity[0]] = []
                entity_pairs[item_entity[0]].append(item_entity)
            else:
                entity_pairs[item_entity[0]].append(item_entity)

        entities = set()
        entities_weight = []
        G = nx.Graph()
        for pairs in entity_attr:
            entity1 = pairs[0]
            entity2 = pairs[1]
            G.add_node(entity1)
            G.add_node(entity2)
            G.add_edge(entity1, entity2)

            entities.add(entity1)
            entities.add(entity2)

        dc = nx.degree_centrality(G)
        cc = nx.closeness_centrality(G)
        bc = nx.betweenness_centrality(G)

        for item_entity in entities:
            temp_weight = dc[item_entity] + cc[item_entity] + bc[item_entity]
            entities_weight.append([item_entity, round(temp_weight, 2)])
        score = sorted(entities_weight, key=lambda x: x[1], reverse=True)
        score_dict = dict((i, j) for i, j in score)

        res_val = []

        for item in entity_pairs:
            if len(entity_pairs[item]) <= 10:
                for item2 in entity_pairs[item]:
                    res_val.append(item2)
            else:
                temp_list = []
                add_set = set()
                for item2 in entity_pairs[item]:
                    if item2[1] == '-':
                        if item2[1] not in add_set:
                            temp_list.append([item2, score_dict[item2[1]] - 100])
                            add_set.add(item2[1])

                    elif "股东" in item2[2] or \
                            "authority" == item2[2] or \
                            "法人" in item2[2] or \
                            "amountPercent" in item2[2] or \
                            "董事" in item2[2] or\
                            "regAddr" in item2[2]:
                        if item2[1] not in add_set:
                            temp_list.append([item2, score_dict[item2[1]] + 100])
                            add_set.add(item2[1])
                    else:
                        temp_list.append([item2, score_dict[item2[1]]])
                        add_set.add(item2[1])

                temp_list_sort = sorted(temp_list, key=lambda x: x[1], reverse=True)
                temp_list_sort = temp_list_sort[:10]
                for item3 in temp_list_sort:
                    res_val.append(item3[0])
        print("11")
        return res_val


    def summary_extraction(self, kw):
        entity_attr = []
        entity_summary = []
        entity_chain = []
        entity_text = []

        for item in self.all_triples:
            if kw in item[0] or kw in item[2]:
                temp_data = (item[0], item[2], item[1])
                if temp_data not in entity_attr:
                    entity_attr.append(temp_data)
        # entity_summary = random.sample(entity_attr, 10)
        entity_summary = self.get_summary(entity_attr)

        for item in self.all_data:
            for item_entities in item["ent_pairs"].split("-..-"):
                if kw in item_entities:
                    temp_data2 = item_entities.split("-.-")
                    temp_data2.append(" ")
                    if temp_data2 not in entity_chain:
                        entity_chain.append(temp_data2)
                        new_text = "*.   " + item["news_sentence"] + "<br>"
                        if new_text not in entity_text:
                            entity_text.append(new_text)
        # entity_chain = [
        #     # ['IPG公司', '大族激光', ' '],
        #     ['大族激光', '海德梅柯汽车装备制造有限公司', ' '],
        #     # ['大族激光', '华昌达', ' '],
        #     # ['大族激光', '德梅柯', ' '],
        #     ['大族激光', '华昌达智能装备集团股份有限公司', ' '],
        #     ['大族激光', 'oppo', ' '],
        #     ['大族激光', '华为', ' '],
        #     ['大族激光', '光越科技', ' '],
        #     ['大族激光', 'IPG', ' '],
        #     ['大族激光', '光库通讯', ' '],
        #     ['中国汽车工业协会专用车分会', '大族激光智能装备集团', ' '],
        #     ['威腾斯坦', '大族激光智能装备集团', ' '],
        #     ['华制智能', '大族激光智能装备集团', ' '],
        #     ['中国联通深圳市分公司', '大族激光智能装备集团', ' '],
        #     ['大族激光', '大族激光智能装备集团', ' '],
            # ['第一创业投资管理有限公司', '深圳市大族激光科技股份有限公司', ' '],
            # ['武汉金石凯激光技术有限公司', '深圳市大族激光科技股份有限公司', ' '],
            # # ['武汉金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
            # # ['金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
            # ['深圳市大族激光科技股份有限公司', '深圳大族', ' '],
            # ['深圳市大族激光科技股份有限公司', '东莞市粤铭激光技术有限公司', ' '],
            # # ['深圳市大族激光科技股份有限公司', '东莞粤铭', ' '],
            # ['深圳市大族激光科技股份有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
            # ['深圳市大族激光科技股份有限公司', '大族粤铭', ' '],
            # ['大族激光', '第一创业投资管理有限公司', ' '],
            # ['深圳大族', '东莞市粤铭激光技术有限公司', ' '],
            # ['深圳大族', '东莞粤铭', ' '],
            # ['深圳大族', '东莞市大族粤铭激光科技有限公司', ' '],
            # ['深圳大族', '大族粤铭', ' '],
            # ['东莞市粤铭激光技术有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
            # ['东莞市粤铭激光技术有限公司', '大族粤铭', ' '],
            # ['东莞粤铭', '东莞市大族粤铭激光科技有限公司', ' '],
            # ['东莞粤铭', '大族粤铭', ' '],
            # ['东莞市大族粤铭激光科技有限公司', '大族粤铭', ' '],
        # ]

        # entity_chain = [  # ['IPG公司', '大族激光', ' '],
        #     ['大族激光', '海德梅柯汽车装备制造有限公司', ' '],
        #     # ['大族激光', '华昌达', ' '],
        #     # ['大族激光', '德梅柯', ' '],
        #     ['大族激光', '华昌达智能装备集团股份有限公司', ' '],
        #     ['大族激光', 'oppo', ' '],
        #     ['大族激光', '华为', ' '],
        #     ['大族激光', '光越科技', ' '],
        #     ['大族激光', 'IPG', ' '],
        #     # ['大族激光', '光库通讯', ' '],
        #     # ['中国汽车工业协会专用车分会', '大族激光智能装备集团', ' '],
        #     # ['威腾斯坦', '大族激光智能装备集团', ' '],
        #     # ['华制智能', '大族激光智能装备集团', ' '],
        #     # ['中国联通深圳市分公司', '大族激光智能装备集团', ' '],
        #     # ['大族激光', '大族激光智能装备集团', ' '],
        #     ['第一创业投资管理有限公司', '深圳市大族激光科技股份有限公司', ' '],
        #     ['武汉金石凯激光技术有限公司', '深圳市大族激光科技股份有限公司', ' '],
        #     # ['武汉金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
        #     # ['金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
        #     ['深圳市大族激光科技股份有限公司', '深圳大族', ' '],
        #     ['深圳市大族激光科技股份有限公司', '东莞市粤铭激光技术有限公司', ' '],
        #     # ['深圳市大族激光科技股份有限公司', '东莞粤铭', ' '],
        #     ['深圳市大族激光科技股份有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
        #     ['深圳市大族激光科技股份有限公司', '大族粤铭', ' '],
        #     ['大族激光', '第一创业投资管理有限公司', ' '],
        #     # ['深圳大族', '东莞市粤铭激光技术有限公司', ' '],
        #     # ['深圳大族', '东莞粤铭', ' '],
        #     # ['深圳大族', '东莞市大族粤铭激光科技有限公司', ' '],
        #     ['深圳大族', '大族粤铭', ' '],
        #     ['东莞市粤铭激光技术有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
        #     ['东莞市粤铭激光技术有限公司', '大族粤铭', ' '],
        #     ['东莞粤铭', '东莞市大族粤铭激光科技有限公司', ' '],
        #     ['东莞粤铭', '大族粤铭', ' '],
        #     ['东莞市大族粤铭激光科技有限公司', '大族粤铭', ' '], ]

    #     entity_chain = entity_chain = [
    #     # ['IPG公司', '大族激光', ' '],
    #     ['大族激光', '海德梅柯汽车装备制造有限公司', ' '],
    #     # ['大族激光', '华昌达', ' '],
    #     # ['大族激光', '德梅柯', ' '],
    #     ['大族激光', '华昌达智能装备集团股份有限公司', ' '],
    #     ['大族激光', 'oppo', ' '],
    #     ['大族激光', '华为', ' '],
    #     ['大族激光', '光越科技', ' '],
    #     ['大族激光', 'IPG', ' '],
    #     ['大族激光', '光库通讯', ' '],
    #     ['中国汽车工业协会专用车分会', '大族激光智能装备集团', ' '],
    #     ['威腾斯坦', '大族激光智能装备集团', ' '],
    #     ['华制智能', '大族激光智能装备集团', ' '],
    #     ['中国联通深圳市分公司', '大族激光智能装备集团', ' '],
    #     ['大族激光', '大族激光智能装备集团', ' '],
    #     ['第一创业投资管理有限公司', '深圳市大族激光科技股份有限公司', ' '],
    #     ['武汉金石凯激光技术有限公司', '深圳市大族激光科技股份有限公司', ' '],
    #     # ['武汉金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
    #     # ['金石凯激光', '深圳市大族激光科技股份有限公司', ' '],
    #     ['深圳市大族激光科技股份有限公司', '深圳大族', ' '],
    #     ['深圳市大族激光科技股份有限公司', '东莞市粤铭激光技术有限公司', ' '],
    #     # ['深圳市大族激光科技股份有限公司', '东莞粤铭', ' '],
    #     ['深圳市大族激光科技股份有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
    #     ['深圳市大族激光科技股份有限公司', '大族粤铭', ' '],
    #     ['大族激光', '第一创业投资管理有限公司', ' '],
    #     ['深圳大族', '东莞市粤铭激光技术有限公司', ' '],
    #     ['深圳大族', '东莞粤铭', ' '],
    #     ['深圳大族', '东莞市大族粤铭激光科技有限公司', ' '],
    #     ['深圳大族', '大族粤铭', ' '],
    #     ['东莞市粤铭激光技术有限公司', '东莞市大族粤铭激光科技有限公司', ' '],
    #     ['东莞市粤铭激光技术有限公司', '大族粤铭', ' '],
    #     ['东莞粤铭', '东莞市大族粤铭激光科技有限公司', ' '],
    #     ['东莞粤铭', '大族粤铭', ' '],
    #     ['东莞市大族粤铭激光科技有限公司', '大族粤铭', ' '],
    # ]

        return entity_attr, entity_summary, entity_chain, entity_text

    def get_import_nodes(self, entity_chain: list) -> list:
        # print(entity_chain)
        entities = set()
        entities_weight = []
        G = nx.Graph()
        for pairs in entity_chain:
            entity1 = pairs[0]
            entity2 = pairs[1]
            G.add_node(entity1)
            G.add_node(entity2)
            G.add_edge(entity1, entity2)

            entities.add(entity1)
            entities.add(entity2)

        dc = nx.degree_centrality(G)
        cc = nx.closeness_centrality(G)
        bc = nx.betweenness_centrality(G)

        for item_entity in entities:
            temp_weight = dc[item_entity] + cc[item_entity] + bc[item_entity]
            # temp_weight = bc[item_entity]
            entities_weight.append([item_entity, round(temp_weight, 2)])
        score = sorted(entities_weight, key=lambda item: item[1], reverse=True)

        res = score[:10]
        res_text = [": ".join([str(i) + ". " + item[0], str(item[1])]) for i, item in enumerate(res)]

        G.clear()

        return res_text


if __name__ == '__main__':
    sentence = "2019年5月，采埃孚、Ibeo与艾迈斯达成合作，共同研发车用固态激光雷达技术，以确保该项技术能在2021年前迅速、安全地投入使用"
    kw = "奔腾激光"
    sm = server_mid()
    # print(sm.entity_extraction(sentence))
    # print(sm.relation_extraction(sentence))
    a = sm.summary_extraction(kw)
    # print(len(a)) # entity_attr, entity_summary, entity_chain, entity_text
    print(a[0])
    print(a[1])
    print(a[2])
    print(a[3])
