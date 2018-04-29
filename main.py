from os import listdir, path
import en_core_web_md
import textacy
import spacy
import nltk
import string
import operator
import requests
import json
from pyjarowinkler import distance
from nltk.corpus import wordnet as wn, wordnet_ic
from nltk.stem.snowball import SnowballStemmer
import gensim

nlp = spacy.load("en")

ner = {}
keywords = {}
events = {}

url = "http://localhost:8080/query"
headers = {'Content-Type': 'application/json;charset=UTF-8'}

files = [f for f in listdir('CoreferencedPlots')]
semcor_ic = wordnet_ic.ic('ic-semcor.dat')

stopwords = set()

queries = [
            "There is a creature from another planet"
        ]

output = [
    "Aseparation(2011)-Synopsis.txt"
]

crimefile = open('SmartStoplist.txt', mode='r', encoding='utf-8')
for line in crimefile.readlines():
    stopwords.add(line[:-1])

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

doc_tokens = []
stemmer = SnowballStemmer("english")

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    # stems = stem_tokens(tokens, stemmer)
    return tokens

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        text = f.read()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" or ent.label_ == "ORG" or ent.label_ == "LOC":
                if file not in ner:
                    ner[file] = []
                ner[file].append(ent.text.lower().strip())
            if ent.label_ == "FACILITY" or ent.label_ == "PRODUCT" or ent.label_ == "GPE":
                if file not in keywords:
                    keywords[file] = []
                keywords[file].append(ent.text.lower().strip())
        
        for token in doc:
            if token.pos_ == "VERB" and token.lemma_ not in stopwords:
                if file not in events:
                    events[file] = []
                events[file].append(token.lemma_)
        
        # for sentence in doc.sents:
        lowers = text.lower()
        translator = str.maketrans('', '', string.punctuation)
        lowers_without_punctuations = lowers.translate(translator)
        stopwords = nltk.corpus.stopwords.words('english')
        tokens = [i for i in tokenize(lowers_without_punctuations) if i not in stopwords]
        doc_tokens.append(tokens)

# print(len(set([y for x in doc_tokens for y in x)))
# print(doc_tokens)
# Word2VecModel = gensim.models.Word2Vec(doc_tokens, min_count=0, size=500, max_vocab_size=1000000)
# Word2VecModel.build_vocab(doc_tokens)
# Word2VecModel.train(doc_tokens)
# Word2VecModel.save('word2vec.model')
Word2VecModel = gensim.models.Word2Vec.load('word2vec.model')


def calculateNerSimilarity(movie):
    queryNerSet = set(queryNer)
    intersection = set()
    # for movie in ner:
    plotNerSet = set(ner[movie])
    intersection = set.intersection(plotNerSet, queryNerSet)
    if len(intersection) == 0 or len(queryNerSet) == 0:
        return 0
    return len(intersection) / len(queryNerSet)

def calculateKeywordsSimilarity(movie):
    queryKeywordsSet = set(queryKeywords)
    # for movie in keywords:
    count = 0
    plotKeywordsSet = set(keywords[movie])
    for plotKeyword in plotKeywordsSet:
        for queryKeyword in queryKeywordsSet:
            winkler_distance = distance.get_jaro_distance(plotKeyword, queryKeyword)
            if winkler_distance > 0.9:
                count += 1
    if count == 0 or len(queryKeywordsSet) == 0:
        return 0
    return count / len(queryKeywordsSet)

def calculateEventSimilarity(movie):
    queryEventsSet = set(queryEvents)
    # for movie in events:
    event_max = events_match_count = avg_event_match = 0
    plotEventsSet = set(events[movie])
    for queryEvent in queryEventsSet:
        flag = False
        max_event_val = 0
        querySyn = wn.synsets(queryEvent, pos=wn.VERB)
        if queryEvent not in plotEventsSet:
            for plotEvent in plotEventsSet:
                plotSyn = wn.synsets(plotEvent, pos=wn.VERB)
                if len(plotSyn) == 0 or len(querySyn) == 0:
                    continue
                lin_similarity = plotSyn[0].lin_similarity(querySyn[0], semcor_ic)
                path_simialarity = plotSyn[0].path_similarity(querySyn[0])
                if ((lin_similarity + path_simialarity) / 2 > 0.4 and (lin_similarity + path_simialarity) / 2 > max_event_val):
                    flag = True
                    max_event_val = max(lin_similarity,path_simialarity)
            event_max = max_event_val
            if flag:
                events_match_count += 1
                avg_event_match += event_max
        else:
            events_match_count += 1
            event_max = 1.5
            flag = True
            avg_event_match= avg_event_match + event_max
    if len(queryEventsSet) == 0:
        return 0
    avg_event_match /= len(queryEventsSet)
    score = ((events_match_count/len(queryEventsSet)) + (avg_event_match/1.5))/2
    return score

