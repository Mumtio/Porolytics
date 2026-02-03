from dataclasses import dataclass
from typing import List, Set, Dict, Optional

@dataclass
class FlowTransition:
    from_encounter_id: int
    to_encounter_id: int
    game_id: str
    
    time_gap_ms: int
    
    # State change
    type_shift: str # e.g., "PRESSURE -> OBJECTIVE"
    location_shift: str # e.g., "MID_LANE -> RIVER"
    
    # Participants
    common_players: Set[str]
    new_players: Set[str]
    dropped_players: Set[str]
    
    # Significance
    is_escalation: bool # e.g., SKIRMISH -> TEAMFIGHT
    is_rotation: bool # e.g., TOP_LANE -> BOT_LANE
