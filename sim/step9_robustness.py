import json
from utils.graph_io import load_graph
from sim.step8_montecarlo import run_mc
from sim.step7_state import default_targets

DENY_SET = [
    "TEAMFIGHT_COMMIT",
    "TOP_PRESSURE",
    "RIVER_CONTROL",
    "PICK_ORIENTED",
    "BOT_PRESSURE",
    "MID_TEMPO",
    "OBJECTIVE_STACKING",
]

if __name__ == "__main__":
    baseline = run_mc("graph_win.json", n_runs=20000, deny_nodes=[], seed=7)
    base_p = baseline["success_rate"]

    rows = []
    for node in DENY_SET:
        res = run_mc("graph_win.json", n_runs=20000, deny_nodes=[node], seed=7)
        p = res["success_rate"]
        robustness = (p / base_p) if base_p > 0 else 0.0
        rows.append({
            "deny": node,
            "success_rate": p,
            "robustness": robustness,
            "top_fail": res["failure_reasons"].most_common(2),
        })

    rows.sort(key=lambda x: x["robustness"])  # lowest robustness = best deny
    out = {"baseline": baseline, "deny_results": rows}

    print("Baseline:", base_p)
    print("Top denies (lowest robustness):")
    for r in rows[:5]:
        print(r["deny"], "robustness=", round(r["robustness"], 4), "p=", round(r["success_rate"], 4))

    with open("out/robustness.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)
