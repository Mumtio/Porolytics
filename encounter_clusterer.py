from collections import defaultdict, deque
from typing import List
from geo import distance
from encounter import Encounter

# Parameters
TIME_EPS_MS = 12_000
DIST_EPS = 1800
MAX_WINDOW_MS = 30_000
MIN_EVENTS = 2

class EncounterClusterer:

    def cluster(self, signals: List, config=None) -> List[Encounter]:
        # Group by game first (CRITICAL)
        by_game = defaultdict(list)
        for s in signals:
            by_game[s.game_id].append(s)

        encounters = []
        encounter_id = 0

        for game_id, game_signals in by_game.items():
            game_signals.sort(key=lambda s: s.timestamp_ms)

            active = deque()
            parent = list(range(len(game_signals)))

            def find(i):
                while parent[i] != i:
                    parent[i] = parent[parent[i]]
                    i = parent[i]
                return i

            def union(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra

            for i, cur in enumerate(game_signals):
                while active and cur.timestamp_ms - game_signals[active[0]].timestamp_ms > MAX_WINDOW_MS:
                    active.popleft()

                for j in active:
                    prev = game_signals[j]

                    if abs(cur.timestamp_ms - prev.timestamp_ms) > TIME_EPS_MS:
                        continue

                    d = distance(cur.x, cur.y, prev.x, prev.y)
                    if d is not None and d > DIST_EPS:
                        continue

                    union(i, j)

                active.append(i)

            clusters = defaultdict(list)
            for i in range(len(game_signals)):
                clusters[find(i)].append(game_signals[i])

            for events in clusters.values():
                if len(events) < MIN_EVENTS:
                    continue

                start = min(e.timestamp_ms for e in events)
                end = max(e.timestamp_ms for e in events)
                duration = end - start

                pos = [(e.x, e.y) for e in events if e.x is not None]

                def infer_location_from_events(events):
                    for e in events:
                        raw = str(e.payload.get("raw_type", "")).lower()
                        sub = str(e.sub_type or "").lower()
                        event_id = str(e.id).lower()

                        if any(k in s for s in [raw, sub, event_id] for k in ["mid"]):
                            return "MID_LANE"
                        if any(k in s for s in [raw, sub, event_id] for k in ["bot"]):
                            return "BOT_LANE"
                        if any(k in s for s in [raw, sub, event_id] for k in ["top"]):
                            return "TOP_LANE"

                        if any(k in raw or k in sub or k in event_id for k in ["dragon", "drake", "chemtech", "infernal", "mountain", "ocean", "cloud", "elder"]):
                            return "RIVER"
                        if any(k in raw or k in sub or k in event_id for k in ["herald", "baron", "nashor", "void"]):
                            return "RIVER"

                    return "UNKNOWN"

                # Objective mapping for centroids
                OBJECTIVE_POSITIONS = {
                    "RIVER": (7500, 7500),
                    "MID_LANE": (7500, 7500),
                    "TOP_LANE": (3000, 12000),
                    "BOT_LANE": (12000, 3000),
                }

                if pos:
                    cx = sum(p[0] for p in pos) / len(pos)
                    cy = sum(p[1] for p in pos) / len(pos)
                    inferred_zone = None
                else:
                    inferred_zone = infer_location_from_events(events)
                    cx, cy = None, None

                def is_real_player(pid):
                    if pid is None:
                        return False
                    return pid.isdigit()

                teams = {e.team_id for e in events if e.team_id}
                players = {
                    p for e in events
                    for p in (e.actor_player_id, e.target_player_id)
                    if is_real_player(p)
                }

                # Players by team
                p_by_team = defaultdict(set)
                for e in events:
                    if is_real_player(e.actor_player_id) and e.team_id:
                        p_by_team[e.team_id].add(e.actor_player_id)
                    if is_real_player(e.target_player_id) and e.opponent_team_id:
                        p_by_team[e.opponent_team_id].add(e.target_player_id)

                # Filter p_by_team to only include teams present in 'teams' set
                p_by_team = {t: pset for t, pset in p_by_team.items() if t in teams}

                # Ensure all players in 'players' set are in 'p_by_team'
                for p in players:
                    found = False
                    for t_players in p_by_team.values():
                        if p in t_players:
                            found = True
                            break
                    if not found:
                        if "UNKNOWN_TEAM" not in p_by_team:
                            p_by_team["UNKNOWN_TEAM"] = set()
                        p_by_team["UNKNOWN_TEAM"].add(p)

                counts = defaultdict(int)
                for e in events:
                    counts[e.event_type] += 1

                # Quality / Validity Gates
                quality = "MED"
                is_structure_only = set(counts.keys()) == {"STRUCTURE"}
                
                if duration == 0 and is_structure_only:
                    quality = "LOW"
                elif len(teams) <= 1 and counts.get("OBJECTIVE", 0) == 0:
                    quality = "LOW"
                elif len(players) <= 1:
                    quality = "LOW"
                elif counts.get("KILL", 0) > 0 or counts.get("OBJECTIVE", 0) > 0:
                    quality = "HIGH"

                encounters.append(
                    Encounter(
                        encounter_id=encounter_id,
                        game_id=game_id,
                        series_id=events[0].series_id,
                        start_ms=start,
                        end_ms=end,
                        centroid_x=cx,
                        centroid_y=cy,
                        teams=teams,
                        players=players,
                        players_by_team=dict(p_by_team),
                        event_counts=dict(counts),
                        event_ids=[e.id for e in events],
                        inferred_zone=inferred_zone,
                        quality=quality
                    )
                )
                encounter_id += 1

        # Post-processing: Merge LOW quality structure-only into nearest neighbors
        merged_encounters = []
        by_game_final = defaultdict(list)
        for e in encounters:
            by_game_final[e.game_id].append(e)

        for game_id, game_encs in by_game_final.items():
            game_encs.sort(key=lambda x: x.start_ms)
            
            i = 0
            while i < len(game_encs):
                cur = game_encs[i]
                is_low_structure = (cur.quality == "LOW" and set(cur.event_counts.keys()) == {"STRUCTURE"})
                
                if is_low_structure:
                    # Find nearest HIGH quality neighbor within 15s that shares a team
                    neighbor = None
                    # Search backward
                    for j in range(i-1, -1, -1):
                        prev = game_encs[j]
                        if abs(cur.start_ms - prev.end_ms) < 15_000 and prev.quality == "HIGH":
                            if cur.teams.intersection(prev.teams):
                                neighbor = prev
                                break
                    # Search forward if not found
                    if not neighbor:
                        for j in range(i+1, len(game_encs)):
                            nxt = game_encs[j]
                            if abs(nxt.start_ms - cur.end_ms) < 15_000 and nxt.quality == "HIGH":
                                if cur.teams.intersection(nxt.teams):
                                    neighbor = nxt
                                    break
                    
                    if neighbor:
                        # Merge cur into neighbor
                        neighbor.event_ids.extend(cur.event_ids)
                        for etype, count in cur.event_counts.items():
                            neighbor.event_counts[etype] = neighbor.event_counts.get(etype, 0) + count
                        neighbor.players.update(cur.players)
                        neighbor.teams.update(cur.teams)
                        for tid, pset in cur.players_by_team.items():
                            if tid not in neighbor.players_by_team:
                                neighbor.players_by_team[tid] = set()
                            neighbor.players_by_team[tid].update(pset)
                        neighbor.start_ms = min(neighbor.start_ms, cur.start_ms)
                        neighbor.end_ms = max(neighbor.end_ms, cur.end_ms)
                        i += 1
                        continue
                    else:
                        # Drop LOW atomic structure encounters that couldn't be merged
                        i += 1
                        continue
                
                if cur.quality == "LOW":
                    # Drop other LOW quality encounters
                    i += 1
                    continue

                merged_encounters.append(cur)
                i += 1

        return merged_encounters
