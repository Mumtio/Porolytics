// ===== PARTICLE GENERATION =====
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDuration = (Math.random() * 15 + 10) + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        
        // Random size variation
        const size = Math.random() * 3 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        particlesContainer.appendChild(particle);
    }
}

// ===== MODAL INTERACTION =====
function initModal() {
    const modalOverlay = document.getElementById('modalOverlay');
    const modalPanel = document.getElementById('modalPanel');
    const btnPrimary = document.querySelector('.btn-primary');
    const btnCancel = document.getElementById('cancelModal');
    const btnBegin = document.getElementById('beginAnalysis');
    const poroCorner = document.querySelector('.poro-corner');
    const yourTeamInput = document.getElementById('yourTeam');
    
    // Open modal
    function openModal() {
        document.body.classList.add('modal-active');
        document.body.classList.remove('modal-closing');
        
        setTimeout(() => {
            modalOverlay.classList.add('active');
            poroCorner.classList.add('analysis-mode');
            
            // Auto-focus first input after modal settles
            setTimeout(() => {
                yourTeamInput.focus();
            }, 900);
        }, 700);
    }
    
    // Close modal
    function closeModal() {
        modalOverlay.classList.remove('active');
        poroCorner.classList.remove('analysis-mode');
        
        // Add closing class for reverse animation
        document.body.classList.add('modal-closing');
        document.body.classList.remove('modal-active');
        
        // Remove closing class after animation completes
        setTimeout(() => {
            document.body.classList.remove('modal-closing');
        }, 1000);
    }
    
    // Event listeners
    btnPrimary.addEventListener('click', openModal);
    btnCancel.addEventListener('click', closeModal);
    
    // Close on overlay click
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
        }
    });
    
    // Close on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
            closeModal();
        }
    });
    
    // Begin Analysis action
    btnBegin.addEventListener('click', () => {
        const yourTeam = document.getElementById('yourTeam').value;
        const opponentTeam = document.getElementById('opponentTeam').value;
        
        if (yourTeam && opponentTeam) {
            console.log('Analysis started:', { yourTeam, opponentTeam });
            
            // Store team names for analysis page
            localStorage.setItem('yourTeam', yourTeam);
            localStorage.setItem('opponentTeam', opponentTeam);
            
            // Transition to loading page
            modalOverlay.classList.remove('active');
            setTimeout(() => {
                window.location.href = 'loading.html';
            }, 500);
        } else {
            // Highlight empty fields with golden border
            if (!yourTeam) {
                document.getElementById('yourTeam').style.borderColor = '#C89B3C';
            }
            if (!opponentTeam) {
                document.getElementById('opponentTeam').style.borderColor = '#C89B3C';
            }
        }
    });
    
    // Reset border color on input
    document.querySelectorAll('.modal-input').forEach(input => {
        input.addEventListener('input', function() {
            this.style.borderColor = '';
        });
    });
}

// ===== BUTTON INTERACTIONS =====
function initButtonEffects() {
    const primaryBtn = document.querySelector('.btn-primary');
    
    // Add ripple effect on click
    primaryBtn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
}

// ===== INITIALIZE ALL =====
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    initModal();
    initButtonEffects();
    
    // Add cursor trail style
    const style = document.createElement('style');
    style.textContent = `
        .cursor-trail {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(10, 200, 185, 0.4);
            border-radius: 50%;
            pointer-events: none;
            animation: trailFade 0.5s ease-out forwards;
            z-index: 9999;
        }
        
        @keyframes trailFade {
            to {
                opacity: 0;
                transform: scale(2);
            }
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: rippleEffect 0.6s ease-out;
            pointer-events: none;
        }
        
        @keyframes rippleEffect {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

// ===== CONSOLE EASTER EGG =====
console.log('%c🎯 POROLYTICS', 'color: #0AC8B9; font-size: 24px; font-weight: bold;');
console.log('%cThe Scout\'s War Room', 'color: #AAB3B8; font-size: 14px;');
console.log('%cEvery team has a lynchpin. Find it.', 'color: #C89B3C; font-size: 12px; font-style: italic;');

