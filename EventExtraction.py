import textacy
import spacy
import csv

from os import listdir, path
from os.path import isfile, join

nlp = spacy.load("en")

stopwords = set()

crimefile = open('SmartStoplist.txt', mode='r', encoding='utf-8')
for line in crimefile.readlines():
    stopwords.add(line[:-1])

files = [f for f in listdir('CoreferencedPlots')]

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        print(file.split(',')[0])
        parsedData = nlp(f.read())
        print(parsedData)
        sents = []
        for span in parsedData.sents:
            sent = ''.join(parsedData[i].string.lower() for i in range(span.start, span.end)).strip()
            sents.append(sent)
        for sentence in sents:
            try:
                doc = textacy.Doc(strip_non_ascii(sentence))
                triplets = textacy.extract.subject_verb_object_triples(doc)
                triple = next(triplets, None)
                if triple != None:
                    if triple[1] in stopwords or triple[1].lemma_ in stopwords:
                        continue
                    print(triple[1].lemma_)
            except:
                pass
    break

print("Done generating triples")