def isVerb(edge):
    if edge == 'objective' or edge == 'previous_event' or \
    edge == 'next_event' or edge == 'caused_by' or \
    edge == 'causes' or edge == 'inhibited_by' or \
    edge == 'verb_compliment' or edge == 'supporting_verb' or \
    edge == 'modal_verb' or edge == 'passive_supporting_verb':
        return True
    return False

def calculateSemanticSimilarity(movieName, queryParseTree, queryNodeCount):
    maxSimilarity = 0
    movieDataLen = 0
    plotSimilarity = 0
    try:
        moviefilename = movieName + '.json'
        moviePath = path.join('kparsedPlots', moviefilename)
        movieData = json.load(open(moviePath))['data']
        movieDataLen = len(movieData)
        for i in range(len(movieData)):
            # print(i)
            # print(movieData[i]['sentence'])
            sentenceData = movieData[i]
            # print(sentenceData['sentence'])
            # print(movieData[i]['sentence'])
            movieSemanticGraph = json.loads(sentenceData['semanticGraph'])
            plotParseTree = {}
            similarity = 0
            sentenceNodeCount = 0
            for levelOneNodes in movieSemanticGraph:
                for child in levelOneNodes['children']:
                    word = child['data']['word'].lower()
                    edge = child['data']['Edge']
                    if len(word) > 2 and word[-2] == '-':
                        word = word[:-2]
                    if len(word) > 2 and word[-3] == '-':
                        word = word[:-3]
                    if edge not in plotParseTree:
                        plotParseTree[edge] = []
                    plotParseTree[edge].append(word)
                    sentenceNodeCount += 1
                # plotParseTree.append(plotTree)

            # print(plotParseTree)

            for queryKey in queryParseTree:
                if queryKey in plotParseTree:
                    wordsPlotTree = plotParseTree[queryKey]
                    for wordone in queryParseTree[queryKey]:
                        for word in wordsPlotTree:
                            try:
                                similarity += Word2VecModel.wv.similarity(wordone, word)
                                # print(Word2VecModel.wv.similarity(queryParseTree[queryKey], word))
                            except:
                                if word == wordone:
                                    similarity += 1
            
            similarity = similarity / (queryNodeCount + sentenceNodeCount)
            maxSimilarity = max(similarity, maxSimilarity) 
            # plotSimilarity += similarity
            # print(similarity)
            # for queryParseTree in queryParseTrees:
            #     for plotParseTree in plotParseTrees:
            #         for keyOne in queryParseTree:
            #             for keyTwo in plotParseTree:
            #                 try:
            #                     similarity += Word2VecModel.wv.similarity(queryParseTree[keyOne], plotParseTree[keyTwo])
            #                     if keyOne == keyTwo:
            #                         similarity += 1
            #                 except:
            #                     continue
            # maxSimilarity = max(maxSimilarity, similarity)
    #         if len(movieNodeData) == 0:
    #             continue
    #         similarityCount = 0
    #         for nodeGraphOne in queryNodeData:
    #             for nodeGraphTwo in movieNodeData:
    #                 similarity = Word2VecModel.wv.similarity(nodeGraphOne['word'], nodeGraphTwo['word'])
    #                 print(nodeGraphOne['word'], " ", nodeGraphTwo['word'], " ", similarity)
    #                 if nodeGraphOne['word'] == nodeGraphTwo['word']:
    #                     similarityCount += 1
    #                     if nodeGraphOne['edge'] == nodeGraphTwo['edge']:
    #                         similarityCount += 1
    #         similarity = similarityCount / (2 * len(movieNodeData))
    #         maxSimilarity = max(similarity, maxSimilarity)
    except Exception as e:
        # print(e)
        maxSimilarity = 0
        return 0
    # print(plotSimilarity)
    return maxSimilarity

# def calculateSemanticSimilarity(movieName, queryNodeData, queryNodes):
#     maxSimilarity = 0
#     plotSimilarity = 0
#     movieDataLen = 0
#     try:
#         moviefilename = movieName + '.json'
#         moviePath = path.join('kparsedPlots', moviefilename)
#         movieData = json.load(open(moviePath))['data']
#         movieDataLen = len(movieData)
#         movieDataLen = len(movieData)
#         for sentenceData in movieData:
#             movieSemanticGraph = json.loads(sentenceData['semanticGraph'])
#             movieNodeData = []
#             # print(sentenceData['sentence'])
#             for levelOneNodes in movieSemanticGraph:
#                 for child in levelOneNodes['children']:
#                     word = child['data']['word'].lower()
#                     if len(word) > 2 and word[-2] == '-':
#                         word = word[:-2]
#                     if len(word) > 2 and word[-3] == '-':
#                         word = word[:-3]
#                     movieNodeData.append({
#                         "word": word,
#                         "edge": child['data']['Edge']
#                     })
#             if len(movieNodeData) == 0:
#                 continue
#             similarityCount = 0
#             for nodeGraphOne in queryNodeData:
#                 for nodeGraphTwo in movieNodeData:
#                     wvsimilarity = 0
#                     try:
#                         wvsimilarity = Word2VecModel.wv.similarity(nodeGraphOne['word'], nodeGraphTwo['word'])
#                         # print(wvsimilarity)
#                     except Exception as e:
#                         # print(e)
#                         if nodeGraphOne['word'] == nodeGraphTwo['word']:
#                             wvsimilarity = 1
#                     if nodeGraphOne['edge'] == nodeGraphTwo['edge']:
#                         wvsimilarity *= 2
#                     # print(wvsimilarity)
#                     similarityCount += wvsimilarity
#             similarity = similarityCount / (len(movieNodeData) + queryNodes)
#             maxSimilarity = max(similarity, maxSimilarity)
#     except Exception as e:
#         maxSimilarity = 0
#         return 0
#     return maxSimilarity

