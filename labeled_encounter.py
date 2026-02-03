from dataclasses import dataclass
from typing import List, Set, Dict, Optional

@dataclass
class LabeledEncounter:
    encounter_id: int
    game_id: str
    series_id: str

    start_ms: int
    end_ms: int
    duration_ms: int

    centroid_x: Optional[float]
    centroid_y: Optional[float]

    teams: Set[str]
    players: Set[str]
    players_by_team: Dict[str, Set[str]]

    event_counts: Dict[str, int]
    
    encounter_type: str
    intent: str
    decisiveness: float
    outcome: str
    tags: List[str]
    location_guess: Optional[Dict[str, float]] = None
    
    quality: str = "MED"
    is_contested: bool = False
    is_atomic: bool = False
    is_structure_only: bool = False
    numbers_adv: int = 0
    numbers_adv_confidence: str = "LOW"
    multi_team_encounter: bool = False
    commitment_proxy: float = 0.0
    strategies: Optional[Dict[str, float]] = None
