import re

file_path = 'C:\\Users\\hye jin\\Desktop'
write_file = open(file_path + '\\뉴테스트6.txt', 'a', encoding='utf-8')
relation_count = {'conj': 0, 'cc': 0, 'nmod / flat': 0, 'nsubj': 0, 'obj': 0, 'csubj': 0, 'ccomp': 0,
                  'obl': 0, 'vocative': 0, 'advcl': 0, 'advmod': 0, 'discourse': 0, 'aux': 0, 'nmod': 0, 'appos': 0,
                  'nummod': 0, 'acl': 0, 'amod': 0, 'det': 0, 'clf': 0, 'fixed': 0, 'flat': 0, 'compound': 0, 'list': 0,
                  'parataxis': 0, 'goeswith': 0, 'reparandum': 0, 'punct': 0, 'ROOT': 0, 'dep': 0}
relation_dic = {}
relation_dic_sejongtag = {}
relations = {}
token_count = 0
sent_count = 0
flag = 0
rule_call_count = [0, 0, 0, 0, 0, 0, 0]
try_count_list = [0, 0, 0, 0, 0, 0]
try_count_list2 = [0, 0, 0, 0, 0, 0]
try_count_list3 = [0,0,0,0,0,0]


class STree:
    def __init__(self):
        self.root = None
        self.children = []
        self.parent = None
        self.id = -1
        self.center = None  # 단말 노드를 포함한 모든 구(phrase)에서 최상위 지배소 노드(STree) 할당
        self.head = None  # terminal 노드인 경우만 할당
        self.sent = None  # root 노드인 경우 "문장"을 할당
        self.tag = None
        self.relation = None

    def setRoot(self, root):
        self.root = root

    def getRoot(self):
        return self.root

    def addChild(self, subTree):
        subTree.parent = self
        self.children.append(subTree)

    def getChildSize(self):
        return len(self.children)

    def hasParent(self):
        if self.parent == None:
            return False
        else:
            return True

    def getParent(self):
        return self.parent

    def hasGrandParent(self):
        if not self.hasParent():
            return False

        parent = self.getParent()
        return parent.hasParent()

    def getGrandParent(self):
        return self.getParent().getParent()

    def findNN(self):
        regex = re.compile('./NN.?')
        if node is not None:
            if re.match(regex, node.children):
                return node.children
            for n in node.children[-1]:
                self.findNN(n)

    def getLastChildOfParent(self):
        node = self.parent

        while node != None:
            if node.getChildSize() == 0:
                if (node.root == "./SF" or ",/SP"):
                    return node.parent.children[0]

                else:
                    return node

            else:
                node = node.children[-1]

    def getLastChildOfGrandParent(self):
        node = self.parent.parent

        while node != None:
            if node.getChildSize() == 0:
                if (node.root == "./SF" or ",/SP"):
                    return node.parent.children[0]
                else:
                    return node

            else:
                node = node.children[-1]

    def getLastChildOfGrandGrandParent(self):
        node = self.parent.parent.parent

        while node != None:
            if node.getChildSize() == 0:
                if (node.root == "./SF" or ",/SP"):
                    return node.parent.children[0]
                else:
                    return node

            else:
                node = node.children[-1]

    def getLastChildOfPhrase(self):
        node = self.parent.parent.parent

        while node != None:  # 계속올라간 부모의 제일 마지막 자식이 self가 아니면 멈춰라.
            if node.getLastChildOfParent() == self:
                node = node.parent
            else:
                node = node.getLastChildOfParent()
                return node

    def assignCenterNode(self):
        global rule_call_count
        if len(self.children) == 0:
            self.center = self
            return

        for c in self.children:
            c.assignCenterNode()

        if self.center is None:
            self.center = self.children[-1].center

        childSize = self.getChildSize()

        # 마지막 child의 center가 "./SF", ",/SP" 인 경우, 그 앞 child의 center를 자신의 center로 지정함
        if childSize > 1 and (self.children[-1].root.endswith('/SF') or self.children[-1].root.endswith('/SP')):
            self.center = self.children[childSize - 2].center
            rule_call_count[0] += 1
            self.relation = 'punct'

            # 명사  및 인 경우 및의 head가 명사 이다.
        elif (childSize > 1 and self.children[0].center.root.find('/NN') != -1 and self.children[-1].children[
            0].center.root.find('및/MA') != -1):
            self.children[-1].children[0].center = self.children[0].center
            rule_call_count[5] += 1

            # 명사 등 인 경우 등의 head가 명사 이다.
            # 19-10-07 startswith('등/NNB')을 endswith('등/NNB')으로 변경  뒤에 조사가 붙는 경우는 조사로 인한 어절의 품사변화발생( ex 등을)은 목적어임.
        elif childSize > 1 and self.children[0].center.root.find('/NN') != -1 and self.children[
            -1].center.root.endswith('등/NNB'):
            self.children[-1].center = self.children[0].center
            rule_call_count[5] += 1

        # 본용언, 보조용언인 경우 본용언을 자신의 center로 지정한다.
        # 본용언, 보조용언의 거리가 1인 경우만 적용한다.
        elif ((self.children[-1].center.root.find('/VX') != -1) and childSize > 1 and (
                self.children[-1].center.id - self.children[childSize - 2].center.id) == 1):
            center_string = self.children[childSize - 2].center.root
            p = re.compile('.+/VV | .+/VA | .+/NNG.+/XS[AV]')
            m = p.match(center_string)
            if m is not None:
                self.center = self.children[childSize - 2].center
                self.relation = 'aux'
                rule_call_count[2] += 1

                # 보조용언 일때 기호들도 본용언으로 root잡아주기
            if (self.children[-1].children[-1].root.endswith('/SF') or self.children[-1].children[-1].root.endswith(
                    '/SP')):
                self.children[-1].children[-1].center = self.children[0].center

            # 끝에서 2번째 child의 center가 용언이고, 마지막 child의 center가 "./NN" 인 경우, 끝에서 2번째 child의 center를 자신의 center로 지정함
        elif (childSize > 1 and self.root.find("(NP") == -1 and
              (self.children[childSize - 2].center.root.find('/VV') != -1 or
               self.children[childSize - 2].center.root.find('/XSV') != -1 or
               self.children[childSize - 2].center.root.find('/VA') != -1 or
               self.children[childSize - 2].center.root.find('/XSA') != -1) and
              (self.children[-1].center.root.find('/NN') != -1 and
               self.children[-1].center.root.find('/XS') == -1)and (
                self.children[-1].center.id - self.children[childSize - 2].center.id) == 1):

            self.center = self.children[childSize - 2].center
            rule_call_count[3] += 1

            # 의존명사 '수/NNB'가 들어간 경우 수<-할 로 만들어주는 부분. '있'과 '없'이 두번째 노드 center에 존재한다면 첫번째 노드 center에서 '수'를 찾고 존재한다면 '수
            # 있다'보다 앞쪽에 위치한 동사 즉, '-ㄹ'이 붙은 토큰을 center로 잡는다.

            # 19.10.17 수정
            # '-ㄹ'이 -ㄹ 수 있다. 에서 final head를 가지도록 변경, fixed태그도 같이 매핑
        elif (childSize > 1 and self.children[-1].center.root.startswith('수/NNB') and self.children[0].center.root.endswith('ᆯ/ETM') and (
                self.children[-1].center.id - self.children[childSize - 2].center.id) == 1):
            self.center = self.children[0].center
            self.relation = 'fixed'
            rule_call_count[4] += 1

        #    if self.hasParent():
        #       parent = self.getParent()
        #        parent.center = self.center
        #        parent.relation = 'fixed_p'

            # 19.10.17 수정
            # '-ㄹ'과 '있|없'에서 '-ㄹ'이 head가 되도록 변경, fixed태그도 같이 매핑
        elif (childSize > 1 and (self.children[-1].center.root.find("있/VV") != -1 or self.children[-1].center.root.find("없/VA") != -1) and
                self.children[0].center.root.endswith("ᆯ/ETM")):
            self.center = self.children[0].center
            self.relation = 'fixed'
            rule_call_count[4] += 1

        # 19.10.14 수정
        # "유니콘프레스"는 과 같은 문장에서 "가 인용절의 head를 head로 취하게 변경시키는 예외 필요
        elif childSize > 1 and self.children[-1].root.startswith('(R'):
            self.center = self.children[0].center
            rule_call_count[1] += 1

            if self.hasGrandParent():
                # 두번 위로 올라가 "유니콘프레스"는 어절에서 '유니콘프레스'와 '는'을 '는'이 유니콘프레스를 head로 취하게 만들어줌.
                grandparent = self.getGrandParent()
                grandparent.center = self.center
                grandparent.relation = 'dep'

            # 19.10.15 수정
            # 밑에 한줄 을 위의 grandparent.center = self.center로 변경
            # assignRelation과 같이 통일하기 위해서
            # grandparent.center.relation = 'dep'

            # 19.10.15 수정
            # "유니콘프레스"는 어절에서 유니콘프레스가 뒤에 동사를 수식할 때 태그를 붙여주는 부분(EX,nsubj를 붙여줘야함). 구구조분석말뭉치에서 구구조 태그를 보고 그에 대응하는 태그를 붙여준다.
            # 위의 grandparent보다 parent인 grandgrandparent에 태그를 매핑한 결과를 relation에 넣어놓고 밑에서 처리
                if grandparent.hasParent():
                    grandgrandparent = grandparent.getParent()
                    grandgrandparent.relation = grandgrandparent.assignRelation()

    def assignRelation(self):
        phrase = self.children[0].root
        if 'X_SBJ' in phrase:
            return 'nsubj'
        elif 'X_OBJ' in phrase:
            return 'obj'
        elif 'X_MOD' in phrase:
            return 'amod'
        elif 'X_AJT' in phrase:
            return 'obl'
        elif 'X_CMP' in phrase:
            return 'dep'
        elif 'X_CNJ' in phrase:
            return 'conj'

    def printPSTree(self, depth):
        for n in range(0, int(depth)):
            print(" ", end=" ")

        if self.parent != None:
            # print( self.root +"\t"+ str(self.id) + "\t" + str(self.parent.id) +"\t"+ str(self.center.id))
            print(self.root + "\t" + str(self.center.id))
        else:
            print(self.root + "\t" + str(self.id) + "\t" + str(self.center.id))

        for c in self.children:
            c.printPSTree(depth + 1)

    def printUDTree(self):
        global token_count

        hangul = re.compile('[^A-Z+]')  # upos를 위해 형태소 태그만 추출하기 위한 정규식
        if self.getChildSize() == 0:
            p = self
            while p is not None:
                if p.center != self:
                    self.head = p.center
                    relate = p.relation    # 19.10.15수정 구구조에 부착해놓은 태그를 가지고오기위해 추가
                    break
                p = p.parent

            if self is not None and self.head is not None:
                token_count = token_count + 1
                upos = hangul.sub('', self.root)

                if relate is not None: # 예외규칙으로 준 tag을 우선 가짐
                    udtag= relate
                    try_count_list3[1] += 1
                    relation_count[udtag] += 1
                else:
                    udtag = matchUDtag(self.root, self.head.root, self.id, self.head.id, p)

                if len(udtag) is not 0:
                    write_file.write(
                        str(self.id) + '\t' + self.root + "\t" + upos + '\t' + '_' + '\t' + "_" + '\t' + str(
                            self.head.id) + '\t' + udtag + '\t' + '_' + '\t' + '_' + '\n')
                # print( self.id,'\t', self.root,"\t",upos,'\t','_','\t',"_",'\t', self.head.id,'\t',udtag,'\t','_','\t','_')

                else:

                    # 여기다 세종태그랑 비교해서 다시 한번 더 UDtag 매핑하는 작업하기.
                    udtag_sejong = matchUDtag_from_Sejongtag(self, self.head.root)

                    # 19.10.14수정
                    # 예외규칙 1번을 수행할 때 dep태그를 할당 할때
                    # 이 규칙에서 생성된 DEPREL 태그를 부여하기 위한 부분
                    # if len(udtag_sejong) is 0 and ((self.head.relation is not None) or (relate is not None)):
                    # 19.10.15수정
                    # 원래는 'dep'태그가 저장된 곳이 center.relation이나, 수정을 통해 구태그 자체에 존재하게 변경
                    # 그로 인해 모든 태그가 구태그 자체게 relation을 저장하도록 수정.
                    '''if len(udtag_sejong) is 0 and relate is not None:
                        udtag_sejong = relate
                        try_count_list3[1] += 1
                        relation_count[udtag_sejong] += 1'''

                    if len(udtag_sejong) is not 0:
                        write_file.write(
                            str(self.id) + '\t' + self.root + "\t" + upos + '\t' + '_' + '\t' + "_" + '\t' + str(
                                self.head.id) + '\t' + udtag_sejong + '\t' + '_' + '\t' + '_' + '\n')
                    else:
                        write_file.write(
                            str(self.id) + '\t' + self.root + "\t" + upos + '\t' + '_' + '\t' + "_" + '\t' + str(
                                self.head.id) + '\t' + '\n')
                    # print( self.id,'\t', self.root,"\t",upos,'\t','_','\t',"_",'\t', self.head.id,'\t')

            else:
                token_count = token_count + 1
                upos = hangul.sub('', self.root)
                relation_count['ROOT'] = relation_count['ROOT'] + 1
                try_count_list[1] = try_count_list[1] + 1
                write_file.write(str(
                    self.id) + '\t' + self.root + "\t" + upos + '\t' + '_' + '\t' + "_" + '\t' + '0' + '\t' + 'ROOT' + '\t' + '_' + '\t' + '_' + '\n')
                # print( self.id,'\t', self.root,'\t',upos,'\t','_','\t',"_",'\t', 0,'\t', "ROOT",'\t','_','\t','_')

        for c in self.children:
            c.printUDTree()