oneAccuracy = 0
threeAccuracy = 0
fiveAccuracy = 0
eightAccuracy = 0
tenAccuracy = 0

for i in range(len(queries)):
    query = queries[i]
    print(query)
    result = output[i]
    doc = nlp(query)
    queryNer = []
    queryKeywords = []
    queryEvents = []
    scores = []
    data = {
        "sentence" : query
    }
    for ent in doc.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG" or ent.label_ == "LOC":
            queryNer.append(ent.text.lower().strip())
        if ent.label_ == "FACILITY" or ent.label_ == "PRODUCT" or ent.label_ == "GPE":
            queryKeywords.append(ent.text.lower().strip())

    for token in doc:
        if token.pos_ == "VERB" and token.lemma_ not in stopwords:
            queryEvents.append(token.lemma_)
    r = requests.post("http://localhost:8080/query", headers=headers, data=json.dumps(data))
    querySemanticGraph = json.loads(r.text)

    lowers = query.lower()
    translator = str.maketrans('', '', string.punctuation)
    lowers_without_punctuations = lowers.translate(translator)
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [i for i in tokenize(lowers_without_punctuations) if i not in stopwords]
    query = ' '.join(tokens)
    # queryNodeData = []
    queryNodeCount = 0
    # for levelOneNodes in querySemanticGraph:
    #     for child in levelOneNodes['children']:
    #         word = child['data']['word'].lower()
    #         if word[-2] == '-':
    #             word = word[:-2]
    #         queryNodeData.append({
    #             "word": word,
    #             "edge": child['data']['Edge']
    #         })
    #         queryNodeCount += 1
    queryParseTree = {}
    
    for levelOneNodes in querySemanticGraph:
        # queryTree = {}
        for child in levelOneNodes['children']:
            word = child['data']['word'].lower()
            edge = child['data']['Edge']
            if len(word) > 2 and word[-2] == '-':
                word = word[:-2]
            if len(word) > 2 and word[-3] == '-':
                word = word[:-3]
            if isVerb(edge):
                doc = nlp(word)
                for token in doc:
                    word = token.lemma_
            if edge not in queryParseTree:
                queryParseTree[edge] = []
            queryNodeCount += 1
            queryParseTree[edge].append(word)
        # queryParseTrees.append(queryTree)

    # print(queryParseTrees)
    for movie in keywords:
        score = (calculateSemanticSimilarity(movie, queryParseTree, queryNodeCount) * 0.5 + calculateNerSimilarity(movie) * 0.2 + calculateKeywordsSimilarity(movie) * 0.1 + calculateEventSimilarity(movie) * 0.2) / 4
        scores.append([movie, score])
    scores.sort(key=operator.itemgetter(1), reverse=True)
    print(result)
    print(scores[0])
    print(scores[0:3])
    print(scores[0:5])
    print(scores[0:8])
    print(scores[0:10])

    if scores[0][0] == result:
        oneAccuracy += 1
    for i in range(3):
        if result == scores[i][0]:
            threeAccuracy += 1
    for i in range(5):
        if result == scores[i][0]:
            fiveAccuracy += 1
    for i in range(8):
        if result == scores[i][0]:
            eightAccuracy += 1
    for i in range(10):
        if result == scores[i][0]:
            tenAccuracy += 1
    # if result in scores[0:3][0]:
    #     threeAccuracy += 1
    # if result in scores[0:5]:
    #     fiveAccuracy += 1
    # if result in scores[0:8]:
    #     eightAccuracy += 1
    # if result in scores[0:10]:
    #     tenAccuracy += 1
    
    print("Next")


print("Accuracy for 1: " + str((oneAccuracy * 100) / len(queries)))
print("Accuracy for 3: " + str((threeAccuracy * 100) / len(queries)))
print("Accuracy for 5: " + str((fiveAccuracy * 100) / len(queries)))
print("Accuracy for 8: " + str((eightAccuracy * 100) / len(queries)))
print("Accuracy for 10: " + str((tenAccuracy * 100) / len(queries)))
