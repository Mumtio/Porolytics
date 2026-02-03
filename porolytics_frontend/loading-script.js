const loadingMessages = [
    "Collecting match history...",
    "Analyzing draft patterns...",
    "Simulating strategic dependencies...",
    "Running Ant Colony Optimization...",
    "Building strategy graphs...",
    "Finalizing analysis..."
];

let currentMessageIndex = 0;
let progress = 0;

function updateLoading() {
    const loadingText = document.getElementById('loadingText');
    const progressBar = document.getElementById('progressBar');
    
    // Update message
    loadingText.style.opacity = '0';
    
    setTimeout(() => {
        loadingText.textContent = loadingMessages[currentMessageIndex];
        loadingText.style.opacity = '1';
        currentMessageIndex = (currentMessageIndex + 1) % loadingMessages.length;
    }, 300);
    
    // Update progress
    progress += 16.67; // 6 steps = 100%
    progressBar.style.width = Math.min(progress, 100) + '%';
    
    if (progress >= 100) {
        setTimeout(() => {
            window.location.href = 'analysis.html';
        }, 1000);
    }
}

// Start loading sequence
setInterval(updateLoading, 2000);
updateLoading();
