import requests
import json
from os import listdir, path
import en_core_web_md

nlp = en_core_web_md.load()

url = "http://localhost:8080/query"
headers = {'Content-Type': 'application/json;charset=UTF-8'}

files = [f for f in listdir('CoreferencedPlots1')]

for file in files:
    relativePath = path.join('CoreferencedPlots1', file)
    with open(relativePath, mode='r') as f:
        doc = nlp(f.read())
        count = 0
        kaprserOutput = []
        for sentence in doc.sents:
            data = {
                'sentence': str(sentence)
            }
            r = requests.post(url, headers=headers, data=json.dumps(data))
            kaprserOutput.append({
                    'sentence': str(sentence),
                    'semanticGraph': r.text
                }
            )
        print(file)
        output = {
            'data': kaprserOutput
        }
        filename = file + '.json'
        kparsedFilePath = path.join('kparsedPlots', filename)
        with open(kparsedFilePath, mode='w') as out:
            json.dump(output, out)

# import json

def findSimilarity(queryGraph, movieSentenceGraph):
    maxSimilarity = 0
    graphOne = queryGraph
    graphTwo = movieSentenceGraph
    graphOneNodes = []
    graphTwoNodes = []
    data = json.load(open('kparsedPlots\Aliens(1986)-Synopsis.txt.json'))
    for levelOneNodes in graphOne:
        for child in levelOneNodes['children']:
            word = child['data']['word'].lower()
            if word[-2] == '-':
                word = word[:-2]
            graphOneNodes.append({
                "word": word,
                "edge": child['data']['Edge']
            })
    for levelOneNodes in graphTwo:
        for child in levelOneNodes['children']:
            word = child['data']['word'].lower()
            if word[-2] == '-':
                word = word[:-2]
            graphTwoNodes.append({
                "word": word,
                "edge": child['data']['Edge']
            })
    similarityCount = 0
    for nodeGraphOne in graphOneNodes:
        for nodeGraphTwo in graphTwoNodes:
            if nodeGraphOne['word'] == nodeGraphTwo['word']:
                similarityCount += 1
                if nodeGraphOne['edge'] == nodeGraphTwo['edge']:
                    similarityCount += 1
    print(graphOneNodes)
    print(graphTwoNodes)

#     print(similarityCount)

# data = json.load(open('kparsedPlots\Aliens(1986)-Synopsis.txt.json'))
# # print(data['data'][0]['semanticGraph'])
# movieGraph = json.loads(data['data'][0]['semanticGraph'])
# query = "red are only in the Special Edition After the opening credits, we see a spacecraft drifting slowly through space."

# headers = {'Content-Type': 'application/json;charset=UTF-8'}
# data = {
#     "sentence" : query
# }
# r = requests.post("http://localhost:8080/query", headers=headers, data=json.dumps(data))

# responseJson = json.loads(r.text)
# queryGraph = responseJson

# findSimilarity(queryGraph, movieGraph)