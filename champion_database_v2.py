"""
League of Legends Champion Archetype Database V2
Properly layered taxonomy - no role/phase mixing
"""
from typing import Dict, Set
from src.part1_champion_archetypes import Archetype


def get_all_champions() -> Dict[str, Set[Archetype]]:
    """
    Complete champion database with proper layered archetypes
    """
    return {
        # ==================== TOP LANE ====================
        
        # Tanks
        "Cho'Gath": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.ZONE_CONTROL},
        "Dr. Mundo": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.SPLIT_PUSH, Archetype.SCALING},
        "Malphite": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Maokai": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.ZONE_CONTROL, Archetype.ENGAGE},
        "Ornn": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Poppy": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.UTILITY},
        "Shen": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.ROAM, Archetype.UTILITY},
        "Sion": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Tahm Kench": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.DUELIST},
        "Zac": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "K'Sante": {Archetype.TANK, Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.ENGAGE, Archetype.SKIRMISHER},
        
        # Bruisers/Fighters
        "Aatrox": {Archetype.STRONG_SIDE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE, Archetype.SKIRMISHER},
        "Camille": {Archetype.SPLIT_PUSH, Archetype.STRONG_SIDE, Archetype.PICK, Archetype.BACKLINE_THREAT, Archetype.SCALING},
        "Darius": {Archetype.STRONG_SIDE, Archetype.EARLY_GAME, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DUELIST},
        "Fiora": {Archetype.SPLIT_PUSH, Archetype.STRONG_SIDE, Archetype.SCALING, Archetype.DUELIST},
        "Garen": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.EARLY_GAME},
        "Gwen": {Archetype.SPLIT_PUSH, Archetype.STRONG_SIDE, Archetype.SCALING, Archetype.ZONE_CONTROL, Archetype.DPS},
        "Illaoi": {Archetype.STRONG_SIDE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DUELIST},
        "Irelia": {Archetype.STRONG_SIDE, Archetype.BACKLINE_THREAT, Archetype.SPLIT_PUSH, Archetype.SKIRMISHER},
        "Jax": {Archetype.SPLIT_PUSH, Archetype.STRONG_SIDE, Archetype.SCALING, Archetype.DUELIST},
        "Mordekaiser": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.DUELIST},
        "Nasus": {Archetype.SPLIT_PUSH, Archetype.SCALING, Archetype.WEAK_SIDE, Archetype.LATE_GAME},
        "Olaf": {Archetype.STRONG_SIDE, Archetype.EARLY_GAME, Archetype.BACKLINE_THREAT, Archetype.SKIRMISHER},
        "Renekton": {Archetype.STRONG_SIDE, Archetype.EARLY_GAME, Archetype.FRONTLINE, Archetype.DUELIST},
        "Riven": {Archetype.STRONG_SIDE, Archetype.BACKLINE_THREAT, Archetype.SPLIT_PUSH, Archetype.BURST, Archetype.SKIRMISHER},
        "Sett": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Trundle": {Archetype.SPLIT_PUSH, Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.DUELIST},
        "Tryndamere": {Archetype.SPLIT_PUSH, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.DUELIST},
        "Urgot": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.DPS},
        "Volibear": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.ENGAGE, Archetype.SKIRMISHER},
        "Warwick": {Archetype.STRONG_SIDE, Archetype.PICK, Archetype.SKIRMISHER, Archetype.EARLY_GAME},
        "Yorick": {Archetype.SPLIT_PUSH, Archetype.SCALING, Archetype.ZONE_CONTROL, Archetype.DUELIST},
        "Ambessa": {Archetype.STRONG_SIDE, Archetype.EARLY_GAME, Archetype.BACKLINE_THREAT, Archetype.SKIRMISHER},
        
        # Ranged/AP Top
        "Gnar": {Archetype.WEAK_SIDE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE, Archetype.POKE},
        "Jayce": {Archetype.STRONG_SIDE, Archetype.POKE, Archetype.EARLY_GAME, Archetype.BURST},
        "Kennen": {Archetype.WEAK_SIDE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.ENGAGE},
        "Quinn": {Archetype.SPLIT_PUSH, Archetype.ROAM, Archetype.EARLY_GAME, Archetype.PICK},
        "Rumble": {Archetype.STRONG_SIDE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.DPS},
        "Teemo": {Archetype.SPLIT_PUSH, Archetype.ZONE_CONTROL, Archetype.POKE},
        "Vladimir": {Archetype.WEAK_SIDE, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Akali": {Archetype.STRONG_SIDE, Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Gragas": {Archetype.WEAK_SIDE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Gangplank": {Archetype.SCALING, Archetype.SPLIT_PUSH, Archetype.TEAMFIGHT_ULTIMATE, Archetype.POKE},
        "Pantheon": {Archetype.STRONG_SIDE, Archetype.ROAM, Archetype.EARLY_GAME, Archetype.PICK, Archetype.BURST},
        
        # Additional Missing Top Laners
        "Kayle": {Archetype.WEAK_SIDE, Archetype.SCALING, Archetype.LATE_GAME, Archetype.HYPERCARRY, Archetype.DPS},
        "Singed": {Archetype.SPLIT_PUSH, Archetype.ROAM, Archetype.ZONE_CONTROL, Archetype.FRONTLINE},
        "Heimerdinger": {Archetype.ZONE_CONTROL, Archetype.POKE, Archetype.SPLIT_PUSH, Archetype.DPS},
        "Kled": {Archetype.STRONG_SIDE, Archetype.EARLY_GAME, Archetype.ROAM, Archetype.ENGAGE, Archetype.SKIRMISHER},
        "Wukong": {Archetype.STRONG_SIDE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE, Archetype.BURST},
        "Viego": {Archetype.STRONG_SIDE, Archetype.SKIRMISHER, Archetype.SCALING, Archetype.BACKLINE_THREAT},
        "Rengar": {Archetype.SPLIT_PUSH, Archetype.ASSASSIN, Archetype.PICK, Archetype.BURST},
        "Ryze": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ROAM, Archetype.DPS},
        "Skarner": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.PICK, Archetype.OBJECTIVE_CONTROL},
        "Udyr": {Archetype.STRONG_SIDE, Archetype.FRONTLINE, Archetype.SPLIT_PUSH, Archetype.SKIRMISHER},
        "Kayn": {Archetype.STRONG_SIDE, Archetype.SCALING, Archetype.SKIRMISHER, Archetype.BACKLINE_THREAT},
        
        # ==================== JUNGLE ====================
        
        # Early Game Junglers
        "Elise": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Lee Sin": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.OBJECTIVE_CONTROL, Archetype.PICK, Archetype.SKIRMISHER},
        "Nidalee": {Archetype.EARLY_GAME, Archetype.FARMING_JUNGLE, Archetype.POKE, Archetype.SKIRMISHER},
        "Rek'Sai": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.PICK, Archetype.SKIRMISHER},
        "Xin Zhao": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.OBJECTIVE_CONTROL, Archetype.SKIRMISHER},
        "Jarvan IV": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.ENGAGE, Archetype.TEAMFIGHT_ULTIMATE},
        "Taliyah": {Archetype.EARLY_GAME, Archetype.ROAM, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Volibear": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.SKIRMISHER},
        
        # Farming/Scaling Junglers
        "Graves": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Karthus": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Kindred": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.OBJECTIVE_CONTROL, Archetype.DPS},
        "Master Yi": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.HYPERCARRY, Archetype.DPS},
        "Shyvana": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.OBJECTIVE_CONTROL, Archetype.DPS},
        "Lillia": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Bel'Veth": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.OBJECTIVE_CONTROL, Archetype.HYPERCARRY, Archetype.DPS},
        
        # Tank/Engage Junglers
        "Amumu": {Archetype.FARMING_JUNGLE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Nunu & Willump": {Archetype.GANK_HEAVY, Archetype.OBJECTIVE_CONTROL, Archetype.FRONTLINE, Archetype.ENGAGE},
        "Rammus": {Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.ENGAGE, Archetype.TANK},
        "Sejuani": {Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Zac": {Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        "Skarner": {Archetype.OBJECTIVE_CONTROL, Archetype.PICK, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE},
        "Maokai": {Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.ZONE_CONTROL, Archetype.ENGAGE},
        
        # Assassin Junglers
        "Kha'Zix": {Archetype.FARMING_JUNGLE, Archetype.ASSASSIN, Archetype.PICK, Archetype.BURST},
        "Rengar": {Archetype.FARMING_JUNGLE, Archetype.ASSASSIN, Archetype.PICK, Archetype.BURST},
        "Evelynn": {Archetype.FARMING_JUNGLE, Archetype.ASSASSIN, Archetype.PICK, Archetype.BURST},
        "Shaco": {Archetype.EARLY_GAME, Archetype.ASSASSIN, Archetype.PICK, Archetype.ZONE_CONTROL},
        
        # Bruiser Junglers
        "Hecarim": {Archetype.FARMING_JUNGLE, Archetype.GANK_HEAVY, Archetype.ENGAGE, Archetype.SKIRMISHER},
        "Nocturne": {Archetype.FARMING_JUNGLE, Archetype.GANK_HEAVY, Archetype.PICK, Archetype.ASSASSIN, Archetype.TEAMFIGHT_ULTIMATE},
        "Vi": {Archetype.GANK_HEAVY, Archetype.PICK, Archetype.ENGAGE, Archetype.BURST},
        "Warwick": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.PICK, Archetype.SKIRMISHER},
        "Wukong": {Archetype.GANK_HEAVY, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE, Archetype.BURST},
        "Diana": {Archetype.FARMING_JUNGLE, Archetype.ASSASSIN, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BURST},
        "Ekko": {Archetype.FARMING_JUNGLE, Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Fiddlesticks": {Archetype.FARMING_JUNGLE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Gragas": {Archetype.GANK_HEAVY, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE},
        
        # Utility/Support Junglers
        "Ivern": {Archetype.FARMING_JUNGLE, Archetype.ENCHANTER, Archetype.OBJECTIVE_CONTROL, Archetype.UTILITY},
        
        # Additional Missing Junglers
        "Kayn": {Archetype.FARMING_JUNGLE, Archetype.SCALING, Archetype.ASSASSIN, Archetype.BACKLINE_THREAT},
        "Viego": {Archetype.FARMING_JUNGLE, Archetype.SKIRMISHER, Archetype.SCALING, Archetype.BACKLINE_THREAT},
        "Udyr": {Archetype.FARMING_JUNGLE, Archetype.OBJECTIVE_CONTROL, Archetype.FRONTLINE, Archetype.SKIRMISHER},
        "Briar": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.SKIRMISHER, Archetype.BACKLINE_THREAT},
        "Kennen": {Archetype.FARMING_JUNGLE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.ENGAGE},
        "Naafiri": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.ASSASSIN, Archetype.PICK},
        "Zyra": {Archetype.FARMING_JUNGLE, Archetype.ZONE_CONTROL, Archetype.POKE, Archetype.TEAMFIGHT_ULTIMATE},
        "Brand": {Archetype.FARMING_JUNGLE, Archetype.BURST, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE},
        "Morgana": {Archetype.FARMING_JUNGLE, Archetype.ZONE_CONTROL, Archetype.UTILITY, Archetype.PICK},
        "Rell": {Archetype.GANK_HEAVY, Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Sion": {Archetype.FARMING_JUNGLE, Archetype.TANK, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Talon": {Archetype.EARLY_GAME, Archetype.GANK_HEAVY, Archetype.ASSASSIN, Archetype.ROAM},
        
        # ==================== MID LANE ====================
        
        # Control Mages
        "Anivia": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE},
        "Azir": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Cassiopeia": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ZONE_CONTROL, Archetype.DPS},
        "Malzahar": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.PICK, Archetype.DPS},
        "Orianna": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Ryze": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ROAM, Archetype.DPS},
        "Syndra": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.PICK, Archetype.BURST},
        "Taliyah": {Archetype.MID_GAME, Archetype.ROAM, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Twisted Fate": {Archetype.MID_GAME, Archetype.ROAM, Archetype.PICK, Archetype.UTILITY},
        "Viktor": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.ZONE_CONTROL, Archetype.DPS},
        "Xerath": {Archetype.SCALING, Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Ziggs": {Archetype.SCALING, Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Vel'Koz": {Archetype.SCALING, Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.DPS},
        "Vex": {Archetype.CONTROL_MAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.PICK, Archetype.BURST},
        "Neeko": {Archetype.CONTROL_MAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.PICK},
        "Hwei": {Archetype.SCALING, Archetype.CONTROL_MAGE, Archetype.POKE, Archetype.UTILITY},
        "Aurora": {Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Mel": {Archetype.CONTROL_MAGE, Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Akshan": {Archetype.MARKSMAN, Archetype.ASSASSIN, Archetype.ROAM, Archetype.BURST},
        
        # Assassins
        "Ahri": {Archetype.MID_GAME, Archetype.ASSASSIN, Archetype.PICK, Archetype.ROAM, Archetype.BURST},
        "Akali": {Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.PICK, Archetype.BURST},
        "Diana": {Archetype.ASSASSIN, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Ekko": {Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.ROAM, Archetype.BURST},
        "Fizz": {Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.PICK, Archetype.BURST},
        "Kassadin": {Archetype.SCALING, Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.LATE_GAME},
        "Katarina": {Archetype.ASSASSIN, Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BURST},
        "LeBlanc": {Archetype.MID_GAME, Archetype.ROAM, Archetype.ASSASSIN, Archetype.PICK, Archetype.BURST},
        "Qiyana": {Archetype.ASSASSIN, Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BURST},
        "Talon": {Archetype.ASSASSIN, Archetype.ROAM, Archetype.PICK, Archetype.BURST},
        "Zed": {Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.PICK, Archetype.BURST},
        "Yone": {Archetype.SCALING, Archetype.ASSASSIN, Archetype.BACKLINE_THREAT, Archetype.SKIRMISHER},
        
        # Battlemages/Bruisers
        "Galio": {Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE, Archetype.ENGAGE, Archetype.UTILITY},
        "Sylas": {Archetype.MID_GAME, Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.SKIRMISHER},
        "Vladimir": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Swain": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE, Archetype.DPS},
        "Rumble": {Archetype.MID_GAME, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.DPS},
        
        # Poke/Artillery
        "Corki": {Archetype.SCALING, Archetype.POKE, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Jayce": {Archetype.MID_GAME, Archetype.POKE, Archetype.EARLY_GAME, Archetype.BURST},
        "Lux": {Archetype.SCALING, Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BURST},
        "Zoe": {Archetype.MID_GAME, Archetype.POKE, Archetype.PICK, Archetype.BURST},
        
        # Unique/Flex
        "Yasuo": {Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Aurelion Sol": {Archetype.ROAM, Archetype.SCALING, Archetype.ZONE_CONTROL, Archetype.DPS},
        
        # Additional Missing Mid Laners
        "Brand": {Archetype.BURST, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.POKE},
        "Morgana": {Archetype.CONTROL_MAGE, Archetype.ZONE_CONTROL, Archetype.UTILITY, Archetype.PICK},
        "Annie": {Archetype.BURST, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENGAGE, Archetype.PICK},
        "Lissandra": {Archetype.CONTROL_MAGE, Archetype.ENGAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Veigar": {Archetype.SCALING, Archetype.LATE_GAME, Archetype.BURST, Archetype.ZONE_CONTROL},
        "Kennen": {Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.ENGAGE, Archetype.BURST},
        "Karma": {Archetype.POKE, Archetype.ENCHANTER, Archetype.ROAM, Archetype.UTILITY},
        "Seraphine": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENCHANTER, Archetype.UTILITY},
        "Naafiri": {Archetype.ASSASSIN, Archetype.ROAM, Archetype.PICK, Archetype.BURST},
        
        # ==================== ADC (BOT LANE) ====================
        
        # Hypercarries
        "Aphelios": {Archetype.HYPERCARRY, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Jinx": {Archetype.HYPERCARRY, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Kai'Sa": {Archetype.SCALING, Archetype.HYPERCARRY, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Kog'Maw": {Archetype.HYPERCARRY, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Twitch": {Archetype.HYPERCARRY, Archetype.SCALING, Archetype.ASSASSIN, Archetype.DPS},
        "Vayne": {Archetype.HYPERCARRY, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.DUELIST, Archetype.DPS},
        "Zeri": {Archetype.SCALING, Archetype.HYPERCARRY, Archetype.ZONE_CONTROL, Archetype.DPS},
        
        # Early Game ADCs
        "Caitlyn": {Archetype.EARLY_GAME, Archetype.POKE, Archetype.SCALING, Archetype.DPS},
        "Draven": {Archetype.EARLY_GAME, Archetype.BACKLINE_THREAT, Archetype.STRONG_SIDE, Archetype.DPS},
        "Kalista": {Archetype.EARLY_GAME, Archetype.OBJECTIVE_CONTROL, Archetype.UTILITY, Archetype.DPS},
        "Lucian": {Archetype.EARLY_GAME, Archetype.BACKLINE_THREAT, Archetype.MID_GAME, Archetype.BURST, Archetype.SKIRMISHER},
        "Miss Fortune": {Archetype.EARLY_GAME, Archetype.TEAMFIGHT_ULTIMATE, Archetype.POKE, Archetype.DPS},
        "Samira": {Archetype.EARLY_GAME, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Tristana": {Archetype.EARLY_GAME, Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.DPS},
        
        # Utility ADCs
        "Ashe": {Archetype.UTILITY, Archetype.PICK, Archetype.ENGAGE, Archetype.DPS},
        "Jhin": {Archetype.UTILITY, Archetype.POKE, Archetype.PICK, Archetype.BURST},
        "Senna": {Archetype.UTILITY, Archetype.SCALING, Archetype.POKE, Archetype.DPS},
        "Sivir": {Archetype.SCALING, Archetype.UTILITY, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Varus": {Archetype.POKE, Archetype.UTILITY, Archetype.PICK, Archetype.DPS},
        
        # Caster ADCs
        "Ezreal": {Archetype.SCALING, Archetype.POKE, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Corki": {Archetype.SCALING, Archetype.POKE, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Xayah": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY, Archetype.DPS},
        
        # Unique ADCs
        "Nilah": {Archetype.SCALING, Archetype.HYPERCARRY, Archetype.TEAMFIGHT_ULTIMATE, Archetype.SKIRMISHER},
        "Smolder": {Archetype.SCALING, Archetype.HYPERCARRY, Archetype.POKE, Archetype.DPS},
        "Ziggs": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.SCALING, Archetype.BURST},
        "Seraphine": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.ENCHANTER, Archetype.UTILITY},
        "Swain": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE, Archetype.DPS},
        "Yasuo": {Archetype.SCALING, Archetype.BACKLINE_THREAT, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        
        # Additional Missing ADCs (Niche/Flex)
        "Jax": {Archetype.SCALING, Archetype.HYPERCARRY, Archetype.SKIRMISHER, Archetype.DPS},
        "Kennen": {Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.ENGAGE, Archetype.BURST},
        "Heimerdinger": {Archetype.ZONE_CONTROL, Archetype.POKE, Archetype.DPS, Archetype.UTILITY},
        "Karthus": {Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS, Archetype.ZONE_CONTROL},
        "Cassiopeia": {Archetype.SCALING, Archetype.DPS, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE},
        "Syndra": {Archetype.BURST, Archetype.PICK, Archetype.ZONE_CONTROL},
        "Veigar": {Archetype.SCALING, Archetype.LATE_GAME, Archetype.BURST, Archetype.ZONE_CONTROL},
        
        # ==================== SUPPORT ====================
        
        # Engage/Tank Supports
        "Alistar": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Blitzcrank": {Archetype.ENGAGE, Archetype.PICK, Archetype.ROAM},
        "Braum": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.ZONE_CONTROL, Archetype.UTILITY},
        "Leona": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.PICK, Archetype.EARLY_GAME},
        "Nautilus": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.PICK},
        "Rakan": {Archetype.ENGAGE, Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Rell": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Thresh": {Archetype.ENGAGE, Archetype.PICK, Archetype.ROAM, Archetype.UTILITY},
        "Pyke": {Archetype.ENGAGE, Archetype.PICK, Archetype.ROAM, Archetype.ASSASSIN},
        "Sett": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Galio": {Archetype.ENGAGE, Archetype.ROAM, Archetype.TEAMFIGHT_ULTIMATE, Archetype.FRONTLINE},
        "Pantheon": {Archetype.ENGAGE, Archetype.ROAM, Archetype.PICK, Archetype.EARLY_GAME},
        "Taric": {Archetype.ENGAGE, Archetype.ENCHANTER, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        
        # Enchanter Supports
        "Janna": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.ZONE_CONTROL},
        "Lulu": {Archetype.ENCHANTER, Archetype.UTILITY},
        "Nami": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.TEAMFIGHT_ULTIMATE},
        "Sona": {Archetype.ENCHANTER, Archetype.SCALING, Archetype.TEAMFIGHT_ULTIMATE, Archetype.POKE},
        "Soraka": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.POKE},
        "Yuumi": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.SCALING},
        "Renata Glasc": {Archetype.ENCHANTER, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Milio": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.ZONE_CONTROL},
        
        # Poke/Mage Supports
        "Brand": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.BURST},
        "Karma": {Archetype.POKE, Archetype.ENCHANTER, Archetype.ROAM, Archetype.UTILITY},
        "Lux": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.PICK, Archetype.BURST},
        "Morgana": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.PICK, Archetype.UTILITY},
        "Vel'Koz": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BACKLINE_THREAT, Archetype.DPS},
        "Xerath": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.BACKLINE_THREAT, Archetype.BURST},
        "Zyra": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Swain": {Archetype.POKE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        "Seraphine": {Archetype.POKE, Archetype.ENCHANTER, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY},
        "Neeko": {Archetype.POKE, Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.PICK},
        
        # Utility/Unique Supports
        "Bard": {Archetype.ROAM, Archetype.UTILITY, Archetype.PICK},
        "Zilean": {Archetype.ENCHANTER, Archetype.UTILITY, Archetype.ZONE_CONTROL, Archetype.ROAM},
        "Shen": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.ROAM, Archetype.UTILITY},
        "Tahm Kench": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.PICK, Archetype.UTILITY},
        "Poppy": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.PICK, Archetype.UTILITY},
        "Maokai": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.ZONE_CONTROL},
        "Senna": {Archetype.ENCHANTER, Archetype.SCALING, Archetype.POKE, Archetype.DPS},
        "Ashe": {Archetype.UTILITY, Archetype.PICK, Archetype.POKE},
        
        # Additional Missing Supports
        "Annie": {Archetype.BURST, Archetype.ENGAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.PICK},
        "Heimerdinger": {Archetype.ZONE_CONTROL, Archetype.POKE, Archetype.DPS},
        "Veigar": {Archetype.BURST, Archetype.ZONE_CONTROL, Archetype.SCALING},
        "Lissandra": {Archetype.ENGAGE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.UTILITY, Archetype.PICK},
        "Zac": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Sion": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE, Archetype.TANK},
        "Volibear": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.SKIRMISHER},
        "Amumu": {Archetype.ENGAGE, Archetype.FRONTLINE, Archetype.TEAMFIGHT_ULTIMATE},
        "Rumble": {Archetype.ZONE_CONTROL, Archetype.TEAMFIGHT_ULTIMATE, Archetype.DPS},
        
        # ==================== FLEX PICKS ====================
        
        "Teemo": {Archetype.SPLIT_PUSH, Archetype.ZONE_CONTROL, Archetype.POKE},
        "Shaco": {Archetype.PICK, Archetype.ZONE_CONTROL, Archetype.ASSASSIN},
        "Fiddlesticks": {Archetype.TEAMFIGHT_ULTIMATE, Archetype.ZONE_CONTROL, Archetype.PICK},
    }