def matchUDtag_from_Sejongtag(depenword2, headword2):
    sejongtag = depenword2.parent.root
    try_count_2 = 0
    result2 = ''
    for a, b in relation_dic_sejongtag.items():
        if re.search(a, sejongtag):
            for i in range(0, len(b)):
                if re.search(b[i][0], headword2):
                    try_count_2 = try_count_2 + 1
                    relation_count[b[i][1]] = relation_count[b[i][1]] + 1
                    result2 = result2 + ' ' + b[i][1]

    try_count_list2[try_count_2] = try_count_list2[try_count_2] + 1
    return result2


def matchUDtag2(depenword, headword):
    try_count = 0
    result = ''
    for k, v in relation_dic.items():
        if re.search(k, depenword):
            for i in range(0, len(v)):
                if re.search(v[i][0], headword):
                    try_count = try_count + 1
                    relation_count[v[i][1]] = relation_count[v[i][1]] + 1
                    result = result + ' ' + v[i][1]
                    # print(relation_count[v[i][1]])
        # 왜 이걸 넣으면 답이 안나오지...? -> 반복문 돌면서 찾아야하는데 한번에 못찾으면 none 해버려서,,,,
        '''else:    
            try_count_list[0] = try_count_list[0] + 1
            return None'''
    try_count_list[try_count] = try_count_list[try_count] + 1
    return result


def matchUDtag(depenWord, headWord, depen_id, head_id, p):
    if ((depenWord.find('/NNG') != -1 or depenWord.find('/NNP') != -1) and depenWord.find('J') == -1 and (
            headWord.find('/NNG') != -1 or headWord.find('/NNP') != -1) and (head_id - depen_id) == 1):
        # relation_count['nmod / flat'] = relation_count['nmod / flat'] + 1
        relation_count['compound'] = relation_count['compound'] + 1
        try_count_list[1] = try_count_list[1] + 1
        return 'compound'

    elif (depenWord != ',/SP') and (depenWord != './SF') and (p.root == '(S') and (p.children[0].root == '(NP_SBJ'):
        relation_count['nsubj'] = relation_count['nsubj'] + 1
        try_count_list[1] = try_count_list[1] + 1
        return 'nsubj'
        # print('이것이다!',depenWord, headWord, depen_id, head_id, p.root, p.children[0].root)
    else:
        return matchUDtag2(depenWord, headWord)


def split_token_sub(tok):
    token_list = []
    while True:
        if tok.endswith(')') or tok.endswith('/SF') or tok.endswith('/SP'):
            if tok.endswith(')'):
                token_list.insert(0, ')')
                tok = tok[:-1]
            elif tok.endswith('/SF'):
                stok = tok[-4:]
                tok = tok[:-4]
                if tok.endswith(' + '):
                    tok = tok[:-3]

                token_list.insert(0, stok)
            elif tok.endswith('/SP'):
                stok = tok[-4:]
                tok = tok[:-4]
                if tok.endswith(' + '):
                    tok = tok[:-3]
                token_list.insert(0, stok)
        else:
            break

    p = re.compile('^\([A-Z_]+ ')
    m = p.match(tok)
    if m:
        s_tok = tok[:m.end()]
        tok = tok[m.end():]
        token_list.insert(0, tok)
        token_list.insert(0, s_tok)
    else:
        token_list.insert(0, tok)
    return token_list


