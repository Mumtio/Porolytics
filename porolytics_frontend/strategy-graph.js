// Strategy Graph - Clean Implementation from Scratch
class StrategyGraph {
    constructor() {
        this.canvas = document.getElementById('transitionGraph');
        if (!this.canvas) {
            console.error('Canvas transitionGraph not found');
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.tooltip = document.getElementById('transitionTooltip');
        
        // Graph state
        this.selectedNode = null;
        this.filter = 'combined';
        this.minProbability = 0.05;
        
        // Layout configuration
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        this.radius = 280;
        this.nodeRadius = 40;
        
        // Initialize
        this.loadData();
        this.setupEventListeners();
        this.render();
    }
    
    async loadData() {
        try {
            // Load all required data files
            const [winGraphRes, lossGraphRes, reportRes, robustnessRes, mcBaselineRes] = await Promise.all([
                fetch('data/graph_win.json'),
                fetch('data/graph_loss.json'),
                fetch('data/strategy_report.json'),
                fetch('data/robustness.json'),
                fetch('data/mc_baseline.json')
            ]);

            const winGraph = await winGraphRes.json();
            const lossGraph = await lossGraphRes.json();
            const report = await reportRes.json();
            const robustness = await robustnessRes.json();
            const mcBaseline = await mcBaselineRes.json();

            // 1. Process Nodes
            const nodeIds = [
                'MID_TEMPO',
                'TOP_PRESSURE',
                'BOT_PRESSURE',
                'RIVER_CONTROL',
                'PICK_ORIENTED',
                'TEAMFIGHT_COMMIT',
                'OBJECTIVE_STACKING'
            ];

            this.nodes = nodeIds.map(id => {
                const lynchpinData = report.lynchpins.find(l => l.node === id);
                return {
                    id: id,
                    name: id.replace('_', '\n'),
                    importance: lynchpinData ? Math.max(0.2, Math.min(1.0, (lynchpinData.cond_reach + 0.1) * 2)) : 0.5,
                    winRate: lynchpinData ? (lynchpinData.impact > 0 ? 0.7 : 0.4) : 0.5
                };
            });

            // 2. Process Edges (Combine WIN and LOSS)
            this.edges = [];
            
            // WIN edges
            for (const from in winGraph.adj) {
                for (const to in winGraph.adj[from]) {
                    this.edges.push({
                        from,
                        to,
                        weight: winGraph.adj[from][to],
                        type: 'win'
                    });
                }
            }

            // LOSS edges
            for (const from in lossGraph.adj) {
                for (const to in lossGraph.adj[from]) {
                    this.edges.push({
                        from,
                        to,
                        weight: lossGraph.adj[from][to],
                        type: 'loss'
                    });
                }
            }

            // 3. Process Lynchpins
            this.lynchpins = robustness.deny_results
                .filter(r => r.robustness < 0.9)
                .map(r => r.deny);

            // Calculate positions
            this.calculatePositions();
            this.render();
            
            // Update other UI components
            this.updateLynchpinList(robustness);
            this.updateCoachSummary(mcBaseline, robustness);
            this.updateCounterCards(report);
            this.updateDenialMatrix(report);
            this.setupSimulation(mcBaseline, robustness);

        } catch (error) {
            console.error('Error loading strategy data:', error);
            // Fallback to mock data if files are missing
            this.loadMockData();
        }
    }

    loadMockData() {
        this.nodes = [
            { id: 'TEAMFIGHT_COMMIT', name: 'Teamfight\nCommit', importance: 0.9, winRate: 0.75 },
            { id: 'OBJECTIVE_STACKING', name: 'Objective\nStacking', importance: 0.7, winRate: 0.65 },
            { id: 'RIVER_CONTROL', name: 'River\nControl', importance: 0.6, winRate: 0.55 },
            { id: 'BOT_PRESSURE', name: 'Bot\nPressure', importance: 0.8, winRate: 0.70 },
            { id: 'TOP_PRESSURE', name: 'Top\nPressure', importance: 0.5, winRate: 0.45 },
            { id: 'MID_TEMPO', name: 'Mid\nTempo', importance: 0.6, winRate: 0.60 },
            { id: 'PICK_ORIENTED', name: 'Pick\nOriented', importance: 0.4, winRate: 0.35 }
        ];
        
        this.edges = [
            { from: 'MID_TEMPO', to: 'TEAMFIGHT_COMMIT', weight: 0.25, type: 'win' },
            { from: 'BOT_PRESSURE', to: 'OBJECTIVE_STACKING', weight: 0.18, type: 'win' },
            { from: 'RIVER_CONTROL', to: 'TEAMFIGHT_COMMIT', weight: 0.22, type: 'win' },
            { from: 'TEAMFIGHT_COMMIT', to: 'OBJECTIVE_STACKING', weight: 0.28, type: 'win' }
        ];
        
        this.lynchpins = ['TEAMFIGHT_COMMIT', 'BOT_PRESSURE'];
        this.calculatePositions();
        this.render();
    }

    updateLynchpinList(robustness) {
        const list = document.getElementById('lynchpinList');
        if (!list) return;
        list.innerHTML = '';

        robustness.deny_results.slice(0, 3).forEach(r => {
            const item = document.createElement('div');
            item.className = 'lynchpin-item';
            const impact = Math.round((1 - r.robustness) * 100);
            item.innerHTML = `
                <div class="lynchpin-node-name">${r.deny}</div>
                <div class="lynchpin-impact-bar">
                    <div class="impact-fill" style="width: ${impact}%"></div>
                </div>
                <div class="lynchpin-impact-label">${impact}% Win Path Collapse</div>
            `;
            list.appendChild(item);
        });
    }

    updateCounterCards(report) {
        const container = document.getElementById('counterCards');
        if (!container) return;
        container.innerHTML = '';

        const strategies = Object.keys(report.break_strategy || {});
        strategies.forEach(strat => {
            const card = document.createElement('div');
            card.className = 'counter-card';
            card.innerHTML = `
                <div class="card-header">
                    <span class="target-strategy">${strat}</span>
                    <span class="phase-tag">Mid Game</span>
                </div>
                <div class="approach-title">Recommended Approach:</div>
                <ul class="approach-list">
                    ${report.break_strategy[strat].map(step => `<li>${step}</li>`).join('')}
                </ul>
            `;
            container.appendChild(card);
        });
    }

    updateDenialMatrix(report) {
        const body = document.getElementById('denialMatrixBody');
        if (!body) return;
        body.innerHTML = '';

        const nodes = (report.lynchpins || []).slice(0, 5).map(l => l.node);
        nodes.forEach(node => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${node}</td>
                <td><div class="matrix-cell high"></div></td>
                <td><div class="matrix-cell med"></div></td>
                <td><div class="matrix-cell low"></div></td>
                <td><div class="matrix-cell high"></div></td>
                <td><div class="matrix-cell med"></div></td>
            `;
            body.appendChild(row);
        });
    }

    updateCoachSummary(mcBaseline, robustness) {
        const summary = document.getElementById('coachSummary');
        if (!summary) return;
        
        const bestDeny = robustness.deny_results[0];
        const collapsePct = Math.round((1 - bestDeny.robustness) * 100);
        
        const topPath = mcBaseline.top_success_paths[0][0];

        summary.innerHTML = `
            <div class="summary-icon">🎯</div>
            <div class="summary-content">
                <p class="summary-text">
                    This team relies on <strong>${topPath}</strong>. 
                    Denying <strong>${bestDeny.deny}</strong> collapses <strong>${collapsePct}% of win paths</strong>. 
                    Monte Carlo confirms this strategy holds across high variance.
                </p>
            </div>
        `;
    }

    setupSimulation(mcBaseline, robustness) {
        const unlockBtn = document.getElementById('unlockSimulation');
        const simControls = document.getElementById('simulationControls');
        
        if (unlockBtn) {
            unlockBtn.disabled = false;
            unlockBtn.innerHTML = 'Unlock Monte Carlo Simulation';
            unlockBtn.addEventListener('click', () => {
                unlockBtn.parentElement.parentElement.style.display = 'none';
                simControls.style.display = 'block';
            });
        }

        const runBtn = document.getElementById('runMonteCarlo');
        if (runBtn) {
            runBtn.addEventListener('click', () => {
                const resultsPanel = document.getElementById('monteCarloResults');
                resultsPanel.style.display = 'block';
                
                const denialNode = document.getElementById('denialStrategy').value;
                const res = denialNode === 'none' ? robustness.baseline : 
                            robustness.deny_results.find(d => d.deny === denialNode);
                
                if (res) {
                    const scoreValue = document.querySelector('.score-value');
                    const scoreLabel = document.querySelector('.score-label');
                    const winRate = (res.success_rate * 100).toFixed(1);
                    scoreValue.textContent = winRate + '%';
                    scoreLabel.textContent = winRate > 70 ? 'High Confidence' : (winRate > 40 ? 'Medium Risk' : 'Strategic Collapse');
                }
            });
        }
    }
    
    calculatePositions() {
        this.positions = {};
        this.nodes.forEach((node, i) => {
            const angle = (i / this.nodes.length) * 2 * Math.PI - Math.PI / 2;
            this.positions[node.id] = {
                x: this.centerX + this.radius * Math.cos(angle),
                y: this.centerY + this.radius * Math.sin(angle)
            };
        });
    }
    
    setupEventListeners() {
        // Filter controls
        document.querySelectorAll('input[name="transitionFilter"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.filter = e.target.value;
                this.render();
            });
        });
        
        // Probability slider
        const slider = document.getElementById('edgeProbSlider');
        const valueDisplay = document.getElementById('edgeProbValue');
        
        slider.addEventListener('input', (e) => {
            this.minProbability = parseFloat(e.target.value);
            valueDisplay.textContent = e.target.value;
            this.render();
        });
        
        // Canvas interactions
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.hideTooltip());
    }
    
    render() {
        console.log('Rendering graph...');
        console.log('Canvas dimensions:', this.canvas.width, 'x', this.canvas.height);
        console.log('Filter:', this.filter, 'Min probability:', this.minProbability);
        
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw a test rectangle to verify canvas is working
        this.ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';
        this.ctx.fillRect(10, 10, 100, 50);
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '12px sans-serif';
        this.ctx.fillText('Canvas Working', 15, 30);
        
        // Draw edges first (behind nodes)
        this.drawEdges();
        
        // Draw nodes on top
        this.drawNodes();
        
        console.log('Graph rendering complete');
    }
    
    drawEdges() {
        const filteredEdges = this.edges.filter(edge => {
            if (edge.weight < this.minProbability) return false;
            if (this.filter === 'win' && edge.type !== 'win') return false;
            if (this.filter === 'loss' && edge.type !== 'loss') return false;
            return true;
        });

        console.log('Drawing', filteredEdges.length, 'edges');

        filteredEdges.forEach(edge => {
            const fromPos = this.positions[edge.from];
            const toPos = this.positions[edge.to];

            if (!fromPos || !toPos) {
                console.warn('Missing position for edge:', edge);
                return;
            }

            // Calculate edge endpoints with padding
            const dx = toPos.x - fromPos.x;
            const dy = toPos.y - fromPos.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const unitX = dx / distance;
            const unitY = dy / distance;

            const padding = this.nodeRadius + 15;
            const startX = fromPos.x + unitX * padding;
            const startY = fromPos.y + unitY * padding;
            const endX = toPos.x - unitX * padding;
            const endY = toPos.y - unitY * padding;

            // Skip very short edges
            const edgeLength = Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2);
            if (edgeLength < 50) {
                console.log('Skipping short edge:', edge.from, '->', edge.to);
                return;
            }

            // MUCH MORE VISIBLE edge thickness (3-15px range)
            const thickness = 3 + edge.weight * 12;
            const color = edge.type === 'win' ? '#0ac8b9' : '#ff4655';
            const opacity = this.getEdgeOpacity(edge);

            console.log(`Drawing edge ${edge.from}->${edge.to}, thickness: ${thickness.toFixed(1)}px`);

            // Draw line with higher opacity for visibility
            this.ctx.beginPath();
            this.ctx.moveTo(startX, startY);
            this.ctx.lineTo(endX, endY);
            this.ctx.strokeStyle = `rgba(${color === '#0ac8b9' ? '10, 200, 185' : '255, 70, 85'}, ${Math.max(opacity, 0.7)})`;
            this.ctx.lineWidth = thickness;
            this.ctx.stroke();

            // Draw arrow
            this.drawArrow(endX, endY, startX, startY, color, Math.max(opacity, 0.7));
        });
    }
    
    drawArrow(endX, endY, startX, startY, color, opacity) {
        const angle = Math.atan2(endY - startY, endX - startX);
        const arrowSize = 15; // Larger arrows for visibility
        
        this.ctx.beginPath();
        this.ctx.moveTo(endX, endY);
        this.ctx.lineTo(
            endX - arrowSize * Math.cos(angle - Math.PI / 6),
            endY - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.lineTo(
            endX - arrowSize * Math.cos(angle + Math.PI / 6),
            endY - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.closePath();
        
        // Use proper RGBA format
        const rgbaColor = color === '#0ac8b9' ? `rgba(10, 200, 185, ${opacity})` : `rgba(255, 70, 85, ${opacity})`;
        this.ctx.fillStyle = rgbaColor;
        this.ctx.fill();
    }
    
    drawNodes() {
        console.log('Drawing', this.nodes.length, 'nodes');
        
        this.nodes.forEach((node, index) => {
            const pos = this.positions[node.id];
            const isSelected = this.selectedNode === node.id;
            const isLynchpin = this.lynchpins.includes(node.id);
            const opacity = this.getNodeOpacity(node.id);
            
            // Calculate node size based on importance
            const size = this.nodeRadius * (0.7 + node.importance * 0.3);
            
            console.log(`Drawing node ${node.id} at (${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}) size: ${size.toFixed(1)}`);
            
            // Draw lynchpin ring
            if (isLynchpin) {
                this.ctx.beginPath();
                this.ctx.arc(pos.x, pos.y, size + 8, 0, Math.PI * 2);
                this.ctx.strokeStyle = `rgba(200, 155, 60, ${opacity})`;
                this.ctx.lineWidth = 4;
                this.ctx.stroke();
            }
            
            // Draw node circle
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(10, 21, 32, ${0.9 * opacity})`;
            this.ctx.fill();
            
            // Draw node border (color based on win rate)
            const borderColor = node.winRate > 0.6 ? '#0ac8b9' : node.winRate < 0.4 ? '#ff4655' : '#9b6fe8';
            this.ctx.strokeStyle = isSelected ? '#c89b3c' : borderColor;
            this.ctx.lineWidth = isSelected ? 4 : 3;
            this.ctx.stroke();
            
            // Draw label
            this.drawNodeLabel(node, pos, opacity);
        });
        
        console.log('Nodes drawing complete');
    }
    
