import json
from sim.step8_montecarlo import run_mc

if __name__ == "__main__":
    loss_base = run_mc("graph_loss.json", n_runs=20000, deny_nodes=[], seed=7)
    print("LOSS-graph success_rate (reaching terminals):", loss_base["success_rate"])
    print("Top failure reasons:", loss_base["failure_reasons"])

    with open("out/mc_loss_baseline.json", "w", encoding="utf-8") as f:
        json.dump(loss_base, f, indent=2, default=str)
