import networkx as nx


if __name__ == '__main__':

    entity_chain  = [
        # ['IPG公司', '大族激光', ' '],
        ['大族激光', '海德梅柯汽车装备制造有限公司', ' '],
        # ['大族激光', '华昌达', ' '],
        # ['大族激光', '德梅柯', ' '],
        ['大族激光', '华昌达智能装备集团股份有限公司', ' '],
        ['大族激光', 'oppo', ' '],
        ['大族激光', '华为', ' '],
        ['大族激光', '光越科技', ' '],
        ['大族激光', 'IPG', ' '],
        ['大族激光', '光库通讯', ' '],
        ['中国汽车工业协会专用车分会', '大族激光智能装备集团', ' '],
        ['威腾斯坦', '大族激光智能装备集团', ' '],
        ['华制智能', '大族激光智能装备集团', ' '],
        ['中国联通深圳市分公司', '大族激光智能装备集团', ' '],
        ['大族激光', '大族激光智能装备集团', ' '],
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
    ]

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
        # temp_weight = dc[item_entity] + cc[item_entity] + bc[item_entity]
        temp_weight =cc[item_entity]
        entities_weight.append([item_entity, round(temp_weight, 2)])
    score = sorted(entities_weight, key=lambda item: item[1], reverse=True)

    res = score[:10]
    print(res)