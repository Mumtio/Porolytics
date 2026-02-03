"""
Porolytics - Complete Opponent Analysis System
Fetches data and generates scouting reports for League of Legends esports

Cloud9 x JetBrains Hackathon Project
"""

import requests
import json
import zipfile
import os
import time
import statistics
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GridAPIClient:
    """Client for interacting with GRID APIs"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.graphql_base_url = "https://api-op.grid.gg"  # Open Access endpoint for GraphQL
        self.file_download_base_url = "https://api.grid.gg"  # Different endpoint for file downloads
        self.headers = {"x-api-key": api_key}
        
    def _graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Make a GraphQL request to Central Data API"""
        response = requests.post(
            f"{self.graphql_base_url}/central-data/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables or {}}
        )
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"\nHTTP Error {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        
        # Check for GraphQL errors
        if 'errors' in result:
            print(f"\nGraphQL Errors:")
            for error in result['errors']:
                print(f"  - {error.get('message', 'Unknown error')}")
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result
    
    def get_team_series(
        self, 
        team_id: str, 
        title_id: int = 3,  # 3 = LoL, 6 = Valorant
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get series IDs for a specific team
        
        Args:
            team_id: GRID team ID
            title_id: 3 for LoL, 6 for Valorant
            limit: Number of series to fetch (max 50 per request)
            start_date: ISO format date string (e.g., "2024-01-01T00:00:00Z")
            end_date: ISO format date string
        """
        
        # Build filter
        filter_parts = [
            f'titleIds: {{ in: [{title_id}] }}',
            f'teamIds: {{ in: ["{team_id}"] }}',
            'types: ESPORTS'
        ]
        
        if start_date and end_date:
            filter_parts.append(
                f'startTimeScheduled: {{ gte: "{start_date}", lte: "{end_date}" }}'
            )
        
        filter_str = ", ".join(filter_parts)
        
        query = f"""
        {{
          allSeries(
            first: {limit},
            filter: {{ {filter_str} }}
            orderBy: StartTimeScheduled
            orderDirection: DESC
          ) {{
            totalCount
            pageInfo {{
              hasNextPage
              endCursor
            }}
            edges {{
              node {{
                id
                startTimeScheduled
                format {{
                  id
                  name
                }}
                title {{
                  id
                  nameShortened
                }}
                tournament {{
                  id
                  name
                }}
                teams {{
                  baseInfo {{
                    id
                    name
                  }}
                  scoreAdvantage
                }}
              }}
            }}
          }}
        }}
        """
        
        result = self._graphql_request(query)
        
        if 'errors' in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        series_list = []
        for edge in result['data']['allSeries']['edges']:
            series_list.append(edge['node'])
        
        print(f"Found {len(series_list)} series for team {team_id}")
        return series_list
    
    def get_series_state(self, series_id: str) -> Dict:
        """
        Get complete series state (end-game snapshot) from Series State API
        Fetches ALL available fields for League of Legends based on actual Grid API schema
        """
        # Series State API uses a different GraphQL endpoint
        response = requests.post(
            f"{self.graphql_base_url}/live-data-feed/series-state/graphql",
            headers=self.headers,
            json={"query": """
        query SeriesState($seriesId: ID!) {
          seriesState(id: $seriesId) {
            id
            version
            valid
            started
            finished
            format
            updatedAt
            startedAt
            duration
            draftActions {
              id
              type
              sequenceNumber
              drafter {
                id
                type
              }
              draftable {
                id
                type
                name
                linkedDraftable {
                  id
                  type
                  name
                }
              }
            }
            teams {
              id
              name
              won
              score
              kills
              deaths
              killAssistsGiven
              killAssistsReceived
              killAssistsReceivedFromPlayer {
                playerId
                killAssistsReceived
              }
              teamkills
              teamkillAssistsGiven
              teamkillAssistsReceived
              selfkills
              firstKill
              structuresDestroyed
              structuresCaptured
              objectives {
                type
                completionCount
              }
              players {
                id
                name
                participationStatus
                kills
                deaths
                killAssistsGiven
                killAssistsReceived
                killAssistsReceivedFromPlayer {
                  playerId
                  killAssistsReceived
                }
                teamkills
                teamkillAssistsGiven
                teamkillAssistsReceived
                selfkills
                firstKill
                structuresDestroyed
                structuresCaptured
                objectives {
                  type
                  completionCount
                }
              }
            }
            games {
              id
              sequenceNumber
              started
              finished
              paused
              startedAt
              duration
              type
              map {
                id
                name
              }
              clock {
                id
                type
                ticking
                ticksBackwards
                currentSeconds
              }
              draftActions {
                id
                type
                sequenceNumber
                drafter {
                  id
                  type
                }
                draftable {
                  id
                  type
                  name
                  linkedDraftable {
                    id
                    type
                    name
                  }
                }
              }
              teams {
                id
                name
                side
                won
                score
                money
                loadoutValue
                netWorth
                kills
                deaths
                killAssistsGiven
                killAssistsReceived
                killAssistsReceivedFromPlayer {
                  playerId
                  killAssistsReceived
                }
                teamkills
                teamkillAssistsGiven
                teamkillAssistsReceived
                selfkills
                firstKill
                structuresDestroyed
                structuresCaptured
                objectives {
                  type
                  completionCount
                }
                players {
                  id
                  name
                  character {
                    id
                    name
                  }
                  participationStatus
                  money
                  loadoutValue
                  netWorth
                  kills
                  deaths
                  killAssistsGiven
                  killAssistsReceived
                  killAssistsReceivedFromPlayer {
                    playerId
                    killAssistsReceived
                  }
                  teamkills
                  teamkillAssistsGiven
                  teamkillAssistsReceived
                  selfkills
                  firstKill
                  structuresDestroyed
                  structuresCaptured
                  position {
                    x
                    y
                  }
                  inventory {
                    items {
                      id
                      name
                      quantity
                    }
                  }
                  objectives {
                    type
                    completionCount
                  }
                }
              }
              segments {
                id
                type
                sequenceNumber
                started
                finished
                startedAt
                duration
                draftActions {
                  id
                  type
                  sequenceNumber
                  drafter {
                    id
                    type
                  }
                  draftable {
                    id
                    type
                    name
                  }
                }
                teams {
                  id
                  name
                  side
                  won
                  kills
                  deaths
                  killAssistsGiven
                  killAssistsReceived
                  killAssistsReceivedFromPlayer {
                    playerId
                    killAssistsReceived
                  }
                  teamkills
                  teamkillAssistsGiven
                  teamkillAssistsReceived
                  selfkills
                  firstKill
                  objectives {
                    type
                    completionCount
                  }
                  players {
                    id
                    name
                    participationStatus
                    kills
                    deaths
                    killAssistsGiven
                    killAssistsReceived
                    killAssistsReceivedFromPlayer {
                      playerId
                      killAssistsReceived
                    }
                    teamkills
                    teamkillAssistsGiven
                    teamkillAssistsReceived
                    selfkills
                    firstKill
                    objectives {
                      type
                      completionCount
                    }
                  }
                }
              }
            }
          }
        }
        """, "variables": {"seriesId": series_id}}
        )
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"\nHTTP Error {response.status_code}")
            print(f"Response: {response.text}")
            response.raise_for_status()
        
        result = response.json()
        
        # Check for GraphQL errors
        if 'errors' in result:
            print(f"\nGraphQL Errors:")
            for error in result['errors']:
                print(f"  - {error.get('message', 'Unknown error')}")
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result['data']['seriesState']
    
    def download_series_events(self, series_id: str, output_path: Optional[str] = None) -> str:
        """
        Download series events file (JSONL format, zipped)
        
        Returns path to downloaded file
        """
        url = f"{self.file_download_base_url}/file-download/events/grid/series/{series_id}"
        
        response = requests.get(url, headers=self.headers, stream=True)
        response.raise_for_status()
        
        if output_path is None:
            output_path = f"events_{series_id}_grid.jsonl.zip"
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded events file: {output_path}")
        return output_path
    
    def download_series_end_state(self, series_id: str, output_path: Optional[str] = None) -> str:
        """
        Download series end state file (JSON format)
        
        Returns path to downloaded file
        """
        url = f"{self.file_download_base_url}/file-download/end-state/grid/series/{series_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        if output_path is None:
            output_path = f"end_state_{series_id}_grid.json"
        
        with open(output_path, 'w') as f:
            json.dump(response.json(), f, indent=2)
        
        print(f"Downloaded end state file: {output_path}")
        return output_path
    
    def download_series_end_state(self, series_id: str, output_path: Optional[str] = None) -> str:
        """
        Download series end state file (JSON format)
        
        Returns path to downloaded file
        """
        url = f"{self.file_download_base_url}/file-download/end-state/grid/series/{series_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        if output_path is None:
            output_path = f"end_state_{series_id}_grid.json"
        
        with open(output_path, 'w') as f:
            json.dump(response.json(), f, indent=2)
        
        print(f"Downloaded end state file: {output_path}")
        return output_path
    
    def download_riot_events(self, series_id: str, output_path: Optional[str] = None) -> str:
        """
        Download Riot's official LiveStats events file (JSONL format, zipped)
        This contains official Riot data for League of Legends matches
        
        Returns path to downloaded file
        """
        url = f"{self.file_download_base_url}/file-download/events/riot/series/{series_id}"
        
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            if output_path is None:
                output_path = f"events_{series_id}_riot.jsonl.zip"
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded Riot events file: {output_path}")
            return output_path
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  Riot events not available for series {series_id}")
                return None
            raise
    
    def download_riot_end_state(self, series_id: str, output_path: Optional[str] = None) -> str:
        """
        Download Riot's official Game Agnostic Match History file (JSON format, zipped)
        This contains official Riot end-game data for League of Legends matches
        
        Returns path to downloaded file
        """
        url = f"{self.file_download_base_url}/file-download/end-state/riot/series/{series_id}"
        
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            if output_path is None:
                output_path = f"end_state_{series_id}_riot.json.zip"
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded Riot end state file: {output_path}")
            return output_path
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  Riot end state not available for series {series_id}")
                return None
            raise
    
    def check_file_availability(self, series_id: str) -> Dict:
        """
        Check which files are available for a series
        """
        url = f"{self.file_download_base_url}/file-download/list/{series_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()


class EventProcessor:
    """Process GRID event files for analysis"""
    
    @staticmethod
    def parse_events_file(file_path: str) -> List[Dict]:
        """
        Parse a GRID events JSONL zip file
        
        Returns list of all events
        """
        events = []
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Get the JSONL file inside the zip
            jsonl_filename = zip_ref.namelist()[0]
            
            with zip_ref.open(jsonl_filename) as jsonl_file:
                for line in jsonl_file:
                    transaction = json.loads(line.decode('utf-8'))
                    
                    # Each transaction contains multiple events
                    for event in transaction.get('events', []):
                        event['transaction_id'] = transaction['id']
                        event['occurred_at'] = transaction['occurredAt']
                        event['sequence_number'] = transaction['sequenceNumber']
                        events.append(event)
        
        print(f"Parsed {len(events)} events from {file_path}")
        return events
    
    @staticmethod
    def filter_events_by_type(events: List[Dict], event_types: List[str]) -> List[Dict]:
        """Filter events by type"""
        return [e for e in events if e['type'] in event_types]
    
    @staticmethod
    def extract_kills(events: List[Dict]) -> List[Dict]:
        """Extract kill events with ALL relevant data including assists"""
        kill_events = EventProcessor.filter_events_by_type(
            events, 
            ['player-killed-player']
        )
        
        kills = []
        for event in kill_events:
            # Extract all participants (killer, victim, assisters)
            actor_state = event.get('actor', {}).get('state', {})
            target_state = event.get('target', {}).get('state', {})
            
            kill_data = {
                'timestamp': event['occurred_at'],
                'sequence_number': event.get('sequence_number'),
                'killer_id': event['actor']['id'],
                'victim_id': event['target']['id'],
                'killer_position': actor_state.get('position'),
                'victim_position': target_state.get('position'),
                'killer_team': actor_state.get('teamId'),
                'victim_team': target_state.get('teamId'),
                'killer_health': actor_state.get('health'),
                'killer_level': actor_state.get('level'),
                'victim_level': target_state.get('level'),
                'game_state': event.get('seriesState', {}),
                # Assists will be in separate events, but we track the kill
                'kill_type': event.get('type')
            }
            kills.append(kill_data)
        
        return kills
    
    @staticmethod
    def extract_objectives(events: List[Dict]) -> List[Dict]:
        """Extract objective completion events"""
        objective_types = [
            'player-completed-slayBaronNashor',
            'player-completed-slayCloudDrake',
            'player-completed-slayInfernalDrake',
            'player-completed-slayMountainDrake',
            'player-completed-slayOceanDrake',
            'player-completed-slayHextechDrake',
            'player-completed-slayChemtechDrake',
            'player-completed-slayElderDragon',
            'player-completed-slayRiftHerald',
            'player-completed-destroyTower',
            'player-completed-destroyInhibitor',
            'player-completed-destroyAncient',
            'team-destroyed-tower',
            'team-destroyed-inhibitor',
            'team-completed-destroyTurretPlateTop',
            'team-completed-destroyTurretPlateMid',
            'team-completed-destroyTurretPlateBot'
        ]
        
        objective_events = EventProcessor.filter_events_by_type(events, objective_types)
        
        objectives = []
        for event in objective_events:
            obj_data = {
                'timestamp': event['occurred_at'],
                'type': event['type'].replace('player-completed-', '').replace('team-completed-', '').replace('team-destroyed-', ''),
                'player_id': event.get('actor', {}).get('id'),
                'team_id': event.get('actor', {}).get('state', {}).get('teamId'),
                'position': event.get('actor', {}).get('state', {}).get('position'),
                'game_state': event.get('seriesState', {})
            }
            objectives.append(obj_data)
        
        return objectives
    
    @staticmethod
    def extract_ability_usage(events: List[Dict]) -> List[Dict]:
        """Extract ability/spell usage events"""
        ability_events = EventProcessor.filter_events_by_type(
            events,
            ['player-used-ability']
        )
        
        abilities = []
        for event in ability_events:
            ability_data = {
                'timestamp': event['occurred_at'],
                'player_id': event['actor']['id'],
                'ability_name': event['target'].get('name', 'Unknown'),
                'position': event['actor'].get('state', {}).get('position'),
                'game_state': event.get('seriesState', {})
            }
            abilities.append(ability_data)
        
        return abilities
    
    @staticmethod
    def extract_item_events(events: List[Dict]) -> List[Dict]:
        """Extract item purchase/pickup/drop events (for vision tracking)"""
        item_event_types = [
            'player-purchased-item',
            'player-picked-up-item',
            'player-dropped-item'
        ]
        
        item_events = EventProcessor.filter_events_by_type(events, item_event_types)
        
        items = []
        for event in item_events:
            item_data = {
                'timestamp': event['occurred_at'],
                'event_type': event['type'],
                'player_id': event['actor']['id'],
                'item_name': event['target'].get('name', 'Unknown'),
                'position': event['actor'].get('state', {}).get('position'),
                'game_state': event.get('seriesState', {})
            }
            items.append(item_data)
        
        return items
    
    @staticmethod
    def extract_position_timeline(events: List[Dict], player_id: str) -> List[Dict]:
        """Extract position timeline for a specific player"""
        positions = []
        
        for event in events:
            # Check if this event involves the player
            if event.get('actor', {}).get('id') == player_id:
                pos = event.get('actor', {}).get('state', {}).get('position')
                if pos:
                    positions.append({
                        'timestamp': event['occurred_at'],
                        'position': pos,
                        'event_type': event['type']
                    })
        
        return positions
    
    @staticmethod
    def extract_all_positions(events: List[Dict]) -> Dict:
        """Extract ALL position data for ALL players with timestamps"""
        player_positions = defaultdict(list)
        
        for event in events:
            # Get actor position
            actor = event.get('actor', {})
            if actor and actor.get('id'):
                actor_state = actor.get('state', {})
                position = actor_state.get('position')
                
                if position:
                    player_positions[actor['id']].append({
                        'timestamp': event.get('occurred_at'),
                        'sequence': event.get('sequence_number'),
                        'position': position,
                        'event_type': event['type'],
                        'team_id': actor_state.get('teamId'),
                        'health': actor_state.get('health'),
                        'level': actor_state.get('level')
                    })
            
            # Get target position (for kills, etc.)
            target = event.get('target', {})
            if target and target.get('id') and isinstance(target.get('state'), dict):
                target_state = target.get('state', {})
                position = target_state.get('position')
                
                if position:
                    player_positions[target['id']].append({
                        'timestamp': event.get('occurred_at'),
                        'sequence': event.get('sequence_number'),
                        'position': position,
                        'event_type': f"{event['type']}_target",
                        'team_id': target_state.get('teamId'),
                        'health': target_state.get('health'),
                        'level': target_state.get('level')
                    })
        
        return dict(player_positions)
    
    @staticmethod
    def extract_ward_events(events: List[Dict]) -> List[Dict]:
        """Extract ward-related item events for vision analysis"""
        ward_items = [
            'stealth ward', 'control ward', 'farsight alteration', 
            'oracle lens', 'warding totem', 'sweeping lens',
            'vision ward', 'sight ward'
        ]
        
        ward_events = []
        for event in events:
            if event['type'] in ['player-purchased-item', 'player-acquired-item', 'player-lost-item', 'player-pickedUp-item']:
                item_name = event.get('target', {}).get('name', '').lower()
                
                # Check if it's a ward-related item
                if any(ward in item_name for ward in ward_items):
                    ward_data = {
                        'timestamp': event['occurred_at'],
                        'event_type': event['type'],
                        'player_id': event.get('actor', {}).get('id'),
                        'team_id': event.get('actor', {}).get('state', {}).get('teamId'),
                        'position': event.get('actor', {}).get('state', {}).get('position'),
                        'item_name': event.get('target', {}).get('name'),
                        'game_state': event.get('seriesState', {})
                    }
                    ward_events.append(ward_data)
        
        return ward_events
    
    @staticmethod
    def extract_gold_events(events: List[Dict]) -> List[Dict]:
        """Extract gold-related events for economic analysis (from item purchases/sales)"""
        gold_events = []
        
        for event in events:
            if event['type'] in ['player-purchased-item', 'player-sold-item']:
                actor_state = event.get('actor', {}).get('state', {})
                data = {
                    'timestamp': event['occurred_at'],
                    'event_type': event['type'],
                    'player_id': event.get('actor', {}).get('id'),
                    'team_id': actor_state.get('teamId'),
                    'item_name': event.get('target', {}).get('name'),
                    'item_cost': event.get('target', {}).get('cost'),
                    'current_gold': actor_state.get('gold'),
                    'position': actor_state.get('position'),
                    'game_state': event.get('seriesState', {})
                }
                gold_events.append(data)
        
        return gold_events
    
    @staticmethod
    def extract_summoner_spell_events(events: List[Dict]) -> List[Dict]:
        """Extract summoner spell usage from ability events"""
        spell_events = []
        
        # Common summoner spell keywords
        summoner_keywords = [
            'flash', 'ignite', 'teleport', 'smite', 'heal', 
            'barrier', 'exhaust', 'cleanse', 'ghost', 'clarity'
        ]
        
        for event in events:
            if event['type'] == 'player-used-ability':
                ability_name = event.get('target', {}).get('name', '').lower()
                
                # Check if it's a summoner spell
                if any(keyword in ability_name for keyword in summoner_keywords):
                    spell_data = {
                        'timestamp': event['occurred_at'],
                        'player_id': event.get('actor', {}).get('id'),
                        'team_id': event.get('actor', {}).get('state', {}).get('teamId'),
                        'spell_name': event.get('target', {}).get('name'),
                        'position': event.get('actor', {}).get('state', {}).get('position'),
                        'game_state': event.get('seriesState', {})
                    }
                    spell_events.append(spell_data)
        
        return spell_events
    
    @staticmethod
    def extract_level_events(events: List[Dict]) -> List[Dict]:
        """Extract level-up events for progression analysis"""
        level_events = EventProcessor.filter_events_by_type(events, ['player-completed-increaseLevel'])
        
        levels = []
        for event in level_events:
            level_data = {
                'timestamp': event['occurred_at'],
                'player_id': event.get('actor', {}).get('id'),
                'team_id': event.get('actor', {}).get('state', {}).get('teamId'),
                'new_level': event.get('actor', {}).get('state', {}).get('level'),
                'position': event.get('actor', {}).get('state', {}).get('position'),
                'game_state': event.get('seriesState', {})
            }
            levels.append(level_data)
        
        return levels
    
    @staticmethod
    def extract_draft_events(events: List[Dict]) -> List[Dict]:
        """Extract draft phase events (picks and bans)"""
        draft_event_types = [
            'player-picked-character',
            'player-banned-character',
            'team-picked-character',
            'team-banned-character',
            'team-picked-map',
            'team-banned-map'
        ]
        
        draft_events = EventProcessor.filter_events_by_type(events, draft_event_types)
        
        drafts = []
        for event in draft_events:
            draft_data = {
                'timestamp': event['occurred_at'],
                'sequence_number': event.get('sequence_number'),
                'event_type': event['type'],
                'actor_id': event.get('actor', {}).get('id'),
                'actor_type': event.get('actor', {}).get('type'),
                'team_id': event.get('actor', {}).get('state', {}).get('teamId') if event.get('actor', {}).get('state') else None,
                'target_id': event.get('target', {}).get('id'),
                'target_name': event.get('target', {}).get('name'),
                'target_type': event.get('target', {}).get('type'),
                'game_state': event.get('seriesState', {})
            }
            drafts.append(draft_data)
        
        return drafts
    
    @staticmethod
    def extract_assist_details(events: List[Dict]) -> List[Dict]:
        """Extract detailed assist information from kill events"""
        kill_events = EventProcessor.filter_events_by_type(events, ['player-killed-player'])
        
        assists = []
        for event in kill_events:
            # Look for assist information in the event
            actor_state = event.get('actor', {}).get('state', {})
            target_state = event.get('target', {}).get('state', {})
            
            # Check if there's assist data in the series state delta
            series_state_delta = event.get('seriesStateDelta', {})
            
            assist_data = {
                'timestamp': event['occurred_at'],
                'sequence_number': event.get('sequence_number'),
                'killer_id': event['actor']['id'],
                'victim_id': event['target']['id'],
                'killer_team': actor_state.get('teamId'),
                'victim_team': target_state.get('teamId'),
                'position': actor_state.get('position'),
                'game_state': event.get('seriesState', {}),
                'series_state_delta': series_state_delta
            }
            assists.append(assist_data)
        
        return assists
    
    @staticmethod
    def extract_structure_events(events: List[Dict]) -> List[Dict]:
        """Extract structure destruction events (turrets, inhibitors, nexus)"""
        structure_event_types = [
            'player-destroyed-tower',
            'player-destroyed-inhibitor',
            'player-destroyed-nexus',
            'team-destroyed-tower',
            'team-destroyed-inhibitor',
            'team-destroyed-nexus',
            'player-completed-destroyTower',
            'player-completed-destroyInhibitor',
            'player-completed-destroyAncient',
            'team-completed-destroyTurretPlateTop',
            'team-completed-destroyTurretPlateMid',
            'team-completed-destroyTurretPlateBot'
        ]
        
        structure_events = EventProcessor.filter_events_by_type(events, structure_event_types)
        
        structures = []
        for event in structure_events:
            actor_state = event.get('actor', {}).get('state', {})
            
            structure_data = {
                'timestamp': event['occurred_at'],
                'sequence_number': event.get('sequence_number'),
                'event_type': event['type'],
                'actor_id': event.get('actor', {}).get('id'),
                'actor_type': event.get('actor', {}).get('type'),
                'team_id': actor_state.get('teamId'),
                'structure_type': event.get('target', {}).get('type'),
                'structure_name': event.get('target', {}).get('name'),
                'position': actor_state.get('position'),
                'game_state': event.get('seriesState', {})
            }
            structures.append(structure_data)
        
        return structures
    
    @staticmethod
    def extract_vision_events(events: List[Dict]) -> List[Dict]:
        """Extract vision-related events (ward placements, destructions, sweeps)"""
        vision_event_types = [
            'player-placed-ward',
            'player-destroyed-ward',
            'player-used-trinket',
            'player-purchased-item',  # For control wards
            'player-acquired-item',
            'player-lost-item'
        ]
        
        vision_events = []
        
        for event in events:
            if event['type'] in vision_event_types:
                actor_state = event.get('actor', {}).get('state', {})
                target = event.get('target', {})
                
                # Check if it's a ward-related item or action
                target_name = target.get('name', '').lower() if target else ''
                is_ward_related = any(ward in target_name for ward in [
                    'ward', 'trinket', 'lens', 'totem', 'farsight', 'oracle', 'sweeping'
                ])
                
                if is_ward_related or event['type'] in ['player-placed-ward', 'player-destroyed-ward']:
                    vision_data = {
                        'timestamp': event['occurred_at'],
                        'sequence_number': event.get('sequence_number'),
                        'event_type': event['type'],
                        'player_id': event.get('actor', {}).get('id'),
                        'team_id': actor_state.get('teamId'),
                        'item_name': target.get('name'),
                        'item_type': target.get('type'),
                        'position': actor_state.get('position'),
                        'game_state': event.get('seriesState', {})
                    }
                    vision_events.append(vision_data)
        
        return vision_events
    
    @staticmethod
    def extract_gold_timeline(events: List[Dict]) -> List[Dict]:
        """Extract gold progression over time for all players"""
        gold_timeline = []
        
        for event in events:
            actor = event.get('actor', {})
            if actor and actor.get('id'):
                actor_state = actor.get('state', {})
                gold = actor_state.get('gold')
                
                if gold is not None:
                    gold_data = {
                        'timestamp': event['occurred_at'],
                        'sequence_number': event.get('sequence_number'),
                        'player_id': actor['id'],
                        'team_id': actor_state.get('teamId'),
                        'gold': gold,
                        'net_worth': actor_state.get('netWorth'),
                        'inventory_value': actor_state.get('inventoryValue'),
                        'event_type': event['type'],
                        'position': actor_state.get('position')
                    }
                    gold_timeline.append(gold_data)
        
        return gold_timeline
    
    @staticmethod
    def extract_experience_timeline(events: List[Dict]) -> List[Dict]:
        """Extract experience and level progression over time"""
        exp_timeline = []
        
        for event in events:
            actor = event.get('actor', {})
            if actor and actor.get('id'):
                actor_state = actor.get('state', {})
                experience = actor_state.get('experience')
                level = actor_state.get('level')
                
                if experience is not None or level is not None:
                    exp_data = {
                        'timestamp': event['occurred_at'],
                        'sequence_number': event.get('sequence_number'),
                        'player_id': actor['id'],
                        'team_id': actor_state.get('teamId'),
                        'experience': experience,
                        'level': level,
                        'event_type': event['type'],
                        'position': actor_state.get('position')
                    }
                    exp_timeline.append(exp_data)
        
        return exp_timeline


class PorolyticsDataCollector:
    """High-level data collector for Porolytics analysis"""
    
    def __init__(self, api_key: str):
        self.client = GridAPIClient(api_key)
        self.processor = EventProcessor()
    
    def collect_team_data(
        self,
        team_id: str,
        num_matches: int = 20,
        title_id: int = 3,
        download_events: bool = True
    ) -> Dict:
        """
        Collect all data needed for a team analysis
        
        Args:
            team_id: GRID team ID
            num_matches: Number of recent matches to analyze
            title_id: 3 for LoL, 6 for Valorant
            download_events: Whether to download full event files
        
        Returns:
            Dictionary with all collected data
        """
        print(f"\n{'='*60}")
        print(f"Collecting data for team {team_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Get series list
        print("Step 1: Fetching series list...")
        series_list = self.client.get_team_series(
            team_id=team_id,
            title_id=title_id,
            limit=min(num_matches, 50)
        )
        
        collected_data = {
            'team_id': team_id,
            'collection_date': datetime.now().isoformat(),
            'series': []
        }
        
        # Step 2: Process each series
        for idx, series in enumerate(series_list[:num_matches], 1):
            series_id = series['id']
            print(f"\nProcessing series {idx}/{num_matches}: {series_id}")
            print(f"  Tournament: {series['tournament']['name']}")
            print(f"  Date: {series['startTimeScheduled']}")
            
            series_data = {
                'series_id': series_id,
                'metadata': series,
                'state': None,
                'events': None,
                'processed': {}
            }
            
            # Check file availability
            try:
                availability = self.client.check_file_availability(series_id)
                print(f"  File availability: {availability}")
            except Exception as e:
                print(f"  Warning: Could not check availability: {e}")
            
            # Get series state
            try:
                print("  Fetching series state...")
                series_data['state'] = self.client.get_series_state(series_id)
            except Exception as e:
                print(f"  Error fetching state: {e}")
            
            # Download and process events
            if download_events:
                try:
                    # Download GRID events
                    print("  Downloading GRID events file...")
                    events_file = self.client.download_series_events(
                        series_id,
                        output_path=f"data/events_{series_id}.jsonl.zip"
                    )
                    
                    # Download GRID end state
                    print("  Downloading GRID end state...")
                    try:
                        self.client.download_series_end_state(
                            series_id,
                            output_path=f"data/end_state_{series_id}_grid.json"
                        )
                    except Exception as e:
                        print(f"  Warning: Could not download GRID end state: {e}")
                    
                    # Download Riot official files (if available)
                    print("  Downloading Riot official events (if available)...")
                    riot_events = self.client.download_riot_events(
                        series_id,
                        output_path=f"data/events_{series_id}_riot.jsonl.zip"
                    )
                    
                    print("  Downloading Riot official end state (if available)...")
                    riot_end_state = self.client.download_riot_end_state(
                        series_id,
                        output_path=f"data/end_state_{series_id}_riot.json.zip"
                    )
                    
                    print("  Parsing events...")
                    events = self.processor.parse_events_file(events_file)
                    series_data['events'] = events
                    
                    # Extract specific data types for Porolytics analysis
                    print("  Extracting kills...")
                    series_data['processed']['kills'] = self.processor.extract_kills(events)
                    
                    print("  Extracting objectives...")
                    series_data['processed']['objectives'] = self.processor.extract_objectives(events)
                    
                    print("  Extracting abilities...")
                    series_data['processed']['abilities'] = self.processor.extract_ability_usage(events)
                    
                    print("  Extracting items...")
                    series_data['processed']['items'] = self.processor.extract_item_events(events)
                    
                    print("  Extracting ward items (vision system)...")
                    series_data['processed']['wards'] = self.processor.extract_ward_events(events)
                    
                    print("  Extracting gold/economy events...")
                    series_data['processed']['gold'] = self.processor.extract_gold_events(events)
                    
                    print("  Extracting summoner spells...")
                    series_data['processed']['summoner_spells'] = self.processor.extract_summoner_spell_events(events)
                    
                    print("  Extracting level progression...")
                    series_data['processed']['levels'] = self.processor.extract_level_events(events)
                    
                    print("  Extracting draft phase (picks/bans)...")
                    series_data['processed']['draft'] = self.processor.extract_draft_events(events)
                    
                    print("  Extracting detailed assist data...")
                    series_data['processed']['assist_details'] = self.processor.extract_assist_details(events)
                    
                    print("  Extracting structure destruction events...")
                    series_data['processed']['structures'] = self.processor.extract_structure_events(events)
                    
                    print("  Extracting vision control events...")
                    series_data['processed']['vision'] = self.processor.extract_vision_events(events)
                    
                    print("  Extracting gold timeline...")
                    series_data['processed']['gold_timeline'] = self.processor.extract_gold_timeline(events)
                    
                    print("  Extracting experience timeline...")
                    series_data['processed']['exp_timeline'] = self.processor.extract_experience_timeline(events)
                    
                    print("  Extracting ALL player positions with timestamps...")
                    series_data['processed']['all_positions'] = self.processor.extract_all_positions(events)
                    
                    print(f"  Processed: {len(series_data['processed']['kills'])} kills, "
                          f"{len(series_data['processed']['objectives'])} objectives, "
                          f"{len(series_data['processed']['draft'])} draft actions, "
                          f"{len(series_data['processed']['structures'])} structure events, "
                          f"{len(series_data['processed']['vision'])} vision events, "
                          f"{len(series_data['processed']['gold_timeline'])} gold snapshots, "
                          f"{len(series_data['processed']['exp_timeline'])} exp snapshots, "
                          f"{len(series_data['processed']['all_positions'])} players tracked")
                    
                except Exception as e:
                    print(f"  Error processing events: {e}")
            
            collected_data['series'].append(series_data)
            
            # Rate limiting
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"Data collection complete!")
        print(f"Collected {len(collected_data['series'])} series")
        print(f"{'='*60}\n")
        
        return collected_data
    
    def save_collected_data(self, data: Dict, output_path: str):
        """Save collected data to JSON file"""
        # Remove raw events to reduce file size (they're already saved separately)
        data_copy = json.loads(json.dumps(data))
        for series in data_copy['series']:
            if 'events' in series:
                series['events'] = f"See events_{series['series_id']}.jsonl.zip"
        
        with open(output_path, 'w') as f:
            json.dump(data_copy, f, indent=2)
        
        print(f"Saved collected data to {output_path}")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def test_connection(api_key: str) -> bool:
    """Test API connection and verify it's working"""
    print("\n" + "="*60)
    print("Testing GRID API Connection")
    print("="*60 + "\n")
    
    client = GridAPIClient(api_key)
    
    try:
        # Test 1: Get titles
        print("Test 1: Fetching available titles...")
        query = """
        {
          titles {
            id
            name
            nameShortened
          }
        }
        """
        result = client._graphql_request(query)
        
        if 'data' in result and 'titles' in result['data']:
            print("✓ Connection successful!")
            print("\nAvailable titles:")
            for title in result['data']['titles']:
                print(f"  ID {title['id']}: {title['name']} ({title['nameShortened']})")
        else:
            print("✗ Unexpected response format")
            return False
        
        # Test 2: Get recent series
        print("\n" + "-"*60)
        print("Test 2: Fetching recent LoL series...")
        query = """
        {
          allSeries(
            first: 3,
            filter: {
              titleIds: { in: [3] }
              types: ESPORTS
            }
            orderBy: StartTimeScheduled
            orderDirection: DESC
          ) {
            edges {
              node {
                id
                startTimeScheduled
                tournament {
                  name
                }
                teams {
                  baseInfo {
                    name
                  }
                }
              }
            }
          }
        }
        """
        result = client._graphql_request(query)
        
        if 'data' in result and 'allSeries' in result['data']:
            series_list = result['data']['allSeries']['edges']
            print(f"✓ Found {len(series_list)} recent series:")
            for edge in series_list:
                series = edge['node']
                teams = ' vs '.join([t['baseInfo']['name'] for t in series['teams']])
                print(f"  {series['id']}: {teams}")
                print(f"    {series['tournament']['name']}")
        else:
            print("✗ Unexpected response format")
            return False
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def find_teams(api_key: str, search_term: str, title_id: int = 3) -> List[Dict]:
    """Search for teams by name"""
    print(f"\nSearching for '{search_term}' in {'LoL' if title_id == 3 else 'Valorant' if title_id == 6 else f'Title {title_id}'}...")
    
    client = GridAPIClient(api_key)
    
    query = f"""
    {{
      teams(
        first: 20,
        filter: {{
          name: {{ contains: "{search_term}" }}
          titleId: {title_id}
        }}
      ) {{
        edges {{
          node {{
            id
            name
            nameShortened
          }}
        }}
      }}
    }}
    """
    
    try:
        result = client._graphql_request(query)
        teams = result['data']['teams']['edges']
        
        if not teams:
            print(f"No teams found matching '{search_term}'")
            return []
        
        print(f"\nFound {len(teams)} team(s):")
        print("="*60)
        for edge in teams:
            team = edge['node']
            print(f"ID: {team['id']:6s} | {team['name']}")
            if team.get('nameShortened'):
                print(f"         Short: {team['nameShortened']}")
            print("-"*60)
        
        return teams
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def quick_test_interactive(api_key: str):
    """Interactive quick test - select a popular team and fetch 1 match"""
    POPULAR_TEAMS = {
        '1': ('47494', 'T1', 'Korea - World Champions'),
        '2': ('47351', 'Cloud9 Kia', 'North America'),
        '3': ('47380', 'G2 Esports', 'Europe'),
        '4': ('47558', 'Gen.G Esports', 'Korea'),
        '5': ('356', 'BILIBILI GAMING', 'China'),
        '6': ('340', 'FlyQuest', 'North America'),
        '7': ('47376', 'Fnatic', 'Europe'),
        '8': ('48179', 'Dplus KIA', 'Korea'),
    }
    
    print("\n" + "="*70)
    print("QUICK TEST - Fetch Single Match Data")
    print("="*70 + "\n")
    
    print("Select a team to test:\n")
    for key, (team_id, name, region) in POPULAR_TEAMS.items():
        print(f"  {key}. {name} ({region})")
    
    print(f"\n  0. Custom team ID")
    print()
    
    choice = input("Enter your choice (1-8 or 0): ").strip()
    
    if choice == '0':
        team_id = input("Enter team ID: ").strip()
        team_name = f"Team_{team_id}"
    elif choice in POPULAR_TEAMS:
        team_id, team_name, region = POPULAR_TEAMS[choice]
        print(f"\n✅ Selected: {team_name} ({region})")
    else:
        print("❌ Invalid choice!")
        return
    
    # Create test_data directory
    os.makedirs('test_data', exist_ok=True)
    
    print(f"\nFetching 1 recent match for {team_name}...\n")
    
    try:
        collector = PorolyticsDataCollector(api_key)
        data = collector.collect_team_data(
            team_id=team_id,
            num_matches=1,
            title_id=3,
            download_events=True
        )
        
        if data['series']:
            output_file = f'test_data/test_{team_id}_{team_name.replace(" ", "_")}.json'
            collector.save_collected_data(data, output_file)
            
            # Display summary
            series = data['series'][0]
            print(f"\n{'='*70}")
            print(f"SUMMARY")
            print(f"{'='*70}")
            print(f"Series: {series['series_id']}")
            if series.get('processed'):
                print(f"  Total events: {len(series.get('events', []))}")
                print(f"  Kills: {len(series['processed'].get('kills', []))}")
                print(f"  Objectives: {len(series['processed'].get('objectives', []))}")
                print(f"  Draft actions: {len(series['processed'].get('draft', []))}")
            
            print(f"\n{'='*70}")
            print(f"✅ TEST COMPLETE!")
            print(f"{'='*70}")
            print(f"\nFiles saved in: test_data/")
            print(f"Results saved in: {output_file}")
        else:
            print("\n❌ No data fetched!")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Grid API Data Fetcher - Flexible data collection for League of Legends esports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test connection
  python grid_data_fetcher.py --test
  
  # Find teams
  python grid_data_fetcher.py --find "Cloud9"
  
  # Quick interactive test
  python grid_data_fetcher.py --quick-test
  
  # Fetch data for a single team
  python grid_data_fetcher.py --team-id 47494 --team-name T1 --num-matches 10
  
  # Fetch data for multiple teams
  python grid_data_fetcher.py --team-ids 47494,47351,47380 --num-matches 5
  
  # Fetch specific series
  python grid_data_fetcher.py --series-id 2847265
  
  # Fetch team data from specific tournament
  python grid_data_fetcher.py --team-id 47494 --tournament-id 12345
  
  # Fetch for Valorant instead of LoL
  python grid_data_fetcher.py --team-id 47494 --title-id 6
  
  # Use as library in your code:
  from grid_data_fetcher import PorolyticsDataCollector
  collector = PorolyticsDataCollector(api_key)
  data = collector.collect_team_data(team_id="47494", num_matches=10)
        """
    )
    
    # Utility commands
    parser.add_argument('--test', action='store_true', help='Test API connection')
    parser.add_argument('--find', type=str, metavar='TEAM_NAME', help='Search for teams by name')
    parser.add_argument('--quick-test', action='store_true', help='Interactive quick test (select team from menu)')
    
    # Data fetching commands
    parser.add_argument('--team-id', type=str, help='Single team ID to fetch data for')
    parser.add_argument('--team-name', type=str, help='Team name (for output file naming)')
    parser.add_argument('--team-ids', type=str, help='Comma-separated list of team IDs')
    parser.add_argument('--series-id', type=str, help='Specific series ID to fetch')
    parser.add_argument('--tournament-id', type=str, help='Tournament ID (requires --team-id)')
    parser.add_argument('--num-matches', type=int, default=20, help='Number of matches per team (default: 20)')
    parser.add_argument('--title-id', type=int, default=3, help='Title ID: 3=LoL, 6=Valorant (default: 3)')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory (default: data)')
    parser.add_argument('--no-events', action='store_true', help='Skip downloading event files (faster)')
    
    args = parser.parse_args()
    
    # Load API key
    API_KEY = os.getenv('GRID_API_KEY')
    if not API_KEY:
        print("❌ ERROR: GRID_API_KEY not found in .env file")
        print("Please create a .env file with your API key:")
        print("  GRID_API_KEY=your_api_key_here")
        print("\nGet your API key from: https://grid.gg/")
        exit(1)
    
    # Handle utility commands
    if args.test:
        test_connection(API_KEY)
        exit(0)
    
    if args.find:
        find_teams(API_KEY, args.find, args.title_id)
        exit(0)
    
    if args.quick_test:
        quick_test_interactive(API_KEY)
        exit(0)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize collector
    collector = PorolyticsDataCollector(API_KEY)
    
    # Determine what to fetch
    teams_to_fetch = []
    
    if args.series_id:
        # Fetch specific series
        print(f"\n{'='*60}")
        print(f"Fetching series: {args.series_id}")
        print(f"{'='*60}\n")
        
        try:
            # Use the client directly for single series
            client = GridAPIClient(API_KEY)
            processor = EventProcessor()
            
            # Get series state
            state = client.get_series_state(args.series_id)
            
            # Download files
            events_file = client.download_series_events(
                args.series_id,
                output_path=f"{args.output_dir}/events_{args.series_id}_grid.jsonl.zip"
            )
            
            client.download_series_end_state(
                args.series_id,
                output_path=f"{args.output_dir}/end_state_{args.series_id}_grid.json"
            )
            
            # Try Riot files
            try:
                client.download_riot_events(args.series_id, f"{args.output_dir}/events_{args.series_id}_riot.jsonl.zip")
                client.download_riot_end_state(args.series_id, f"{args.output_dir}/end_state_{args.series_id}_riot.json.zip")
            except:
                pass
            
            print(f"\n✅ Series {args.series_id} downloaded successfully!")
            print(f"Files saved in: {args.output_dir}/")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            exit(1)
    
    elif args.team_id:
        # Single team
        team_name = args.team_name or f"Team_{args.team_id}"
        teams_to_fetch.append((args.team_id, team_name))
    
    elif args.team_ids:
        # Multiple teams
        team_ids = args.team_ids.split(',')
        for team_id in team_ids:
            team_id = team_id.strip()
            teams_to_fetch.append((team_id, f"Team_{team_id}"))
    
    else:
        print("❌ ERROR: Must provide --team-id, --team-ids, or --series-id")
        parser.print_help()
        exit(1)
    
    # Fetch data for teams
    if teams_to_fetch:
        print(f"\n{'='*60}")
        print(f"GRID API DATA COLLECTION")
        print(f"{'='*60}")
        print(f"Teams: {len(teams_to_fetch)}")
        print(f"Matches per team: {args.num_matches}")
        print(f"Title: {'League of Legends' if args.title_id == 3 else 'Valorant' if args.title_id == 6 else f'Title {args.title_id}'}")
        print(f"Output: {args.output_dir}/")
        print(f"{'='*60}\n")
        
        for idx, (team_id, team_name) in enumerate(teams_to_fetch, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(teams_to_fetch)}] {team_name} (ID: {team_id})")
            print(f"{'='*60}\n")
            
            try:
                # Collect data
                data = collector.collect_team_data(
                    team_id=team_id,
                    num_matches=args.num_matches,
                    title_id=args.title_id,
                    download_events=not args.no_events
                )
                
                # Save results
                output_file = f"{args.output_dir}/team_{team_id}_{team_name}_analysis.json"
                collector.save_collected_data(data, output_file)
                
                print(f"\n✅ {team_name} complete!")
                print(f"   Saved to: {output_file}")
                
            except Exception as e:
                print(f"❌ Error collecting data for {team_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ DATA COLLECTION COMPLETE!")
        print(f"{'='*60}")
        print(f"Files saved in: {args.output_dir}/")
        print(f"\nTo analyze the data:")
        print(f"  python porolytics_analyzer.py {args.output_dir}/team_<ID>_<NAME>_analysis.json")
        print(f"{'='*60}")
