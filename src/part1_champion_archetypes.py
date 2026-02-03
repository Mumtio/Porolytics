"""
PART 1: Champion Archetype Mapping
Translate champions into strategic meaning using layered taxonomy
"""
from typing import List, Set, Dict
from enum import Enum


class Archetype(Enum):
    """Strategic archetypes for champions - Layered taxonomy"""
    
    # === LAYER 1: STRATEGIC PLAYSTYLE (Core Identity) ===
    # These define HOW a champion wins fights/games
    
    # Engage & Initiation
    ENGAGE = "ENGAGE"  # Initiates teamfights
    PICK = "PICK"  # Catches isolated targets
    
    # Damage Patterns
    BURST = "BURST"  # High burst damage
    DPS = "DPS"  # Sustained damage
    POKE = "POKE"  # Long-range harass
    
    # Utility & Support
    ENCHANTER = "ENCHANTER"  # Buffs/heals/shields allies
    UTILITY = "UTILITY"  # Provides non-damage value (CC, vision, etc)
    
    # Positioning & Threat
    FRONTLINE = "FRONTLINE"  # Absorbs damage, front-to-back
    BACKLINE_THREAT = "BACKLINE_THREAT"  # Dives/threatens enemy carries
    ZONE_CONTROL = "ZONE_CONTROL"  # Controls space/areas
    
    # Macro Patterns
    SPLIT_PUSH = "SPLIT_PUSH"  # Excels at side lane pressure
    ROAM = "ROAM"  # High map mobility/roaming
    OBJECTIVE_CONTROL = "OBJECTIVE_CONTROL"  # Secures dragons/barons
    
    # === LAYER 2: GAME PHASE BIAS ===
    EARLY_GAME = "EARLY_GAME"  # Strong levels 1-6
    MID_GAME = "MID_GAME"  # Strong levels 7-13
    LATE_GAME = "LATE_GAME"  # Strong levels 14+
    SCALING = "SCALING"  # Needs time/items to come online
    
    # === LAYER 3: TEAMFIGHT ROLE ===
    TEAMFIGHT_ULTIMATE = "TEAMFIGHT_ULTIMATE"  # Game-changing teamfight ult
    SKIRMISHER = "SKIRMISHER"  # Excels in small fights (2v2, 3v3)
    DUELIST = "DUELIST"  # Excels in 1v1s
    
    # === LAYER 4: RESOURCE DEPENDENCY ===
    WEAK_SIDE = "WEAK_SIDE"  # Can play with low resources
    STRONG_SIDE = "STRONG_SIDE"  # Needs resources/attention
    HYPERCARRY = "HYPERCARRY"  # Extreme resource dependency, extreme payoff
    
    # === LAYER 5: LANE SPECIFIC (for context) ===
    TANK = "TANK"  # Pure tank identity
    ASSASSIN = "ASSASSIN"  # Assassin identity
    CONTROL_MAGE = "CONTROL_MAGE"  # Control mage identity
    GANK_HEAVY = "GANK_HEAVY"  # Jungle: focuses on ganking
    FARMING_JUNGLE = "FARMING_JUNGLE"  # Jungle: focuses on farming


