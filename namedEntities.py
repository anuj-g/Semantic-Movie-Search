from os import listdir, path
import en_core_web_md

nlp = en_core_web_md.load()

files = [f for f in listdir('CoreferencedPlots')]

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        doc = nlp(f.read())
        for ent in doc.ents:
            if ent.label_ == "PERSON" or ent.label_ == "ORG" or ent.label_ == "LOC":
                print(ent.text)
            if ent.label_ == "FACILITY" or ent.label_ == "PRODUCT" or ent.label_ == "GPE":
                print(ent.text)
    break