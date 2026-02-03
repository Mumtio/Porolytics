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
    
    // Load team names from localStorage or set defaults
    const yourTeam = localStorage.getItem('yourTeam') || 'Cloud9';
    const opponentTeam = localStorage.getItem('opponentTeam') || 'T1';
    
    // Set defaults in localStorage if not present
    if (!localStorage.getItem('yourTeam')) {
        localStorage.setItem('yourTeam', 'Cloud9');
    }
    if (!localStorage.getItem('opponentTeam')) {
        localStorage.setItem('opponentTeam', 'T1');
    }
    
    const teamNames = document.querySelectorAll('.team-name');
    if (teamNames.length >= 2) {
        teamNames[0].textContent = yourTeam;
        teamNames[1].textContent = opponentTeam;
    }
});


// ===== STRATEGY TRANSITION GRAPH =====

class StrategyTransitionGraph {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Strategy transition canvas not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.edges = [];
        this.lynchpins = [];
        this.currentFilter = 'combined';
        this.minFrequency = 0.05;
        this.hoveredElement = null;
        this.selectedNode = null;
        
        // Pan and zoom state
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        
        // Set canvas size to fit container
        this.resizeCanvas();
        
        this.initData();
        this.setupControls();
        this.setupMouseEvents();
        this.render();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.calculatePositions();
            this.render();
        });
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set canvas to fill container
        this.canvas.width = rect.width - 40;
        this.canvas.height = rect.height - 40;
    }
    
    initData() {
        // Strategy nodes with realistic in-game data
        this.nodes = [
            {
                id: 'BOT_PRESSURE',
                name: 'Bot Pressure',
                x: 0, y: 0,
                usageRate: 0.32,
                winRate: 0.68,
                nextStrategies: ['Objective Control', 'Teamfight']
            },
            {
                id: 'TEAMFIGHT',
                name: 'Frontline\nTeamfight',
                x: 0, y: 0,
                usageRate: 0.35,
                winRate: 0.72,
                nextStrategies: ['Objective Control', 'Scaling']
            },
            {
                id: 'OBJECTIVE',
                name: 'Objective\nControl',
                x: 0, y: 0,
                usageRate: 0.35,
                winRate: 0.72,
                nextStrategies: ['Teamfight', 'Mid Tempo']
            },
            {
                id: 'MID_TEMPO',
                name: 'Mid Tempo',
                x: 0, y: 0,
                usageRate: 0.24,
                winRate: 0.58,
                nextStrategies: ['Objective Control', 'Dive Comp']
            },
            {
                id: 'DIVE',
                name: 'Dive Comp',
                x: 0, y: 0,
                usageRate: 0.22,
                winRate: 0.55,
                nextStrategies: ['Objective Control', 'Pick Off']
            },
            {
                id: 'PICK_OFF',
                name: 'Pick Off',
                x: 0, y: 0,
                usageRate: 0.15,
                winRate: 0.35,
                nextStrategies: ['Scaling', 'Dive Comp']
            },
            {
                id: 'SCALING',
                name: 'Scaling\nInsurance',
                x: 0, y: 0,
                usageRate: 0.28,
                winRate: 0.62,
                nextStrategies: ['Teamfight', 'Objective Control']
            },
            {
                id: 'POKE',
                name: 'Poke Siege',
                x: 0, y: 0,
                usageRate: 0.12,
                winRate: 0.32,
                nextStrategies: ['Bot Pressure', 'Scaling']
            }
        ];
        
        // Transition edges - matching reference graph structure
        this.edges = [
            { from: 'OBJECTIVE', to: 'TEAMFIGHT', frequency: 0.28, successRate: 0.72 },
            { from: 'TEAMFIGHT', to: 'SCALING', frequency: 0.25, successRate: 0.68 },
            { from: 'TEAMFIGHT', to: 'BOT_PRESSURE', frequency: 0.22, successRate: 0.65 },
            { from: 'BOT_PRESSURE', to: 'OBJECTIVE', frequency: 0.20, successRate: 0.62 },
            { from: 'MID_TEMPO', to: 'OBJECTIVE', frequency: 0.18, successRate: 0.58 },
            { from: 'MID_TEMPO', to: 'DIVE', frequency: 0.15, successRate: 0.55 },
            { from: 'DIVE', to: 'OBJECTIVE', frequency: 0.14, successRate: 0.52 },
            { from: 'DIVE', to: 'PICK_OFF', frequency: 0.10, successRate: 0.38 },
            { from: 'SCALING', to: 'TEAMFIGHT', frequency: 0.16, successRate: 0.60 },
            { from: 'PICK_OFF', to: 'SCALING', frequency: 0.08, successRate: 0.35 },
            { from: 'POKE', to: 'SCALING', frequency: 0.06, successRate: 0.32 }
        ];
        
        // Lynchpin strategies
        this.lynchpins = ['TEAMFIGHT', 'OBJECTIVE', 'SCALING'];
        
        this.calculatePositions();
    }
    
    calculatePositions() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        // Scale factor - more conservative to ensure everything fits
        const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
        
        // Manual positioning with increased spacing
        const positions = {
            'MID_TEMPO': { x: centerX, y: centerY - 140 * scale },
            'BOT_PRESSURE': { x: centerX + 190 * scale, y: centerY - 70 * scale },
            'DIVE': { x: centerX - 190 * scale, y: centerY - 70 * scale },
            'OBJECTIVE': { x: centerX - 110 * scale, y: centerY },
            'TEAMFIGHT': { x: centerX + 110 * scale, y: centerY },
            'SCALING': { x: centerX, y: centerY + 95 * scale },
            'PICK_OFF': { x: centerX - 190 * scale, y: centerY + 95 * scale },
            'POKE': { x: centerX + 190 * scale, y: centerY + 95 * scale }
        };
        
        this.nodes.forEach(node => {
            if (positions[node.id]) {
                node.x = positions[node.id].x;
                node.y = positions[node.id].y;
            }
        });
    }
    
    setupControls() {
        // Outcome filter
        document.querySelectorAll('input[name="outcome-filter"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.currentFilter = e.target.value;
                this.render();
            });
        });
        
        // Frequency slider
        const slider = document.getElementById('transition-frequency');
        const valueDisplay = document.getElementById('frequency-value');
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                this.minFrequency = parseFloat(e.target.value);
                valueDisplay.textContent = Math.round(this.minFrequency * 100) + '%';
                this.render();
            });
        }
        
        // Zoom controls
        const zoomInBtn = document.getElementById('zoom-in-btn');
        const zoomOutBtn = document.getElementById('zoom-out-btn');
        const resetZoomBtn = document.getElementById('reset-zoom-btn');
        
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                this.zoom = Math.min(this.zoom * 1.2, 3);
                this.render();
            });
        }
        
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                this.zoom = Math.max(this.zoom / 1.2, 0.5);
                this.render();
            });
        }
        
        if (resetZoomBtn) {
            resetZoomBtn.addEventListener('click', () => {
                this.zoom = 1;
                this.panX = 0;
                this.panY = 0;
                this.render();
            });
        }
    }
    
    setupMouseEvents() {
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.handleMouseLeave());
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        
        // Pan controls
        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0 && e.shiftKey) { // Shift + Left click to pan
                this.isDragging = true;
                this.dragStartX = e.clientX - this.panX;
                this.dragStartY = e.clientY - this.panY;
                this.canvas.style.cursor = 'grabbing';
            }
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.panX = e.clientX - this.dragStartX;
                this.panY = e.clientY - this.dragStartY;
                this.render();
            }
        });
        
        this.canvas.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.canvas.style.cursor = 'crosshair';
        });
        
        // Zoom with mouse wheel
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            this.zoom = Math.max(0.5, Math.min(3, this.zoom * delta));
            this.render();
        });
    }
    
    handleMouseMove(e) {
        if (this.isDragging) return; // Skip hover detection while dragging
        
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.panX) / this.zoom;
        const y = (e.clientY - rect.top - this.panY) / this.zoom;
        
        let newHovered = null;
        
        // Check nodes
        for (const node of this.nodes) {
            const size = this.getNodeSize(node);
            const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
            if (distance <= size) {
                newHovered = { type: 'node', element: node };
                break;
            }
        }
        
        // Check edges if no node hovered
        if (!newHovered) {
            for (const edge of this.getVisibleEdges()) {
                if (this.isPointOnEdge(x, y, edge)) {
                    newHovered = { type: 'edge', element: edge };
                    break;
                }
            }
        }
        
        if (JSON.stringify(newHovered) !== JSON.stringify(this.hoveredElement)) {
            this.hoveredElement = newHovered;
            this.updateTooltip(e.clientX, e.clientY);
            this.render();
        }
    }
    
    handleMouseLeave() {
        this.hoveredElement = null;
        this.hideTooltips();
        this.render();
    }
    
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left - this.panX) / this.zoom;
        const y = (e.clientY - rect.top - this.panY) / this.zoom;
        
        for (const node of this.nodes) {
            const size = this.getNodeSize(node);
            const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
            if (distance <= size) {
                this.selectedNode = this.selectedNode === node.id ? null : node.id;
                this.render();
                return;
            }
        }
        
        this.selectedNode = null;
        this.render();
    }
    
    isPointOnEdge(x, y, edge) {
        const fromNode = this.nodes.find(n => n.id === edge.from);
        const toNode = this.nodes.find(n => n.id === edge.to);
        
        if (!fromNode || !toNode) return false;
        
        const A = x - fromNode.x;
        const B = y - fromNode.y;
        const C = toNode.x - fromNode.x;
        const D = toNode.y - fromNode.y;
        
        const dot = A * C + B * D;
        const lenSq = C * C + D * D;
        
        if (lenSq === 0) return false;
        
        const param = dot / lenSq;
        if (param < 0 || param > 1) return false;
        
        const xx = fromNode.x + param * C;
        const yy = fromNode.y + param * D;
        
        const distance = Math.sqrt((x - xx) ** 2 + (y - yy) ** 2);
        const thickness = this.getEdgeThickness(edge);
        
        return distance <= thickness / 2 + 5;
    }
    
    updateTooltip(clientX, clientY) {
        if (!this.hoveredElement) {
            this.hideTooltips();
            return;
        }
        
        const tooltip = this.hoveredElement.type === 'node' ? 
            document.getElementById('nodeTooltip') : 
            document.getElementById('edgeTooltip');
        
        if (!tooltip) return;
        
        if (this.hoveredElement.type === 'node') {
            const node = this.hoveredElement.element;
            tooltip.querySelector('.tooltip-title').textContent = node.name;
            tooltip.querySelector('.usage-rate').textContent = Math.round(node.usageRate * 100) + '%';
            tooltip.querySelector('.win-rate').textContent = Math.round(node.winRate * 100) + '%';
            tooltip.querySelector('.next-strategies').textContent = node.nextStrategies.join(', ');
        } else {
            const edge = this.hoveredElement.element;
            const fromNode = this.nodes.find(n => n.id === edge.from);
            const toNode = this.nodes.find(n => n.id === edge.to);
            tooltip.querySelector('.tooltip-title').textContent = `${fromNode.name} → ${toNode.name}`;
            tooltip.querySelector('.frequency').textContent = Math.round(edge.frequency * 100) + '%';
            tooltip.querySelector('.success-rate').textContent = Math.round(edge.successRate * 100) + '%';
        }
        
        // Position tooltip with smart placement to avoid going off-screen
        const tooltipRect = tooltip.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        let left = clientX + 15;
        let top = clientY - 10;
        
        // Adjust horizontal position if tooltip would go off right edge
        if (left + tooltipRect.width > viewportWidth - 20) {
            left = clientX - tooltipRect.width - 15;
        }
        
        // Adjust vertical position if tooltip would go off bottom edge
        if (top + tooltipRect.height > viewportHeight - 20) {
            top = viewportHeight - tooltipRect.height - 20;
        }
        
        // Adjust vertical position if tooltip would go off top edge
        if (top < 20) {
            top = 20;
        }
        
        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        tooltip.classList.add('active');
        
        // Hide other tooltip
        const otherTooltip = this.hoveredElement.type === 'node' ? 
            document.getElementById('edgeTooltip') : 
            document.getElementById('nodeTooltip');
        if (otherTooltip) otherTooltip.classList.remove('active');
    }
    
    hideTooltips() {
        document.getElementById('nodeTooltip')?.classList.remove('active');
        document.getElementById('edgeTooltip')?.classList.remove('active');
    }
    
    getVisibleEdges() {
        return this.edges.filter(edge => edge.frequency >= this.minFrequency);
    }
    
    getNodeSize(node) {
        // Scale node size based on canvas dimensions
        const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
        const baseSize = 45 * scale;
        const maxSize = 70 * scale;
        return baseSize + (node.usageRate * (maxSize - baseSize));
    }
    
    getNodeColor(node) {
        if (node.winRate >= 0.6) return '#0AC8B9'; // Cyan for wins
        if (node.winRate <= 0.4) return '#FF4655'; // Red for losses
        return '#9B6FE8'; // Purple for mixed
    }
    
    getEdgeThickness(edge) {
        const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
        const minThickness = 2 * scale;
        const maxThickness = 6 * scale;
        return minThickness + (edge.frequency / 0.3) * (maxThickness - minThickness);
    }
    
    getEdgeColor(edge) {
        if (edge.successRate >= 0.6) return '#0AC8B9';
        if (edge.successRate <= 0.4) return '#FF4655';
        return '#9B6FE8';
    }
    
    render() {
        // Clear with gradient
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, 'rgba(1, 10, 19, 0.95)');
        gradient.addColorStop(1, 'rgba(10, 21, 32, 0.8)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Apply zoom and pan transformations
        this.ctx.save();
        this.ctx.translate(this.panX, this.panY);
        this.ctx.scale(this.zoom, this.zoom);
        
        // Draw edges first
        this.drawEdges();
        
        // Draw nodes on top
        this.drawNodes();
        
        // Restore transformation
        this.ctx.restore();
    }
    
    drawEdges() {
        const visibleEdges = this.getVisibleEdges();
        
        visibleEdges.forEach(edge => {
            const fromNode = this.nodes.find(n => n.id === edge.from);
            const toNode = this.nodes.find(n => n.id === edge.to);
            
            if (!fromNode || !toNode) return;
            
            // Filter by outcome
            if (this.currentFilter === 'win' && edge.successRate < 0.5) return;
            if (this.currentFilter === 'loss' && edge.successRate >= 0.5) return;
            
            const dx = toNode.x - fromNode.x;
            const dy = toNode.y - fromNode.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const unitX = dx / distance;
            const unitY = dy / distance;
            
            const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
            const padding = 65 * scale;
            const startX = fromNode.x + unitX * padding;
            const startY = fromNode.y + unitY * padding;
            const endX = toNode.x - unitX * (padding + 5 * scale);
            const endY = toNode.y - unitY * (padding + 5 * scale);
            
            const isHovered = this.hoveredElement?.type === 'edge' && 
                             this.hoveredElement.element === edge;
            const thickness = this.getEdgeThickness(edge) + (isHovered ? 3 * scale : 0);
            const color = this.getEdgeColor(edge);
            
            // Draw shadow/outline for definition
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            this.ctx.lineTo(endX, endY);
            this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.lineWidth = thickness + 2 * scale;
            this.ctx.lineCap = 'round';
            this.ctx.stroke();
            
            // Draw main line
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            this.ctx.lineTo(endX, endY);
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = thickness;
            this.ctx.lineCap = 'round';
            this.ctx.stroke();
            
            // Calculate angle for arrowhead
            const angle = Math.atan2(endY - startY, endX - startX);
            
            // Draw arrowhead (scaled)
            const arrowSize = Math.max(16 * scale, thickness * 1.2);
            
            // Arrow shadow
            this.ctx.beginPath();
            this.ctx.moveTo(endX, endY);
            this.ctx.lineTo(
                endX - arrowSize * Math.cos(angle - Math.PI / 7),
                endY - arrowSize * Math.sin(angle - Math.PI / 7)
            );
            this.ctx.lineTo(
                endX - arrowSize * Math.cos(angle + Math.PI / 7),
                endY - arrowSize * Math.sin(angle + Math.PI / 7)
            );
            this.ctx.closePath();
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fill();
            
            // Arrow main
            this.ctx.beginPath();
            this.ctx.moveTo(endX, endY);
            this.ctx.lineTo(
                endX - (arrowSize - 1) * Math.cos(angle - Math.PI / 7),
                endY - (arrowSize - 1) * Math.sin(angle - Math.PI / 7)
            );
            this.ctx.lineTo(
                endX - (arrowSize - 1) * Math.cos(angle + Math.PI / 7),
                endY - (arrowSize - 1) * Math.sin(angle + Math.PI / 7)
            );
            this.ctx.closePath();
            this.ctx.fillStyle = color;
            this.ctx.fill();
            
            // Subtle glow for important edges
            if (thickness > 10 || isHovered) {
                this.ctx.shadowColor = color;
                this.ctx.shadowBlur = isHovered ? 12 : 6;
                this.ctx.beginPath();
                this.ctx.moveTo(startX, startY);
                this.ctx.lineTo(endX, endY);
                this.ctx.strokeStyle = color;
                this.ctx.lineWidth = thickness;
                this.ctx.stroke();
                this.ctx.shadowBlur = 0;
            }
        });
    }
    
    drawNodes() {
        const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
        
        this.nodes.forEach(node => {
            const size = this.getNodeSize(node);
            const color = this.getNodeColor(node);
            const isSelected = this.selectedNode === node.id;
            const isHovered = this.hoveredElement?.type === 'node' && 
                            this.hoveredElement.element === node;
            const isLynchpin = this.lynchpins.includes(node.id);
            
            // Lynchpin gold ring
            if (isLynchpin) {
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, size + 10 * scale, 0, Math.PI * 2);
                this.ctx.strokeStyle = '#C89B3C';
                this.ctx.lineWidth = 5 * scale;
                this.ctx.shadowColor = '#C89B3C';
                this.ctx.shadowBlur = 10 * scale;
                this.ctx.stroke();
                this.ctx.shadowBlur = 0;
            }
            
            // Node background (dark)
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
            this.ctx.fillStyle = 'rgba(1, 10, 19, 0.95)';
            this.ctx.fill();
            
            // Node border outline (subtle)
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
            this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.6)';
            this.ctx.lineWidth = (isSelected ? 6 : (isHovered ? 5 : 4)) * scale;
            this.ctx.stroke();
            
            // Node border (colored)
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
            this.ctx.strokeStyle = isSelected ? '#C89B3C' : color;
            this.ctx.lineWidth = (isSelected ? 4 : (isHovered ? 3.5 : 3)) * scale;
            this.ctx.stroke();
            
            // Subtle glow for important nodes
            if (node.usageRate > 0.3 || isHovered) {
                this.ctx.shadowColor = color;
                this.ctx.shadowBlur = (isHovered ? 15 : 8) * scale;
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
                this.ctx.strokeStyle = color;
                this.ctx.lineWidth = (isHovered ? 3.5 : 3) * scale;
                this.ctx.stroke();
                this.ctx.shadowBlur = 0;
            }
            
            // Node label with shadow for readability
            this.ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
            this.ctx.shadowBlur = 4 * scale;
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.font = `bold ${Math.max(13 * scale, size * 0.22)}px sans-serif`;
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            // Handle multi-line text
            const lines = node.name.split('\n');
            const lineHeight = Math.max(15 * scale, size * 0.25);
            const startY = node.y - ((lines.length - 1) * lineHeight) / 2;
            
            lines.forEach((line, i) => {
                this.ctx.fillText(line, node.x, startY + i * lineHeight);
            });
            
            this.ctx.shadowBlur = 0;
        });
    }
}

// Initialize strategy transition graph when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.strategyTransitionGraph = new StrategyTransitionGraph('strategyTransitionGraph');
});


// ===== STRATEGY IMPORTANCE RANKING INTERACTIONS =====

document.addEventListener('DOMContentLoaded', () => {
    const rankingCards = document.querySelectorAll('.ranking-card');
    
    rankingCards.forEach(card => {
        card.addEventListener('click', () => {
            const strategyId = card.getAttribute('data-strategy');
            
            // Find the strategy transition graph instance
            if (window.strategyTransitionGraph) {
                // Highlight the corresponding node
                window.strategyTransitionGraph.selectedNode = strategyId;
                window.strategyTransitionGraph.render();
                
                // Scroll to the strategy transition graph
                const graphSection = document.querySelector('.strategy-transition-section');
                if (graphSection) {
                    graphSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
            
            // Visual feedback on card
            rankingCards.forEach(c => c.style.borderColor = 'rgba(155, 111, 232, 0.2)');
            card.style.borderColor = '#C89B3C';
        });
    });
});


// ===== STRATEGY FAILURE MODES INTERACTIONS =====

document.addEventListener('DOMContentLoaded', () => {
    const failureCards = document.querySelectorAll('.failure-card');
    
    failureCards.forEach(card => {
        card.addEventListener('click', () => {
            const pattern = card.getAttribute('data-pattern');
            const strategies = pattern.split('-');
            
            // Find the strategy transition graph instance
            if (window.strategyTransitionGraph) {
                // Highlight the failure path in the graph
                // For now, highlight the first strategy in the path
                window.strategyTransitionGraph.selectedNode = strategies[0];
                window.strategyTransitionGraph.render();
                
                // Scroll to the strategy transition graph
                const graphSection = document.querySelector('.strategy-transition-section');
                if (graphSection) {
                    graphSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
            
            // Visual feedback on card
            failureCards.forEach(c => c.style.borderColor = 'rgba(255, 70, 85, 0.3)');
            card.style.borderColor = '#FF4655';
            card.style.borderWidth = '3px';
        });
    });
});


// ===== LYNCHPIN STRESS TEST GRAPH =====

class StressTestGraph {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Stress test canvas not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.deniedLynchpin = 'OBJECTIVE'; // Default
        this.nodes = [];
        this.edges = [];
        this.hoveredNode = null;
        
        this.resizeCanvas();
        this.initData();
        this.setupControls();
        this.setupMouseEvents();
        this.render();
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        this.canvas.width = Math.min(1200, rect.width - 60);
        this.canvas.height = Math.min(500, rect.height - 60);
    }
    
    initData() {
        // Same nodes as strategy transition graph
        this.nodes = [
            { id: 'MID_TEMPO', name: 'Mid Tempo', x: 0, y: 0 },
            { id: 'BOT_PRESSURE', name: 'Bot Pressure', x: 0, y: 0 },
            { id: 'DIVE', name: 'Dive Comp', x: 0, y: 0 },
            { id: 'OBJECTIVE', name: 'Objective\nControl', x: 0, y: 0 },
            { id: 'TEAMFIGHT', name: 'Frontline\nTeamfight', x: 0, y: 0 },
            { id: 'SCALING', name: 'Scaling\nInsurance', x: 0, y: 0 },
            { id: 'PICK_OFF', name: 'Pick Off', x: 0, y: 0 },
            { id: 'POKE', name: 'Poke Siege', x: 0, y: 0 }
        ];
        
        this.edges = [
            { from: 'OBJECTIVE', to: 'TEAMFIGHT' },
            { from: 'TEAMFIGHT', to: 'SCALING' },
            { from: 'TEAMFIGHT', to: 'BOT_PRESSURE' },
            { from: 'BOT_PRESSURE', to: 'OBJECTIVE' },
            { from: 'MID_TEMPO', to: 'OBJECTIVE' },
            { from: 'MID_TEMPO', to: 'DIVE' },
            { from: 'DIVE', to: 'OBJECTIVE' },
            { from: 'DIVE', to: 'PICK_OFF' },
            { from: 'SCALING', to: 'TEAMFIGHT' },
            { from: 'PICK_OFF', to: 'SCALING' },
            { from: 'POKE', to: 'SCALING' }
        ];
        
        this.calculatePositions();
    }
    
    calculatePositions() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const scale = Math.min(this.canvas.width / 900, this.canvas.height / 600);
        
        const positions = {
            'MID_TEMPO': { x: centerX, y: centerY - 140 * scale },
            'BOT_PRESSURE': { x: centerX + 190 * scale, y: centerY - 70 * scale },
            'DIVE': { x: centerX - 190 * scale, y: centerY - 70 * scale },
            'OBJECTIVE': { x: centerX - 110 * scale, y: centerY },
            'TEAMFIGHT': { x: centerX + 110 * scale, y: centerY },
            'SCALING': { x: centerX, y: centerY + 95 * scale },
            'PICK_OFF': { x: centerX - 190 * scale, y: centerY + 95 * scale },
            'POKE': { x: centerX + 190 * scale, y: centerY + 95 * scale }
        };
        
        this.nodes.forEach(node => {
            if (positions[node.id]) {
                node.x = positions[node.id].x;
                node.y = positions[node.id].y;
            }
        });
    }
    
    setupControls() {
        const chips = document.querySelectorAll('.lynchpin-chip');
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                this.deniedLynchpin = chip.getAttribute('data-lynchpin');
                this.updateImpactMetrics();
                this.render();
            });
        });
    }
    
    setupMouseEvents() {
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.handleMouseLeave());
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        let newHovered = null;
        
        for (const node of this.nodes) {
            const size = 50;
            const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
            if (distance <= size) {
                newHovered = node;
                break;
            }
        }
        
        if (newHovered !== this.hoveredNode) {
            this.hoveredNode = newHovered;
            this.updateTooltip(e.clientX, e.clientY);
            this.render();
        }
    }
    
    handleMouseLeave() {
        this.hoveredNode = null;
        this.hideTooltip();
        this.render();
    }
    
    updateTooltip(clientX, clientY) {
        const tooltip = document.getElementById('stressTooltip');
        if (!tooltip) return;
        
        if (!this.hoveredNode) {
            this.hideTooltip();
            return;
        }
        
        const node = this.hoveredNode;
        const isCollapsed = this.isNodeCollapsed(node.id);
        
        if (isCollapsed) {
            tooltip.querySelector('.tooltip-content').innerHTML = 
                `<strong>${node.name}</strong><br>This strategy becomes unreachable without <strong>${this.getDeniedNodeName()}</strong>.`;
        } else if (node.id === this.deniedLynchpin) {
            tooltip.querySelector('.tooltip-content').innerHTML = 
                `<strong>${node.name}</strong><br>This strategy has been <strong>denied</strong>.`;
        } else {
            tooltip.querySelector('.tooltip-content').innerHTML = 
                `<strong>${node.name}</strong><br>This strategy survives but with reduced effectiveness.`;
        }
        
        tooltip.style.left = (clientX + 15) + 'px';
        tooltip.style.top = (clientY - 10) + 'px';
        tooltip.classList.add('active');
    }
    
    hideTooltip() {
        const tooltip = document.getElementById('stressTooltip');
        if (tooltip) tooltip.classList.remove('active');
    }
    
    getDeniedNodeName() {
        const node = this.nodes.find(n => n.id === this.deniedLynchpin);
        return node ? node.name.replace('\n', ' ') : '';
    }
    
    isNodeCollapsed(nodeId) {
        // Check if node depends on denied lynchpin
        const hasPathFromLynchpin = this.edges.some(e => 
            e.from === this.deniedLynchpin && e.to === nodeId
        );
        return hasPathFromLynchpin;
    }
    
    isEdgeCollapsed(edge) {
        return edge.from === this.deniedLynchpin || edge.to === this.deniedLynchpin;
    }
    
    updateImpactMetrics() {
        // Update metrics based on denied lynchpin
        const metrics = {
            'OBJECTIVE': { drop: 12, paths: 4, phases: ['critical', 'critical', 'moderate'] },
            'TEAMFIGHT': { drop: 15, paths: 5, phases: ['moderate', 'critical', 'critical'] },
            'SCALING': { drop: 8, paths: 3, phases: ['minimal', 'moderate', 'critical'] }
        };
        
        const metric = metrics[this.deniedLynchpin] || metrics['OBJECTIVE'];
        
        document.querySelector('.meter-fill').style.width = metric.drop + '%';
        document.querySelector('.metric-value').textContent = '−' + metric.drop + '%';
        document.querySelector('.count-number').textContent = metric.paths;
        
        const badges = document.querySelectorAll('.phase-badge');
        badges.forEach((badge, i) => {
            badge.className = 'phase-badge ' + metric.phases[i];
        });
    }
    
    render() {
        // Clear
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, 'rgba(1, 10, 19, 0.95)');
        gradient.addColorStop(1, 'rgba(10, 21, 32, 0.8)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw edges
        this.edges.forEach(edge => {
            const fromNode = this.nodes.find(n => n.id === edge.from);
            const toNode = this.nodes.find(n => n.id === edge.to);
            if (!fromNode || !toNode) return;
            
            const isCollapsed = this.isEdgeCollapsed(edge);
            
            const dx = toNode.x - fromNode.x;
            const dy = toNode.y - fromNode.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const unitX = dx / distance;
            const unitY = dy / distance;
            
            const padding = 55;
            const startX = fromNode.x + unitX * padding;
            const startY = fromNode.y + unitY * padding;
            const endX = toNode.x - unitX * padding;
            const endY = toNode.y - unitY * padding;
            
            // Draw line
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            this.ctx.lineTo(endX, endY);
            this.ctx.strokeStyle = isCollapsed ? 'rgba(155, 111, 232, 0.2)' : 'rgba(10, 200, 185, 0.4)';
            this.ctx.lineWidth = isCollapsed ? 1 : 3;
            this.ctx.setLineDash(isCollapsed ? [5, 5] : []);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            
            // Draw arrow
            if (!isCollapsed) {
                const angle = Math.atan2(endY - startY, endX - startX);
                const arrowSize = 12;
                
                this.ctx.beginPath();
                this.ctx.moveTo(endX, endY);
                this.ctx.lineTo(
                    endX - arrowSize * Math.cos(angle - Math.PI / 7),
                    endY - arrowSize * Math.sin(angle - Math.PI / 7)
                );
                this.ctx.lineTo(
                    endX - arrowSize * Math.cos(angle + Math.PI / 7),
                    endY - arrowSize * Math.sin(angle + Math.PI / 7)
                );
                this.ctx.closePath();
                this.ctx.fillStyle = 'rgba(10, 200, 185, 0.4)';
                this.ctx.fill();
            }
        });
        
        // Draw nodes
        this.nodes.forEach(node => {
            const size = 50;
            const isDenied = node.id === this.deniedLynchpin;
            const isCollapsed = this.isNodeCollapsed(node.id);
            const isHovered = this.hoveredNode === node;
            
            // Node background
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
            this.ctx.fillStyle = 'rgba(1, 10, 19, 0.95)';
            this.ctx.fill();
            
            // Node border
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
            if (isDenied) {
                this.ctx.strokeStyle = '#FF4655';
                this.ctx.lineWidth = 3;
                this.ctx.setLineDash([8, 4]);
            } else if (isCollapsed) {
                this.ctx.strokeStyle = 'rgba(155, 111, 232, 0.4)';
                this.ctx.lineWidth = 2;
            } else {
                this.ctx.strokeStyle = isHovered ? '#0AC8B9' : 'rgba(10, 200, 185, 0.6)';
                this.ctx.lineWidth = isHovered ? 4 : 3;
            }
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            
            // Strike-through for denied
            if (isDenied) {
                this.ctx.beginPath();
                this.ctx.moveTo(node.x - size, node.y);
                this.ctx.lineTo(node.x + size, node.y);
                this.ctx.strokeStyle = '#FF4655';
                this.ctx.lineWidth = 3;
                this.ctx.stroke();
            }
            
            // Node label
            this.ctx.fillStyle = isDenied ? 'rgba(255, 70, 85, 0.6)' : (isCollapsed ? 'rgba(255, 255, 255, 0.4)' : '#FFFFFF');
            this.ctx.font = 'bold 13px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            
            const lines = node.name.split('\n');
            const lineHeight = 16;
            const startY = node.y - ((lines.length - 1) * lineHeight) / 2;
            
            lines.forEach((line, i) => {
                this.ctx.fillText(line, node.x, startY + i * lineHeight);
            });
        });
    }
}

// Initialize stress test graph
document.addEventListener('DOMContentLoaded', () => {
    window.stressTestGraph = new StressTestGraph('stressTestGraph');
});


// ===== PHASE PROFILE TOOLTIPS =====

document.addEventListener('DOMContentLoaded', () => {
    // Handle objective marker tooltips
    const markers = document.querySelectorAll('.marker, .fight-marker');
    
    markers.forEach(marker => {
        marker.addEventListener('mouseenter', (e) => {
            const tooltip = marker.getAttribute('data-tooltip');
            if (!tooltip) return;
            
            // Create tooltip element
            const tooltipEl = document.createElement('div');
            tooltipEl.className = 'phase-marker-tooltip';
            tooltipEl.textContent = tooltip;
            tooltipEl.style.position = 'fixed';
            tooltipEl.style.background = 'rgba(1, 10, 19, 0.98)';
            tooltipEl.style.border = '2px solid #C89B3C';
            tooltipEl.style.borderRadius = '6px';
            tooltipEl.style.padding = '8px 12px';
            tooltipEl.style.fontSize = '12px';
            tooltipEl.style.color = '#F0F6F6';
            tooltipEl.style.zIndex = '10000';
            tooltipEl.style.pointerEvents = 'none';
            tooltipEl.style.whiteSpace = 'nowrap';
            
            const rect = marker.getBoundingClientRect();
            tooltipEl.style.left = (rect.left + rect.width / 2) + 'px';
            tooltipEl.style.top = (rect.top - 35) + 'px';
            tooltipEl.style.transform = 'translateX(-50%)';
            
            marker._tooltip = tooltipEl;
            document.body.appendChild(tooltipEl);
        });
        
        marker.addEventListener('mouseleave', () => {
            if (marker._tooltip) {
                document.body.removeChild(marker._tooltip);
                marker._tooltip = null;
            }
        });
    });
});


// ===== MONTE CARLO MATCH OUTCOME SIMULATOR =====

class MonteCarloSimulator {
    constructor() {
        this.canvas = document.getElementById('outcomeDistribution');
        if (!this.canvas) {
            console.error('Monte Carlo canvas not found');
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.numSimulations = 10000;
        this.isRunning = false;
        this.results = null;
        
        // Scenario modifiers
        this.denyLynchpin = false;
        this.forceEarly = false;
        this.delayScaling = false;
        
        this.setupControls();
        this.drawInitialChart();
    }
    
    setupControls() {
        // Preset buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.numSimulations = parseInt(btn.getAttribute('data-sims'));
            });
        });
        
        // Scenario toggles
        document.getElementById('deny-lynchpin')?.addEventListener('change', (e) => {
            this.denyLynchpin = e.target.checked;
        });
        
        document.getElementById('force-early')?.addEventListener('change', (e) => {
            this.forceEarly = e.target.checked;
        });
        
        document.getElementById('delay-scaling')?.addEventListener('change', (e) => {
            this.delayScaling = e.target.checked;
        });
        
        // Run button
        document.getElementById('runMonteCarlo')?.addEventListener('click', () => {
            if (!this.isRunning) {
                this.runSimulation();
            }
        });
    }
    
    async runSimulation() {
        this.isRunning = true;
        const btn = document.getElementById('runMonteCarlo');
        const statusText = document.querySelector('.status-text');
        const progressFill = document.querySelector('.progress-fill');
        
        if (btn) {
            btn.classList.add('running');
            btn.querySelector('.btn-text').textContent = 'Simulating...';
        }
        
        // Simulate in chunks to allow UI updates
        const chunkSize = 1000;
        const numChunks = Math.ceil(this.numSimulations / chunkSize);
        let wins = 0;
        let totalDuration = 0;
        const durations = [];
        
        // Strategy attribution tracking
        const winReasons = {
            'Objective Control dominance': 0,
            'Teamfight superiority': 0,
            'Scaling execution': 0
        };
        
        const lossReasons = {
            'Failed early tempo': 0,
            'Scaling denied': 0,
            'Lynchpin collapsed': 0
        };
        
        for (let chunk = 0; chunk < numChunks; chunk++) {
            const currentChunkSize = Math.min(chunkSize, this.numSimulations - chunk * chunkSize);
            
            for (let i = 0; i < currentChunkSize; i++) {
                const result = this.simulateMatch();
                if (result.won) {
                    wins++;
                    // Attribute win reason
                    const reasons = Object.keys(winReasons);
                    const reason = reasons[Math.floor(Math.random() * reasons.length)];
                    winReasons[reason]++;
                } else {
                    // Attribute loss reason
                    const reasons = Object.keys(lossReasons);
                    const reason = reasons[Math.floor(Math.random() * reasons.length)];
                    lossReasons[reason]++;
                }
                totalDuration += result.duration;
                durations.push(result.duration);
            }
            
            // Update progress
            const progress = ((chunk + 1) / numChunks) * 100;
            if (progressFill) progressFill.style.width = progress + '%';
            if (statusText) statusText.textContent = `Simulating... ${Math.round(progress)}%`;
            
            // Allow UI to update
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // Calculate results
        const winRate = wins / this.numSimulations;
        const avgDuration = totalDuration / this.numSimulations;
        
        // Calculate volatility (standard deviation of durations)
        const variance = durations.reduce((sum, d) => sum + Math.pow(d - avgDuration, 2), 0) / durations.length;
        const stdDev = Math.sqrt(variance);
        const volatility = stdDev > 8 ? 'High after 25 min' : (stdDev > 5 ? 'Moderate' : 'Low');
        
        this.results = {
            winRate,
            avgDuration,
            volatility,
            durations,
            winReasons,
            lossReasons
        };
        
        // Update UI
        this.updateMetrics();
        this.updateAttribution();
        this.drawChart();
        
        // Reset button
        if (btn) {
            btn.classList.remove('running');
            btn.querySelector('.btn-text').textContent = 'Run Simulation';
        }
        if (statusText) statusText.textContent = 'Simulation complete';
        if (progressFill) progressFill.style.width = '100%';
        
        this.isRunning = false;
    }
    
    simulateMatch() {
        // Base win probability from strategy transition graph
        let baseWinProb = 0.58;
        
        // Apply scenario modifiers
        if (this.denyLynchpin) {
            baseWinProb -= 0.12; // Lynchpin denial impact
        }
        
        if (this.forceEarly) {
            baseWinProb += 0.08; // Early tempo advantage
        }
        
        if (this.delayScaling) {
            baseWinProb -= 0.06; // Scaling delay disadvantage
        }
        
        // Add randomness
        const randomFactor = (Math.random() - 0.5) * 0.2;
        const finalWinProb = Math.max(0.1, Math.min(0.9, baseWinProb + randomFactor));
        
        // Determine outcome
        const won = Math.random() < finalWinProb;
        
        // Generate duration (normal distribution around 33 minutes)
        const baseDuration = 33;
        const durationVariance = 8;
        const duration = Math.max(20, Math.min(50, 
            baseDuration + (Math.random() - 0.5) * 2 * durationVariance
        ));
        
        return { won, duration };
    }
    
    updateMetrics() {
        if (!this.results) return;
        
        document.querySelector('.metric-value.win-rate').textContent = 
            Math.round(this.results.winRate * 100) + '%';
        
        document.querySelector('.metric-value.duration').textContent = 
            this.results.avgDuration.toFixed(1) + ' min';
        
        document.querySelector('.metric-value.volatility').textContent = 
            this.results.volatility;
    }
    
    updateAttribution() {
        if (!this.results) return;
        
        // Update win attribution
        const totalWins = Object.values(this.results.winReasons).reduce((a, b) => a + b, 0);
        const winItems = document.querySelectorAll('.attribution-section.wins .attribution-item');
        
        Object.entries(this.results.winReasons).forEach(([reason, count], index) => {
            if (winItems[index]) {
                const percentage = totalWins > 0 ? (count / totalWins) * 100 : 0;
                winItems[index].querySelector('.item-label').textContent = reason;
                winItems[index].querySelector('.bar-fill').style.width = percentage + '%';
                winItems[index].querySelector('.bar-value').textContent = Math.round(percentage) + '%';
            }
        });
        
        // Update loss attribution
        const totalLosses = Object.values(this.results.lossReasons).reduce((a, b) => a + b, 0);
        const lossItems = document.querySelectorAll('.attribution-section.losses .attribution-item');
        
        Object.entries(this.results.lossReasons).forEach(([reason, count], index) => {
            if (lossItems[index]) {
                const percentage = totalLosses > 0 ? (count / totalLosses) * 100 : 0;
                lossItems[index].querySelector('.item-label').textContent = reason;
                lossItems[index].querySelector('.bar-fill').style.width = percentage + '%';
                lossItems[index].querySelector('.bar-value').textContent = Math.round(percentage) + '%';
            }
        });
    }
    
    drawInitialChart() {
        // Draw placeholder chart
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, 'rgba(1, 10, 19, 0.95)');
        gradient.addColorStop(1, 'rgba(10, 21, 32, 0.8)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw placeholder text
        this.ctx.fillStyle = '#AAB3B8';
        this.ctx.font = '14px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('Run simulation to see outcome distribution', 
            this.canvas.width / 2, this.canvas.height / 2);
    }
    
    drawChart() {
        if (!this.results) return;
        
        // Clear canvas
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, 'rgba(1, 10, 19, 0.95)');
        gradient.addColorStop(1, 'rgba(10, 21, 32, 0.8)');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Create histogram of durations
        const bins = 15;
        const minDuration = 20;
        const maxDuration = 50;
        const binWidth = (maxDuration - minDuration) / bins;
        const histogram = new Array(bins).fill(0);
        
        this.results.durations.forEach(duration => {
            const binIndex = Math.min(bins - 1, Math.floor((duration - minDuration) / binWidth));
            histogram[binIndex]++;
        });
        
        // Find max count for scaling
        const maxCount = Math.max(...histogram);
        
        // Draw histogram
        const padding = 40;
        const chartWidth = this.canvas.width - 2 * padding;
        const chartHeight = this.canvas.height - 2 * padding;
        const barWidth = chartWidth / bins;
        
        histogram.forEach((count, i) => {
            const barHeight = (count / maxCount) * chartHeight;
            const x = padding + i * barWidth;
            const y = this.canvas.height - padding - barHeight;
            
            // Gradient for bars
            const barGradient = this.ctx.createLinearGradient(x, y, x, y + barHeight);
            barGradient.addColorStop(0, '#0AC8B9');
            barGradient.addColorStop(1, '#9B6FE8');
            
            this.ctx.fillStyle = barGradient;
            this.ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
            
            // Bar outline
            this.ctx.strokeStyle = 'rgba(10, 200, 185, 0.5)';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(x + 2, y, barWidth - 4, barHeight);
        });
        
        // Draw win rate line
        const winRateX = padding + (this.results.avgDuration - minDuration) / (maxDuration - minDuration) * chartWidth;
        this.ctx.beginPath();
        this.ctx.moveTo(winRateX, padding);
        this.ctx.lineTo(winRateX, this.canvas.height - padding);
        this.ctx.strokeStyle = '#C89B3C';
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([5, 5]);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Draw axes
        this.ctx.strokeStyle = 'rgba(170, 179, 184, 0.3)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(padding, padding);
        this.ctx.lineTo(padding, this.canvas.height - padding);
        this.ctx.lineTo(this.canvas.width - padding, this.canvas.height - padding);
        this.ctx.stroke();
        
        // Draw labels
        this.ctx.fillStyle = '#AAB3B8';
        this.ctx.font = '11px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        
        // X-axis labels (duration)
        for (let i = 0; i <= 3; i++) {
            const duration = minDuration + (maxDuration - minDuration) * (i / 3);
            const x = padding + (chartWidth * i / 3);
            this.ctx.fillText(Math.round(duration) + ' min', x, this.canvas.height - padding + 10);
        }
        
        // Y-axis label
        this.ctx.save();
        this.ctx.translate(padding - 25, this.canvas.height / 2);
        this.ctx.rotate(-Math.PI / 2);
        this.ctx.textAlign = 'center';
        this.ctx.fillText('Frequency', 0, 0);
        this.ctx.restore();
        
        // Title
        this.ctx.fillStyle = '#F0F6F6';
        this.ctx.font = 'bold 13px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'bottom';
        this.ctx.fillText('Match Duration Distribution', this.canvas.width / 2, padding - 10);
        
        // Legend for average line
        this.ctx.fillStyle = '#C89B3C';
        this.ctx.font = '11px sans-serif';
        this.ctx.textAlign = 'left';
        this.ctx.fillText('Avg: ' + this.results.avgDuration.toFixed(1) + ' min', 
            winRateX + 5, padding + 15);
    }
}

// Initialize Monte Carlo simulator
document.addEventListener('DOMContentLoaded', () => {
    window.monteCarloSimulator = new MonteCarloSimulator();
});


// ===== POST-MONTE CARLO PANELS DATA & LOGIC =====

// Mock data for all panels (would come from backend in production)
const ANALYSIS_DATA = {
    robustness: {
        baseWinRate: 0.58,
        winRateMin: 0.51,
        winRateMax: 0.64,
        volatilityLabel: "MED",
        topFailureCauses: [
            { label: "Lost early river control", share: 0.27 },
            { label: "Failed objective setup", share: 0.19 },
            { label: "Late game scaling denied", share: 0.15 }
        ]
    },
    
    redundancy: {
        redundancyScore: 1,
        primaryWinPath: {
            steps: ["RIVER_CONTROL", "OBJECTIVE_STACKING", "TEAMFIGHT_COMMIT"],
            probability: 0.21,
            label: "WIN_HEAVY"
        },
        backupPaths: [
            {
                steps: ["BOT_PRESSURE", "SCALING_INSURANCE"],
                probability: 0.14,
                label: "MIXED"
            }
        ]
    },
    
    predictability: {
        predictabilityLabel: "READABLE",
        entropyScore: 0.21,
        mostRepeatedPath: {
            steps: ["OBJECTIVE_CONTROL", "TEAMFIGHT", "SCALING"],
            share: 0.72
        },
        flags: [
            "Single dominant mid pivot",
            "Few alternative late-game transitions",
            "Predictable objective timing"
        ]
    },
    
    denialStack: {
        items: [
            {
                strategy: "OBJECTIVE_CONTROL",
                expectedWinDrop: 0.12,
                phaseImpact: "MID",
                risk: "LOW",
                oneLineWhy: "Collapses entire mid-game strategy",
                details: {
                    whatCollapses: [
                        "Dragon control becomes unreliable",
                        "Vision setup around objectives fails",
                        "Teamfight positioning deteriorates"
                    ],
                    howToExecute: [
                        "Ban jungle champions with objective control",
                        "Contest early vision aggressively",
                        "Force fights away from objectives"
                    ],
                    whatToAvoid: [
                        "Don't let them get free dragon setups",
                        "Avoid 5v5 near Baron pit"
                    ]
                }
            },
            {
                strategy: "FRONTLINE_TEAMFIGHT",
                expectedWinDrop: 0.15,
                phaseImpact: "LATE",
                risk: "MED",
                oneLineWhy: "Removes primary win condition",
                details: {
                    whatCollapses: [
                        "Cannot engage 5v5 fights",
                        "Backline becomes exposed",
                        "Objective contests become impossible"
                    ],
                    howToExecute: [
                        "Ban engage champions (Malphite, Ornn)",
                        "Pick poke/disengage compositions",
                        "Kite backwards in fights"
                    ],
                    whatToAvoid: [
                        "Don't group tightly",
                        "Avoid narrow jungle paths"
                    ]
                }
            },
            {
                strategy: "SCALING_INSURANCE",
                expectedWinDrop: 0.08,
                phaseImpact: "LATE",
                risk: "HIGH",
                oneLineWhy: "Forces early fights they can't win",
                details: {
                    whatCollapses: [
                        "Late game power spikes never reached",
                        "Forced into unfavorable early fights",
                        "Gold deficit becomes insurmountable"
                    ],
                    howToExecute: [
                        "Ban scaling carries (Jinx, Aphelios)",
                        "Force early tempo with aggressive junglers",
                        "End game before 30 minutes"
                    ],
                    whatToAvoid: [
                        "Don't let game go past 35 minutes",
                        "Avoid giving free farm"
                    ]
                }
            }
        ]
    },
    
    coachSummary: {
        identityPrimary: "Vision-based objective control with scaling teamfight compositions",
        identityFallback: "Mid-jungle roam pressure into late game insurance",
        mustDeny: [
            {
                strategy: "Objective Control",
                why: "Removes T1's primary win condition and vision dominance",
                expectedWinDrop: 0.15,
                phase: "MID"
            },
            {
                strategy: "Frontline Teamfight",
                why: "Collapses late-game teamfight execution and objective contests",
                expectedWinDrop: 0.12,
                phase: "LATE"
            }
        ],
        timing: {
            pressureWindow: "8–15 min",
            avoidWindow: ">25 min"
        },
        mapPlan: {
            early: ["Contest vision around first dragon", "Pressure Oner's jungle pathing"],
            mid: ["Deny vision setups before objectives", "Force fights away from Baron pit"],
            late: ["Avoid 5v5 teamfights", "Split map pressure", "Catch isolated targets"]
        },
        warnings: [
            "T1 becomes extremely strong with vision control after 20 minutes",
            "Do not give free objective setups with vision advantage",
            "Avoid extended teamfights in open areas where T1 can position"
        ],
        confidence: "HIGH",
        simCount: 10000
    }
};

// ===== ROBUSTNESS & VARIANCE PANEL =====

function initRobustnessPanel() {
    const data = ANALYSIS_DATA.robustness;
    
    // Update metrics
    document.getElementById('expectedWinRate').textContent = Math.round(data.baseWinRate * 100) + '%';
    document.getElementById('winRateRange').textContent = 
        Math.round(data.winRateMin * 100) + '% → ' + Math.round(data.winRateMax * 100) + '%';
    document.getElementById('volatilityLabel').textContent = data.volatilityLabel;
    
    // Update volatility chip color
    const volatilityChip = document.getElementById('volatilityChip');
    if (data.volatilityLabel === 'LOW') {
        volatilityChip.classList.add('good');
    } else if (data.volatilityLabel === 'HIGH') {
        volatilityChip.classList.add('bad');
    } else {
        volatilityChip.classList.add('warn');
    }
    
    // Update band chart
    document.getElementById('bandMin').textContent = Math.round(data.winRateMin * 100) + '%';
    document.getElementById('bandMax').textContent = Math.round(data.winRateMax * 100) + '%';
    
    const markerPosition = ((data.baseWinRate - data.winRateMin) / (data.winRateMax - data.winRateMin)) * 100;
    document.getElementById('bandMarker').style.left = markerPosition + '%';
    
    // Update failure causes
    const causesContainer = document.getElementById('failureCauses');
    causesContainer.innerHTML = '';
    
    data.topFailureCauses.forEach(cause => {
        const item = document.createElement('div');
        item.className = 'cause-item';
        item.innerHTML = `
            <span class="cause-label">${cause.label}</span>
            <div class="cause-bar">
                <div class="cause-fill" style="width: ${cause.share * 100}%;"></div>
            </div>
            <span class="cause-share">${Math.round(cause.share * 100)}%</span>
        `;
        causesContainer.appendChild(item);
    });
}

// ===== REDUNDANCY & BACKUP PATHS PANEL =====

function initRedundancyPanel() {
    const data = ANALYSIS_DATA.redundancy;
    
    // Update score
    document.getElementById('redundancyScore').textContent = data.redundancyScore;
    
    const interpretations = {
        0: "One-dimensional",
        1: "Limited backup",
        2: "Adaptable",
        3: "Highly flexible"
    };
    document.getElementById('redundancyInterpretation').textContent = interpretations[data.redundancyScore];
    
    // Render primary path
    const primaryPath = document.getElementById('primaryPath');
    primaryPath.innerHTML = '';
    
    data.primaryWinPath.steps.forEach((step, index) => {
        const stepEl = document.createElement('span');
        stepEl.className = 'path-step';
        stepEl.textContent = step.replace(/_/g, ' ');
        primaryPath.appendChild(stepEl);
        
        if (index < data.primaryWinPath.steps.length - 1) {
            const arrow = document.createElement('span');
            arrow.className = 'path-arrow';
            arrow.textContent = '→';
            primaryPath.appendChild(arrow);
        }
    });
    
    document.getElementById('primaryProbability').textContent = Math.round(data.primaryWinPath.probability * 100) + '%';
    
    const primaryTag = document.getElementById('primaryTag');
    primaryTag.textContent = data.primaryWinPath.label.replace(/_/g, '-');
    primaryTag.className = 'path-tag ' + data.primaryWinPath.label.toLowerCase().replace(/_/g, '-');
    
    // Render backup paths
    const backupContainer = document.getElementById('backupPaths');
    backupContainer.innerHTML = '';
    
    if (data.backupPaths.length === 0) {
        backupContainer.innerHTML = '<div class="empty-backup">No reliable backup paths detected.</div>';
    } else {
        data.backupPaths.forEach((path, index) => {
            const card = document.createElement('div');
            card.className = 'backup-path-card';
            
            const pathHtml = path.steps.map(step => 
                `<span class="path-step">${step.replace(/_/g, ' ')}</span>`
            ).join('<span class="path-arrow">→</span>');
            
            card.innerHTML = `
                <h5>Backup Path ${String.fromCharCode(65 + index)}</h5>
                <div class="path-renderer">${pathHtml}</div>
                <div class="path-meta">
                    <span class="path-probability">${Math.round(path.probability * 100)}%</span>
                    <span class="path-tag ${path.label.toLowerCase().replace(/_/g, '-')}">${path.label.replace(/_/g, '-')}</span>
                </div>
            `;
            
            backupContainer.appendChild(card);
        });
    }
}

// ===== PREDICTABILITY INDEX PANEL =====

function initPredictabilityPanel() {
    const data = ANALYSIS_DATA.predictability;
    
    // Update gauge
    document.querySelectorAll('.gauge-segment').forEach(seg => seg.classList.remove('active'));
    const activeSegment = document.querySelector('.gauge-segment.' + data.predictabilityLabel.toLowerCase());
    if (activeSegment) activeSegment.classList.add('active');
    
    document.getElementById('entropyScore').textContent = data.entropyScore.toFixed(2);
    
    // Render most repeated path
    const repeatedPath = document.getElementById('repeatedPath');
    repeatedPath.innerHTML = '';
    
    data.mostRepeatedPath.steps.forEach((step, index) => {
        const stepEl = document.createElement('span');
        stepEl.className = 'path-step';
        stepEl.textContent = step.replace(/_/g, ' ');
        repeatedPath.appendChild(stepEl);
        
        if (index < data.mostRepeatedPath.steps.length - 1) {
            const arrow = document.createElement('span');
            arrow.className = 'path-arrow';
            arrow.textContent = '→';
            repeatedPath.appendChild(arrow);
        }
    });
    
    document.getElementById('repeatedShareFill').style.width = (data.mostRepeatedPath.share * 100) + '%';
    document.getElementById('repeatedShareValue').textContent = Math.round(data.mostRepeatedPath.share * 100) + '%';
    
    // Render flags
    const flagsList = document.getElementById('predictabilityFlags');
    flagsList.innerHTML = '';
    
    data.flags.forEach(flag => {
        const li = document.createElement('li');
        li.textContent = flag;
        flagsList.appendChild(li);
    });
}

// ===== DENIAL PRIORITY STACK PANEL =====

function initDenialPanel() {
    const data = ANALYSIS_DATA.denialStack;
    
    const listContainer = document.getElementById('denialRankList');
    listContainer.innerHTML = '';
    
    data.items.forEach((item, index) => {
        const denialItem = document.createElement('div');
        denialItem.className = 'denial-item';
        denialItem.dataset.index = index;
        
        const riskClass = item.risk.toLowerCase();
        
        denialItem.innerHTML = `
            <div class="denial-rank">${index + 1}</div>
            <div class="denial-info">
                <div class="denial-strategy">${item.strategy.replace(/_/g, ' ')}</div>
                <div class="denial-chips">
                    <span class="denial-chip win-drop">−${Math.round(item.expectedWinDrop * 100)}%</span>
                    <span class="denial-chip phase">${item.phaseImpact}</span>
                    <span class="denial-chip risk ${riskClass}">${item.risk} RISK</span>
                </div>
                <div class="denial-why">${item.oneLineWhy}</div>
            </div>
        `;
        
        denialItem.addEventListener('click', () => openDenialDrawer(item));
        
        listContainer.appendChild(denialItem);
    });
}

function openDenialDrawer(item) {
    const drawer = document.getElementById('denialDrawer');
    const title = document.getElementById('drawerTitle');
    const content = document.getElementById('drawerContent');
    
    title.textContent = item.strategy.replace(/_/g, ' ') + ' - Denial Strategy';
    
    content.innerHTML = `
        <div class="drawer-section">
            <h4>What Collapses</h4>
            <ul>
                ${item.details.whatCollapses.map(point => `<li>${point}</li>`).join('')}
            </ul>
        </div>
        <div class="drawer-section">
            <h4>How to Execute</h4>
            <ul>
                ${item.details.howToExecute.map(point => `<li>${point}</li>`).join('')}
            </ul>
        </div>
        <div class="drawer-section">
            <h4>What to Avoid</h4>
            <ul>
                ${item.details.whatToAvoid.map(point => `<li>${point}</li>`).join('')}
            </ul>
        </div>
    `;
    
    drawer.classList.add('active');
}

document.getElementById('closeDrawer')?.addEventListener('click', () => {
    document.getElementById('denialDrawer').classList.remove('active');
});

// ===== COACH SUMMARY MODAL =====

function initCoachSummary() {
    const data = ANALYSIS_DATA.coachSummary;
    
    // Update identity
    document.getElementById('identityPrimary').textContent = 'Primary identity: ' + data.identityPrimary;
    document.getElementById('identityFallback').textContent = 'Fallback identity: ' + data.identityFallback;
    
    // Update must deny
    const mustDenyContainer = document.getElementById('mustDenyItems');
    mustDenyContainer.innerHTML = '';
    
    data.mustDeny.forEach(item => {
        const denialItem = document.createElement('div');
        denialItem.className = 'deny-item-modal';
        denialItem.innerHTML = `
            <h4>${item.strategy}</h4>
            <p>${item.why}</p>
            <div class="denial-chips">
                <span class="denial-chip win-drop">−${Math.round(item.expectedWinDrop * 100)}%</span>
                <span class="denial-chip phase">${item.phase}</span>
            </div>
        `;
        mustDenyContainer.appendChild(denialItem);
    });
    
    // Update timing
    document.getElementById('pressureWindow').textContent = data.timing.pressureWindow;
    document.getElementById('avoidWindow').textContent = data.timing.avoidWindow;
    
    // Update map plan
    const mapEarly = document.getElementById('mapEarly');
    const mapMid = document.getElementById('mapMid');
    const mapLate = document.getElementById('mapLate');
    
    mapEarly.innerHTML = data.mapPlan.early.map(item => `<li>${item}</li>`).join('');
    mapMid.innerHTML = data.mapPlan.mid.map(item => `<li>${item}</li>`).join('');
    mapLate.innerHTML = data.mapPlan.late.map(item => `<li>${item}</li>`).join('');
    
    // Update warnings
    const warningsList = document.getElementById('warningsList');
    warningsList.innerHTML = data.warnings.map(warning => `<li>${warning}</li>`).join('');
    
    // Update footer
    document.getElementById('confidenceValue').textContent = data.confidence;
    document.getElementById('simCountValue').textContent = data.simCount.toLocaleString();
}

// Modal controls
document.getElementById('coachSummaryBtn')?.addEventListener('click', () => {
    document.getElementById('coachModal').classList.add('active');
});

document.getElementById('closeCoachModal')?.addEventListener('click', () => {
    document.getElementById('coachModal').classList.remove('active');
});

// Close modal on overlay click
document.getElementById('coachModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'coachModal') {
        document.getElementById('coachModal').classList.remove('active');
    }
});

// ===== INITIALIZE ALL PANELS =====

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all post-Monte Carlo panels
    initRobustnessPanel();
    initRedundancyPanel();
    initPredictabilityPanel();
    initDenialPanel();
    initCoachSummary();
});
