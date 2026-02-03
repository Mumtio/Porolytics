// ===== STRATEGIC CAPABILITY NODES =====
// Adjusted positions to fit 500x375 canvas with padding
const STRATEGIC_NODES = {
    MID_TEMPO: { 
        x: 250, 
        y: 70, 
        label: 'Mid Tempo',
        meaning: 'Mid lane can control wave state and move first.',
        requires: 'Waveclear or kill threat, safe sidelane access, jungle proximity',
        breaks: 'Mid is forced under tower, vision denied, counter-pick pressure'
    },
    BOT_PRESSURE: { 
        x: 400, 
        y: 100, 
        label: 'Bot Pressure',
        meaning: 'Ability to consistently force priority, dives, or tower damage in bot lane.',
        requires: 'Strong 2v2 lane, reliable engage or poke, early jungle access',
        breaks: 'Support is forced mid/top, ADC lacks early agency, jungle pathing disrupted'
    },
    FRONTLINE_TEAMFIGHT: { 
        x: 375, 
        y: 220, 
        label: 'Frontline\nTeamfight',
        meaning: 'Team can start and survive 5v5 engagements.',
        requires: 'Durable engage champions, follow-up damage, vision setup',
        breaks: 'Engage tools are banned, poke outranges frontline, carries are exposed'
    },
    DIVE_COMP: { 
        x: 125, 
        y: 100, 
        label: 'Dive Comp',
        meaning: 'Team can collapse under towers or into backlines decisively.',
        requires: 'Lockdown CC, burst damage, numbers advantage or tempo',
        breaks: 'Vision denied, defensive cooldowns available, wave state unfavorable'
    },
    OBJECTIVE_CONTROL: { 
        x: 180, 
        y: 220, 
        label: 'Objective\nControl',
        meaning: 'Team can reliably secure neutral objectives.',
        requires: 'Vision dominance, jungle control, lane priority',
        breaks: 'Smite pressure lost, vision collapsed, lanes pushed in'
    },
    PICK_OFF: { 
        x: 100, 
        y: 310, 
        label: 'Pick Off',
        meaning: 'Team can isolate and punish positioning errors.',
        requires: 'Vision traps, burst or CC, fog of war control',
        breaks: 'Grouped play, vision cleared, defensive positioning'
    },
    SCALING_INSURANCE: { 
        x: 315, 
        y: 325, 
        label: 'Scaling\nInsurance',
        meaning: 'Team can safely reach late-game power spikes.',
        requires: 'Defensive play, waveclear, late-game carries',
        breaks: 'Early snowball conceded, key scaling picks banned, nexus threatened early'
    },
    POKE_SIEGE: { 
        x: 430, 
        y: 310, 
        label: 'Poke Siege',
        meaning: 'Team can safely chip objectives without committing.',
        requires: 'Long-range abilities, disengage tools, vision control',
        breaks: 'Hard engage lands, flanks are available, cooldowns mismanaged'
    }
};

// Edge types
const EDGE_TYPES = {
    ENABLES: 'enables',
    AMPLIFIES: 'amplifies',
    PROTECTS: 'protects'
};

// ===== ACO PARAMETERS =====
const ACO_CONFIG = {
    evaporationRate: 0.15,
    winMultiplier: 1.5,
    lossMultiplier: 0.7,
    minConfidence: 0.1,
    maxConfidence: 1.0
};

// ===== GRAPH STATE =====
class StrategyGraph {
    constructor() {
        this.nodes = {};
        this.edges = [];
        
        // Initialize all nodes with 0 strength
        Object.keys(STRATEGIC_NODES).forEach(nodeId => {
            this.nodes[nodeId] = {
                ...STRATEGIC_NODES[nodeId],
                strength: 0,
                confidence: 0,
                winStrength: 0,    // Strength from wins
                lossStrength: 0,   // Strength from losses
                winCount: 0,
                lossCount: 0
            };
        });
        
        // Initialize edges with 0 pheromone
        this.initializeEdges();
    }
    
