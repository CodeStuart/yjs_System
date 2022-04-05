def main():
    word_set = set()
    triples = []
    with open("./data/all_laser_company_triples_new.txt", "r", encoding="utf-8") as f, \
            open("./data/huagong.txt", "w", encoding="utf-8") as f2:
        index = 0

        for item in f.readlines():
            if "华工" in item and "股东" in item and "公司" in item:
                f2.write(item)

            if "华工" in item and "amountPercent" in item and "公司" in item:
                f2.write(item)
        # if "大族" in item.split("\t")[0]:
        #     word_set.add(item.strip("\n"))
        #     index += 1

        print(len(word_set))


if __name__ == '__main__':
    main()
