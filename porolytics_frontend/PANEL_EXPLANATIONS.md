# Panel Explanations Guide

## Complete breakdown of what each panel shows and how to interpret it

---

## SECTION 1 — In-Game Strategy Identity

### 1.1 Strategy Transition Graph
**What It Shows:** Temporal flow map of strategic intent derived from encounter sequences

**How to Read:**
- **Node Size:** Larger = more important (frequency × decisiveness × win_weight)
- **Node Color:** Cyan = wins | Red = losses | Purple = mixed/fragile
- **Gold Ring:** Lynchpin strategy (critical dependency)
- **Edge Thickness:** Transition probability
- **Edge Color:** Outcome-conditioned (cyan = winning, red = losing)

**What It Reveals:**
- Strategy chains (their identity)
- Dead ends (strategy traps)
- Fork points (flexibility or inconsistency)
- Forced paths (predictability)

**Interaction:** Hover for details | Click to focus paths

---

### 1.2 Strategy Phase Timeline
**What It Shows:** Dominant strategy over game time (0-40 minutes)

**How to Read:**
- **Colored Segments:** Dominant strategy per time period
- **Circles Above:** Major objectives
- **Circles Below:** Teamfights
- **X-Axis:** Game time in minutes

**What It Reveals:**
- Early game identity
- Midgame pivot points
- Late game scaling/collapse
- Strategy switch timing

---

## SECTION 2 — Win vs Loss Structural Contrast

### 2.1 Win Graph vs Loss Graph Diff View
**What It Shows:** Side-by-side comparison of WIN vs LOSS patterns

**How to Read:**
- **Left (WIN):** Winning transitions (cyan)
- **Right (LOSS):** Losing transitions (red)
- **Shared Positions:** Easy comparison
- **Edge Presence:** WIN-only = winning patterns

