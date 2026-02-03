import json

def load_graph(path: str):
    with open(path, "r", encoding="utf-8") as f:
        g = json.load(f)
    nodes = g["nodes"]
    out_probs = g["out_probs"]   # dict[str][str] = float
    return nodes, out_probs
