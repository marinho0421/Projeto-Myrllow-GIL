import json, os
PATH = os.path.join(os.path.expanduser("~"), ".joia_conhecimento_save.json")
# done = niveis concluidos na campanha (0..9); char = personagem escolhido; chosen = ja escolheu alguma vez
DEFAULT = {"done": 0, "lang": "pt", "sound": True, "char": "joao", "chosen": False}

def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            d = {**DEFAULT, **json.load(f)}
    except Exception:
        d = dict(DEFAULT)
    if d["char"] not in ("joao", "emilia"): d["char"] = "joao"
    return d

def write(data):
    try:
        with open(PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass
