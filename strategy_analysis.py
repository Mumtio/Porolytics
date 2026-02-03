import json
import math
import random
from collections import defaultdict

NODES = [
  "TEAMFIGHT_COMMIT",
  "OBJECTIVE_STACKING",
  "RIVER_CONTROL",
  "BOT_PRESSURE",
  "TOP_PRESSURE",
  "MID_TEMPO",
  "PICK_ORIENTED"
]

TARGETS = ["TEAMFIGHT_COMMIT", "OBJECTIVE_STACKING"]

GOOD_QUALITIES = {"HIGH", "MED"}

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_good_encounter(e):
    if e.get("quality") not in GOOD_QUALITIES:
        return False
    if e.get("is_atomic") is True and e.get("duration_ms", 0) == 0:
        return False
    return True

def decay(dt_ms, tau_ms=45000.0):
    return math.exp(-dt_ms / tau_ms)

def build_raw_graph(encounters, mode="WIN", next_k=2, tau_ms=45000.0):
    """
    mode:
      WIN  -> use encounters whose outcome == SUCCESS as sources
      LOSS -> use encounters whose outcome == FAIL as sources
    """
    raw = defaultdict(lambda: defaultdict(float))

    encounters = sorted(encounters, key=lambda x: x["start_ms"])
    good = [e for e in encounters if is_good_encounter(e)]

    for idx, e in enumerate(good):
        outcome = e.get("outcome", "NEUTRAL")
        # SUCCESS -> WIN, FAILURE -> LOSS (matching user outcome strings)
        if mode == "WIN" and outcome != "SUCCESS":
            continue
        if mode == "LOSS" and outcome != "FAILURE":
            continue

        A = e.get("strategies", {})
        if not A:
            continue

        for step in range(1, next_k + 1):
            if idx + step >= len(good):
                break
            nxt = good[idx + step]
            dt = max(0, nxt["start_ms"] - e["start_ms"])
            d = decay(dt, tau_ms=tau_ms)

            B = nxt.get("strategies", {})
            if not B:
                continue

            # contribute all pairwise strategy transitions
            for sa, wa in A.items():
                if sa not in NODES: 
                    continue
                if wa <= 0: 
                    continue
                for sb, wb in B.items():
                    if sb not in NODES: 
                        continue
                    if wb <= 0:
                        continue
                    raw[sa][sb] += wa * wb * d

    return raw

def smooth_and_normalize(raw, alpha=0.5):
    """
    returns out_probs[A][B] = P(B|A)
    """
    out_probs = {}
    V = NODES[:]
    Vn = len(V)

    for a in V:
        row = raw.get(a, {})
        denom = sum(row.values()) + alpha * Vn
        out_probs[a] = {}
        for b in V:
            out_probs[a][b] = (row.get(b, 0.0) + alpha) / denom

    return out_probs

def export_edges_from_probs(out_probs, min_p=0.02):
    edges = []
    for a, row in out_probs.items():
        for b, p in row.items():
            if p >= min_p:
                edges.append({"from": a, "to": b, "weight": round(p, 6)})
    return edges

def pagerank(out_probs, d=0.85, iters=50):
    V = list(out_probs.keys())
    n = len(V)
    pr = {v: 1.0/n for v in V}

    for _ in range(iters):
        new = {v: (1-d)/n for v in V}
        for a in V:
            for b, p in out_probs[a].items():
                new[b] += d * pr[a] * p
        pr = new
    return pr

def ablate_node(out_probs, node):
    V = list(out_probs.keys())
    n = len(V)

    # deep copy
    P = {a: dict(out_probs[a]) for a in V}

    # remove outgoing
    for b in V:
        P[node][b] = 1.0/n

    # remove incoming
    for a in V:
        P[a][node] = 1.0/n

    # renormalize each row
    for a in V:
        s = sum(P[a].values())
        if s > 0:
            for b in V:
                P[a][b] /= s
        else:
            for b in V:
                P[a][b] = 1.0/n

    return P

def conditional_reach(out_probs, banned_node, targets):
    V = list(out_probs.keys())
    P = {a: dict(out_probs[a]) for a in V}

    # hard-remove banned_node
    for a in V:
        P[a][banned_node] = 0.0
        P[banned_node][a] = 0.0

    # renormalize
    for a in V:
        s = sum(P[a].values())
        if s > 0:
            for b in V:
                P[a][b] /= s

    pr = pagerank(P)
    return sum(pr[t] for t in targets)

def ablate_edge(out_probs, from_node, to_node):
    V = list(out_probs.keys())
    P = {a: dict(out_probs[a]) for a in V}

    # remove edge
    P[from_node][to_node] = 0.0

    # renormalize row
    s = sum(P[from_node].values())
    if s > 0:
        for b in V:
            P[from_node][b] /= s
    else:
        for b in V:
            P[from_node][b] = 1.0/len(V)

    return P

COACH_ACTIONS = {
  "RIVER_CONTROL": [
    "Do not 50/50 river objectives; cross-map or arrive first with vision.",
    "Force them to show on side lanes before committing to river.",
    "Draft/plan for river vision denial + disengage when they control chokepoints."
  ],
  "PICK_ORIENTED": [
    "Avoid facechecks; trade vision slowly and move in pairs.",
    "Draft anti-pick tools (disengage, spell shields, cleanses) and protect supports.",
    "Delay rotations: don’t answer pressure with isolated paths through fog."
  ],
  "BOT_PRESSURE": [
    "Stabilize bot wave states early; avoid giving free turret plates.",
    "Match bot roams with controlled timing; don’t overreact to pressure.",
  ],
  "TOP_PRESSURE": [
    "Track top wave and jungle timing; don’t give isolated top deaths into plates.",
  ],
  "MID_TEMPO": [
    "Keep mid priority stable; prevent mid from becoming a free corridor to river.",
  ],
  "OBJECTIVE_STACKING": [
    "Contest earlier, not at spawn; deny setup windows, not just the objective.",
  ],
  "TEAMFIGHT_COMMIT": [
    "Force split fights; don’t give 5v5 when their commit windows are strongest.",
  ]
}

