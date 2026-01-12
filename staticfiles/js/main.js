// GSAP Animations
document.addEventListener('DOMContentLoaded', function() {
    // Header animation
    gsap.from('header', {
        duration: 1,
        y: -100,
        opacity: 0,
        ease: "power3.out"
    });
    
    // Hero section animation
    gsap.from('.hero-content', {
        duration: 1.5,
        y: 50,
        opacity: 0,
        delay: 0.5,
        ease: "power3.out"
    });
    
    // Cards animation
    gsap.from('.content-card', {
        duration: 1,
        y: 30,
        opacity: 0,
        stagger: 0.2,
        scrollTrigger: {
            trigger: '.content-grid',
            start: 'top 80%',
        }
    });
    
    // Initialize dropdowns
    initDropdowns();
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Count up animations
    initCounters();
    
    // Link display timer
    initLinkDisplay();
});

// Dropdown functionality
function initDropdowns() {
    const dropdowns = document.querySelectorAll('[data-dropdown]');
    
    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('[data-dropdown-toggle]');
        const menu = dropdown.querySelector('[data-dropdown-menu]');
        
        if (button && menu) {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('hidden');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    menu.classList.add('hidden');
                }
            });
        }
    });
}

// Mobile menu functionality
function initMobileMenu() {
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            
            // Animate menu
            if (!mobileMenu.classList.contains('hidden')) {
                gsap.from(mobileMenu, {
                    duration: 0.3,
                    x: 300,
                    opacity: 0,
                    ease: "power3.out"
                });
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && !mobileMenuButton.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

// Count up animation for statistics
function initCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = parseInt(counter.getAttribute('data-duration') || 2000);
        const increment = target / (duration / 16); // 60fps
        
        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.floor(current).toLocaleString();
        }, 16);
    });
}

// Link display with countdown
function initLinkDisplay() {
    const linkContainers = document.querySelectorAll('[data-link-container]');
    
    linkContainers.forEach(container => {
        const duration = parseInt(container.getAttribute('data-duration') || 30);
        const link = container.querySelector('[data-link]');
        const countdownElement = container.querySelector('[data-countdown]');
        
        if (link && countdownElement) {
            let countdown = duration;
            
            const timer = setInterval(() => {
                countdownElement.textContent = countdown;
                countdown--;
                
                if (countdown < 0) {
                    clearInterval(timer);
                    container.classList.remove('hidden');
                    
                    // Animate link appearance
                    gsap.from(link, {
                        duration: 0.5,
                        scale: 0.5,
                        opacity: 0,
                        ease: "back.out(1.7)"
                    });
                }
            }, 1000);
        }
    });
}