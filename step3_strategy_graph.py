import json
from collections import defaultdict

INPUT = "encounters_step2_labeled.json"
OUTPUT = "strategy_graph_v1.json"

def build_strategy_graph():
    with open(INPUT, "r") as f:
        encounters = json.load(f)
    
    # We only care about HIGH/MED quality encounters
    relevant = [e for e in encounters if e.get("quality") in ["HIGH", "MED"]]
    
    # Group by game
    by_game = defaultdict(list)
    for e in relevant:
        by_game[e.get("game_id")].append(e)
    
    # Strategy nodes and edges
    # Node: strategy_name
    # Edge: (strat_a, strat_b) -> weight
    nodes = set()
    edges = defaultdict(float)
    
    for game_id, game_encs in by_game.items():
        # Sort by time
        game_encs.sort(key=lambda x: x["start_ms"])
        
        for i in range(len(game_encs)):
            current = game_encs[i]
            curr_strats = current.get("strategies", {})
            
            # Record nodes
            for s in curr_strats:
                nodes.add(s)
            
            # Look ahead up to 2 encounters
            look_ahead = game_encs[i+1 : i+3]
            
            for future in look_ahead:
                fut_strats = future.get("strategies", {})
                
                # Weight of edge is determined by the product of strategy weights
                for s_curr, w_curr in curr_strats.items():
                    for s_fut, w_fut in fut_strats.items():
                        edges[(s_curr, s_fut)] += w_curr * w_fut

    # Format for JSON output
    graph = {
        "nodes": list(nodes),
        "edges": [
            {"from": k[0], "to": k[1], "weight": round(v, 2)}
            for k, v in edges.items()
        ]
    }
    
    with open(OUTPUT, "w") as f:
        json.dump(graph, f, indent=2)
    
    print(f"Strategy graph generated with {len(nodes)} nodes and {len(graph['edges'])} edges.")
    print(f"Results saved to {OUTPUT}")

if __name__ == "__main__":
    build_strategy_graph()
