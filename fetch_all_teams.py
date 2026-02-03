import os
import json
from grid_data_fetcher import PorolyticsDataCollector, GridAPIClient
from dotenv import load_dotenv

def move_existing_files(team_name, team_folder):
    import shutil
    if not os.path.exists('data'):
        return
    data_files = os.listdir('data')
    if not data_files:
        return
    print(f"    Moving {len(data_files)} existing files to {team_folder}...")
    for file in data_files:
        src = os.path.join('data', file)
        dst = os.path.join(team_folder, file)
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"      Error moving {file}: {e}")

def fetch_all_data():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    if not api_key:
        print("❌ Error: GRID_API_KEY not found in .env")
        return

    # Popular teams from grid_data_fetcher.py
    POPULAR_TEAMS = {
        '47380': 'G2_Esports',
        '47558': 'Gen.G_Esports',
        '356': 'BILIBILI_GAMING',
        '340': 'FlyQuest',
        '47376': 'Fnatic',
        '48179': 'Dplus_KIA',
    }

    collector = PorolyticsDataCollector(api_key)
    output_base_dir = 'matches_data'
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Ensure 'data' directory exists
    os.makedirs('data', exist_ok=True)

    print(f"Starting raw data extraction for {len(POPULAR_TEAMS)} teams...")

    for team_id, team_name in POPULAR_TEAMS.items():
        print(f"\n>>> Processing {team_name} (ID: {team_id})")
        
        # Create team-specific folder
        team_folder = os.path.join(output_base_dir, team_name)
        os.makedirs(team_folder, exist_ok=True)
        
        # FIRST: Move anything already in data/ to the right folder
        # (This helps if we timed out previously)
        move_existing_files(team_name, team_folder)

        try:
            # Collect ALL available data for the team (limit to 10 for reliability in this environment)
            num_matches = 10
            print(f"    Fetching ALL available matches (up to {num_matches})...")
            
            data = collector.collect_team_data(
                team_id=team_id,
                num_matches=num_matches,
                title_id=3,
                download_events=True
            )

            # Save the summarized data file
            summary_file = os.path.join(team_folder, f"team_{team_id}_{team_name}_summary.json")
            collector.save_collected_data(data, summary_file)

            # Move files downloaded in this batch
            move_existing_files(team_name, team_folder)
            
            print(f"    ✅ Raw data for {team_name} complete")

        except Exception as e:
            print(f"    ❌ Error for {team_name}: {e}")

    print("\n✅ All teams processed!")

if __name__ == "__main__":
    fetch_all_data()
