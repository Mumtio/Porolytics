import json, random
from collections import Counter, defaultdict

from utils.graph_io import load_graph
from utils.math_utils import normalize_row, sample_from_dist
from sim.step7_state import SimState, default_starters, default_targets

def apply_denial(row: dict, nodes: list[str], state: SimState) -> dict:
    out = dict(row)
    # hard disable
    for n in state.disabled:
        out[n] = 0.0
    # soft damp
    for n, m in state.damp.items():
        if n in out:
            out[n] *= max(0.0, min(1.0, m))
    return normalize_row(out, nodes)

def rollout(nodes, out_probs, state: SimState, starters: list[str], targets: set[str],
            max_steps=12):
    # pick a start node that isn't disabled
    start_choices = [s for s in starters if s in nodes and s not in state.disabled]
    if not start_choices:
        return {"success": False, "reason": "no_valid_starters", "path": []}

    current = random.choice(start_choices)
    path = [current]
    visit_count = defaultdict(int)
    visit_count[current] += 1

    for step_idx in range(max_steps):
        row = out_probs.get(current, {})
        dist = apply_denial(row, nodes, state)

        # Step 8.2 - Conversion Pressure
        if step_idx >= 4:
            if "TEAMFIGHT_COMMIT" in dist:
                dist["TEAMFIGHT_COMMIT"] *= 1.3
            if "OBJECTIVE_STACKING" in dist:
                dist["OBJECTIVE_STACKING"] *= 1.2
            dist = normalize_row(dist, nodes)

        nxt = sample_from_dist(dist)
        path.append(nxt)

        if nxt in targets:
            return {"success": True, "reason": "reached_target", "path": path}

        # Step 8.1 - Loop Softening
        visit_count[nxt] += 1
        if visit_count[nxt] > 2:
            return {
                "success": False,
                "reason": "tempo_stall",
                "stall_node": nxt,
                "path": path
            }

        current = nxt

    return {"success": False, "reason": "max_steps", "path": path}

def compress(path):
    if not path: return []
    out = [path[0]]
    for x in path[1:]:
        if x != out[-1]:
            out.append(x)
    return out

def run_mc(graph_path: str, n_runs=20000, deny_nodes=None, damp=None,
           max_steps=12, seed=7):
    random.seed(seed)
    nodes, out_probs = load_graph(graph_path)

    state = SimState(
        disabled=set(deny_nodes or []),
        damp=damp or {}
    )
    starters = default_starters()
    targets = set(default_targets())

    results = []
    success = 0
    reasons = Counter()
    path_counter = Counter()

    for _ in range(n_runs):
        r = rollout(nodes, out_probs, state, starters, targets, max_steps=max_steps)
        results.append(r)
        reasons[r["reason"]] += 1
        if r["success"]:
            success += 1
            # compress path signature
            sig = " -> ".join(compress(r["path"]))
            path_counter[sig] += 1

    return {
        "graph": graph_path,
        "n_runs": n_runs,
        "deny_nodes": list(state.disabled),
        "damp": state.damp,
        "max_steps": max_steps,
        "success_rate": success / n_runs,
        "failure_reasons": reasons,
        "top_success_paths": path_counter.most_common(10),
    }

if __name__ == "__main__":
    baseline = run_mc("graph_win.json", n_runs=20000, deny_nodes=[], seed=7)
    print("BASELINE success_rate:", baseline["success_rate"])
    print("Top failure reasons:", baseline["failure_reasons"])
    print("Top success paths:")
    for p, c in baseline["top_success_paths"]:
        print(c, p)

    with open("out/mc_baseline.json", "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2, default=str)
