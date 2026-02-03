import random

def normalize_row(row: dict, nodes: list[str]) -> dict:
    s = sum(row.get(n, 0.0) for n in nodes)
    if s <= 0:
        # fallback uniform
        u = 1.0 / len(nodes)
        return {n: u for n in nodes}
    return {n: row.get(n, 0.0) / s for n in nodes}

def sample_from_dist(dist: dict[str, float]) -> str:
    r = random.random()
    c = 0.0
    for k, p in dist.items():
        c += p
        if r <= c:
            return k
    # numerical fallback
    return next(iter(dist.keys()))
