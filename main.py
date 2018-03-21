from os import listdir, path
import en_core_web_md
import textacy
import spacy
import nltk
import operator
from pyjarowinkler import distance
from nltk.corpus import wordnet as wn, wordnet_ic

nlp = spacy.load("en")

ner = {}
keywords = {}
events = {}

files = [f for f in listdir('CoreferencedPlots')]
semcor_ic = wordnet_ic.ic('ic-semcor.dat')

stopwords = set()

query = "Two police officers go to a federal mental hospital.Police officers interview mental hospital staff and patients.A mental patient escapes from a federal mental hospital."

crimefile = open('SmartStoplist.txt', mode='r', encoding='utf-8')
for line in crimefile.readlines():
    stopwords.add(line[:-1])

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        doc = nlp(f.read())
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

doc = nlp(query)
queryNer = []
queryKeywords = []
queryEvents = []

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
    avg_event_match /= len(queryEventsSet)
    score = ((events_match_count/len(queryEventsSet)) + (avg_event_match/1.5))/2
    return score

for ent in doc.ents:
    if ent.label_ == "PERSON" or ent.label_ == "ORG" or ent.label_ == "LOC":
        queryNer.append(ent.text.lower().strip())
    if ent.label_ == "FACILITY" or ent.label_ == "PRODUCT" or ent.label_ == "GPE":
        queryKeywords.append(ent.text.lower().strip())

for token in doc:
    if token.pos_ == "VERB" and token.lemma_ not in stopwords:
        queryEvents.append(token.lemma_)

scores = []

for movie in keywords:
    score = (calculateNerSimilarity(movie) + calculateKeywordsSimilarity(movie) + calculateEventSimilarity(movie)) / 3
    scores.append([movie, score])

scores.sort(key=operator.itemgetter(1), reverse=True)

print(scores[:10])

# max_score = 0.0
# most_similar_movie = ""
# for movie in scores:
#     if scores[movie] > max_score:
#         max_score = scores[movie]
#         most_similar_movie = movie

# print(scores)
# print(max_score)
# print(most_similar_movie)