def split_token(stru):
    tok = re.split("[\t\n]", stru)
    return_token = []
    for t in tok:
        sub_token = split_token_sub(t)
        return_token.extend(sub_token)

    return_token = [t.strip() for t in return_token if t != ""]
    return return_token


def relationDic_Sejongtag():  # terminal node보다 한단계 위인 parent의 세종구문분석태그를 보고 udtag와 매핑
    f1 = open(file_path + "\\relationRule_from_Sejongtag.txt", "r", encoding='utf-8')
    fileList = f1.readlines()

    for line2 in fileList:
        line2 = line2.rstrip()
        line2 = line2.split('\t')
        if not line2:
            continue
        if len(line2[1:]) == 0:
            continue
        if line2[0] in relation_dic_sejongtag.keys():
            data = relation_dic_sejongtag.get(line2[0])
            data.append(tuple(line2[1:]))
            relation_dic_sejongtag[line2[0]] = data
        else:
            relation_dic_sejongtag[line2[0]] = [tuple(line2[1:])]


def relationDic():  # terminal node의 단어의 형태소를 보고 udtag와 매핑
    f = open(file_path + "\\relation_rule.txt", "r", encoding='utf-8')
    flist = f.readlines()

    for line in flist:
        line = line.rstrip()
        line = line.split('\t')
        if not line:
            continue
        if '#' in line:
            continue
        if len(line[1:]) == 0:
            continue
        if line[0] in relation_dic.keys():
            data = relation_dic.get(line[0])
            data.append(tuple(line[1:]))
            relation_dic[line[0]] = data
        else:
            relation_dic[line[0]] = [tuple(line[1:])]


