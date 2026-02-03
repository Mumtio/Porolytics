from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class SimState:
    disabled: set[str] = field(default_factory=set)
    # optional: scale some nodes instead of hard-disable
    damp: Dict[str, float] = field(default_factory=dict)  # node -> multiplier in [0,1]

def default_starters():
    # safe default starters for early game. You can tune later.
    return ["BOT_PRESSURE", "TOP_PRESSURE", "PICK_ORIENTED", "MID_TEMPO"]

def default_targets():
    return ["TEAMFIGHT_COMMIT", "OBJECTIVE_STACKING"]
