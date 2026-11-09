import json, os
PATH = os.path.join(os.path.expanduser("~"), ".joia_conhecimento_save.json")
DEFAULT = {"done": 0, "lang": "pt", "sound": True}   # done = niveis concluidos (0..9)

def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            return {**DEFAULT, **json.load(f)}
    except Exception:
        return dict(DEFAULT)

def write(data):
    try:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass
