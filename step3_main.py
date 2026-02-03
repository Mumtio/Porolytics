import json
from flow_generator import FlowGenerator
from labeled_encounter import LabeledEncounter

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

INPUT = "encounters_step2_labeled.json"
OUTPUT = "encounters_step3_flows.json"

generator = FlowGenerator()
labeled_encounters = []

try:
    with open(INPUT, "r") as f:
        raw = json.load(f)
        for e in raw:
            # Reconstruct LabeledEncounter object
            # Note: need to handle players/teams being lists in JSON
            e['teams'] = set(e['teams'])
            e['players'] = set(e['players'])
            pbt = {}
            for tid, pset in e.get('players_by_team', {}).items():
                pbt[tid] = set(pset)
            e['players_by_team'] = pbt
            le = LabeledEncounter(**e)
            labeled_encounters.append(le)

    transitions = generator.generate_flows(labeled_encounters)

    with open(OUTPUT, "w") as f:
        json.dump([t.__dict__ for t in transitions], f, indent=2, cls=SetEncoder)

    print(f"Generated flows: {len(transitions)}")
    print(f"Successfully saved to {OUTPUT}")
except FileNotFoundError:
    print(f"Error: {INPUT} not found. Please run Step 2 (step2_main.py) first.")
except Exception as ex:
    print(f"An error occurred: {ex}")