    initializeEdges() {
        // Define strategic dependencies
        const dependencies = [
            { from: 'MID_TEMPO', to: 'OBJECTIVE_CONTROL', type: EDGE_TYPES.ENABLES },
            { from: 'MID_TEMPO', to: 'DIVE_COMP', type: EDGE_TYPES.AMPLIFIES },
            { from: 'BOT_PRESSURE', to: 'OBJECTIVE_CONTROL', type: EDGE_TYPES.ENABLES },
            { from: 'BOT_PRESSURE', to: 'SCALING_INSURANCE', type: EDGE_TYPES.PROTECTS },
            { from: 'FRONTLINE_TEAMFIGHT', to: 'DIVE_COMP', type: EDGE_TYPES.ENABLES },
            { from: 'FRONTLINE_TEAMFIGHT', to: 'OBJECTIVE_CONTROL', type: EDGE_TYPES.PROTECTS },
            { from: 'DIVE_COMP', to: 'PICK_OFF', type: EDGE_TYPES.AMPLIFIES },
            { from: 'OBJECTIVE_CONTROL', to: 'SCALING_INSURANCE', type: EDGE_TYPES.PROTECTS },
            { from: 'PICK_OFF', to: 'OBJECTIVE_CONTROL', type: EDGE_TYPES.ENABLES },
            { from: 'SCALING_INSURANCE', to: 'POKE_SIEGE', type: EDGE_TYPES.ENABLES },
            { from: 'POKE_SIEGE', to: 'OBJECTIVE_CONTROL', type: EDGE_TYPES.AMPLIFIES }
        ];
        
        this.edges = dependencies.map(dep => ({
            ...dep,
            pheromone: 0,
            confidence: 0,
            winPheromone: 0,
            lossPheromone: 0
        }));
    }
    
    // Evaporate pheromones - DISABLED to allow stacking
    evaporate() {
        // No evaporation - weights keep stacking up
        // This allows patterns to accumulate over time
    }
    
    // Deposit pheromones based on match
    depositPheromones(match, isPicksGraph) {
        const multiplier = match.won ? ACO_CONFIG.winMultiplier : ACO_CONFIG.lossMultiplier;
        
        // Get strategies from match
        const strategies = isPicksGraph ? match.strategies : match.deniedStrategies;
        
        // Deposit on nodes with win/loss tracking
        strategies.forEach(strategy => {
            if (this.nodes[strategy]) {
                const deposit = 0.1 * multiplier;
                this.nodes[strategy].strength += deposit;
                
                // Track win vs loss separately
                if (match.won) {
                    this.nodes[strategy].winStrength += deposit;
                    this.nodes[strategy].winCount++;
                } else {
                    this.nodes[strategy].lossStrength += deposit;
                    this.nodes[strategy].lossCount++;
                }
                
                this.nodes[strategy].confidence = Math.min(
                    this.nodes[strategy].confidence + 0.05,
                    ACO_CONFIG.maxConfidence
                );
            }
        });
        
        // Deposit on edges between active strategies with win/loss tracking
        for (let i = 0; i < strategies.length; i++) {
            for (let j = i + 1; j < strategies.length; j++) {
                const edge = this.edges.find(e => 
                    (e.from === strategies[i] && e.to === strategies[j]) ||
                    (e.from === strategies[j] && e.to === strategies[i])
                );
                
                if (edge) {
                    const deposit = 0.15 * multiplier;
                    edge.pheromone += deposit;
                    
                    // Track win vs loss separately
                    if (match.won) {
                        edge.winPheromone += deposit;
                    } else {
                        edge.lossPheromone += deposit;
                    }
                    
                    edge.confidence = Math.min(
                        edge.confidence + 0.05,
                        ACO_CONFIG.maxConfidence
                    );
                }
            }
        }
    }
    
    // Calculate fragility (lynchpin detection)
    getFragility(nodeId) {
        const node = this.nodes[nodeId];
        if (!node || node.strength === 0) return 0;
        
        // Count connected edges
        const degree = this.edges.filter(e => 
            (e.from === nodeId || e.to === nodeId) && e.pheromone > 0
        ).length;
        
        // Calculate win rate delta
        const totalGames = node.winCount + node.lossCount;
        if (totalGames === 0) return 0;
        
        const winRate = node.winCount / totalGames;
        const deltaWinRate = Math.abs(winRate - 0.5); // Distance from 50%
        
        return degree * deltaWinRate * node.strength;
    }
}

