import udtree

filename = 'C:\\Users\\hye jin\\Desktop\\BGAB0166.utf8.txt'

f2 = open(filename, 'r', encoding='utf-8')
flist = f2.readlines()

sent = ""
sent_prev = ""
pstree = ""
body_checked = 0

for i in flist:
    if i.find("<body>") != -1:
        body_checked = 1
        continue
    if i.find("</body>") != -1:
        break
    if body_checked == 0:
        continue
    if i[0] != ";":
        pstree = pstree + i
    else:
        if sent_prev == "":
            sent_prev = i
        else:
            sent = sent_prev
            sent_prev = i
            print("#", sent, end='')
            # print("##### " , pstree)
            test.makeUDTree(sent, pstree)
            sent = ""
            pstree = ""

sent = sent_prev
print("#", sent, end='')
# print("##### " , pstree)
udtree.makeUDTree(sent, pstree)
print("문장 개수 : ", udtree.sent_count)
print("어절 개수 : ", udtree.token_count)
print("규칙 호출 개수 : ", udtree.rule_call_count)
print("태그 호출 개수 : ", udtree.relation_count)
print("태그된 개수 :", udtree.try_count_list)
print("태그된 개수 세종구문태그로:", udtree.try_count_list2)
print("head에 할당한 태그를 붙인 갯수 : ", udtree.try_count_list3)
f2.close()
udtree.write_file.close()
