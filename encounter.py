from dataclasses import dataclass
from typing import List, Set, Dict, Optional

@dataclass
class Encounter:
    encounter_id: int
    game_id: str
    series_id: str

    start_ms: int
    end_ms: int

    centroid_x: Optional[float]
    centroid_y: Optional[float]

    teams: Set[str]
    players: Set[str]
    players_by_team: Dict[str, Set[str]]

    event_counts: Dict[str, int]
    event_ids: List[str]
    inferred_zone: Optional[str] = None
    quality: str = "MED" # HIGH, MED, LOW
