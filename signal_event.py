from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class SignalEvent:
    id: str
    game_id: str
    series_id: str
    timestamp_ms: int

    x: Optional[float]
    y: Optional[float]

    team_id: Optional[str]
    opponent_team_id: Optional[str]

    actor_player_id: Optional[str]
    target_player_id: Optional[str]

    event_type: str          # KILL, OBJECTIVE, SPELL, STRUCTURE, WARD
    sub_type: Optional[str]  # FLASH, DRAGON_INFERNAL, TOWER, etc

    payload: Dict
