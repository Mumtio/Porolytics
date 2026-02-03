# Porolytics - League of Legends Esports Data Fetcher

Complete opponent analysis system for League of Legends esports using Grid API.

## Overview

This project fetches comprehensive match data from the Grid API for League of Legends professional matches, including:
- Draft phase (picks/bans)
- Kills, deaths, assists
- Objectives (Baron, Dragons, Herald, etc.)
- Structure destruction (Towers, Inhibitors)
- Item purchases and builds
- Ability usage
- Level progression
- Complete game statistics

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GRID_API_KEY=your_api_key_here" > .env
```

Get your API key from: https://grid.gg/

### 2. Test Connection

```bash
# Test your API connection
python grid_data_fetcher.py --test
```

### 3. Find Teams

```bash
# Search for teams by name
python grid_data_fetcher.py --find "Cloud9"
python grid_data_fetcher.py --find "T1"
```

### 4. Quick Test

```bash
# Interactive menu to test with popular teams
python grid_data_fetcher.py --quick-test
```

### 5. Fetch Production Data

```bash
# Single team
python grid_data_fetcher.py --team-id 47494 --team-name T1 --num-matches 10

# Multiple teams
python grid_data_fetcher.py --team-ids 47494,47351,47380 --num-matches 5

# See all options
python grid_data_fetcher.py --help
```

### 6. Analyze Team Data

```bash
# Analyze a team
python porolytics_analyzer.py data/team_47494_T1_analysis.json

# Run specific analyses only
python porolytics_analyzer.py data/team_47494_T1_analysis.json --analyses champion_dependency draft_gameplan

# Compare two teams
python porolytics_analyzer.py --compare data/team_47494_T1_analysis.json data/team_47351_Cloud9_analysis.json

# See all options
python porolytics_analyzer.py --help
```

## Project Structure

```
├── grid_data_fetcher.py          # Main library (all-in-one)
├── porolytics_analyzer.py        # Data analyzer
├── requirements.txt              # Python dependencies
├── .env                          # API key (create this)
└── data/                         # Downloaded data
    ├── events_*.jsonl.zip        # Event files
    ├── end_state_*.json          # End state files
    └── team_*_analysis.json      # Processed data
```

**grid_data_fetcher.py** contains:
- Core API client classes
- Event processing functions
- Data collection functions
- Utility functions (test, find, quick-test)
- Command-line interface

**porolytics_analyzer.py** contains:
- 9 analysis modules
- Team comparison functionality
- Report generation
- Command-line interface

## What Data Is Available

### ✅ From Grid API

**Series State (GraphQL):**
- Draft actions (picks/bans) with complete details
- Final game statistics (kills, deaths, assists)
- Assist relationships (who assisted whom)
- Objectives completed (counts)
- Structures destroyed (counts)
- Final player positions
- Final gold, net worth, inventory
- Character/champion information
- Game duration, clock, map

**Events (JSONL Files):**
- Kill events (who killed whom, when)
- Objective captures (Baron, Dragons, Herald - with timing)
- Structure destruction (Towers, Inhibitors - with timing)
- Item purchases and sales (with timing)
- Ability usage (with timing)
- Level-up events (with timing)
- Draft actions (picks/bans - with timing)
- Player respawns

### ❌ Not Available for League of Legends

Grid's LoL events do NOT include:
- Player position timelines (only final positions)
- Gold/money progression over time (only final values)
- Experience progression over time
- Ward placement positions
- Summoner spell usage tracking

**Note:** These limitations are specific to Grid's League of Legends data. Other games (CS:GO, Valorant) may have more detailed position/economy tracking.

## Usage Examples

### Quick Reference

| Task | Command |
|------|---------|
| Test connection | `python grid_data_fetcher.py --test` |
| Find teams | `python grid_data_fetcher.py --find "Team Name"` |
| Quick test | `python grid_data_fetcher.py --quick-test` |
| Single team | `python grid_data_fetcher.py --team-id 47494 --num-matches 10` |
| Multiple teams | `python grid_data_fetcher.py --team-ids 47494,47351 --num-matches 5` |
| Specific series | `python grid_data_fetcher.py --series-id 2847265` |
| Analyze team | `python porolytics_analyzer.py data/team_47494_T1_analysis.json` |
| Compare teams | `python porolytics_analyzer.py --compare team1.json team2.json` |
| See all options | `python grid_data_fetcher.py --help` or `python porolytics_analyzer.py --help` |

### Command Line Usage

**Test & Utilities:**
```bash
# Test API connection
python grid_data_fetcher.py --test

