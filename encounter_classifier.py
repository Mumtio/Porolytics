from labeled_encounter import LabeledEncounter
from map_zones import get_lol_location
from participant_utils import classify_scale

class EncounterClassifier:

    def classify(self, encounter, prev_encounter=None, next_encounter=None) -> LabeledEncounter:
        duration = encounter.end_ms - encounter.start_ms
        scale = classify_scale(encounter.players)
        
        # Determine zone: numeric centroid takes priority, then fallback to inferred_zone
        zone = "UNKNOWN"
        if encounter.centroid_x is not None and encounter.centroid_y is not None:
            zone = get_lol_location(encounter.centroid_x, encounter.centroid_y)
        elif encounter.inferred_zone:
            zone = encounter.inferred_zone

        kills = encounter.event_counts.get("KILL", 0)
        objectives = encounter.event_counts.get("OBJECTIVE", 0)
        spells = encounter.event_counts.get("SPELL", 0)
        structures = encounter.event_counts.get("STRUCTURE", 0)

        is_structure_only = set(encounter.event_counts.keys()) == {"STRUCTURE"}
        encounter_type = self._infer_type(scale, kills, objectives, encounter)
        intent = self._infer_intent(encounter_type, zone, objectives, spells)
        decisiveness = self._score_decisiveness(kills, objectives, duration, encounter)
        outcome = self._infer_outcome(decisiveness)

        # Tier-2: Probabilistic Location Inference with smoothing
        location_guess = self._infer_probabilistic_location(encounter, encounter_type, scale, duration, prev_encounter, next_encounter)
        
        # Apply Threshold Rule for soft tagging if zone is still UNKNOWN
        if zone == "UNKNOWN":
            best_guess = max(location_guess.items(), key=lambda x: x[1])
            if best_guess[1] >= 0.6:
                zone = best_guess[0]
            else:
                zone = "AMBIGUOUS"

        tags = [zone, scale]
        if objectives > 0:
            tags.append("OBJECTIVE_PLAY")
        if spells >= 2:
            tags.append("SPELL_COMMIT")
            
        # Numbers advantage calculation (Refined)
        team_list = [t for t in encounter.players_by_team.keys() if t != "UNKNOWN_TEAM"]
        numbers_adv = 0
        multi_team_encounter = len(team_list) > 2
        numbers_adv_confidence = "HIGH" if "UNKNOWN_TEAM" not in encounter.players_by_team else "LOW"
        
        if len(team_list) == 2:
            counts = [len(encounter.players_by_team[t]) for t in team_list]
            numbers_adv = counts[0] - counts[1]
        elif len(team_list) > 2:
            numbers_adv = 0

        commitment_proxy = round(decisiveness * (kills + objectives + structures), 2)
        
        # Strategy Activation Layer 1
        strategies = self._extract_strategies_v1(encounter, encounter_type, intent, zone, location_guess, commitment_proxy)

        return LabeledEncounter(
            encounter_id=encounter.encounter_id,
            game_id=encounter.game_id,
            series_id=encounter.series_id,
            start_ms=encounter.start_ms,
            end_ms=encounter.end_ms,
            duration_ms=duration,
            centroid_x=encounter.centroid_x,
            centroid_y=encounter.centroid_y,
            teams=encounter.teams,
            players=encounter.players,
            players_by_team=encounter.players_by_team,
            event_counts=encounter.event_counts,
            encounter_type=encounter_type,
            intent=intent,
            decisiveness=round(decisiveness, 2),
            outcome=outcome,
            tags=tags,
            location_guess=location_guess,
            quality=encounter.quality,
            is_contested=len(encounter.teams) > 1,
            is_atomic=duration == 0,
            is_structure_only=is_structure_only,
            numbers_adv=numbers_adv,
            numbers_adv_confidence=numbers_adv_confidence,
            multi_team_encounter=multi_team_encounter,
            commitment_proxy=commitment_proxy,
            strategies=strategies
        )

    def _extract_strategies_v1(self, encounter, etype, intent, zone, location_guess, commitment) -> dict:
        strats = {
            "BOT_PRESSURE": 0.0,
            "TOP_PRESSURE": 0.0,
            "MID_TEMPO": 0.0,
            "RIVER_CONTROL": 0.0,
            "OBJECTIVE_STACKING": 0.0,
            "PICK_ORIENTED": 0.0,
            "TEAMFIGHT_COMMIT": 0.0
        }
        
        # Spatial Weights
        strats["BOT_PRESSURE"] += location_guess.get("BOT_LANE", 0) * 0.8
        strats["TOP_PRESSURE"] += location_guess.get("TOP_LANE", 0) * 0.8
        strats["MID_TEMPO"] += location_guess.get("MID_LANE", 0) * 0.8
        strats["RIVER_CONTROL"] += location_guess.get("RIVER", 0) * 0.7
        
        # Intent & Type Weights
        if etype == "PRESSURE":
            strats["MID_TEMPO"] += 0.2 if zone == "MID_LANE" else 0.1
            if zone == "BOT_LANE": strats["BOT_PRESSURE"] += 0.3
            if zone == "TOP_LANE": strats["TOP_PRESSURE"] += 0.3
            
        if etype == "OBJECTIVE":
            strats["OBJECTIVE_STACKING"] += 0.6
            strats["RIVER_CONTROL"] += 0.3
            
        if intent == "PICK":
            strats["PICK_ORIENTED"] += 0.7
            
        if etype == "TEAMFIGHT":
            strats["TEAMFIGHT_COMMIT"] += 0.8
            
        # Commitment multiplier
        if commitment > 2.0:
            for k in strats:
                strats[k] *= 1.2
                
        # Normalize/Clean
        return {k: round(v, 2) for k, v in strats.items() if v > 0.1}

    # ----------------------------

    def _infer_probabilistic_location(self, encounter, etype, scale, duration, prev_enc=None, next_enc=None) -> dict:
        scores = {"RIVER": 0.0, "MID_LANE": 0.0, "BOT_LANE": 0.0, "TOP_LANE": 0.0, "JUNGLE": 0.0}
        
        # 1. Direct Evidence Prior
        if encounter.inferred_zone and encounter.inferred_zone in scores:
            scores[encounter.inferred_zone] += 0.8
        
        # 2. Encounter Type Votes
        if etype == "TEAMFIGHT":
            scores["RIVER"] += 0.3
            scores["MID_LANE"] += 0.2
            scores["JUNGLE"] += 0.2
        elif etype == "SKIRMISH":
            scores["JUNGLE"] += 0.3
            scores["MID_LANE"] += 0.1
            scores["RIVER"] += 0.1
        
        # 3. Objective Votes
        if encounter.event_counts.get("OBJECTIVE", 0) > 0:
            scores["RIVER"] += 0.6
            
        # 3. Structure Votes
        if encounter.event_counts.get("STRUCTURE", 0) > 0:
            # If we don't have a direct lane prior, distribute
            if not encounter.inferred_zone or encounter.inferred_zone not in scores:
                scores["MID_LANE"] += 0.2
                scores["BOT_LANE"] += 0.2
                scores["TOP_LANE"] += 0.2
            else:
                scores[encounter.inferred_zone] += 0.4
            
        # 5. Scale Votes
        if len(encounter.players) >= 5:
            scores["RIVER"] += 0.2
        elif len(encounter.players) >= 3:
            scores["JUNGLE"] += 0.1
            
        # 6. Duration Votes
        if duration > 15000:
            scores["RIVER"] += 0.1
            scores["JUNGLE"] += 0.2

        # 7. Neighbor Smoothing (Markov-ish)
        if prev_enc and hasattr(prev_enc, 'location_guess') and prev_enc.location_guess:
            for k, v in prev_enc.location_guess.items():
                if k in scores:
                    scores[k] += v * 0.2
        if next_enc and hasattr(next_enc, 'inferred_zone') and next_enc.inferred_zone:
            if next_enc.inferred_zone in scores:
                scores[next_enc.inferred_zone] += 0.3

        # Normalize to probabilities
        total = sum(scores.values())
        if total > 0:
            return {k: round(v / total, 2) for k, v in scores.items()}
        
        # Default fallback: Uniform
        return {k: 0.2 for k in scores.keys()}

    def _infer_type(self, scale, kills, objectives, encounter):
        is_structure_only = set(encounter.event_counts.keys()) == {"STRUCTURE"}
        if objectives > 0:
            return "OBJECTIVE"
        if kills >= 2 and scale == "TEAMFIGHT" and not is_structure_only:
            return "TEAMFIGHT"
        if kills >= 1:
            return "SKIRMISH"
        if (kills == 0 and encounter.event_counts.get("STRUCTURE", 0) > 0) or is_structure_only:
            return "PRESSURE"
        if kills == 0:
            return "SETUP"
        return "UNKNOWN"

    def _infer_intent(self, etype, zone, objectives, spells):
        if etype == "OBJECTIVE":
            return "CONTEST" if spells > 0 else "SECURE"
        if etype == "TEAMFIGHT":
            return "COMMIT"
        if etype == "SKIRMISH":
            return "PICK"
        if etype == "PRESSURE":
            return "LANE_ADVANCE"
        if etype == "SETUP":
            return "SETUP"
        return "UNKNOWN"

    def _score_decisiveness(self, kills, objectives, duration, encounter):
        score = 0.0
        score += min(kills * 0.25, 0.5)
        score += min(objectives * 0.4, 0.6)
        plates = encounter.event_counts.get("STRUCTURE", 0)
        score += min(plates * 0.15, 0.4)
        score += min(duration / 30000, 0.2)
        return min(score, 1.0)

    def _infer_outcome(self, decisiveness):
        if decisiveness >= 0.6:
            return "SUCCESS"
        if decisiveness >= 0.3:
            return "NEUTRAL"
        return "FAILURE"
