"""
Porolytics Analyzer - AI-Powered Opponent Analysis
Implements all 9 analysis features with realistic approaches
"""

import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import statistics


class PorolyticsAnalyzer:
    """Main analyzer for opponent scouting"""
    
    def __init__(self, team_data_path: str):
        """Load team data from JSON file"""
        with open(team_data_path, 'r') as f:
            self.data = json.load(f)
        
        self.team_id = self.data['team_id']
        self.series = self.data['series']
    
    def analyze_all(self) -> Dict:
        """Run all analyses and return complete report"""
        return {
            'team_id': self.team_id,
            'team_identity': self.analyze_team_identity(),
            'winning_recipe': self.analyze_winning_recipe(),
            'vision_investment': self.analyze_vision_investment(),
            'roaming_system': self.analyze_roaming_system(),
            'champion_dependency': self.analyze_champion_dependency(),
            'losing_recipe': self.analyze_losing_recipe(),
            'role_correlation': self.analyze_role_correlation(),
            'break_strategy': self.generate_break_strategy(),
            'draft_gameplan': self.generate_draft_gameplan()
        }

    
    # ========================================
    # 1. TEAM IDENTITY
    # ========================================
    
    def analyze_team_identity(self) -> Dict:
        """Analyze gold distribution and role impact"""
        print("Analyzing Team Identity...")
        
        role_stats = defaultdict(lambda: {
            'total_gold': 0,
            'kills': 0,
            'deaths': 0,
            'objectives': 0,
            'games': 0,
            'wins': 0
        })
        
        for series in self.series:
            if not series.get('state'):
                continue
            
            won = series['state']['teams'][0]['won']
            
            for game in series['state'].get('games', []):
                for player in game['teams'][0]['players']:
                    # Infer role from position (simplified)
                    role = self._infer_role(player)
                    
                    role_stats[role]['games'] += 1
                    role_stats[role]['kills'] += player.get('kills', 0)
                    role_stats[role]['deaths'] += player.get('deaths', 0)
                    if won:
                        role_stats[role]['wins'] += 1
        
        # Calculate gold distribution from purchases
        for series in self.series:
            for event in series['processed'].get('gold', []):
                role = self._get_role_from_player(event.get('player_id'), series)
                if role:
                    cost = event.get('item_cost') or 0
                    role_stats[role]['total_gold'] += cost
        
        # Calculate metrics
        total_gold = sum(stats['total_gold'] for stats in role_stats.values())
        
        identity = {}
        for role, stats in role_stats.items():
            if stats['games'] > 0:
                identity[role] = {
                    'gold_share': (stats['total_gold'] / total_gold * 100) if total_gold > 0 else 0,
                    'avg_kills': stats['kills'] / stats['games'],
                    'avg_deaths': stats['deaths'] / stats['games'],
                    'win_rate': (stats['wins'] / stats['games'] * 100) if stats['games'] > 0 else 0
                }
        
        # Identify primary win condition
        primary_role = max(identity.items(), key=lambda x: x[1]['gold_share'])[0]
        secondary_role = sorted(identity.items(), key=lambda x: x[1]['gold_share'], reverse=True)[1][0]
        sacrificed_role = min(identity.items(), key=lambda x: x[1]['gold_share'])[0]
        
        return {
            'role_distribution': identity,
            'primary_win_condition': primary_role,
            'secondary_plan': secondary_role,
            'sacrificed_lane': sacrificed_role,
            'summary': f"Primary: {primary_role}, Secondary: {secondary_role}, Sacrificed: {sacrificed_role}"
        }

    
    # ========================================
    # 2. WINNING RECIPE (Frequent Pattern Mining)
    # ========================================
    
    def analyze_winning_recipe(self) -> Dict:
        """Find frequent winning patterns using sequence mining"""
        print("Analyzing Winning Recipe...")
        
        win_sequences = []
        
        for series in self.series:
            if not series.get('state') or not series['state']['teams'][0]['won']:
                continue
            
            # Extract objective sequence
            objectives = sorted(series['processed'].get('objectives', []), 
                              key=lambda x: x['timestamp'])
            
            sequence = []
            for obj in objectives:
                obj_type = obj['type'].replace('slay', '').replace('destroy', '')
                sequence.append(obj_type)
            
            if sequence:
                win_sequences.append(sequence)
        
        # Find frequent patterns (simplified FP-Growth)
        patterns = self._find_frequent_patterns(win_sequences, min_support=0.3)
        
        return {
            'total_wins': len(win_sequences),
            'frequent_patterns': patterns[:5],  # Top 5 patterns
            'primary_recipe': patterns[0] if patterns else None,
            'summary': f"Most common: {' → '.join(patterns[0]['pattern']) if patterns else 'N/A'}"
        }
    
    def _find_frequent_patterns(self, sequences: List[List[str]], min_support: float) -> List[Dict]:
        """Simple frequent pattern mining"""
        pattern_counts = Counter()
        
        for seq in sequences:
            # Generate all subsequences
            for length in range(2, len(seq) + 1):
                for i in range(len(seq) - length + 1):
                    pattern = tuple(seq[i:i+length])
                    pattern_counts[pattern] += 1
        
        # Filter by support
        min_count = len(sequences) * min_support
        frequent = [
            {
                'pattern': list(pattern),
                'count': count,
                'support': count / len(sequences) * 100
            }
            for pattern, count in pattern_counts.items()
            if count >= min_count
        ]
        
        return sorted(frequent, key=lambda x: x['support'], reverse=True)

    
    # ========================================
    # 3. VISION INVESTMENT
    # ========================================
    
    def analyze_vision_investment(self) -> Dict:
        """Analyze vision spending patterns"""
        print("Analyzing Vision Investment...")
        
        vision_items = ['control ward', 'stealth ward', 'farsight', 'oracle']
        
        total_wards = 0
        total_games = 0
        wards_in_wins = []
        wards_in_losses = []
        pre_objective_wards = 0
        total_objectives = 0
        
        for series in self.series:
            if not series.get('state'):
                continue
            
            won = series['state']['teams'][0]['won']
            game_wards = 0
            
            # Count ward purchases
            for event in series['processed'].get('gold', []):
                item_name = (event.get('item_name') or '').lower()
                if any(ward in item_name for ward in vision_items):
                    game_wards += 1
                    total_wards += 1
            
            if won:
                wards_in_wins.append(game_wards)
            else:
                wards_in_losses.append(game_wards)
            
            # Check ward timing relative to objectives
            objectives = series['processed'].get('objectives', [])
            for obj in objectives:
                if 'dragon' in obj['type'].lower() or 'baron' in obj['type'].lower():
                    obj_time = obj['timestamp']
                    total_objectives += 1
                    
                    # Check if wards were bought 60-90s before
                    for event in series['processed'].get('gold', []):
                        item_name = (event.get('item_name') or '').lower()
                        if any(ward in item_name for ward in vision_items):
                            event_time = event.get('timestamp')
                            if event_time:
                                time_diff = (obj_time - event_time) / 1000  # Convert to seconds
                                if 60 <= time_diff <= 90:
                                    pre_objective_wards += 1
                                    break
            
            total_games += 1
        
        avg_wards_wins = statistics.mean(wards_in_wins) if wards_in_wins else 0
        avg_wards_losses = statistics.mean(wards_in_losses) if wards_in_losses else 0
        
        return {
            'wards_per_game': total_wards / total_games if total_games > 0 else 0,
            'wards_in_wins': avg_wards_wins,
            'wards_in_losses': avg_wards_losses,
            'vision_drop_in_losses': ((avg_wards_wins - avg_wards_losses) / avg_wards_wins * 100) if avg_wards_wins > 0 else 0,
            'pre_objective_setup_rate': (pre_objective_wards / total_objectives * 100) if total_objectives > 0 else 0,
            'summary': f"Avg {total_wards / total_games:.1f} wards/game, {pre_objective_wards / total_objectives * 100:.0f}% pre-objective setup"
        }

    
    # ========================================
    # 4. ROAMING SYSTEM
    # ========================================
    
    def analyze_roaming_system(self) -> Dict:
        """Analyze player movement and roaming patterns"""
        print("Analyzing Roaming System...")
        
        roam_events = []
        
        for series in self.series:
            kills = series['processed'].get('kills', [])
            
            # Track player positions from kills
            player_positions = defaultdict(list)
            
            for kill in kills:
                killer_id = kill.get('killer_id')
                killer_pos = kill.get('killer_position')
                timestamp = kill.get('timestamp')
                
                if killer_id and killer_pos:
                    player_positions[killer_id].append({
                        'time': timestamp,
                        'pos': killer_pos
                    })
            
            # Calculate roaming distance
            for player_id, positions in player_positions.items():
                if len(positions) < 2:
                    continue
                
                sorted_pos = sorted(positions, key=lambda x: x['time'])
                
                for i in range(len(sorted_pos) - 1):
                    pos1 = sorted_pos[i]['pos']
                    pos2 = sorted_pos[i+1]['pos']
                    
                    if pos1 and pos2:
                        distance = self._calculate_distance(pos1, pos2)
                        time_diff = (sorted_pos[i+1]['time'] - sorted_pos[i]['time']) / 1000
                        
                        # Consider it a roam if distance > 3000 units
                        if distance > 3000:
                            roam_events.append({
                                'player': player_id,
                                'distance': distance,
                                'time_diff': time_diff
                            })
        
        # Analyze roaming patterns
        total_roams = len(roam_events)
        avg_distance = statistics.mean([r['distance'] for r in roam_events]) if roam_events else 0
        
        return {
            'total_roams': total_roams,
            'roams_per_game': total_roams / len(self.series) if self.series else 0,
            'avg_roam_distance': avg_distance,
            'summary': f"{total_roams / len(self.series):.1f} roams/game, avg {avg_distance:.0f} units"
        }
    
    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate Euclidean distance between two positions"""
        if not pos1 or not pos2:
            return 0
        x1, y1 = pos1.get('x', 0), pos1.get('y', 0)
        x2, y2 = pos2.get('x', 0), pos2.get('y', 0)
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    
    # ========================================
    # 5. CHAMPION DEPENDENCY
    # ========================================
    
    def analyze_champion_dependency(self) -> Dict:
        """Analyze champion picks and dependencies"""
        print("Analyzing Champion Dependency...")
        
        champion_stats = defaultdict(lambda: {'picks': 0, 'wins': 0, 'kills': 0, 'deaths': 0})
        role_champion_pool = defaultdict(set)
        
        for series in self.series:
            if not series.get('state'):
                continue
            
            won = series['state']['teams'][0]['won']
            
            for game in series['state'].get('games', []):
                for player in game['teams'][0]['players']:
                    champ = player.get('character', {}).get('name')
                    if not champ:
                        continue
                    
                    role = self._infer_role(player)
                    role_champion_pool[role].add(champ)
                    
                    champion_stats[champ]['picks'] += 1
                    champion_stats[champ]['kills'] += player.get('kills', 0)
                    champion_stats[champ]['deaths'] += player.get('deaths', 0)
                    
                    if won:
                        champion_stats[champ]['wins'] += 1
        
        # Calculate win rates and identify patterns
        champion_analysis = {}
        for champ, stats in champion_stats.items():
            if stats['picks'] >= 2:  # At least 2 picks
                champion_analysis[champ] = {
                    'picks': stats['picks'],
                    'win_rate': (stats['wins'] / stats['picks'] * 100) if stats['picks'] > 0 else 0,
                    'avg_kda': ((stats['kills'] + 0) / max(stats['deaths'], 1)) if stats['picks'] > 0 else 0
                }
        
        # Identify comfort picks (high pick rate + high win rate)
        comfort_picks = {
            champ: data for champ, data in champion_analysis.items()
            if data['picks'] >= 3 and data['win_rate'] >= 60
        }
        
        # Identify trap picks (high pick rate + low win rate)
        trap_picks = {
            champ: data for champ, data in champion_analysis.items()
            if data['picks'] >= 3 and data['win_rate'] < 45
        }
        
        # Analyze champion pool diversity
        pool_diversity = {
            role: len(champs) for role, champs in role_champion_pool.items()
        }
        
        return {
            'total_unique_champions': len(champion_stats),
            'champion_stats': dict(sorted(champion_analysis.items(), 
                                         key=lambda x: x[1]['picks'], reverse=True)[:10]),
            'comfort_picks': comfort_picks,
            'trap_picks': trap_picks,
            'pool_diversity': pool_diversity,
            'summary': f"{len(comfort_picks)} comfort picks, {len(trap_picks)} trap picks"
        }

    
    # ========================================
    # 6. LOSING RECIPE
    # ========================================
    
    def analyze_losing_recipe(self) -> Dict:
        """Identify common failure patterns"""
        print("Analyzing Losing Recipe...")
        
        loss_patterns = {
            'early_deaths': 0,
            'failed_objectives': 0,
            'vision_collapse': 0,
            'gold_deficit': 0
        }
        
        total_losses = 0
        
        for series in self.series:
            if not series.get('state'):
                continue
            
            won = series['state']['teams'][0]['won']
            if won:
                continue
            
            total_losses += 1
            
            # Check for early deaths (before 10 minutes)
            early_deaths = [
                kill for kill in series['processed'].get('kills', [])
                if isinstance(kill.get('timestamp'), (int, float)) and kill.get('timestamp', 0) < 600000  # 10 minutes in ms
            ]
            if len(early_deaths) >= 2:
                loss_patterns['early_deaths'] += 1
            
            # Check for vision collapse (low ward count)
            vision_items = ['control ward', 'stealth ward']
            ward_count = sum(
                1 for event in series['processed'].get('gold', [])
                if any(ward in (event.get('item_name') or '').lower() for ward in vision_items)
            )
            if ward_count < 8:
                loss_patterns['vision_collapse'] += 1
            
            # Check for failed objectives (enemy gets more)
            team_objectives = len([
                obj for obj in series['processed'].get('objectives', [])
                if obj.get('team_id') == self.team_id
            ])
            if team_objectives < 5:
                loss_patterns['failed_objectives'] += 1
        
        # Calculate percentages
        loss_analysis = {
            pattern: (count / total_losses * 100) if total_losses > 0 else 0
            for pattern, count in loss_patterns.items()
        }
        
        # Identify primary failure mode
        primary_failure = max(loss_analysis.items(), key=lambda x: x[1])[0] if loss_analysis else None
        
        return {
            'total_losses': total_losses,
            'loss_patterns': loss_analysis,
            'primary_failure_mode': primary_failure,
            'summary': f"Primary failure: {primary_failure} ({loss_analysis.get(primary_failure, 0):.0f}% of losses)"
        }

    
    # ========================================
    # 7. ROLE CORRELATION
    # ========================================
    
    def analyze_role_correlation(self) -> Dict:
        """Identify role dependencies using correlation"""
        print("Analyzing Role Correlation...")
        
        role_performance = defaultdict(list)
        
        for series in self.series:
            if not series.get('state'):
                continue
            
            won = series['state']['teams'][0]['won']
            game_performance = {}
            
            for game in series['state'].get('games', []):
                for player in game['teams'][0]['players']:
                    role = self._infer_role(player)
                    kills = player.get('kills', 0)
                    deaths = max(player.get('deaths', 1), 1)
                    kda = kills / deaths
                    
                    if role not in game_performance:
                        game_performance[role] = []
                    game_performance[role].append(kda)
            
            # Average KDA per role for this series
            for role, kdas in game_performance.items():
                avg_kda = statistics.mean(kdas) if kdas else 0
                role_performance[role].append({
                    'kda': avg_kda,
                    'won': won
                })
        
        # Calculate win correlation for each role
        role_correlations = {}
        for role, performances in role_performance.items():
            if len(performances) < 3:
                continue
            
            # Simple correlation: avg KDA in wins vs losses
            wins = [p['kda'] for p in performances if p['won']]
            losses = [p['kda'] for p in performances if not p['won']]
            
            avg_kda_wins = statistics.mean(wins) if wins else 0
            avg_kda_losses = statistics.mean(losses) if losses else 0
            
            # Correlation score (higher = more important for wins)
            correlation = avg_kda_wins - avg_kda_losses
            
            role_correlations[role] = {
                'correlation_score': correlation,
                'avg_kda_wins': avg_kda_wins,
                'avg_kda_losses': avg_kda_losses
            }
        
        # Identify lynchpin role
        lynchpin = max(role_correlations.items(), key=lambda x: x[1]['correlation_score'])[0] if role_correlations else None
        
        return {
            'role_correlations': role_correlations,
            'lynchpin_role': lynchpin,
            'summary': f"Lynchpin: {lynchpin} (highest win correlation)"
        }

    
    # ========================================
    # 8. BREAK STRATEGY
    # ========================================
    
    def generate_break_strategy(self) -> Dict:
        """Generate counter-strategy based on analysis"""
        print("Generating Break Strategy...")
        
        # This requires other analyses to be run first
        identity = self.analyze_team_identity()
        losing = self.analyze_losing_recipe()
        champion = self.analyze_champion_dependency()
        
        strategies = []
        
        # Strategy based on primary failure mode
        failure_mode = losing.get('primary_failure_mode')
        if failure_mode == 'early_deaths':
            strategies.append("Apply early game pressure to force mistakes")
        elif failure_mode == 'vision_collapse':
            strategies.append("Deny vision control and force blind fights")
        elif failure_mode == 'failed_objectives':
            strategies.append("Contest all objectives to prevent their scaling")
        
        # Strategy based on champion dependency
        comfort_picks = champion.get('comfort_picks', {})
        if comfort_picks:
            top_comfort = list(comfort_picks.keys())[0]
            strategies.append(f"Ban {top_comfort} (comfort pick)")
        
        # Strategy based on team identity
        primary_role = identity.get('primary_win_condition')
        if primary_role:
            strategies.append(f"Target {primary_role} lane to disrupt win condition")
        
        return {
            'strategies': strategies,
            'priority': strategies[0] if strategies else "No clear strategy",
            'summary': " | ".join(strategies[:3])
        }
    
    # ========================================
    # 9. DRAFT & GAMEPLAN
    # ========================================
    
    def generate_draft_gameplan(self) -> Dict:
        """Generate draft and early game recommendations"""
        print("Generating Draft & Gameplan...")
        
        champion = self.analyze_champion_dependency()
        identity = self.analyze_team_identity()
        losing = self.analyze_losing_recipe()
        
        recommendations = {
            'bans': [],
            'picks': [],
            'early_game_plan': []
        }
        
        # Ban recommendations
        comfort_picks = champion.get('comfort_picks', {})
        for champ in list(comfort_picks.keys())[:3]:
            recommendations['bans'].append(f"{champ} (comfort pick)")
        
        # Pick recommendations (counter their style)
        primary_role = identity.get('primary_win_condition')
        if primary_role == 'mid':
            recommendations['picks'].append("Roaming mid laner to match pressure")
        elif primary_role == 'adc':
            recommendations['picks'].append("Early game bot lane to deny scaling")
        
        # Early game plan
        failure_mode = losing.get('primary_failure_mode')
        if failure_mode == 'early_deaths':
            recommendations['early_game_plan'].append("Invade jungle level 1")
            recommendations['early_game_plan'].append("Gank vulnerable lanes early")
        
        sacrificed_lane = identity.get('sacrificed_lane')
        if sacrificed_lane:
            recommendations['early_game_plan'].append(f"Pressure {sacrificed_lane} lane (weak side)")
        
        return {
            'ban_recommendations': recommendations['bans'],
            'pick_recommendations': recommendations['picks'],
            'early_game_plan': recommendations['early_game_plan'],
            'summary': f"Ban: {', '.join(recommendations['bans'][:2])}"
        }

    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _infer_role(self, player: Dict) -> str:
        """Infer player role from champion or position"""
        # Simplified role inference based on common patterns
        # In production, you'd use more sophisticated logic
        champ = player.get('character', {}).get('name', '').lower()
        
        # Common role indicators
        if any(x in champ for x in ['jinx', 'aphelios', 'kaisa', 'ezreal', 'jhin']):
            return 'adc'
        elif any(x in champ for x in ['thresh', 'leona', 'nautilus', 'lulu', 'nami']):
            return 'support'
        elif any(x in champ for x in ['lee sin', 'graves', 'nidalee', 'elise', 'kha']):
            return 'jungle'
        elif any(x in champ for x in ['gnar', 'jax', 'camille', 'aatrox', 'renekton']):
            return 'top'
        else:
            return 'mid'
    
    def _get_role_from_player(self, player_id: str, series: Dict) -> str:
        """Get role for a specific player ID"""
        if not series.get('state'):
            return None
        
        for game in series['state'].get('games', []):
            for player in game['teams'][0]['players']:
                if player.get('id') == player_id:
                    return self._infer_role(player)
        return None


# ========================================
# UTILITY FUNCTIONS
# ========================================

def analyze_team_from_file(data_file: str, output_file: str = None, analyses: List[str] = None) -> Dict:
    """
    Analyze a team from a data file
    
    Args:
        data_file: Path to team data JSON file
        output_file: Path to save report (optional, auto-generated if None)
        analyses: List of specific analyses to run (None = all)
    
    Returns:
        Complete analysis report
    """
    analyzer = PorolyticsAnalyzer(data_file)
    
    if analyses:
        # Run only specified analyses
        report = {'team_id': analyzer.team_id}
        for analysis in analyses:
            method_name = f"analyze_{analysis}"
            if hasattr(analyzer, method_name):
                report[analysis] = getattr(analyzer, method_name)()
            elif analysis == 'break_strategy':
                report[analysis] = analyzer.generate_break_strategy()
            elif analysis == 'draft_gameplan':
                report[analysis] = analyzer.generate_draft_gameplan()
    else:
        # Run all analyses
        report = analyzer.analyze_all()
    
    # Save report
    if output_file is None:
        output_file = data_file.replace('_analysis.json', '_porolytics_report.json')
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def compare_teams(team1_file: str, team2_file: str, output_file: str = None) -> Dict:
    """
    Compare two teams side-by-side
    
    Args:
        team1_file: Path to first team data
        team2_file: Path to second team data
        output_file: Path to save comparison (optional)
    
    Returns:
        Comparison report
    """
    print(f"\n{'='*60}")
    print(f"COMPARING TEAMS")
    print(f"{'='*60}\n")
    
    # Analyze both teams
    print("Analyzing Team 1...")
    report1 = analyze_team_from_file(team1_file)
    
    print("Analyzing Team 2...")
    report2 = analyze_team_from_file(team2_file)
    
    # Build comparison
    comparison = {
        'team1': {
            'id': report1['team_id'],
            'file': team1_file,
            'report': report1
        },
        'team2': {
            'id': report2['team_id'],
            'file': team2_file,
            'report': report2
        },
        'comparison': {
            'champion_pools': {
                'team1_unique': report1['champion_dependency']['total_unique_champions'],
                'team2_unique': report2['champion_dependency']['total_unique_champions']
            },
            'playstyle': {
                'team1_primary': report1['team_identity']['primary_win_condition'],
                'team2_primary': report2['team_identity']['primary_win_condition']
            },
            'vision_investment': {
                'team1_wards': report1['vision_investment']['wards_per_game'],
                'team2_wards': report2['vision_investment']['wards_per_game']
            }
        }
    }
    
    # Save comparison
    if output_file is None:
        output_file = 'team_comparison.json'
    
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n✅ Comparison saved to: {output_file}\n")
    
    return comparison


def print_summary(report: Dict):
    """Print a formatted summary of the analysis report"""
    print(f"\n{'='*60}")
    print(f"ANALYSIS SUMMARY")
    print(f"{'='*60}\n")
    
    if 'team_identity' in report:
        print(f"Team Identity: {report['team_identity']['summary']}")
    if 'winning_recipe' in report:
        print(f"Winning Recipe: {report['winning_recipe']['summary']}")
    if 'vision_investment' in report:
        print(f"Vision Investment: {report['vision_investment']['summary']}")
    if 'roaming_system' in report:
        print(f"Roaming System: {report['roaming_system']['summary']}")
    if 'champion_dependency' in report:
        print(f"Champion Dependency: {report['champion_dependency']['summary']}")
    if 'losing_recipe' in report:
        print(f"Losing Recipe: {report['losing_recipe']['summary']}")
    if 'role_correlation' in report:
        print(f"Role Correlation: {report['role_correlation']['summary']}")
    if 'break_strategy' in report:
        print(f"Break Strategy: {report['break_strategy']['summary']}")
    if 'draft_gameplan' in report:
        print(f"Draft & Gameplan: {report['draft_gameplan']['summary']}")
    print()


# ========================================
# COMMAND-LINE INTERFACE
# ========================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Porolytics Analyzer - AI-Powered Opponent Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single team
  python porolytics_analyzer.py data/team_47494_T1_analysis.json
  
  # Analyze with specific output file
  python porolytics_analyzer.py data/team_47494_T1_analysis.json -o t1_report.json
  
  # Run only specific analyses
  python porolytics_analyzer.py data/team_47494_T1_analysis.json --analyses champion_dependency draft_gameplan
  
  # Compare two teams
  python porolytics_analyzer.py --compare data/team_47494_T1_analysis.json data/team_47351_Cloud9_analysis.json
  
  # Quiet mode (no summary output)
  python porolytics_analyzer.py data/team_47494_T1_analysis.json --quiet
        """
    )
    
    parser.add_argument('data_file', nargs='?', help='Team data JSON file')
    parser.add_argument('-o', '--output', type=str, help='Output file path')
    parser.add_argument('--analyses', nargs='+', 
                       choices=['team_identity', 'winning_recipe', 'vision_investment', 
                               'roaming_system', 'champion_dependency', 'losing_recipe',
                               'role_correlation', 'break_strategy', 'draft_gameplan'],
                       help='Specific analyses to run (default: all)')
    parser.add_argument('--compare', nargs=2, metavar=('TEAM1', 'TEAM2'),
                       help='Compare two teams')
    parser.add_argument('--quiet', action='store_true', help='Suppress summary output')
    
    args = parser.parse_args()
    
    # Handle comparison mode
    if args.compare:
        comparison = compare_teams(args.compare[0], args.compare[1], args.output)
        
        if not args.quiet:
            print("COMPARISON SUMMARY:")
            print(f"  Team 1: {comparison['team1']['id']}")
            print(f"    Primary: {comparison['comparison']['playstyle']['team1_primary']}")
            print(f"    Champions: {comparison['comparison']['champion_pools']['team1_unique']}")
            print(f"    Wards/game: {comparison['comparison']['vision_investment']['team1_wards']:.1f}")
            print()
            print(f"  Team 2: {comparison['team2']['id']}")
            print(f"    Primary: {comparison['comparison']['playstyle']['team2_primary']}")
            print(f"    Champions: {comparison['comparison']['champion_pools']['team2_unique']}")
            print(f"    Wards/game: {comparison['comparison']['vision_investment']['team2_wards']:.1f}")
            print()
        
        sys.exit(0)
    
    # Handle single team analysis
    if not args.data_file:
        parser.print_help()
        sys.exit(1)
    
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"POROLYTICS OPPONENT ANALYSIS")
        print(f"{'='*60}\n")
    
    # Run analysis
    report = analyze_team_from_file(args.data_file, args.output, args.analyses)
    
    if not args.quiet:
        output_file = args.output or args.data_file.replace('_analysis.json', '_porolytics_report.json')
        print(f"\n{'='*60}")
        print(f"✅ ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print(f"Report saved to: {output_file}\n")
        
        # Print summary
        print_summary(report)