# Find teams by name
python grid_data_fetcher.py --find "Cloud9"
python grid_data_fetcher.py --find "T1"

# Interactive quick test (select from popular teams)
python grid_data_fetcher.py --quick-test
```

**Fetch Data:**
```bash
# Single team
python grid_data_fetcher.py --team-id 47494 --team-name T1 --num-matches 10

# Multiple teams at once
python grid_data_fetcher.py --team-ids 47494,47351,47380 --num-matches 5

# Specific series only
python grid_data_fetcher.py --series-id 2847265

# Team in specific tournament
python grid_data_fetcher.py --team-id 47494 --tournament-id 12345

# Valorant data
python grid_data_fetcher.py --team-id 47494 --title-id 6 --num-matches 10

# Custom output directory
python grid_data_fetcher.py --team-id 47494 --output-dir my_data

# Skip event files (faster, state only)
python grid_data_fetcher.py --team-id 47494 --no-events

# See all options
python grid_data_fetcher.py --help
```

**Analyze Data:**
```bash
# Analyze single team
python porolytics_analyzer.py data/team_47494_T1_analysis.json

# Run specific analyses only
python porolytics_analyzer.py data/team_47494_T1_analysis.json --analyses champion_dependency draft_gameplan

# Compare two teams
python porolytics_analyzer.py --compare data/team_47494_T1_analysis.json data/team_47351_Cloud9_analysis.json

# Custom output file
python porolytics_analyzer.py data/team_47494_T1_analysis.json -o custom_report.json

# Quiet mode (no console output)
python porolytics_analyzer.py data/team_47494_T1_analysis.json --quiet

# See all options
python porolytics_analyzer.py --help
```

### Using as Python Library

**Data Collection:**
```python
from grid_data_fetcher import PorolyticsDataCollector, GridAPIClient, EventProcessor

# Initialize collector
collector = PorolyticsDataCollector(api_key="your_key")

# Fetch data for a team
data = collector.collect_team_data(
    team_id="47494",  # T1
    num_matches=10,
    title_id=3,  # League of Legends
    download_events=True
)

# Save the data
collector.save_collected_data(data, "data/t1_analysis.json")

# Or use lower-level API directly
client = GridAPIClient(api_key="your_key")
processor = EventProcessor()

# Get series list
series_list = client.get_team_series(team_id="47494", limit=5)

# Get specific series state
state = client.get_series_state(series_id="2847265")

# Download files
events_file = client.download_series_events("2847265", "events.jsonl.zip")

# Parse and extract data
events = processor.parse_events_file(events_file)
kills = processor.extract_kills(events)
objectives = processor.extract_objectives(events)
```

**Data Analysis:**
```python
from porolytics_analyzer import PorolyticsAnalyzer, analyze_team_from_file, compare_teams

# Analyze a team
report = analyze_team_from_file("data/team_47494_T1_analysis.json")

# Access specific analyses
print(report['champion_dependency']['comfort_picks'])
print(report['draft_gameplan']['ban_recommendations'])

# Or use the class directly
analyzer = PorolyticsAnalyzer("data/team_47494_T1_analysis.json")
champion_analysis = analyzer.analyze_champion_dependency()
draft_plan = analyzer.generate_draft_gameplan()

