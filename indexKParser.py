import requests
from os import listdir, path

r = requests.post("http://localhost:8080/query", json={"sentence" : "abc loves xyz"})

files = [f for f in listdir('CoreferencedPlots')]

for file in files:
    relativePath = path.join('CoreferencedPlots', file)
    with open(relativePath, 'r') as f:
        lines = f.readlines()
        print(lines)
    break