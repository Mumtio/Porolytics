import json
from encounter_classifier import EncounterClassifier
from encounter import Encounter

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

INPUT = "encounters_step1.json"
OUTPUT = "encounters_step2_labeled.json"

classifier = EncounterClassifier()
labeled = []
labeled_encounters_raw = []

try:
    with open(INPUT, "r") as f:
        raw = json.load(f)
        for e in raw:
            # Reconstruct Encounter object
            e['teams'] = set(e['teams'])
            e['players'] = set(e['players'])
            # Reconstruct players_by_team as dict of sets
            pbt = {}
            for tid, pset in e.get('players_by_team', {}).items():
                pbt[tid] = set(pset)
            e['players_by_team'] = pbt
            encounter = Encounter(**e)
            labeled_encounters_raw.append(encounter)

    # Sort by time for neighbor smoothing
    labeled_encounters_raw.sort(key=lambda x: x.start_ms)

    for i in range(len(labeled_encounters_raw)):
        prev = labeled[i-1] if i > 0 else None
        # Note: next is tricky because it's not labeled yet. 
        # But we can pass the raw next one if we just need its inferred_zone
        nxt = labeled_encounters_raw[i+1] if i < len(labeled_encounters_raw) - 1 else None
        
        labeled.append(classifier.classify(labeled_encounters_raw[i], prev, nxt))

    with open(OUTPUT, "w") as f:
        json.dump([le.__dict__ for le in labeled], f, indent=2, cls=SetEncoder)

    print(f"Labeled encounters: {len(labeled)}")
    print(f"Successfully saved to {OUTPUT}")
except FileNotFoundError:
    print(f"Error: {INPUT} not found. Please run Step 1 (main.py) first.")
except Exception as ex:
    import traceback
    traceback.print_exc()
    print(f"An error occurred: {ex}")