# Compare two teams
comparison = compare_teams(
    "data/team_47494_T1_analysis.json",
    "data/team_47351_Cloud9_analysis.json"
)
```

## Popular Team IDs

| Team | ID | Region |
|------|-----|--------|
| T1 | 47494 | Korea |
| Cloud9 Kia | 47351 | North America |
| G2 Esports | 47380 | Europe |
| Gen.G Esports | 47558 | Korea |
| BILIBILI GAMING | 356 | China |
| FlyQuest | 340 | North America |
| Fnatic | 47376 | Europe |
| Dplus KIA | 48179 | Korea |
| 100 Thieves | 47497 | North America |
| Karmine Corp | 53165 | Europe |

## Analysis Features

The **porolytics_analyzer.py** provides 9 comprehensive analysis modules:

### 1. Team Identity
Analyzes gold distribution and role impact to identify:
- Primary win condition (which role gets resources)
- Secondary plan
- Sacrificed lane
- Role-specific win rates

### 2. Winning Recipe
Uses frequent pattern mining to find:
- Common objective sequences in wins
- Frequent winning patterns
- Primary recipe for success

### 3. Vision Investment
Analyzes vision spending patterns:
- Wards per game
- Vision investment in wins vs losses
- Pre-objective setup rate

### 4. Roaming System
Detects player movement patterns:
- Roaming frequency
- Average roam distance
- Movement patterns from event positions

### 5. Champion Dependency
Comprehensive champion pool analysis:
- Comfort picks (high pick rate + high win rate)
- Trap picks (high pick rate + low win rate)
- Pool diversity per role
- Champion-specific statistics

### 6. Losing Recipe
Identifies common failure patterns:
- Early death patterns
- Failed objectives
- Vision collapse
- Primary failure mode

### 7. Role Correlation
Identifies role dependencies:
- Which roles correlate with wins
- Lynchpin role identification
- Role performance in wins vs losses

### 8. Break Strategy
Generates counter-strategies based on:
- Opponent weaknesses
- Failure patterns
- Champion dependencies

### 9. Draft & Gameplan
Provides actionable recommendations:
- Ban recommendations (target comfort picks)
- Pick suggestions
- Early game plan

### Analysis Output Example

```json
{
  "team_identity": {
    "primary_win_condition": "mid",
    "secondary_plan": "jungle",
    "sacrificed_lane": "top"
  },
  "champion_dependency": {
    "comfort_picks": {
      "Jinx": {"picks": 5, "win_rate": 80.0}
    },
    "trap_picks": {
      "Azir": {"picks": 4, "win_rate": 25.0}
    }
  },
  "draft_gameplan": {
    "ban_recommendations": ["Jinx (comfort pick)", "Orianna (comfort pick)"],
    "early_game_plan": ["Pressure top lane (weak side)", "Invade jungle level 1"]
  }
}
```

## Data Structure

### Processed Data Format

```python
{
    "series_id": "2847265",
    "fetch_time": "2026-01-30T...",
    "files_downloaded": [...],
    "state": {
        # Complete series state from GraphQL
        "draftActions": [...],
        "games": [...],
        "teams": [...]
    },
    "processed": {
        "kills": [...],           # Kill events
        "objectives": [...],      # Objective captures
        "abilities": [...],       # Ability usage
        "items": [...],           # Item purchases
        "draft": [...],           # Draft actions
        "structures": [...],      # Structure destruction
        "levels": [...],          # Level-up events
        "assist_details": [...]   # Detailed assists
    },
    "stats": {
        "total_events": 4839,
        "total_kills": 134,
        "total_objectives": 99,
        "total_draft_actions": 100
    }
}
```

### Accessing Data

```python
import json

# Load results
with open('data/team_47494_T1_analysis.json', 'r') as f:
    data = json.load(f)

# Get first series
series = data['series'][0]

# Draft phase
draft = series['processed']['draft']
for action in draft:
    print(f"{action['event_type']}: {action['target_name']}")

# Kills
kills = series['processed']['kills']
for kill in kills:
    print(f"{kill['killer_id']} killed {kill['victim_id']} at {kill['timestamp']}")

# Objectives
objectives = series['processed']['objectives']
for obj in objectives:
    print(f"{obj['type']} at {obj['timestamp']}")

# Final game state
state = series['state']
for game in state['games']:
    for team in game['teams']:
        print(f"Team {team['name']}: {team['kills']} kills, {team['netWorth']} gold")
