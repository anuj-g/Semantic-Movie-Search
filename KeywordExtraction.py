from os import listdir, path
from rake_nltk import Rake

files = [f for f in listdir('CoreferencedPlots')]
r = rake.Rake("SmartStoplist.txt", 5, 1)

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        text = f.read()
        r.extract_keywords_from_text(text)
        print(r.get_ranked_phrases())
    break