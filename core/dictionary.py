import json, os

DICT_PATH = os.path.expanduser("data/wordnet.json")

with open(DICT_PATH, "r") as f:
    WORDNET = json.load(f)

def lookup_word(word, max_results=5):
    word = word.lower().strip()
    if word in WORDNET:
        return WORDNET[word][:max_results]
    return [{"definition": "No definition found.", "pos": ""}]