**What It Reveals:**
- What actually works
- What fails
- Bait strategies (looks good, doesn't work)
- Win-only paths (exploit these!)

---

### 2.2 Fragility Overlay
**What It Shows:** Strategy fragility heatmap

**How to Read:**
- **Green:** Stable (high appearance + high win)
- **Yellow:** Fragile (moderate reliability)
- **Red:** BAIT (high appearance + LOW win)

**What It Reveals:**
- Fake identity (red = they use it but lose)
- Overused patterns
- Exploitable habits
- True strengths (green = must deny)

**Coach Insight:** Red = don't ban it, let them pick it

---

## SECTION 3 — Lynchpin Strategy Detection (CORE IP)

### 3.1 Lynchpin Centrality Graph
**What It Shows:** Structurally critical nodes that collapse win paths when denied

**How to Read:**
- **Gold Ring + Pulse:** Confirmed lynchpin
- **Large Bright:** High importance
- **Small Faded:** Low importance
- **Detection:** PageRank + reach collapse

**What It Reveals:**
- Single points of failure
- Dependency depth
- Collapse probability
- Draft priority

**Coach Insight:** Ban champions that enable lynchpin strategies

---

### 3.2 Dependency Fan-Out View
**What It Shows:** Radial tree of downstream dependencies

**How to Read:**
- **Center:** Selected lynchpin (gold)
- **Outer Nodes:** Downstream strategies
- **Edge Thickness:** Dependency strength
- **Percentages:** Transition probability

**What It Reveals:**
- Downstream count
- Collapse % (win paths removed)
- Alternative paths
- Team flexibility

**Coach Insight:** "Denying this removes X% of win paths"

---

## SECTION 4 — In-Game Denial Matrix

### 4.1 Denial Matrix Table
**What It Shows:** Map-level tactics effectiveness

**How to Read:**
- **Rows:** Opponent strategies
- **Columns:** Your denial methods
- **🔴 Red:** High effectiveness
- **🟡 Yellow:** Medium effectiveness
- **🟢 Green:** Low effectiveness

**What It Reveals:**
- Optimal counters (red cells)
- Multi-strategy denials (columns with multiple reds)
- Resistant strategies (no reds = ban in draft)
- Execution plan (graph → gameplay)

**Coach Insight:** Red cells = prioritize these tactics

---

## SECTION 5 — Counter-Strategy Suggestions

**What It Shows:** Auto-generated counters from analysis

**How to Read:**
- **Each Card:** One counter-strategy
- **Opponent Strategy:** What they're doing
- **Approach:** How to disrupt
- **Meta Tags:** When to apply
- **Success Rate:** Historical effectiveness

**What It Reveals:**
- Prioritized counters (top 3)
- Phase-specific tactics
- Champion implications
- Clear execution instructions

**Coach Insight:** Rule-driven, data-backed tactics

---

## SECTION 6 — Strategy Consistency Index

### 6.1 Consistency Radar Chart
**What It Shows:** 5-axis strategic discipline measurement

**How to Read:**
- **5 Axes:** Early Identity, Midgame Pivot, Late Execution, Dependency Breadth, Recovery
- **Outer Edge:** Perfect consistency
- **Center:** Complete chaos
- **Shape:** Tight = predictable | Spiky = volatile

**What It Reveals:**
- Disciplined vs chaotic
- Strong axes (reliable phases)
- Weak axes (vulnerable phases)
- Adaptation capability

**Coach Insight:** Low "Recovery After Denial" = can't adapt, go aggressive early

---

## SECTION 7 — Monte Carlo Simulation

**What It Shows:** Stress-test conclusions under variance

**How to Read:**
- **Win Probability:** Histogram of simulated win rates
- **Strategy Survival:** % viable across simulations
- **Collapse Frequency:** Lynchpin denial impact
- **Confidence Score:** High (>85%) | Medium (60-85%) | Unstable (<60%)

**What It Reveals:**
- Robustness across 10,000+ games
- Draft variance resilience
- Execution variance resilience
- Confidence level

**Coach Insight:**
- 89% confidence = safe bet
- 45% confidence = unstable, need backup

---

## SECTION 8 — Final Coach Summary

**What It Shows:** Single authoritative conclusion

**How to Read:**
- **Identity Spine:** Primary strategy path
- **Lynchpin:** Critical dependency
- **Collapse %:** Win paths removed
- **Monte Carlo:** Confidence level

**What It Reveals:**
- TL;DR for coaches
- What they rely on
- What to deny
- How much it hurts
- How confident to be

**Example:**
"This team relies on **Frontline Teamfight → River Control → Objective Stack**. 
Denying **Frontline Teamfight** collapses **61% of win paths**. 
Monte Carlo confirms this denial holds across **89% of simulated drafts**."

---

## Quick Reference: Color Coding

- **Cyan (#0AC8B9):** Winning patterns, stable strategies
- **Red (#FF4655):** Losing patterns, bait strategies
- **Purple (#9B6FE8):** Mixed/fragile, moderate reliability
- **Gold (#C89B3C):** Lynchpins, critical dependencies
- **Green:** Stable, reliable
- **Yellow:** Fragile, situational

---

## Workflow

1. **View Transition Graph** → Understand their flow
2. **Compare Win/Loss** → Identify what works
3. **Check Fragility** → Find bait strategies
4. **Detect Lynchpins** → Find critical dependencies
5. **Review Denial Matrix** → See actionable counters
6. **Read Counter-Strategies** → Get specific tactics
7. **Check Consistency** → Assess adaptability
8. **Run Monte Carlo** → Validate conclusions
9. **Read Coach Summary** → Get final insight

---

## Mental Models

- **Transition Graph:** Subway map of team movement
- **Win/Loss Diff:** Before/after comparison
- **Fragility:** Trap detector
- **Lynchpin:** Jenga tower (remove one piece, it collapses)
- **Denial Matrix:** Rock-paper-scissors effectiveness chart
- **Consistency Radar:** Personality profile
- **Monte Carlo:** Stress test
- **Coach Summary:** Executive summary
