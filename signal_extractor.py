from typing import List, Tuple, Optional
from signal_event import SignalEvent
from time_utils import iso_to_ms

class SignalExtractor:

    def extract(self, json_line: dict) -> List[SignalEvent]:
        series_id = json_line.get("seriesId")
        occurred_at = json_line.get("occurredAt")
        base_ts = iso_to_ms(occurred_at)

        events = json_line.get("events", [])
        signals = []

        for e in events:
            raw_type = e.get("type", "").lower()
            event_id = e.get("id", f"{raw_type}_{base_ts}")

            game_id = (
                json_line.get("seriesStateDelta", {}).get("id")
                or json_line.get("seriesState", {}).get("id")
            )

            # Fallback: some events nest the game state inside another list/object
            if not game_id:
                for key in ["seriesStateDelta", "seriesState"]:
                    gs = json_line.get(key, {})
                    if "games" in gs and isinstance(gs["games"], list) and len(gs["games"]) > 0:
                        game_id = gs["games"][0].get("id")
                        if game_id: break

            actor = e.get("actor", {})
            target = e.get("target", {})

            actor_player_id = actor.get("id")
            actor_team_id = (
                actor.get("state", {}).get("id")
                or actor.get("stateDelta", {}).get("id")
            )

            target_player_id = target.get("id")
            target_team_id = (
                target.get("state", {}).get("id")
                or target.get("stateDelta", {}).get("id")
            )

            x, y = self._extract_position(e)
            sub_type = self._extract_subtype(e)

            event_type = self._classify_event(raw_type, sub_type)
            if not event_type:
                continue

            signals.append(
                SignalEvent(
                    id=event_id,
                    game_id=game_id,
                    series_id=series_id,
                    timestamp_ms=base_ts,
                    x=x, y=y,
                    team_id=actor_team_id,
                    opponent_team_id=target_team_id,
                    actor_player_id=actor_player_id,
                    target_player_id=target_player_id,
                    event_type=event_type,
                    sub_type=sub_type,
                    payload={"raw_type": raw_type}
                )
            )

        return signals

    # ----------------------

    def _extract_position(self, e) -> Tuple[Optional[float], Optional[float]]:
        # 1. Direct position
        paths = [
            e.get("position"),
            e.get("location"),
            e.get("actor", {}).get("state", {}).get("position"),
            e.get("actor", {}).get("stateDelta", {}).get("position"),
            e.get("target", {}).get("state", {}).get("position"),
            e.get("target", {}).get("stateDelta", {}).get("position"),
        ]

        for p in paths:
            if isinstance(p, dict) and "x" in p and "y" in p:
                return p["x"], p["y"]

        # 2. Deep search in actor/target state for position
        # (Needed because some events nest position inside player/team lists)
        for entity in [e.get("actor", {}), e.get("target", {})]:
            for state_key in ["state", "stateDelta"]:
                state = entity.get(state_key, {})
                if not isinstance(state, dict): continue
                
                # Check direct position in state
                if "position" in state:
                    p = state["position"]
                    if isinstance(p, dict) and "x" in p and "y" in p:
                        return p["x"], p["y"]
                
                # Check players/teams lists for matching IDs
                actor_id = entity.get("id")
                for list_key in ["players", "teams"]:
                    if list_key in state and isinstance(state[list_key], list):
                        for item in state[list_key]:
                            if item.get("id") == actor_id and "position" in item:
                                p = item["position"]
                                if isinstance(p, dict) and "x" in p and "y" in p:
                                    return p["x"], p["y"]

        # 3. Objective fallback
        name = (
            e.get("target", {})
             .get("state", {})
             .get("name", "")
             .lower()
        )

        OBJECTIVE_POSITIONS = {
            "chemtechdrake": (9850, 4300),
            "infernaldrake": (9850, 4300),
            "clouddrake": (9850, 4300),
            "mountaindrake": (9850, 4300),
            "elderdrake": (9850, 4300),
            "riftherald": (4500, 9800),
            "baronnashor": (4500, 9800),
        }

        for key, pos in OBJECTIVE_POSITIONS.items():
            if key in name:
                return pos

        return None, None

    def _extract_subtype(self, e) -> Optional[str]:
        for key in ["subType", "action", "spell", "ability"]:
            if key in e:
                return str(e[key]).upper()
        if "target" in e:
            return e["target"].get("state", {}).get("name")
        return None

    def _classify_event(self, raw_type: str, sub: Optional[str]) -> Optional[str]:
        s = (sub or "").lower()

        if "kill" in raw_type:
            return "KILL"
        if any(o in raw_type for o in ["dragon", "baron", "herald"]):
            return "OBJECTIVE"
        if any(t in raw_type for t in ["tower", "inhib", "plate", "nexus"]):
            return "STRUCTURE"
        if s in {"flash", "teleport", "ignite", "exhaust", "heal", "ghost"}:
            return "SPELL"
        if "ward" in raw_type or "ward" in s:
            return "WARD"

        return None
