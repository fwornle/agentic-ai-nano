/**
 * Custom navigation toggle functionality for MkDocs Material theme
 * Allows collapsing/expanding navigation sections on click
 */

document.addEventListener('DOMContentLoaded', function() {
    // Wait for navigation to be fully loaded
    setTimeout(function() {
        initializeNavToggle();
    }, 100);
});

function initializeNavToggle() {
    // Get all navigation sections with expandable content
    const navSections = document.querySelectorAll('.md-nav__item--nested');
    
    navSections.forEach(function(section) {
        const toggle = section.querySelector('.md-nav__link');
        const isActive = section.querySelector('.md-nav__toggle:checked');
        
        if (toggle) {
            // Store original click behavior
            const originalOnClick = toggle.onclick;
            
            // Add custom click handler
            toggle.addEventListener('click', function(e) {
                const checkbox = section.querySelector('.md-nav__toggle');
                const isCurrentlyExpanded = checkbox && checkbox.checked;
                
                // If clicking on already active section, toggle it
                if (section.classList.contains('md-nav__item--active')) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    if (checkbox) {
                        // Toggle the checkbox state
                        checkbox.checked = !isCurrentlyExpanded;
                        
                        // Update aria-expanded attribute
                        toggle.setAttribute('aria-expanded', checkbox.checked);
                        
                        // Add/remove expanded class for visual feedback
                        if (checkbox.checked) {
                            section.classList.add('md-nav__item--expanded');
                        } else {
                            section.classList.remove('md-nav__item--expanded');
                        }
                    }
                    
                    return false;
                }
                
                // For non-active sections, allow normal navigation
                if (originalOnClick) {
                    originalOnClick.call(this, e);
                }
            });
            
            // Add visual indicator for collapsible sections
            toggle.style.cursor = 'pointer';
            
            // Set initial state
            if (isActive) {
                section.classList.add('md-nav__item--expanded');
            }
        }
    });
    
    // Handle navigation state persistence across page loads
    handleNavigationState();
}

function handleNavigationState() {
    // Store navigation state in sessionStorage
    const navState = sessionStorage.getItem('navState');
    
    if (navState) {
        try {
            const state = JSON.parse(navState);
            
            // Restore previous navigation state
            Object.keys(state).forEach(function(key) {
                const section = document.querySelector(`[data-md-nav-section="${key}"]`);
                if (section) {
                    const checkbox = section.querySelector('.md-nav__toggle');
                    if (checkbox) {
                        checkbox.checked = state[key];
                    }
                }
            });
        } catch (e) {
            console.error('Error restoring navigation state:', e);
        }
    }
    
    // Save navigation state on change
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('md-nav__toggle')) {
            saveNavigationState();
        }
    });
}

function saveNavigationState() {
    const navToggles = document.querySelectorAll('.md-nav__toggle');
    const state = {};
    
    navToggles.forEach(function(toggle) {
        const section = toggle.closest('[data-md-nav-section]');
        if (section) {
            const sectionId = section.getAttribute('data-md-nav-section');
            state[sectionId] = toggle.checked;
        }
    });
    
    sessionStorage.setItem('navState', JSON.stringify(state));
}

// Add CSS for smooth transitions
const style = document.createElement('style');
style.textContent = `
    /* Smooth transition for navigation expansion/collapse */
    .md-nav__item--nested .md-nav {
        transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out;
        overflow: hidden;
    }
    
    /* Visual feedback for collapsible sections */
    .md-nav__item--nested > .md-nav__link::after {
        content: ' ▾';
        display: inline-block;
        transition: transform 0.3s ease;
        margin-left: 0.3em;
        font-size: 0.8em;
        opacity: 0.6;
    }
    
    .md-nav__item--nested:not(.md-nav__item--expanded) > .md-nav__link::after {
        transform: rotate(-90deg);
    }
    
    /* Highlight active but collapsed sections */
    .md-nav__item--active:not(.md-nav__item--expanded) > .md-nav__link {
        background-color: var(--md-default-bg-color--light);
        border-left: 3px solid var(--md-primary-fg-color);
        padding-left: calc(0.6rem - 3px);
    }
    
    /* Ensure nested navigation is properly hidden when collapsed */
    .md-nav__item--nested:not(.md-nav__item--expanded) .md-nav__toggle:not(:checked) ~ .md-nav {
        display: none;
    }
`;
document.head.appendChild(style);