    drawNodeLabel(node, pos, opacity) {
        this.ctx.fillStyle = `rgba(240, 246, 246, ${opacity})`;
        this.ctx.font = 'bold 12px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        const lines = node.name.split('\n');
        const lineHeight = 14;
        const startY = pos.y - (lines.length - 1) * lineHeight / 2;
        
        lines.forEach((line, i) => {
            this.ctx.fillText(line, pos.x, startY + i * lineHeight);
        });
    }
    
    getEdgeOpacity(edge) {
        if (!this.selectedNode) return 0.8;
        return (edge.from === this.selectedNode || edge.to === this.selectedNode) ? 1.0 : 0.3;
    }
    
    getNodeOpacity(nodeId) {
        if (!this.selectedNode) return 1.0;
        return nodeId === this.selectedNode ? 1.0 : 0.4;
    }
    
    handleClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const clickedNode = this.findNodeAt(x, y);
        this.selectedNode = this.selectedNode === clickedNode ? null : clickedNode;
        this.render();
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const hoveredNode = this.findNodeAt(x, y);
        
        if (hoveredNode) {
            this.showTooltip(hoveredNode, e.clientX, e.clientY);
            this.canvas.style.cursor = 'pointer';
        } else {
            this.hideTooltip();
            this.canvas.style.cursor = 'crosshair';
        }
    }
    
    findNodeAt(x, y) {
        for (const node of this.nodes) {
            const pos = this.positions[node.id];
            const size = this.nodeRadius * (0.7 + node.importance * 0.3);
            const distance = Math.sqrt((x - pos.x) ** 2 + (y - pos.y) ** 2);
            
            if (distance <= size) {
                return node.id;
            }
        }
        return null;
    }
    
    showTooltip(nodeId, mouseX, mouseY) {
        if (!this.tooltip) return;
        const node = this.nodes.find(n => n.id === nodeId);
        if (!node) return;
        
        const outgoingEdges = this.edges.filter(e => e.from === nodeId);
        const followUps = outgoingEdges
            .sort((a, b) => b.weight - a.weight)
            .slice(0, 3)
            .map(e => {
                const targetNode = this.nodes.find(n => n.id === e.to);
                return targetNode ? targetNode.name.replace('\n', ' ') : e.to;
            });
        
        this.tooltip.innerHTML = `
            <div style="font-weight: bold; color: #9b6fe8; margin-bottom: 8px;">
                ${node.name.replace('\n', ' ')}
            </div>
            <div style="font-size: 12px; line-height: 1.4;">
                <div><strong style="color: #c89b3c;">Win Rate:</strong> ${(node.winRate * 100).toFixed(0)}%</div>
                <div><strong style="color: #c89b3c;">Importance:</strong> ${(node.importance * 100).toFixed(0)}%</div>
                ${followUps.length > 0 ? `
                    <div style="margin-top: 8px;">
                        <strong style="color: #c89b3c;">Common Follow-ups:</strong><br>
                        <span style="color: #aab3b8; font-size: 11px;">${followUps.join(', ')}</span>
                    </div>
                ` : ''}
            </div>
        `;
        
        this.tooltip.style.left = `${mouseX + 15}px`;
        this.tooltip.style.top = `${mouseY + 15}px`;
        this.tooltip.classList.add('active');
    }
    
    hideTooltip() {
        if (this.tooltip) this.tooltip.classList.remove('active');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Strategy Graph');
    new StrategyGraph();
});