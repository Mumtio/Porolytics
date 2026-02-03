import json
import zipfile
import os
import glob
from signal_extractor import SignalExtractor
from encounter_clusterer import EncounterClusterer

INPUT_PATTERN = "matches_data/**/*.jsonl.zip"
OUTPUT = "encounters_step1.json"

extractor = SignalExtractor()
clusterer = EncounterClusterer()

def process_file(zip_path):
    all_signals = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            all_signals.extend(extractor.extract(data))
                        except Exception as e:
                            print(f"Error parsing line in {zip_path}: {e}")
    except Exception as e:
        print(f"Error opening zip {zip_path}: {e}")
    return all_signals

print(f"Searching for files matching {INPUT_PATTERN}...")
zip_files = glob.glob(INPUT_PATTERN, recursive=True)
print(f"Found {len(zip_files)} files.")

all_signals = []
for i, zip_file in enumerate(zip_files):
    if (i+1) % 10 == 0 or i == 0:
        print(f"Processing file {i+1}/{len(zip_files)}: {zip_file}")
    all_signals.extend(process_file(zip_file))

print(f"Total signals extracted: {len(all_signals)}")

if not all_signals:
    print("No signals found. Check if the input pattern is correct.")
else:
    print(f"Clustering {len(all_signals)} signals...")
    encounters = clusterer.cluster(all_signals)
    print(f"Encounters detected: {len(encounters)}")

    # Custom encoder for Set objects which are not JSON serializable
    class SetEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return super().default(obj)

    # Sort by time for better merge visualization if needed
    # Note: with multiple games/series, sort by game_id then start_ms
    encounters.sort(key=lambda x: (str(x.game_id), x.start_ms))

    with open(OUTPUT, "w") as f:
        json.dump(
            [e.__dict__ for e in encounters],
            f,
            indent=2,
            cls=SetEncoder
        )
    print(f"Saved encounters to {OUTPUT}")
