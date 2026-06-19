/**
 * Main Application
 * GSAP animations, utilities, and global functions
 */

// ===== NOTIFICATION SYSTEM =====

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const messageEl = document.getElementById('notificationMessage');

    messageEl.textContent = message;
    
    // Set background color based on type
    notification.style.background = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#06b6d4',
    }[type] || '#06b6d4';

    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, NOTIFICATION_DURATION);
}

// ===== SCROLL UTILITIES =====

function scrollTo(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// ===== GSAP ANIMATIONS =====

function initGSAPAnimations() {
    if (typeof gsap === 'undefined') {
        Logger.warn('GSAP not loaded');
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // Hero animations
    gsap.from('.hero-content', {
        duration: 1,
        opacity: 0,
        y: 50,
        ease: 'power3.out'
    });

    gsap.from('.hero-card', {
        duration: 1,
        opacity: 0,
        y: -50,
        ease: 'power3.out',
        delay: 0.3
    });

    // Features animation
    gsap.utils.toArray('.feature-card').forEach((card, index) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            opacity: 0,
            y: 30,
            delay: index * 0.1,
            ease: 'power3.out'
        });
    });

    // Pricing cards
    gsap.utils.toArray('.price-card').forEach((card, index) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 80%',
                toggleActions: 'play none none reverse'
            },
            duration: 0.8,
            opacity: 0,
            scale: 0.8,
            delay: index * 0.15,
            ease: 'back.out'
        });
    });

    // Floating animation
    gsap.to('.badge', {
        y: 20,
        duration: 3,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });

    // Parallax on hero
    gsap.to('.hero-card', {
        scrollTrigger: {
            trigger: '.hero',
            start: 'top top',
            end: 'bottom top',
            scrub: 1
        },
        y: 100,
        ease: 'none'
    });

    Logger.log('GSAP animations initialized');
}

// ===== MOUSE EFFECTS =====

let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) - 0.5;
    mouseY = (e.clientY / window.innerHeight) - 0.5;

    // Apply tilt to cards
    updateCardTilt();
});

function updateCardTilt() {
    const cards = document.querySelectorAll('.feature-card, .glass-card, .price-card');
    cards.forEach(card => {
        if (card.matches(':hover') && typeof gsap !== 'undefined') {
            const rect = card.getBoundingClientRect();
            const x = (mouseX * window.innerWidth - rect.left - rect.width / 2) / (rect.width / 2);
            const y = (mouseY * window.innerHeight - rect.top - rect.height / 2) / (rect.height / 2);

            gsap.to(card, {
                rotationX: y * 5,
                rotationY: x * 5,
                duration: 0.5,
                ease: 'power2.out',
                transformPerspective: 1000
            });
        } else if (typeof gsap !== 'undefined') {
            gsap.to(card, {
                rotationX: 0,
                rotationY: 0,
                duration: 0.5,
                ease: 'power2.out'
            });
        }
    });
}

// ===== BUTTON EFFECTS =====

function initButtonEffects() {
    const buttons = document.querySelectorAll('button');

    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            if (typeof gsap !== 'undefined') {
                gsap.to(this, {
                    duration: 0.3,
                    scale: 1.05,
                    ease: 'power2.out'
                });
            }
        });

        button.addEventListener('mouseleave', function() {
            if (typeof gsap !== 'undefined') {
                gsap.to(this, {
                    duration: 0.3,
                    scale: 1,
                    ease: 'power2.out'
                });
            }
        });

        button.addEventListener('click', function(e) {
            createRipple(e, this);
        });
    });
}

function createRipple(event, button) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    button.appendChild(ripple);

    if (typeof gsap !== 'undefined') {
        gsap.to(ripple, {
            duration: 0.6,
            scale: 2,
            opacity: 0,
            onComplete: () => ripple.remove()
        });
    }
}

// ===== SMOOTH SCROLL =====

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// ===== FORM VALIDATION =====

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// ===== API HEALTH CHECK =====

async function checkAPIHealth() {
    try {
        const response = await api.checkHealth();
        Logger.log('API Health:', response);
        return response.status === 'healthy';
    } catch (error) {
        Logger.error('API Health Check Failed', error);
        return false;
    }
}

// ===== INITIALIZATION =====

async function initApp() {
    Logger.log('🚀 NeuroSphere AI - Initializing...');

    try {
        // Check API health
        const apiHealthy = await checkAPIHealth();
        if (!apiHealthy) {
            Logger.warn('Backend API is not responding. Some features may not work.');
        }

        // Initialize features
        initGSAPAnimations();
        initButtonEffects();
        initSmoothScroll();

        // Show welcome message
        Logger.log('✅ Application initialized successfully');
        showNotification('Welcome to NeuroSphere AI!', 'success');

    } catch (error) {
        Logger.error('Initialization error', error);
    }
}

// ===== PAGE LIFECYCLE =====

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    Logger.log('Application closing...');
});

// Handle visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        Logger.log('App hidden');
    } else {
        Logger.log('App visible');
    }
});

// ===== DEMO MODE =====

if (PAGE_CONFIG.DEMO_MODE) {
    Logger.warn('Running in DEMO MODE - API calls are simulated');
}

// ===== RIPPLE STYLES =====

const style = document.createElement('style');
style.textContent = `
    button {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.6), transparent);
        pointer-events: none;
        transform: scale(0);
    }
`;
document.head.appendChild(style);

// ===== RESPONSIVE MENU =====

function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) {
        navLinks.classList.toggle('hidden');
    }
}

// Hide mobile menu on larger screens
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        const navLinks = document.getElementById('navLinks');
        if (navLinks) {
            navLinks.classList.remove('hidden');
        }
    }
});

// Export for modular use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        scrollTo,
        validateEmail,
        validatePassword,
        checkAPIHealth,
    };
}