// ===== MOCK MATCH DATA =====
const MOCK_MATCHES = [
    {
        id: 1,
        picks: ['Azir', 'Lee Sin', 'Gnar', 'Jinx', 'Thresh'],
        bans: ['Fiora', 'Camille', 'Jax', 'Yone', 'Akali'],
        strategies: ['MID_TEMPO', 'OBJECTIVE_CONTROL', 'SCALING_INSURANCE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 2,
        picks: ['Orianna', 'Viego', 'Ornn', 'Aphelios', 'Nautilus'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'BOT_PRESSURE', 'SCALING_INSURANCE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 3,
        picks: ['Syndra', 'Lee Sin', 'Renekton', 'Kai\'Sa', 'Leona'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['MID_TEMPO', 'DIVE_COMP', 'PICK_OFF'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: false
    },
    {
        id: 4,
        picks: ['Viktor', 'Elise', 'Gnar', 'Jinx', 'Thresh'],
        bans: ['Fiora', 'Jax', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['MID_TEMPO', 'OBJECTIVE_CONTROL', 'FRONTLINE_TEAMFIGHT'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 5,
        picks: ['Azir', 'Viego', 'Ornn', 'Aphelios', 'Rell'],
        bans: ['Fiora', 'Camille', 'Vayne', 'Yone', 'Akali'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'BOT_PRESSURE', 'SCALING_INSURANCE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 6,
        picks: ['Sylas', 'Graves', 'Sion', 'Xayah', 'Rakan'],
        bans: ['Jax', 'Fiora', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'OBJECTIVE_CONTROL', 'BOT_PRESSURE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 7,
        picks: ['Corki', 'Nidalee', 'Jayce', 'Ezreal', 'Karma'],
        bans: ['Fiora', 'Camille', 'Jax', 'Yone', 'Akali'],
        strategies: ['POKE_SIEGE', 'MID_TEMPO', 'SCALING_INSURANCE'],
        deniedStrategies: ['DIVE_COMP', 'FRONTLINE_TEAMFIGHT'],
        won: false
    },
    {
        id: 8,
        picks: ['Twisted Fate', 'Elise', 'Malphite', 'Ashe', 'Leona'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['MID_TEMPO', 'DIVE_COMP', 'FRONTLINE_TEAMFIGHT'],
        deniedStrategies: ['PICK_OFF', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 9,
        picks: ['Ryze', 'Sejuani', 'Gnar', 'Jinx', 'Thresh'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 10,
        picks: ['LeBlanc', 'Lee Sin', 'Renekton', 'Lucian', 'Nami'],
        bans: ['Fiora', 'Jax', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['MID_TEMPO', 'DIVE_COMP', 'BOT_PRESSURE'],
        deniedStrategies: ['SCALING_INSURANCE', 'POKE_SIEGE'],
        won: false
    },
    {
        id: 11,
        picks: ['Cassiopeia', 'Kindred', 'Ornn', 'Aphelios', 'Nautilus'],
        bans: ['Fiora', 'Camille', 'Vayne', 'Yone', 'Akali'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE', 'BOT_PRESSURE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 12,
        picks: ['Ahri', 'Viego', 'Camille', 'Kai\'Sa', 'Thresh'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['PICK_OFF', 'DIVE_COMP', 'MID_TEMPO'],
        deniedStrategies: ['FRONTLINE_TEAMFIGHT', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 13,
        picks: ['Ziggs', 'Graves', 'Jayce', 'Ezreal', 'Xerath'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['POKE_SIEGE', 'SCALING_INSURANCE', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['DIVE_COMP', 'FRONTLINE_TEAMFIGHT'],
        won: false
    },
    {
        id: 14,
        picks: ['Galio', 'Jarvan IV', 'Sion', 'Ashe', 'Leona'],
        bans: ['Fiora', 'Jax', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'DIVE_COMP', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['PICK_OFF', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 15,
        picks: ['Viktor', 'Graves', 'Gnar', 'Jinx', 'Rell'],
        bans: ['Fiora', 'Camille', 'Vayne', 'Yone', 'Akali'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 16,
        picks: ['Zoe', 'Nidalee', 'Jayce', 'Caitlyn', 'Lux'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['POKE_SIEGE', 'MID_TEMPO', 'BOT_PRESSURE'],
        deniedStrategies: ['DIVE_COMP', 'FRONTLINE_TEAMFIGHT'],
        won: false
    },
    {
        id: 17,
        picks: ['Orianna', 'Lee Sin', 'Malphite', 'Kai\'Sa', 'Nautilus'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'DIVE_COMP', 'MID_TEMPO'],
        deniedStrategies: ['PICK_OFF', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 18,
        picks: ['Azir', 'Sejuani', 'Ornn', 'Aphelios', 'Thresh'],
        bans: ['Fiora', 'Jax', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE', 'BOT_PRESSURE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 19,
        picks: ['Qiyana', 'Lee Sin', 'Renekton', 'Draven', 'Pyke'],
        bans: ['Fiora', 'Camille', 'Vayne', 'Yone', 'Akali'],
        strategies: ['PICK_OFF', 'DIVE_COMP', 'BOT_PRESSURE'],
        deniedStrategies: ['SCALING_INSURANCE', 'POKE_SIEGE'],
        won: false
    },
    {
        id: 20,
        picks: ['Syndra', 'Graves', 'Gnar', 'Jinx', 'Leona'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['MID_TEMPO', 'FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 21,
        picks: ['Taliyah', 'Viego', 'Camille', 'Kai\'Sa', 'Rakan'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['MID_TEMPO', 'PICK_OFF', 'DIVE_COMP'],
        deniedStrategies: ['FRONTLINE_TEAMFIGHT', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 22,
        picks: ['Corki', 'Kindred', 'Jayce', 'Ezreal', 'Karma'],
        bans: ['Fiora', 'Jax', 'Camille', 'Zed', 'Yasuo'],
        strategies: ['POKE_SIEGE', 'SCALING_INSURANCE', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['DIVE_COMP', 'FRONTLINE_TEAMFIGHT'],
        won: false
    },
    {
        id: 23,
        picks: ['Galio', 'Jarvan IV', 'Malphite', 'Ashe', 'Nautilus'],
        bans: ['Fiora', 'Camille', 'Vayne', 'Yone', 'Akali'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'DIVE_COMP', 'OBJECTIVE_CONTROL'],
        deniedStrategies: ['PICK_OFF', 'POKE_SIEGE'],
        won: true
    },
    {
        id: 24,
        picks: ['Ryze', 'Sejuani', 'Ornn', 'Aphelios', 'Rell'],
        bans: ['Fiora', 'Jax', 'Vayne', 'Zed', 'Yasuo'],
        strategies: ['FRONTLINE_TEAMFIGHT', 'SCALING_INSURANCE', 'BOT_PRESSURE'],
        deniedStrategies: ['DIVE_COMP', 'PICK_OFF'],
        won: true
    },
    {
        id: 25,
        picks: ['Twisted Fate', 'Elise', 'Renekton', 'Lucian', 'Leona'],
        bans: ['Camille', 'Fiora', 'Yone', 'Akali', 'LeBlanc'],
        strategies: ['MID_TEMPO', 'DIVE_COMP', 'BOT_PRESSURE'],
        deniedStrategies: ['SCALING_INSURANCE', 'POKE_SIEGE'],
        won: true
    }
];

// ===== SIMULATION STATE =====
let picksGraph = new StrategyGraph();
let bansGraph = new StrategyGraph();
let picksSimulationRunning = false;
let bansSimulationRunning = false;
let picksCurrentMatch = 0;
let bansCurrentMatch = 0;

// ===== CANVAS DRAWING =====
function drawGraph(canvasId, graph, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw edges with win/loss coloring
    graph.edges.forEach(edge => {
        const fromNode = graph.nodes[edge.from];
        const toNode = graph.nodes[edge.to];
        
        if (!fromNode || !toNode) return;
        
        // Calculate node radii
        const fromRadius = 25 + (fromNode.strength * 15);
        const toRadius = 25 + (toNode.strength * 15);
        
        // Calculate angle between nodes
        const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x);
        
        // Calculate start and end points at circle edges
        const startX = fromNode.x + fromRadius * Math.cos(angle);
        const startY = fromNode.y + fromRadius * Math.sin(angle);
        const endX = toNode.x - toRadius * Math.cos(angle);
        const endY = toNode.y - toRadius * Math.sin(angle);
        
        // Calculate win/loss delta for edge color
        const winLossDelta = edge.winPheromone - edge.lossPheromone;
        let edgeColor;
        
        if (edge.pheromone === 0) {
            // No data - use base color
            edgeColor = color === 'purple' ? '155, 111, 232' : '200, 155, 60';
        } else if (winLossDelta > 0.1) {
            // Wins - cyan
            edgeColor = '10, 200, 185';
        } else if (winLossDelta < -0.1) {
            // Losses - red
            edgeColor = '255, 70, 85';
        } else {
            // Mixed - purple (fragile)
            edgeColor = '155, 111, 232';
        }
        
        // Calculate opacity
        const baseOpacity = 0.1;
        const pheromoneOpacity = Math.min(edge.pheromone, 1.0);
        const opacity = baseOpacity + (pheromoneOpacity * 0.9);
        
        // Line width based on pheromone
        const lineWidth = 1 + (edge.pheromone * 3);
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.strokeStyle = `rgba(${edgeColor}, ${opacity})`;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
        
        // Draw arrow at the end point
        const arrowSize = 8 + (edge.pheromone * 4);
        ctx.beginPath();
        ctx.moveTo(endX, endY);
        ctx.lineTo(
            endX - arrowSize * Math.cos(angle - Math.PI / 6),
            endY - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        ctx.lineTo(
            endX - arrowSize * Math.cos(angle + Math.PI / 6),
            endY - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fillStyle = `rgba(${edgeColor}, ${opacity})`;
        ctx.fill();
    });
    
    // Draw nodes with win/loss coloring and fragility indicator
    Object.keys(graph.nodes).forEach(nodeId => {
        const node = graph.nodes[nodeId];
        
        // Calculate win/loss delta for node color
        const winLossDelta = node.winStrength - node.lossStrength;
        let nodeColor;
        
        if (node.strength === 0) {
            // No data - use base color
            nodeColor = color === 'purple' ? '155, 111, 232' : '200, 155, 60';
        } else if (winLossDelta > 0.05) {
            // Wins - cyan
            nodeColor = '10, 200, 185';
        } else if (winLossDelta < -0.05) {
            // Losses - red (bait strategy)
            nodeColor = '255, 70, 85';
        } else {
            // Mixed - purple (fragile)
            nodeColor = '155, 111, 232';
        }
        
        // Calculate opacity
        const baseOpacity = 0.2;
        const strengthOpacity = Math.min(node.strength, 1.0);
        const opacity = baseOpacity + (strengthOpacity * 0.8);
        
        // Node size based on strength
        const baseRadius = 25;
        const radius = baseRadius + (node.strength * 15);
        
        // Calculate fragility
        const fragility = graph.getFragility(nodeId);
        
        // Draw fragility ring if high fragility (lynchpin)
        if (fragility > 0.5) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 5, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(200, 155, 60, ${opacity * 0.8})`;
            ctx.lineWidth = 3;
            ctx.stroke();
        }
        
        // Draw node circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${nodeColor}, ${opacity * 0.3})`;
        ctx.fill();
        ctx.strokeStyle = `rgba(${nodeColor}, ${opacity})`;
        ctx.lineWidth = 3 + (node.strength * 2);
        ctx.stroke();
        
        // Draw label
        ctx.fillStyle = `rgba(240, 246, 246, ${opacity})`;
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const lines = node.label.split('\n');
        lines.forEach((line, i) => {
            ctx.fillText(line, node.x, node.y + (i - lines.length / 2 + 0.5) * 14);
        });
    });
}

// ===== NODE HOVER DETECTION =====
function setupCanvasHover(canvasId, graph, tooltipId) {
    const canvas = document.getElementById(canvasId);
    const tooltip = document.getElementById(tooltipId);
    
    if (!canvas || !tooltip) return;
    
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        let hoveredNode = null;
        
        // Check if mouse is over any node - use STRATEGIC_NODES for positions
        Object.keys(STRATEGIC_NODES).forEach(nodeId => {
            const nodeData = STRATEGIC_NODES[nodeId];
            const nodeState = graph.nodes[nodeId];
            
            // Use base radius of 25 + strength-based growth
            const radius = 25 + (nodeState ? nodeState.strength * 15 : 0);
            const distance = Math.sqrt((x - nodeData.x) ** 2 + (y - nodeData.y) ** 2);
            
            if (distance <= radius) {
                hoveredNode = { id: nodeId, ...nodeData };
            }
        });
        
        if (hoveredNode) {
            // Show tooltip
            tooltip.querySelector('.tooltip-title').textContent = hoveredNode.label.replace('\n', ' ');
            tooltip.querySelector('.tooltip-meaning').textContent = hoveredNode.meaning;
            tooltip.querySelector('.tooltip-requires').textContent = hoveredNode.requires;
            tooltip.querySelector('.tooltip-breaks').textContent = hoveredNode.breaks;
            tooltip.classList.add('active');
            canvas.style.cursor = 'pointer';
        } else {
            // Hide tooltip
            tooltip.classList.remove('active');
            canvas.style.cursor = 'default';
        }
    });
    
    canvas.addEventListener('mouseleave', () => {
        tooltip.classList.remove('active');
        canvas.style.cursor = 'default';
    });
}

// ===== SIMULATION CONTROL =====
function toggleButton(isPicksGraph, isRunning) {
    const buttonId = isPicksGraph ? 'runPicksSimulation' : 'runBansSimulation';
    const button = document.getElementById(buttonId);
    
    if (!button) return;
    
    const playIcon = button.querySelector('.play-icon');
    const pauseIcon = button.querySelector('.pause-icon');
    const btnText = button.querySelector('.btn-text');
    
    if (isRunning) {
        button.classList.add('running');
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
        btnText.textContent = 'Pause';
    } else {
        button.classList.remove('running');
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
        btnText.textContent = 'Run Simulation';
    }
}

function updateConclusions(isPicksGraph, graph) {
    const conclusionsId = isPicksGraph ? 'picksConclusions' : 'bansConclusions';
    const conclusionsPanel = document.getElementById(conclusionsId);
    
    if (!conclusionsPanel) return;
    
    const insightContent = conclusionsPanel.querySelector('.insight-content');
    
    // Find top 3 strongest nodes
    const sortedNodes = Object.keys(graph.nodes)
        .map(nodeId => ({
            id: nodeId,
            label: graph.nodes[nodeId].label.replace('\n', ' '),
            strength: graph.nodes[nodeId].strength,
            winStrength: graph.nodes[nodeId].winStrength,
            lossStrength: graph.nodes[nodeId].lossStrength,
            winCount: graph.nodes[nodeId].winCount,
            lossCount: graph.nodes[nodeId].lossCount,
            fragility: graph.getFragility(nodeId)
        }))
        .filter(node => node.strength > 0)
        .sort((a, b) => b.strength - a.strength)
        .slice(0, 3);
    
    // Find lynchpin (most fragile critical node)
    const lynchpin = Object.keys(graph.nodes)
        .map(nodeId => ({
            id: nodeId,
            label: graph.nodes[nodeId].label.replace('\n', ' '),
            fragility: graph.getFragility(nodeId),
            winCount: graph.nodes[nodeId].winCount,
            lossCount: graph.nodes[nodeId].lossCount
        }))
        .filter(node => node.fragility > 0)
        .sort((a, b) => b.fragility - a.fragility)[0];
    
    // Find bait strategies (high usage, low win rate)
    const baitStrategies = Object.keys(graph.nodes)
        .map(nodeId => {
            const node = graph.nodes[nodeId];
            const totalGames = node.winCount + node.lossCount;
            const winRate = totalGames > 0 ? node.winCount / totalGames : 0;
            return {
                id: nodeId,
                label: node.label.replace('\n', ' '),
                winRate: winRate,
                totalGames: totalGames,
                delta: node.lossStrength - node.winStrength
            };
        })
        .filter(node => node.totalGames >= 3 && node.winRate < 0.4)
        .sort((a, b) => b.delta - a.delta)
        .slice(0, 1);
    
    if (sortedNodes.length === 0) {
        insightContent.innerHTML = '<p class="insight-placeholder">Run the simulation to see strategic patterns emerge...</p>';
        return;
    }
    
    let html = '';
    
    // Primary strategies with win/loss context
    if (sortedNodes.length > 0) {
        html += '<div class="insight-item">';
        html += '<strong>Primary Strategies:</strong>';
        sortedNodes.forEach(n => {
            const totalGames = n.winCount + n.lossCount;
            const winRate = totalGames > 0 ? Math.round((n.winCount / totalGames) * 100) : 0;
            const delta = n.winStrength - n.lossStrength;
            
            let indicator = '';
            if (delta > 0.05) indicator = ' <span style="color: #0AC8B9">✓ Works</span>';
            else if (delta < -0.05) indicator = ' <span style="color: #FF4655">✗ Bait</span>';
            else indicator = ' <span style="color: #9B6FE8">⚠ Fragile</span>';
            
            html += `<p>• ${n.label} (${winRate}% WR)${indicator}</p>`;
        });
        html += '</div>';
    }
    
    // Lynchpin detection
    if (lynchpin && lynchpin.fragility > 0.5) {
        html += '<div class="insight-item">';
        html += '<strong>🎯 Lynchpin Strategy:</strong>';
        html += `<p>${lynchpin.label} - High dependency, critical to composition. Denying this collapses the entire strategy.</p>`;
        html += '</div>';
    }
    
    // Bait strategies
    if (baitStrategies.length > 0) {
        html += '<div class="insight-item">';
        html += '<strong>⚠️ Bait Strategy:</strong>';
        const bait = baitStrategies[0];
        html += `<p>${bait.label} - Looks good in draft but loses games (${Math.round(bait.winRate * 100)}% WR). Avoid or counter-draft.</p>`;
        html += '</div>';
    }
    
    // Coach-facing insight
    html += '<div class="insight-item">';
    html += '<strong>Coach Insight:</strong>';
    if (isPicksGraph) {
        if (lynchpin && sortedNodes.length > 0) {
            const primary = sortedNodes[0].label;
            html += `<p>Team drafts ${primary}, but composition depends on ${lynchpin.label}. Denying ${lynchpin.label} converts their comp into a low-impact draft.</p>`;
        } else if (sortedNodes.length > 0) {
            html += `<p>Team consistently builds around ${sortedNodes[0].label}. Target this strategy in bans or draft counter-engage tools.</p>`;
        }
    } else {
        if (sortedNodes.length > 0) {
            html += `<p>Team fears ${sortedNodes[0].label} strategies. They ban these when threatened. Force them into uncomfortable matchups by securing these early.</p>`;
        }
    }
    html += '</div>';
    
    insightContent.innerHTML = html;
}

function runSimulation(isPicksGraph) {
    const graph = isPicksGraph ? picksGraph : bansGraph;
    const currentMatchIndex = isPicksGraph ? picksCurrentMatch : bansCurrentMatch;
    const canvasId = isPicksGraph ? 'picksGraph' : 'bansGraph';
    const color = isPicksGraph ? 'purple' : 'gold';
    
    if (currentMatchIndex >= MOCK_MATCHES.length) {
        if (isPicksGraph) {
            picksSimulationRunning = false;
            toggleButton(true, false);
        } else {
            bansSimulationRunning = false;
            toggleButton(false, false);
        }
        return;
    }
    
    // Evaporate (disabled - no decay)
    graph.evaporate();
    
    // Deposit pheromones for current match
    const match = MOCK_MATCHES[currentMatchIndex];
    graph.depositPheromones(match, isPicksGraph);
    
    // Update timeline
    updateTimeline(isPicksGraph, currentMatchIndex);
    
    // Draw graph
    drawGraph(canvasId, graph, color);
    
    // Update conclusions
    updateConclusions(isPicksGraph, graph);
    
    // Increment match counter
    if (isPicksGraph) {
        picksCurrentMatch++;
    } else {
        bansCurrentMatch++;
    }
    
    // Continue simulation
    if ((isPicksGraph && picksSimulationRunning) || (!isPicksGraph && bansSimulationRunning)) {
        setTimeout(() => runSimulation(isPicksGraph), 1000);
    }
}

function initializeTimeline(isPicksGraph) {
    const timelineId = isPicksGraph ? 'picksTimeline' : 'bansTimeline';
    const timeline = document.getElementById(timelineId);
    
    if (!timeline) return;
    
    // Clear existing nodes
    timeline.innerHTML = '';
    
    // Create all match nodes
    MOCK_MATCHES.forEach((match, index) => {
        const node = document.createElement('div');
        node.className = 'match-node';
        node.innerHTML = `<span>M${match.id}</span>`;
        node.dataset.matchIndex = index;
        
        node.addEventListener('click', () => {
            showMatchDetail(isPicksGraph, index);
        });
        
        timeline.appendChild(node);
    });
}

function updateTimeline(isPicksGraph, currentMatchIndex) {
    const timelineId = isPicksGraph ? 'picksTimeline' : 'bansTimeline';
    const timeline = document.getElementById(timelineId);
    
    if (!timeline) return;
    
    // Update active state
    Array.from(timeline.children).forEach((node, index) => {
        if (index <= currentMatchIndex) {
            node.classList.add('active');
        } else {
            node.classList.remove('active');
        }
    });
}

function showMatchDetail(isPicksGraph, matchIndex) {
    const match = MOCK_MATCHES[matchIndex];
    const popupId = isPicksGraph ? 'picksDetailPopup' : 'bansDetailPopup';
    const popup = document.getElementById(popupId);
    
    if (!popup) return;
    
    const matchNumberSpan = popup.querySelector(`#${isPicksGraph ? 'picks' : 'bans'}MatchNumber`);
    const matchDataDiv = popup.querySelector(`#${isPicksGraph ? 'picks' : 'bans'}MatchData`);
    
    matchNumberSpan.textContent = match.id;
    
    if (isPicksGraph) {
        matchDataDiv.innerHTML = `
            <h5>Champion Picks:</h5>
            <p>${match.picks.join(', ')}</p>
            <h5>Inferred Strategies:</h5>
            <p>${match.strategies.map(s => STRATEGIC_NODES[s].label.replace('\n', ' ')).join(', ')}</p>
            <h5>Result:</h5>
            <p style="color: ${match.won ? '#0AC8B9' : '#FF4655'}">${match.won ? 'Victory' : 'Defeat'}</p>
        `;
    } else {
        matchDataDiv.innerHTML = `
            <h5>Champion Bans:</h5>
            <p>${match.bans.join(', ')}</p>
            <h5>Denied Strategies:</h5>
            <p>${match.deniedStrategies.map(s => STRATEGIC_NODES[s].label.replace('\n', ' ')).join(', ')}</p>
            <h5>Result:</h5>
            <p style="color: ${match.won ? '#0AC8B9' : '#FF4655'}">${match.won ? 'Victory' : 'Defeat'}</p>
        `;
    }
    
    popup.classList.add('active');
    
    // Don't auto-close - user must click X or click another match
}

// ===== EVENT LISTENERS =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize graphs with initial draw
    drawGraph('picksGraph', picksGraph, 'purple');
    drawGraph('bansGraph', bansGraph, 'gold');
    
    // Initialize timelines with all matches visible
    initializeTimeline(true);  // Picks timeline
    initializeTimeline(false); // Bans timeline
    
    // Setup canvas hover for node tooltips
    setupCanvasHover('picksGraph', picksGraph, 'picksNodeTooltip');
    setupCanvasHover('bansGraph', bansGraph, 'bansNodeTooltip');
    
    // Picks simulation controls
    document.getElementById('runPicksSimulation')?.addEventListener('click', () => {
        if (!picksSimulationRunning) {
            picksSimulationRunning = true;
            toggleButton(true, true);
            runSimulation(true);
        } else {
            picksSimulationRunning = false;
            toggleButton(true, false);
        }
    });
    
    document.getElementById('resetPicksSimulation')?.addEventListener('click', () => {
        picksSimulationRunning = false;
        picksCurrentMatch = 0;
        picksGraph = new StrategyGraph();
        drawGraph('picksGraph', picksGraph, 'purple');
        initializeTimeline(true);
        toggleButton(true, false);
        setupCanvasHover('picksGraph', picksGraph, 'picksNodeTooltip');
        
        // Reset conclusions
        const conclusionsPanel = document.getElementById('picksConclusions');
        if (conclusionsPanel) {
            const insightContent = conclusionsPanel.querySelector('.insight-content');
            insightContent.innerHTML = '<p class="insight-placeholder">Run the simulation to see strategic patterns emerge...</p>';
        }
    });
    
    // Bans simulation controls
    document.getElementById('runBansSimulation')?.addEventListener('click', () => {
        if (!bansSimulationRunning) {
            bansSimulationRunning = true;
            toggleButton(false, true);
            runSimulation(false);
        } else {
            bansSimulationRunning = false;
            toggleButton(false, false);
        }
    });
    
    document.getElementById('resetBansSimulation')?.addEventListener('click', () => {
        bansSimulationRunning = false;
        bansCurrentMatch = 0;
        bansGraph = new StrategyGraph();
        drawGraph('bansGraph', bansGraph, 'gold');
        initializeTimeline(false);
        toggleButton(false, false);
        setupCanvasHover('bansGraph', bansGraph, 'bansNodeTooltip');
        
        // Reset conclusions
        const conclusionsPanel = document.getElementById('bansConclusions');
        if (conclusionsPanel) {
            const insightContent = conclusionsPanel.querySelector('.insight-content');
            insightContent.innerHTML = '<p class="insight-placeholder">Run the simulation to see strategic patterns emerge...</p>';
        }
    });
    
    // Load team names from localStorage
    const yourTeam = localStorage.getItem('yourTeam') || 'G2 Esports';
    const opponentTeam = localStorage.getItem('opponentTeam') || 'GIANTX';
    
    const teamNames = document.querySelectorAll('.team-name');
    if (teamNames.length >= 2) {
        teamNames[0].textContent = yourTeam;
        teamNames[1].textContent = opponentTeam;
    }
});
