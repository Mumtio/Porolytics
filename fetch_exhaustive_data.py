import os
import json
import time
import shutil
from grid_data_fetcher import PorolyticsDataCollector, GridAPIClient
from dotenv import load_dotenv
from datetime import datetime

def move_files_to_team_folder(team_folder):
    if not os.path.exists('data'):
        return
    data_files = os.listdir('data')
    if not data_files:
        return
    for file in data_files:
        src = os.path.join('data', file)
        dst = os.path.join(team_folder, file)
        try:
            if os.path.exists(dst):
                os.remove(dst) # Overwrite if exists to ensure latest
            shutil.move(src, dst)
        except Exception as e:
            print(f"      Error moving {file}: {e}")

def get_all_series(client, team_id, title_id=3):
    all_series = []
    has_next_page = True
    after_cursor = None
    
    print(f"Fetching all series for team {team_id}...")
    
    while has_next_page:
        cursor_str = f', after: "{after_cursor}"' if after_cursor else ""
        query = f"""
        {{
          allSeries(
            first: 50
            {cursor_str}
            filter: {{ 
                titleIds: {{ in: [{title_id}] }},
                teamIds: {{ in: ["{team_id}"] }},
                types: ESPORTS
            }}
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
                tournament {{
                  name
                }}
              }}
            }}
          }}
        }}
        """
        result = client._graphql_request(query)
        data = result['data']['allSeries']
        
        edges = data['edges']
        for edge in edges:
            all_series.append(edge['node'])
        
        has_next_page = data['pageInfo']['hasNextPage']
        after_cursor = data['pageInfo']['endCursor']
        
        print(f"  Fetched {len(all_series)} / {data['totalCount']} series...")
        
        if not has_next_page:
            break
            
        time.sleep(0.5) # Small delay for rate limiting
        
    return all_series

def fetch_exhaustive_for_team(team_id, team_name, api_key):
    print(f"\n{'#'*60}")
    print(f"EXHAUSTIVE FETCH: {team_name} ({team_id})")
    print(f"{'#'*60}\n")
    
    client = GridAPIClient(api_key)
    collector = PorolyticsDataCollector(api_key)
    
    output_base_dir = 'matches_data'
    team_folder = os.path.join(output_base_dir, team_name)
    os.makedirs(team_folder, exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    series_list = get_all_series(client, team_id)
    print(f"Total series found: {len(series_list)}")
    
    # Track what we already have to avoid redundant downloads if possible
    # However, collector.collect_team_data doesn't easily support skipping
    # We'll just let it run.
    
    # We can't use collector.collect_team_data directly because it fetches the list again
    # and has its own limit. Let's process series by series.
    
    collected_data = {
        'team_id': team_id,
        'collection_date': datetime.now().isoformat(),
        'series': []
    }
    
    # Sort series by date to process newest first if desired, or keep as is
    # series_list.sort(key=lambda x: x['startTimeScheduled'], reverse=True)
    
    # Check what we already have
    existing_events = {f.replace('events_', '').replace('.jsonl.zip', '') for f in os.listdir(team_folder) if f.startswith('events_')}
    
    for idx, series in enumerate(series_list, 1):
        series_id = series['id']
        
        if series_id in existing_events:
             # print(f"[{idx}/{len(series_list)}] Series {series_id} already exists.")
             continue

        print(f"[{idx}/{len(series_list)}] Downloading {series_id} ({series.get('startTimeScheduled', 'N/A')})...", end='', flush=True)
        
        try:
            # Download files directly to team folder to avoid move overhead
            # Fetching only the essential files to speed up the process
            client.download_series_events(series_id, output_path=os.path.join(team_folder, f"events_{series_id}.jsonl.zip"))
            client.download_series_end_state(series_id, output_path=os.path.join(team_folder, f"end_state_{series_id}_grid.json"))
            
            print(" ✅")
            
            # Very short delay to respect API but maintain speed
            time.sleep(0.2)
            
        except Exception as e:
            print(f" ❌ ({e})")

    print(f"Exhaustive fetch for {team_name} complete!")

def main():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    if not api_key:
        print("GRID_API_KEY not found")
        return
        
    teams = {
        '47494': 'T1',
        '47351': 'Cloud9_Kia'
    }
    
    for team_id, team_name in teams.items():
        fetch_exhaustive_for_team(team_id, team_name, api_key)

if __name__ == "__main__":
    main()
