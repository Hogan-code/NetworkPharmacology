import requests,time,re
from bs4 import BeautifulSoup

class TTD:

    def __self__(self):
        pass

    def Gene_find(self,genes):
        '''判断Gene是否可以搜索，生成两个列表

        genes:  所要搜索的gene列表
        
        return: genes_exist,exist_flag

        genes_exist:    可以搜索的gene列表
        exist_flag: genes是否可以搜索的判断标志列表
        '''
        exist_flag = []
        genes_exist = []
        nothing = '[<p>Sorry! Nothing is found.</p>]'

        for index,gene in enumerate(genes):
            website = 'http://db.idrblab.net/ttd/search/ttd/target?search_api_fulltext=' + str(gene)
            try:
                response = requests.get(website)
            except requests.exceptions.ConnectionError:
                print('Error,writing 60s.')
                time.sleep(60)
                response = requests.get(website)
            response.encoding = response.apparent_encoding
            html = BeautifulSoup(response.text,'lxml')

            content = html.select('#fixed-width-page > div > main > div.col-md-12 > div.not-found > p')

            if (str(gene) != '') & (str(content) != nothing):
                exist_flag.append('Y')
                genes_exist.append(gene)
            else:
                exist_flag.append('N')
    
            print('序号:%d 已完成' % index)

        return genes_exist,exist_flag
    
    def Target_id(self,genes_exist):
        '''根据基因获取相关Targetid，生成三个列表

        genes_exist:    可以搜索的gene列表
        return: genes_contain,genes_not_contain,targetIds

        genes_contain:  包含相关targetid的gene列表
        genes_not_contain:  不包含相关targetid的gene列表(存在可以搜索的target的gene)
        targetIds:  targetid列表
        '''
        genes_contain = []
        targetIds = []

        for index,gene in enumerate(genes_exist):
            website = 'http://db.idrblab.net/ttd/search/ttd/target?search_api_fulltext=' + str(gene)
            try:
                response = requests.get(website)
            except requests.exceptions.ConnectionError:
                print('Error,writing 60s.')
                time.sleep(60)
                response = requests.get(website)
            response.encoding = response.apparent_encoding
            html = BeautifulSoup(response.text,'lxml')

            contents = html.find_all('th',attrs={'width': '15%', 'rowspan': '4', 'class': ['v-center', 'h-center']})

            for content in contents:
                targetId = (content.text)[:-12]
                website = 'http://db.idrblab.net/ttd/data/target/details/' + str(targetId)

                try:
                    response = requests.get(website)
                except requests.exceptions.ConnectionError:
                    print('Error,writing 60s.')
                    time.sleep(60)
                    response = requests.get(website)
                response.encoding = response.apparent_encoding
                html = BeautifulSoup(response.text,'lxml')

                targetName = html.find_all('div',attrs={'class': 'target__name'})
                geneName = re.findall(r"[(](.*?)[)]", str(targetName[0].text))
                difference = set(geneName[0]).difference(set(str(gene)))

                if (str(geneName[0]) == str(gene)) or difference == {'-'}:
                    genes_contain.append(gene)
                    targetIds.append(targetId)
                    print('序号:%d 已完成' % index)

        genes_not_contain = list(set(genes_exist) - set(genes_contain))

        return genes_contain,genes_not_contain,targetIds
    
    def Disease_name(self,genes_contain,targetIds):
        '''根据target搜索疾病，生成三个列表

        genes_contain:  包含相关targetid的gene列表
        targetIds:  targetid列表
        return:genes_disease,targetIds_disease,diseases

        genes_disease:  包含相关disease的基因列表
        targetIds_disease:  包含相关disease的targetid列表
        diseases:   根据targetIds获得的疾病名称列表
        '''
        genes_disease = []
        targetIds_disease = []
        diseases = []

        for index, targetId in enumerate(targetIds):
                website = 'http://db.idrblab.net/ttd/data/target/details/' + str(targetId)

                try:
                    response = requests.get(website)
                except requests.exceptions.ConnectionError:
                    print('Error,writing 60s.')
                    time.sleep(60)
                    response = requests.get(website)
                response.encoding = response.apparent_encoding

                html = BeautifulSoup(response.text,'lxml')
                diseaseTitle = html.select("#%s-disease > th" %str(targetId))

                if not diseaseTitle:
                    genes_disease.append(genes_contain[index])
                    targetIds_disease.append(targetId)
                    diseases.append('')
                    print('序号:%d 已完成' % index)
                else:
                    num = html.select("#drug_more > b")
                    disease_num = int(str(num[0])[3:-4])
                    content_start = html.select('#table-target-general > tbody > tr:nth-child(7) > td:nth-child(2)')

                    if str(content_start)[2:16] == 'td colspan="6"':
                        strat_i = 7
                    else:
                        strat_i = 8
                    for i in range(strat_i,strat_i+disease_num):
                            content = html.select('#table-target-general > tbody > tr:nth-child(%d) > td:nth-child(2)' %i)

                            genes_disease.append(genes_contain[index])
                            targetIds_disease.append(targetId)
                            diseases.append(str(content)[26:-52])
                            print('序号:%d 已完成' % index)

        return genes_disease,targetIds_disease,diseases