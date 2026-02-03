from collections import defaultdict
from flow_transition import FlowTransition

class FlowGenerator:
    def __init__(self):
        pass

    def generate_flows(self, labeled_encounters: list) -> list:
        # Group by game
        by_game = defaultdict(list)
        for e in labeled_encounters:
            by_game[e.game_id].append(e)
            
        transitions = []
        
        for game_id, encounters in by_game.items():
            # Ensure chronological order
            encounters.sort(key=lambda x: x.start_ms)
            
            for i in range(len(encounters) - 1):
                prev = encounters[i]
                curr = encounters[i+1]
                
                # We only link them if they are reasonably close in time (e.g., within 2 minutes)
                # or if they share players
                time_gap = curr.start_ms - prev.end_ms
                common_players = set(prev.players).intersection(set(curr.players))
                
                if time_gap > 120_000 and not common_players:
                    continue
                
                type_shift = f"{prev.encounter_type} -> {curr.encounter_type}"
                
                prev_zone = prev.tags[0] if prev.tags else "UNKNOWN"
                curr_zone = curr.tags[0] if curr.tags else "UNKNOWN"
                location_shift = f"{prev_zone} -> {curr_zone}"
                
                new_players = set(curr.players) - set(prev.players)
                dropped_players = set(prev.players) - set(curr.players)
                
                # Logic for escalation
                escalation_levels = {"SETUP": 0, "PRESSURE": 1, "SKIRMISH": 2, "OBJECTIVE": 3, "TEAMFIGHT": 4}
                p_level = escalation_levels.get(prev.encounter_type, 0)
                c_level = escalation_levels.get(curr.encounter_type, 0)
                is_escalation = c_level > p_level
                
                # Logic for rotation
                is_rotation = prev_zone != curr_zone and prev_zone != "UNKNOWN" and curr_zone != "UNKNOWN"
                
                transitions.append(FlowTransition(
                    from_encounter_id=prev.encounter_id,
                    to_encounter_id=curr.encounter_id,
                    game_id=game_id,
                    time_gap_ms=time_gap,
                    type_shift=type_shift,
                    location_shift=location_shift,
                    common_players=common_players,
                    new_players=new_players,
                    dropped_players=dropped_players,
                    is_escalation=is_escalation,
                    is_rotation=is_rotation
                ))
                
        return transitions
