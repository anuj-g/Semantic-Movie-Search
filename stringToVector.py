import nltk
import string
from os import listdir, path
import logging

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.stem.porter import PorterStemmer
import gensim

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

doc_tokens = []
stemmer = PorterStemmer()

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

files = [f for f in listdir('Synopsis')]

for file in files:
    relativePath = path.join('Synopsis', file)
    with open(relativePath, 'r') as f:
        text = f.read()
        lowers = text.lower()
        translator = str.maketrans('', '', string.punctuation)
        lowers_without_punctuations = lowers.translate(translator)
        stopwords = nltk.corpus.stopwords.words('english')
        tokens = [i for i in tokenize(lowers_without_punctuations) if i not in stopwords]
        doc_tokens.append(tokens)

dictionary = gensim.corpora.Dictionary(doc_tokens)
dictionary.save('deerwester.dict')
corpus = [dictionary.doc2bow(tokens) for tokens in doc_tokens]
lsi = gensim.models.LsiModel(corpus, id2word=dictionary, num_topics=500)
lsi.save('lsi.model')
index = gensim.similarities.MatrixSimilarity(lsi[corpus])
index.save('deerwester.index')

# lsi = gensim.models.LsiModel.load('lsi.model')
# index = gensim.similarities.MatrixSimilarity.load('deerwester.index')
# dictionary = gensim.corpora.Dictionary.load('deerwester.dict')

queries = [
            "Father of a man suffers from Alzheimer disease.", 
            "A man camps in alaska in an abandoned bus.A man travels from Mexico to United States on foot.",
            "A dog goes to train station with his master everyday.",
            "There is a creature from another planet"
        ]

output = [
    "Aseparation(2011)-Synopsis.txt",
    "IntotheWild(2007)-Synopsis.txt",
    "hachi.txt",
    "Abc.txt"
]
# query = "A man's car is caught in flash flood and left abandoned.A man donates all his savings and goes on a cross-country drive.A man camps in alaska in an abandoned bus.A man travels from Mexico to United States on foot."
count = 0
score = 0

oneAccuracy = 0
threeAccuracy = 0
fiveAccuracy = 0
eightAccuracy = 0
tenAccuracy = 0

for i in range(len(queries)):
    query = queries[i]
    result = output[i]
    query_lowers = query.lower()
    translator = str.maketrans('', '', string.punctuation)
    query_tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
    query_tfs = query_tfidf.fit_transform(query_lowers.translate(translator).split())
    vec_bow = dictionary.doc2bow(list(query_tfidf.vocabulary_.keys()))
    vec_lsi = lsi[vec_bow]

    sims = index[vec_lsi]

    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    # for i in range(5):
    #     print(output[count])
    #     print(files[sims[i][0]])
    
    
    # if output[count] in files[0:3][0]:
    #     score += 1
    print("\n")
    print("Top 1 movies")
    if files[sims[0][0]] == result:
        print(files[sims[0][0]])
        oneAccuracy += 1
    print("\n")
    print("Top 3 movies")
    for i in range(3):
        print(files[sims[i][0]])
        if result == files[sims[i][0]]:
            threeAccuracy += 1
    print("\n")
    print("Top 5 movies")
    for i in range(5):
        print(files[sims[i][0]])
        if result == files[sims[i][0]]:
            fiveAccuracy += 1
    print("\n")
    print("Top 8 movies")
    for i in range(8):
        print(files[sims[i][0]])
        if result == files[sims[i][0]]:
            eightAccuracy += 1
    print("\n")
    print("Top 10 movies")
    for i in range(10):
        print(files[sims[i][0]])
        if result == files[sims[i][0]]:
            tenAccuracy += 1
    print("#########################################################")
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
    
    # if files[sims[0][0]] == output[count]:
    #     score += 1
    
    

# print(score)