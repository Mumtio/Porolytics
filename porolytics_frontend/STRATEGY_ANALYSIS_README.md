# Advanced Strategy Analysis Pages

## Overview

This document describes the new advanced strategy analysis pages added to Porolytics. These pages implement the 8-section framework for in-depth opponent analysis based on in-game execution patterns.

## Files Added

1. **strategy-analysis.html** - Main HTML structure for all 8 sections
2. **strategy-analysis-styles.css** - Complete styling for all components
3. **strategy-analysis-script.js** - JavaScript logic for data visualization and interaction

## Sections Implemented

### SECTION 1 — In-Game Strategy Identity Graphs
**Purpose:** Move from draft intent → in-game execution reality

**Components:**
- **1.1 Strategy Transition Graph** - Directed weighted graph showing strategic state transitions
  - Toggle filters: WIN only, LOSS only, Combined
  - Minimum edge probability slider
  - Hover tooltips showing transition details
  
- **1.2 Strategy Phase Timeline** - Horizontal timeline showing dominant strategy over game time
  - Color-coded strategy segments
  - Major objective markers
  - Teamfight occurrence indicators

### SECTION 2 — Win vs Loss Structural Contrast
**Purpose:** Expose what works vs what looks similar but fails

**Components:**
- **2.1 Win Graph vs Loss Graph Diff View** - Split view comparison
  - WIN edges (cyan)
  - LOSS edges (red)
  - Mixed edges (purple)
  - Shared node positions for easy comparison
  
- **2.2 Fragility Overlay** - Heatmap showing strategy fragility
  - Green = Stable strategies
  - Yellow = Fragile strategies
  - Red = Bait strategies (high appearance, low win contribution)

### SECTION 3 — Lynchpin Strategy Detection
**Purpose:** Identify structurally critical nodes that collapse win paths

**Components:**
- **3.1 Lynchpin Centrality Graph** - Graph highlighting critical nodes
  - Gold outer ring for lynchpins
  - Subtle pulse animation
  - Muted opacity for non-lynchpin nodes
  - Detected lynchpins list panel
  
- **3.2 Dependency Fan-Out View** - Interactive radial tree
  - Click lynchpin to see downstream strategies
  - Edge thickness = dependency strength
  - Shows collapse probability if denied

### SECTION 4 — In-Game Denial Matrix
**Purpose:** Translate strategy theory → map-level actions

**Components:**
- **4.1 Denial Matrix Table** - Color-coded effectiveness matrix
  - Rows: Opponent strategies
  - Columns: Denial methods (Vision Control, Top Pressure, River Control, etc.)
  - Cells: 🔴 High effectiveness, 🟡 Medium, 🟢 Low

### SECTION 5 — Counter-Strategy Suggestions
**Purpose:** Provide actionable counter-strategies

**Components:**
- **Counter-Strategy Cards** - Generated from lynchpin analysis
  - Opponent strategy identification
  - Recommended denial approach
  - Champions/roles involved
  - Phase timing (draft/early/mid)
  - Success rate metrics

### SECTION 6 — Strategy Consistency Index
**Purpose:** Determine if team is disciplined or chaotic

**Components:**
- **6.1 Consistency Radar Chart** - 5-axis radar visualization
  - Early identity consistency
  - Midgame pivot stability
  - Late game execution
  - Dependency breadth
  - Recovery after denial
  - Interpretation: Tight radar = predictable, Spiky radar = volatile

### SECTION 7 — Monte Carlo Simulation
**Purpose:** Confirmation & stress-test, not discovery

**Components:**
- **7.1 Simulation Entry Point** - Gated access
  - Unlocks after lynchpin analysis complete
  
- **7.2 Simulation Controls** - Parameter configuration
  - Number of simulations slider (1,000 - 50,000)
  - Denial strategy selector
  - Run simulation button
  
- **7.3 Monte Carlo Outcome View** - Results visualization
  - Win probability distribution chart
  - Strategy survival histogram
  - Collapse frequency per lynchpin
  - Confidence score (High Certainty / Medium Risk / Unstable)

### SECTION 8 — Final Coach Summary
**Purpose:** Single authoritative conclusion

**Components:**
- **Coach Summary Card** - Comprehensive summary
  - Team identity spine
  - Primary lynchpin strategy
  - Collapse percentage
  - Monte Carlo confirmation
  - Example: "This team relies on Frontline Teamfight → River Control → Objective Stack. Denying Frontline Teamfight collapses 61% of win paths. Monte Carlo confirms this denial holds across 89% of simulated drafts."

## Data Sources

The pages expect the following JSON files in the parent directory:

1. **strategy_report.json** - Lynchpin analysis data
   - `lynchpins[]` - Node impact and conditional reach
   - `edge_lynchpins[]` - Critical edges
   - `win_fragile_edges[]` - Fragile patterns
   - `confidence{}` - Confidence scores
   - `break_strategy{}` - Counter-strategies

2. **out/coach_report.json** - Coach-facing summary
   - `team` - Team name
   - `baseline_success_rate` - Baseline win rate
   - `identity_spine` - Primary strategy path
   - `top_denies[]` - Ranked denial strategies
   - `backup_paths{}` - Alternative paths

3. **graph_win.json** - Win graph structure
   - `nodes[]` - Strategy nodes
   - `edges[]` - Transitions with weights
   - `out_probs{}` - Transition probabilities

4. **graph_loss.json** - Loss graph structure
   - Same structure as win graph

## Features

### Interactive Elements
- **Hover tooltips** on all graph nodes and edges
- **Click interactions** for lynchpin fan-out view
- **Radio buttons** for graph filtering (WIN/LOSS/Combined)
- **Sliders** for threshold adjustments
- **Gated simulation** that unlocks after analysis completion

### Visual Encoding
- **Edge thickness** = transition probability
- **Edge glow** = win-conditioned strength
- **Node size** = frequency × decisiveness
- **Color coding**:
  - Cyan (#0AC8B9) = WIN patterns
  - Red (#FF4655) = LOSS patterns
  - Purple (#9B6FE8) = Mixed/Fragile
  - Gold (#C89B3C) = Lynchpins

### Responsive Design
- Grid layouts adapt to screen size
- Mobile-friendly controls
- Scrollable containers for overflow content

## Usage

### Accessing the Pages

1. From the main analysis page (`analysis.html`), click the "View Advanced Strategy Analysis →" button
2. Or navigate directly to `strategy-analysis.html`

### Navigation

- **Back to Draft Analysis** link in top navigation
- **Fixed Poro Guide** in bottom-right corner with contextual help

### Workflow

1. **View Strategy Transitions** - Understand how strategies flow
2. **Compare Win vs Loss** - Identify what actually works
3. **Detect Lynchpins** - Find critical dependencies
4. **Review Denial Matrix** - See actionable counters
5. **Read Counter-Strategies** - Get specific recommendations
6. **Check Consistency** - Assess predictability
7. **Run Monte Carlo** - Validate conclusions
8. **Read Coach Summary** - Get final authoritative insight

## Technical Details

### Dependencies
- **Chart.js 4.4.0** - For radar charts, bar charts, and doughnut charts
- **Vanilla JavaScript** - No framework dependencies
- **CSS Grid & Flexbox** - Modern layout techniques

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript features
- CSS Grid and Flexbox support required

### Performance
- Canvas-based graph rendering for smooth performance
- Lazy loading of Monte Carlo simulation
- Efficient data structures for graph traversal

## Customization

### Colors
All colors are defined in CSS variables and can be easily customized:
- Primary: `#9B6FE8` (purple)
- Secondary: `#C89B3C` (gold)
- Success: `#0AC8B9` (cyan)
- Danger: `#FF4655` (red)
- Background: `#010A13` (dark blue)

### Graph Layouts
Node positions can be adjusted in the JavaScript:
- Circular layout (default)
- Radial tree for fan-out
- Custom positions via `nodePositions` object

### Data Thresholds
Configurable thresholds in JavaScript:
- Minimum edge probability: 0.05 (adjustable via slider)
- Lynchpin impact threshold: 0.005
- Fragility thresholds: 0.1 (stable), 0.3 (fragile)

## Future Enhancements

Potential additions:
1. **Real-time data updates** via WebSocket
2. **Export functionality** for reports (PDF/PNG)
3. **Comparison mode** for multiple teams
4. **Historical trend analysis** over time
5. **Custom denial strategy builder**
6. **Integration with live match data**

## Troubleshooting

### Data Not Loading
- Check that JSON files exist in correct locations
- Verify JSON structure matches expected format
- Check browser console for errors
- Falls back to mock data if files not found

### Graphs Not Rendering
- Ensure Canvas API is supported
- Check for JavaScript errors in console
- Verify Chart.js is loaded correctly

### Simulation Not Unlocking
- Complete lynchpin analysis first
- Check that `lynchpinsDetected` flag is set
- Verify lynchpin data exists in strategy_report.json

## Credits

Developed for the Porolytics project - League of Legends esports opponent analysis system.

Based on advanced graph theory, Monte Carlo simulation, and strategic pattern recognition algorithms.