# 입력 (token_list): 세종구구조부착 말뭉치에서 문장 단위로 분리한 뒤, 해당 문장을 토큰 단위로 분리한 리스트
# 출력 : 입력문장에 대한 UD tree list
def makeUDTree(sent, pstree):
    global token_count
    global sent_count
    global flag
    token_list = split_token(pstree)

    relations.clear()

    tok_start = {"(S", "(DP_CNJ", "(NP_SBJ", "(NP", "(VP_MOD", "(VNP", "(S_MOD", "(VNP_MOD", "(NP_MOD", "(VP",
                 "(VP_CMP", "(NP_CMP", "(NP_AJT", "(AP", "(NP_OBJ", "(DP_MOD", "(DP", "(L", "(IP", "(R", "(NP_CNJ",
                 "(X_SBJ", "(X", "(X_AJT", "(X_CNJ", "(X_MOD", "(S_PRN", "(S_AJT", "(VP_SBJ", "(VP_AJT", "(VP_OBJ",
                 "(VP", "(S_CMP", "(Q", "(NP_INT", "(IP", "(L", "(R", "(VNP_CMP", "(IP_INT", "(X", "(R_PRN", "(VP_CNJ",
                 "(AP_MOD", "(LP_OBJ", "(LP", "(X_OBJ", "(S_OBJ", "(X_CMP", "(AP_AJT", "(Q_CMP", "(S_SBJ", "(AP_CMP",
                 "(VP_PRD", "(NP_COM", "(NP_PRD", "(VP_COM", "(VP_INT", "(AP_SBJ", "(AP_OBJ", "(AP_COM", "(AP_INT",
                 "(AP_PRD", "(DP_SBJ", "(DP_OBJ", "(DP_COM", "(DP_INT", "(DP_PRD", "(NP_PRN", "(VP_PRN", "(AP_PRN",
                 "(S_PRD", "(VNP_OBJ", "(VNP_SBJ", "(VNP_COM", "(VNP_AJT", "(LP_CMP", "(LP_AJT", "(DP_AJT", "(IP_CMP",
                 "(Q_MOD", "(S_CNJ", "(LP_SBJ", "(VNP_CNJ", "(S_INT", "(VNP_PRN", "(Q_PRN", "(IP_AJT", "(VNP_INT", "(X",
                 "(X_PRN", "(S-", "(L_PRN", "(IP_CNJ", "(R_CMP"}
    count = 1
    root_list = []  # root node 1개만 저장

    for t in token_list:

        if t in tok_start:
            tree = STree()
            tree.setRoot(t)
            root_list.append(tree)

        elif ';Q' in t:
            return 0
        elif ';U' in t:
            return 0

        elif t == ')':
            c_list = []
            while True:
                poped = root_list.pop()

                if poped.getRoot() in tok_start and poped.getChildSize() == 0:
                    for c in c_list:
                        poped.addChild(c)

                    root_list.append(poped)
                    break

                else:
                    c_list.insert(0, poped)

        else:
            tree = STree()
            tree.setRoot(t)
            tree.id = count
            root_list.append(tree)
            count = count + 1

    root_list[0].sent = sent

    root_list[0].assignCenterNode()
    # root_list[0].printPSTree(0)
    if flag == 0:
        relationDic()
        relationDic_Sejongtag()
        flag = 1

    write_file.write('#' + sent[2:])
    root_list[0].printUDTree()
    write_file.write('\n')
    sent_count = sent_count + 1
