import requests
import json
from os import listdir, path

url = "http://localhost:8080/query"
headers = {'Content-Type': 'application/json;charset=UTF-8'}

def calculateSemanticSimilarity(movieName, query):
    data = {
        "sentence" : query
    }
    r = requests.post("http://localhost:8080/query", headers=headers, data=json.dumps(data))
    querySemanticGraph = json.loads(r.text)
    queryNodeData = []
    for levelOneNodes in querySemanticGraph:
        for child in levelOneNodes['children']:
            word = child['data']['word'].lower()
            if word[-2] == '-':
                word = word[:-2]
            queryNodeData.append({
                "word": word,
                "edge": child['data']['Edge']
            })
    print(len(queryNodeData))
    print(queryNodeData)
    moviefilename = movieName + '.json'
    moviePath = path.join('kparsedPlots', moviefilename)
    movieData = json.load(open(moviePath))['data']
    maxSimilarity = -1
    for sentenceData in movieData:
        movieSemanticGraph = json.loads(sentenceData['semanticGraph'])
        movieNodeData = []
        
        for levelOneNodes in movieSemanticGraph:
            for child in levelOneNodes['children']:
                word = child['data']['word'].lower()
                if len(word) > 2 and word[-2] == '-':
                    word = word[:-2]
                movieNodeData.append({
                    "word": word,
                    "edge": child['data']['Edge']
                })
        if len(movieNodeData) == 0:
            continue
        print(movieNodeData)
        similarityCount = 0
        for nodeGraphOne in queryNodeData:
            for nodeGraphTwo in movieNodeData:
                if nodeGraphOne['word'] == nodeGraphTwo['word']:
                    similarityCount += 1
                    if nodeGraphOne['edge'] == nodeGraphTwo['edge']:
                        similarityCount += 1
        print(similarityCount)
        similarity = similarityCount / (2 * len(movieNodeData))
        maxSimilarity = max(similarity, maxSimilarity)
    return maxSimilarity

query = "Father of a man suffers from Alzheimer disease."
movieName = "Aliens(1986)-Synopsis.txt"

calculateSemanticSimilarity(movieName, query)