if __name__ == "__main__":
    encounters = load_json("encounters_step2_labeled.json")

    win_raw = build_raw_graph(encounters, mode="WIN")
    loss_raw = build_raw_graph(encounters, mode="LOSS")

    win_probs = smooth_and_normalize(win_raw, alpha=0.5)
    loss_probs = smooth_and_normalize(loss_raw, alpha=0.5)

    win_graph = {
        "nodes": NODES,
        "edges": export_edges_from_probs(win_probs, min_p=0.03),
        "out_probs": win_probs
    }
    loss_graph = {
        "nodes": NODES,
        "edges": export_edges_from_probs(loss_probs, min_p=0.03),
        "out_probs": loss_probs
    }

    with open("graph_win.json", "w", encoding="utf-8") as f:
        json.dump(win_graph, f, indent=2)
    with open("graph_loss.json", "w", encoding="utf-8") as f:
        json.dump(loss_graph, f, indent=2)

    print("WIN edges:", len(win_graph["edges"]))
    print("LOSS edges:", len(loss_graph["edges"]))
    
    # Sort win edges by weight
    sorted_win_edges = sorted(win_graph["edges"], key=lambda x: x["weight"], reverse=True)
    print("\nTop 10 WIN edges (by probability):")
    for e in sorted_win_edges[:10]:
        print(f" {e['from']} -> {e['to']}: {e['weight']}")

    # Step 5 & 6 (and 7, 8, 9, 10)
    win_pr = pagerank(win_probs)
    baseline = sum(win_pr[t] for t in TARGETS)

    print("\n--- STEP 5 & 7: Node Lynchpins (Global & Conditional) ---")
    node_impacts = []
    for node in NODES:
        # Global ablation
        P_global = ablate_node(win_probs, node)
        pr_global = pagerank(P_global)
        score_global = sum(pr_global[t] for t in TARGETS)
        impact_global = baseline - score_global
        
        # Conditional reach (Step 7)
        score_cond = conditional_reach(win_probs, node, TARGETS)
        
        node_impacts.append({
            "node": node,
            "impact": impact_global,
            "cond_reach": score_cond
        })

    node_impacts.sort(key=lambda x: x["impact"], reverse=True)
    for res in node_impacts[:5]:
        status = "STRUCTURAL" if res["cond_reach"] < 0.05 else "PREFERENCE"
        print(f" {res['node']}: Global Impact {round(res['impact'], 6)}, Cond Reach {round(res['cond_reach'], 6)} -> {status}")

    print("\n--- STEP 8: Edge Lynchpins ---")
    edge_impacts = []
    for edge in win_graph["edges"]:
        P_edge = ablate_edge(win_probs, edge["from"], edge["to"])
        pr_edge = pagerank(P_edge)
        score_edge = sum(pr_edge[t] for t in TARGETS)
        edge_impacts.append({
            "from": edge["from"],
            "to": edge["to"],
            "impact": baseline - score_edge
        })

    edge_impacts.sort(key=lambda x: x["impact"], reverse=True)
    for res in edge_impacts[:5]:
        print(f" {res['from']} -> {res['to']}: Impact {round(res['impact'], 6)}")

    print("\n--- STEP 9: Failure Graph Contrast (Delta P) ---")
    deltas = []
    for a in NODES:
        for b in NODES:
            dp = win_probs[a][b] - loss_probs[a][b]
            deltas.append({"from": a, "to": b, "dp": dp})
    
    deltas.sort(key=lambda x: x["dp"], reverse=True)
    print(" Top Win-Fragile Edges (Strong in Win, Weak in Loss):")
    for d in deltas[:5]:
        print(f"  {d['from']} -> {d['to']}: Delta P {round(d['dp'], 4)}")

    print("\n--- STEP 10: Confidence Bands (Bootstrapping 50x) ---")
    boot_counts = defaultdict(int)
    num_boots = 50
    good_encounters = [e for e in encounters if is_good_encounter(e)]
    
    for _ in range(num_boots):
        sample = random.choices(good_encounters, k=len(good_encounters))
        b_win_raw = build_raw_graph(sample, mode="WIN")
        b_win_probs = smooth_and_normalize(b_win_raw, alpha=0.5)
        b_win_pr = pagerank(b_win_probs)
        b_baseline = sum(b_win_pr[t] for t in TARGETS)
        
        b_impacts = []
        for node in NODES:
            bP2 = ablate_node(b_win_probs, node)
            bpr2 = pagerank(bP2)
            bscore2 = sum(bpr2[t] for t in TARGETS)
            b_impacts.append((node, b_baseline - bscore2))
        
        b_impacts.sort(key=lambda x: x[1], reverse=True)
        top_node = b_impacts[0][0]
        boot_counts[top_node] += 1
    
    print(" Lynchpin Confidence:")
    for node, count in sorted(boot_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node}: {round(count/num_boots * 100, 1)}% confident")

    # Final Strategy Report Export
    top2 = [res["node"] for res in node_impacts[:2]]
    report = {
        "lynchpins": node_impacts,
        "edge_lynchpins": edge_impacts[:10],
        "win_fragile_edges": deltas[:10],
        "confidence": {node: round(count/num_boots * 100, 1) for node, count in boot_counts.items()},
        "break_strategy": {
            node: COACH_ACTIONS.get(node, [])
            for node in top2
        }
    }
    with open("strategy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nFinal analysis saved to strategy_report.json")
