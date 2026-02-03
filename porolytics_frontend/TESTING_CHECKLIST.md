# Testing Checklist - Strategy Transition Graph

## Server Running
✅ Server started at: http://localhost:8080/

## Access Points
- Main page: http://localhost:8080/strategy-analysis.html
- Direct section: http://localhost:8080/strategy-analysis.html#section1

## Visual Encoding Tests

### 1. Graph Renders
- [ ] Canvas element visible (900x600px)
- [ ] No JavaScript errors in console
- [ ] Graph appears within 2 seconds of page load
- [ ] Mock data loads if real data unavailable

### 2. Edge Thickness (CRITICAL)
- [ ] Thinnest edges are ~1px (barely visible hairlines)
- [ ] Thickest edges are ~12px (very obvious, dominant)
- [ ] Thickness difference is IMMEDIATELY obvious (5-second rule)
- [ ] Can identify high-probability transitions at a glance

### 3. Edge Color (CRITICAL)
- [ ] WIN mode: All edges are bright cyan `rgb(10, 200, 185)`
- [ ] LOSS mode: All edges are bright red `rgb(255, 70, 85)`
- [ ] Combined mode: Mix of cyan (winning), red (losing), purple (mixed)
- [ ] Colors are high contrast, not muted
- [ ] Can distinguish win/loss paths immediately

### 4. Edge Directionality (CRITICAL)
- [ ] All edges have large arrows (12-22px)
- [ ] Arrows are unmistakable, not subtle
- [ ] Gradient effect visible (tail faded, head strong)
- [ ] Direction of flow is obvious

### 5. Edge Boundaries
- [ ] Edges stop at circle boundary (no overlap with nodes)
- [ ] Edges start from circle edge, not center
- [ ] Curved edges look smooth
- [ ] No visual artifacts or gaps

### 6. Node Size (CRITICAL)
- [ ] Smallest nodes are ~20px radius
- [ ] Largest nodes are ~60px radius (3× difference)
- [ ] Size difference is dramatic and obvious
- [ ] Important nodes dominate visually

### 7. Node Color
- [ ] Win-biased nodes: Bright cyan `rgb(10, 220, 200)`
- [ ] Loss-biased nodes: Bright red `rgb(255, 85, 100)`
- [ ] Mixed nodes: Bright purple `rgb(175, 130, 255)`
- [ ] Colors are saturated, not muted

### 8. Lynchpin Gold Ring (CRITICAL)
- [ ] Lynchpin nodes have prominent gold rings
- [ ] Outer ring: 6px thick, bright gold
- [ ] Inner ring: 2px thick, lighter gold
- [ ] Gold glow effect visible
- [ ] Lynchpins are IMMEDIATELY identifiable

### 9. Node Border
- [ ] Border thickness scales with importance (3-7px)
- [ ] Important nodes have thicker borders
- [ ] Border color matches node outcome bias

### 10. Labels
- [ ] All node labels are readable
- [ ] Multi-word labels split across lines
- [ ] Font size scales with importance (10-15px)
- [ ] Labels don't overlap

## Interaction Tests

### 11. Hover Tooltips
- [ ] Hovering over node shows tooltip
- [ ] Tooltip displays: strategy name, win rate, follow-ups
- [ ] Tooltip follows mouse cursor
- [ ] Tooltip disappears when mouse leaves

### 12. Click to Focus
- [ ] Clicking node highlights it
- [ ] Other nodes/edges dim to 0.3 opacity
- [ ] Focused node and connected edges stay at 1.0 opacity
- [ ] Clicking again unfocuses

### 13. Radio Button Filters
- [ ] "Combined" shows all edges (default)
- [ ] "WIN only" shows only win edges (cyan)
- [ ] "LOSS only" shows only loss edges (red)
- [ ] Graph morphs smoothly between modes
- [ ] Node positions stay consistent

### 14. Slider Filter
- [ ] Slider ranges from 0 to 0.3
- [ ] Moving slider filters out low-probability edges
- [ ] Value display updates in real-time
- [ ] Graph updates immediately
- [ ] At 0.3, only strongest edges remain

## Performance Tests

### 15. Load Time
- [ ] Graph renders within 2 seconds
- [ ] No lag when switching filters
- [ ] Smooth interaction (no stuttering)

### 16. Console Output
- [ ] No errors in browser console
- [ ] Debug logs show successful data load
- [ ] Node metrics calculated correctly

## Browser Compatibility

### 17. Chrome/Edge
- [ ] All features work
- [ ] Canvas renders correctly
- [ ] Colors display correctly

### 18. Firefox
- [ ] All features work
- [ ] Canvas renders correctly
- [ ] Colors display correctly

## Data Tests

### 19. Mock Data
- [ ] Mock data includes 7 nodes
- [ ] Mock data includes 12 edges
- [ ] Lynchpins identified (TEAMFIGHT_COMMIT, BOT_PRESSURE, TOP_PRESSURE)
- [ ] Edge weights range from 0.12 to 0.28

### 20. Real Data (if available)
- [ ] Loads from data/graph_win.json
- [ ] Loads from data/graph_loss.json
- [ ] Loads from data/strategy_report.json
- [ ] All nodes and edges render correctly

## Visual Hierarchy Test (5-Second Rule)

### 21. First Glance (0-5 seconds)
Can you immediately identify:
- [ ] Which edges are thickest (most frequent transitions)?
- [ ] Which edges are cyan vs red (winning vs losing)?
- [ ] Which nodes are largest (most important)?
- [ ] Which nodes have gold rings (lynchpins)?

### 22. Second Glance (5-15 seconds)
Can you quickly understand:
- [ ] The dominant strategy chain (thick cyan path)?
- [ ] Dead ends (nodes with no outgoing edges)?
- [ ] Fork points (nodes with multiple strong outgoing edges)?
- [ ] Forced paths (nodes with one dominant outgoing edge)?

## Known Issues (To Be Implemented)

### 23. Lynchpin Hover Effect (NOT YET IMPLEMENTED)
- [ ] Hovering lynchpin dims entire graph
- [ ] Only paths through lynchpin stay bright
- [ ] Shows "X% of wins pass through this node"

### 24. Pulse Animation (OPTIONAL, NOT YET IMPLEMENTED)
- [ ] Lynchpin gold rings pulse subtly
- [ ] Animation is smooth, not distracting

## Debugging

If graph doesn't render:
1. Open browser console (F12)
2. Check for errors
3. Look for "✅ Drawing graph:" log
4. Verify node metrics calculated
5. Check if canvas element exists
6. Verify data loaded (winGraph, lossGraph)

If visual encoding not obvious:
1. Check edge thickness range (should be 1-12px)
2. Check node size range (should be 20-60px)
3. Check color values (should be bright, saturated)
4. Check lynchpin ring thickness (should be 6px outer, 2px inner)

## Success Criteria

The graph passes if:
✅ All CRITICAL tests pass
✅ Visual hierarchy is obvious within 5 seconds
✅ No JavaScript errors
✅ Interactions work smoothly
✅ Colors are high contrast and saturated
✅ Lynchpins are immediately identifiable

## Test Results

Date: _____________
Tester: _____________

Overall Status: [ ] PASS [ ] FAIL

Notes:
_____________________________________________
_____________________________________________
_____________________________________________
