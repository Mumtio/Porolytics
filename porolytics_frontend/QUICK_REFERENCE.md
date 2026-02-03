# Porolytics Analysis Page - Quick Reference

## Complete Section List

### Sections 1-4: Draft Analysis
1. **What This Analysis Provides** - Overview cards
2. **Champion Picks Strategy Graph** - ACO simulation
3. **Champion Bans Strategy Graph** - ACO simulation
4. **Draft Conclusions** - Summary cards

### Sections 5-9: In-Game Strategy Analysis
5. **Strategy Transition Graph** - Interactive graph with zoom/pan
6. **Strategy Importance Ranking** - Top 6 strategies ranked
7. **Strategy Failure Modes** - 4 failure pattern cards
8. **Lynchpin Stress Test** - Denial impact simulation
9. **In-Game Strategy Phase Profile** - Timeline visualization

### Section 10: Monte Carlo Simulator
10. **Monte Carlo Match Outcome Simulator** - 10k simulation with controls

### Sections 11-14: Post-Monte Carlo Analysis
11. **Robustness & Variance** - Win rate stability analysis
12. **Redundancy & Backup Paths** - Alternative win conditions
13. **Predictability Index** - Behavioral scripting analysis
14. **Denial Priority Stack** - Ranked ban/deny targets

### Overlay: Coach Summary
- **Coach Summary Modal** - Complete strategic recommendations

---

## Key Interactive Elements

### Buttons & Triggers
- `#runPicksSimulation` - Run picks ACO simulation
- `#runBansSimulation` - Run bans ACO simulation
- `#runMonteCarlo` - Run Monte Carlo simulation
- `#coachSummaryBtn` - Open coach summary modal (sticky)

### Interactive Graphs
- `#picksGraph` - Champion picks strategy graph
- `#bansGraph` - Champion bans strategy graph
- `#strategyTransitionGraph` - Strategy transition graph (zoom/pan)
- `#stressTestGraph` - Lynchpin stress test graph
- `#outcomeDistribution` - Monte Carlo outcome chart

### Clickable Cards
- `.ranking-card` - Strategy importance cards (scroll to graph)
- `.failure-card` - Failure mode cards (highlight in graph)
- `.denial-item` - Denial priority items (open drawer)

### Modals & Drawers
- `#denialDrawer` - Denial rationale details
- `#coachModal` - Coach summary modal

---

## Data Flow

### 1. Initial Load
```
Page Load → Initialize Graphs → Show Empty States
```

### 2. Picks/Bans Simulation
```
Click Run → ACO Simulation → Update Graph → Show Insights
```

### 3. Monte Carlo Simulation
```
Click Run → 10k Simulations → Update Chart → Enable Post-Panels
```

### 4. Post-Monte Carlo Panels
```
Monte Carlo Complete → Load Analysis Data → Render All Panels
```

### 5. Coach Summary
```
Click Button → Open Modal → Show Recommendations
```

---

## CSS Class Reference

### Panel Structure
- `.panel-shell` - Main panel wrapper
- `.panel-header` - Header with title/subtitle
- `.metric-chip` - Compact metric display
- `.metric-chip.good` - Positive metric (cyan)
- `.metric-chip.bad` - Negative metric (red)
- `.metric-chip.warn` - Warning metric (orange)

### Path Rendering
- `.path-renderer` - Path container
- `.path-step` - Individual strategy step
- `.path-arrow` - Arrow between steps
- `.path-tag.win-heavy` - Win-heavy tag (cyan)
- `.path-tag.loss-heavy` - Loss-heavy tag (red)
- `.path-tag.mixed` - Mixed tag (purple)

### Denial Stack
- `.denial-item` - Denial list item
- `.denial-rank` - Rank number
- `.denial-chip.win-drop` - Win drop chip (red)
- `.denial-chip.phase` - Phase chip (purple)
- `.denial-chip.risk` - Risk chip (varies)

### Modal
- `.coach-modal-overlay` - Modal backdrop
- `.coach-modal` - Modal container
- `.modal-body` - 2-column grid
- `.modal-left` - Left column
- `.modal-right` - Right column

---

## JavaScript Function Reference

### Initialization Functions
```javascript
initRobustnessPanel()      // Section 11
initRedundancyPanel()      // Section 12
initPredictabilityPanel()  // Section 13
initDenialPanel()          // Section 14
initCoachSummary()         // Coach Modal
```

### Graph Classes
```javascript
StrategyGraph              // Picks/Bans ACO graphs
StrategyTransitionGraph    // Strategy transition graph
StressTestGraph            // Lynchpin stress test
MonteCarloSimulator        // Monte Carlo simulator
```

### Utility Functions
```javascript
drawGraph(canvasId, graph, color)
updateConclusions(isPicksGraph, graph)
openDenialDrawer(item)
```

---

## Color Palette

### Primary Colors
- **Purple**: `#9B6FE8` - Primary accent
- **Cyan**: `#0AC8B9` - Positive/wins
- **Gold**: `#C89B3C` - Important/lynchpin
- **Red**: `#FF4655` - Negative/losses
- **Orange**: `#FFA500` - Warning

### Background Colors
- **Dark**: `#010A13` - Main background
- **Medium**: `#0A1520` - Panel background
- **Light**: `#AAB3B8` - Text secondary

### Text Colors
- **Primary**: `#F0F6F6` - Main text
- **Secondary**: `#AAB3B8` - Muted text

---

## Responsive Breakpoints

### Desktop (>1024px)
- Full 2-column layouts
- Side-by-side elements
- Expanded visualizations

### Tablet (768-1024px)
- Single column modals
- Stacked elements
- Maintained spacing

### Mobile (<768px)
- Vertical stacking
- Bottom-positioned sticky button
- Touch-friendly targets
- Simplified visualizations

---

## Common Tasks

### Add New Panel
1. Add HTML section with `.panel-shell`
2. Add CSS in `analysis-styles.css`
3. Create init function in `analysis-script.js`
4. Call init in `DOMContentLoaded`

### Update Mock Data
Edit `ANALYSIS_DATA` object in `analysis-script.js`

### Change Colors
Update CSS variables or direct color values in styles

### Add New Metric Chip
```html
<div class="metric-chip good">
    <span class="chip-label">Label</span>
    <span class="chip-value">Value</span>
</div>
```

### Add New Path
```javascript
{
    steps: ["STEP_1", "STEP_2", "STEP_3"],
    probability: 0.21,
    label: "WIN_HEAVY"
}
```

---

## Troubleshooting

### Graph Not Rendering
- Check canvas element exists
- Verify canvas ID matches JavaScript
- Check browser console for errors

### Modal Not Opening
- Verify button ID matches event listener
- Check modal overlay has correct ID
- Ensure JavaScript initialized

### Styles Not Applied
- Check CSS file is loaded
- Verify class names match
- Check for CSS conflicts

### Data Not Displaying
- Check `ANALYSIS_DATA` structure
- Verify element IDs match
- Check JavaScript console for errors

---

## Performance Notes

- ACO simulations: ~1 second per match
- Monte Carlo: ~0.5-1 second for 10k sims
- Graph rendering: <100ms
- Panel initialization: <50ms per panel

---

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

---

## File Sizes

- `analysis.html`: ~1,300 lines
- `analysis-styles.css`: ~2,900 lines
- `analysis-script.js`: ~2,900 lines

Total: ~7,100 lines of code