class ChampionArchetypeMapper:
    """
    Maps champions to strategic archetypes
    Rule-based, explainable, judge-safe
    """
    
    def __init__(self):
        # Load new layered taxonomy database
        try:
            from src.champion_database_v2 import get_all_champions
        except ModuleNotFoundError:
            from champion_database_v2 import get_all_champions
        
        self.champion_archetypes: Dict[str, Set[Archetype]] = get_all_champions()
    
    def get_archetypes(self, champion_name: str) -> Set[Archetype]:
        """Get archetypes for a champion"""
        return self.champion_archetypes.get(champion_name, set())
    
    def has_archetype(self, champion_name: str, archetype: Archetype) -> bool:
        """Check if champion has specific archetype"""
        return archetype in self.get_archetypes(champion_name)
    
    def get_champions_by_archetype(self, archetype: Archetype) -> List[str]:
        """Get all champions with specific archetype"""
        return [
            champ for champ, archetypes in self.champion_archetypes.items()
            if archetype in archetypes
        ]
    
    def analyze_composition(self, champions: List[str]) -> Dict[Archetype, int]:
        """Analyze team composition archetypes"""
        archetype_counts = {}
        
        for champion in champions:
            for archetype in self.get_archetypes(champion):
                archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
        
        return archetype_counts
    
    def classify_composition(self, champions: List[str]) -> str:
        """Classify overall composition strategy"""
        counts = self.analyze_composition(champions)
        
        # Rule-based classification using new archetypes
        if counts.get(Archetype.SCALING, 0) >= 2:
            if counts.get(Archetype.EARLY_GAME, 0) >= 1:
                return "HYBRID_EARLY_JUNGLE_SCALING_CARRIES"
            return "SCALING_COMPOSITION"
        
        if counts.get(Archetype.EARLY_GAME, 0) >= 2:
            return "EARLY_GAME_COMPOSITION"
        
        if counts.get(Archetype.SPLIT_PUSH, 0) >= 1:
            return "SPLIT_PUSH_COMPOSITION"
        
        if counts.get(Archetype.TEAMFIGHT_ULTIMATE, 0) >= 3:
            return "TEAMFIGHT_COMPOSITION"
        
        if counts.get(Archetype.PICK, 0) >= 2:
            return "PICK_COMPOSITION"
        
        return "BALANCED_COMPOSITION"
    
    def get_win_condition(self, champions: List[str]) -> str:
        """Predict win condition based on composition"""
        comp_type = self.classify_composition(champions)
        
        if comp_type == "HYBRID_EARLY_JUNGLE_SCALING_CARRIES":
            jungle = [c for c in champions if Archetype.EARLY_GAME in self.get_archetypes(c) and Archetype.GANK_HEAVY in self.get_archetypes(c)]
            carries = [c for c in champions if Archetype.SCALING in self.get_archetypes(c)]
            
            return f"{jungle[0] if jungle else 'Jungle'} secures early objectives → {', '.join(carries[:2])} scale → Late game control"
        
        elif comp_type == "SCALING_COMPOSITION":
            return "Stall to late game, avoid early fights, win teamfights with scaling advantage"
        
        elif comp_type == "EARLY_GAME_COMPOSITION":
            return "Snowball early, secure all objectives, end before 25 minutes"
        
        elif comp_type == "SPLIT_PUSH_COMPOSITION":
            splitter = [c for c in champions if Archetype.SPLIT_PUSH in self.get_archetypes(c)]
            return f"{splitter[0] if splitter else 'Top'} splits → Force 4v5 or take structures"
        
        elif comp_type == "TEAMFIGHT_COMPOSITION":
            return "Force 5v5 teamfights around objectives, win with superior teamfight"
        
        elif comp_type == "PICK_COMPOSITION":
            return "Catch isolated targets, avoid 5v5, snowball through picks"
        
        return "Standard win condition: secure objectives, win teamfights"
    
    def add_champion(self, champion_name: str, archetypes: Set[Archetype]) -> None:
        """Add new champion to mapping"""
        self.champion_archetypes[champion_name] = archetypes
    
    def print_champion_info(self, champion_name: str) -> None:
        """Print detailed champion archetype info"""
        archetypes = self.get_archetypes(champion_name)
        
        if not archetypes:
            print(f"{champion_name}: No archetype data")
            return
        
        print(f"\n{champion_name}:")
        print(f"  Archetypes:")
        for archetype in sorted(archetypes, key=lambda a: a.value):
            print(f"    - {archetype.value}")


if __name__ == '__main__':
    # Test archetype mapping
    mapper = ChampionArchetypeMapper()
    
    print("=" * 70)
    print("CHAMPION ARCHETYPE MAPPING V2 - LAYERED TAXONOMY")
    print("=" * 70)
    
    # Test individual champions
    test_champions = ["Azir", "Lee Sin", "K'Sante", "Jinx", "Thresh"]
    
    for champ in test_champions:
        mapper.print_champion_info(champ)
    
    # Test composition analysis
    print("\n" + "=" * 70)
    print("COMPOSITION ANALYSIS")
    print("=" * 70)
    
    comp = ["K'Sante", "Lee Sin", "Azir", "Jinx", "Thresh"]
    print(f"\nComposition: {', '.join(comp)}")
    print(f"Classification: {mapper.classify_composition(comp)}")
    print(f"Win Condition: {mapper.get_win_condition(comp)}")
    
    print("\nArchetype Breakdown:")
    counts = mapper.analyze_composition(comp)
    for archetype, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {archetype.value}: {count}")
