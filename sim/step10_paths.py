import json
from collections import Counter
from sim.step8_montecarlo import run_mc, rollout
from utils.graph_io import load_graph
from sim.step7_state import SimState, default_starters, default_targets

def analyze_stalls(graph_path, deny_nodes=None, n_runs=20000, seed=7):
    import random
    random.seed(seed)
    nodes, out_probs = load_graph(graph_path)
    state = SimState(disabled=set(deny_nodes or []), damp={})
    starters = default_starters()
    targets = set(default_targets())
    
    stalls = Counter()
    success = 0
    for _ in range(n_runs):
        r = rollout(nodes, out_probs, state, starters, targets)
        if r["success"]:
            success += 1
        elif r["reason"] == "tempo_stall":
            stalls[r["stall_node"]] += 1
            
    print(f"\nAnalysis for denying {deny_nodes}:")
    print(f"Success Rate: {success/n_runs:.4f}")
    total_stalls = sum(stalls.values())
    print(f"Total tempo_stalls: {total_stalls}")
    for node, count in stalls.most_common(5):
        pct = (count / total_stalls) * 100 if total_stalls > 0 else 0
        print(f"  Stall at {node}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    # Baseline
    analyze_stalls("graph_win.json", deny_nodes=[])
    # Deny TEAMFIGHT_COMMIT (#1 Deny)
    analyze_stalls("graph_win.json", deny_nodes=["TEAMFIGHT_COMMIT"])
    # Deny OBJECTIVE_STACKING (#2 Deny)
    analyze_stalls("graph_win.json", deny_nodes=["OBJECTIVE_STACKING"])