```

## Analysis Capabilities

### What You CAN Analyze

✅ **Draft Analysis**
- Pick/ban patterns
- Champion pool
- Draft priority
- Counter-pick strategies

✅ **Kill Patterns**
- Who killed whom
- Kill timing
- First blood patterns
- Multi-kill events

✅ **Objective Control**
- Baron/Dragon timing
- Objective priority
- Contest patterns
- Trade analysis

✅ **Structure Pressure**
- Tower taking patterns
- Plate gold timing
- Inhibitor timing
- Split push analysis

✅ **Item Builds**
- Item purchase order
- Build paths
- Item timing
- Gold efficiency

✅ **Level Progression**
- Level-up timing
- Level advantages
- Experience patterns

✅ **Final Game State**
- End-game statistics
- Final positions
- Final gold/items
- Assist networks

### What You CANNOT Analyze

❌ Player movement patterns (no position timeline)
❌ Gold leads over time (no gold timeline)
❌ Vision control (no ward positions)
❌ XP advantages over time (no XP timeline)
❌ Summoner spell usage (not in events)

## API Endpoints

### GraphQL (Series State)
```
https://api-op.grid.gg/live-data-feed/series-state/graphql
```

### REST (File Downloads)
```
https://api.grid.gg/file-download/events/grid/series/{seriesId}
https://api.grid.gg/file-download/end-state/grid/series/{seriesId}
```

### Authentication
All requests require `x-api-key` header with your API key.

## Files Downloaded Per Series

1. **events_{series_id}_grid.jsonl.zip** - Grid events (5-10 MB)
   - All game events with timing
   - Kills, objectives, items, abilities, etc.

2. **end_state_{series_id}_grid.json** - Grid end state (100-500 KB)
   - Final game state
   - Complete statistics

3. **events_{series_id}_riot.jsonl.zip** - Riot official events (if available)
   - Requires special permissions
   - More detailed data

4. **end_state_{series_id}_riot.json.zip** - Riot official end state (if available)
   - Requires special permissions
   - Official Riot data

## Configuration

### Environment Variables (.env)
```bash
GRID_API_KEY=your_api_key_here
```

### Team Configuration (grid_data_fetcher.py)
Edit the `TEAMS_TO_ANALYZE` list to add/remove teams:

```python
TEAMS_TO_ANALYZE = [
    ("47494", "T1"),
    ("47351", "Cloud9_Kia"),
    # Add more teams...
]
```

## Troubleshooting

### "No API key found"
- Create `.env` file in project root
- Add `GRID_API_KEY=your_key`
- Get key from https://grid.gg/

### "No series found"
- Team might not have recent matches
- Try different team ID
- Check if team ID is correct

### "403 Forbidden" for Riot files
- Normal - Riot files require special permissions
- Grid files are always available
- You still get complete data from Grid files

### Some extractors return 0
- Normal for League of Legends
- Grid's LoL events don't include position/gold timelines
- You still get action events (kills, objectives, items)

## Performance

- **Time per team:** ~2-3 minutes
- **Files per series:** 2-4 files
- **Data per series:** ~5-15 MB
- **Total for 20 teams:** ~40-60 minutes

## Requirements

```
requests>=2.31.0
python-dotenv>=1.0.0
```

Python 3.8+ required.

## Project History

This project was developed for the Cloud9 x JetBrains Hackathon to provide comprehensive opponent scouting data for League of Legends esports teams.

### Key Features
- Complete Grid API integration
- All available fields extracted
- Production-ready code
- Flexible testing tools
- Comprehensive data processing

## Support

For Grid API issues:
- Email: support@grid.gg
- Documentation: https://docs.grid.gg/

For project issues:
- Check this README
- Review code comments
- Test with `quick_test.py`

## License

See LICENSE file for details.

## Acknowledgments

- Grid.gg for providing the esports data API
- Cloud9 for the hackathon opportunity
- JetBrains for sponsorship

---

**Ready to start?** Run `python quick_test.py` to test with a single match!
