/**
 * Network Detection and Conditional Content Display
 * Shows BMW-specific content only when accessed from corporate network
 */

(function() {
    'use strict';

    // BMW corporate network detection
    function isCorporateNetwork() {
        // Check if accessing from BMW corporate network indicators
        const hostname = window.location.hostname;
        const host = window.location.host;
        
        // Corporate network indicators
        const corporateIndicators = [
            // Internal IP ranges (adjust as needed)
            /^10\./,
            /^192\.168\./,
            /^172\.(1[6-9]|2[0-9]|3[01])\./,
            // BMW-specific domains
            /bmw\.com$/,
            /bmwgroup\.com$/
        ];

        // Check hostname against corporate patterns
        for (const pattern of corporateIndicators) {
            if (pattern.test(hostname) || pattern.test(host)) {
                console.log('Corporate network detected via hostname:', hostname);
                return true;
            }
        }

        // For development/testing - check if we're on GitHub Pages from public internet
        if (hostname.includes('github.io')) {
            console.log('GitHub Pages detected - showing public content');
            return false;
        }

        // For localhost/127.0.0.1 - default to corporate for testing
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            console.log('Localhost detected - defaulting to corporate content for testing');
            return true;
        }

        // Check user agent or other indicators that might suggest corporate network
        // This is a fallback check
        console.log('No corporate network indicators found for hostname:', hostname);

        // Default to public network if no corporate indicators found
        return false;
    }

    function checkInternalService() {
        // Run internal service check to detect corporate network access
        console.log('Running internal service check to detect corporate network access');
        
        // Attempt to reach BMW internal service (non-blocking)
        const img = new Image();
        img.onload = function() {
            // If image loads, we're likely on corporate network
            console.log('Internal service reachable - showing corporate content');
            showCorporateContent();
        };
        img.onerror = function() {
            // If image fails, we're likely on public network
            console.log('Internal service not reachable - showing public content');
            hideCorporateContent();
        };
        // Use a small internal resource that exists only on corporate network
        img.src = 'http://10.21.202.14/favicon.ico?' + Date.now();
    }

    function showCorporateContent() {
        console.log('Showing BMW corporate content');
        
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(element => {
            element.style.setProperty('display', 'block', 'important');
            element.classList.add('corporate-network-detected');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(element => {
            element.style.setProperty('display', 'none', 'important');
        });

        // Show BMW-specific navigation items in corporate mode
        showNavigationItems([
            'Overview: Developing in the BMW Cloud',
            'BMW Cloud Development Environment with Coder',
            'BMW Cloud Development Environment',
            'Why BMW Cloud Development'
        ]);

        // Update any dynamic text content
        updateNetworkSpecificContent(true);
    }

    function hideCorporateContent() {
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(element => {
            element.style.setProperty('display', 'none', 'important');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(element => {
            element.style.setProperty('display', 'block', 'important');
            element.classList.add('public-network-detected');
        });

        // Hide BMW-specific navigation items in public mode
        hideNavigationItems([
            'Overview: Developing in the BMW Cloud',
            'BMW Cloud Development Environment with Coder',
            'BMW Cloud Development Environment',
            'Why BMW Cloud Development'
        ]);

        // Update any dynamic text content
        updateNetworkSpecificContent(false);
    }

    function hideNavigationItems(itemTexts) {
        // Wait for navigation to load
        setTimeout(() => {
            const navItems = document.querySelectorAll('.md-nav__item');
            navItems.forEach(item => {
                const link = item.querySelector('.md-nav__link');
                if (link) {
                    const linkText = link.textContent.trim();
                    if (itemTexts.some(text => linkText.includes(text))) {
                        item.style.display = 'none';
                    }
                }
            });
        }, 500);
    }

    function showNavigationItems(itemTexts) {
        // Wait for navigation to load and show specified items
        setTimeout(() => {
            const navItems = document.querySelectorAll('.md-nav__item');
            navItems.forEach(item => {
                const link = item.querySelector('.md-nav__link');
                if (link) {
                    const linkText = link.textContent.trim();
                    if (itemTexts.some(text => linkText.includes(text))) {
                        item.style.display = 'block';
                    }
                }
            });
        }, 500);
    }

    function updateNetworkSpecificContent(isCorporate) {
        // Update setup instructions based on network
        const setupInstructions = document.querySelector('.setup-instructions');
        if (setupInstructions) {
            if (isCorporate) {
                setupInstructions.innerHTML = `
                    <h3>🚀 BMW Corporate Network Detected</h3>
                    <p><strong>Access your pre-configured development environment:</strong></p>
                    <ol>
                        <li><a href="http://10.21.202.14/workspaces">Open Coder Workspace</a></li>
                        <li>Use your BMW credentials to log in</li>
                        <li>Launch your pre-configured environment</li>
                    </ol>
                `;
            } else {
                setupInstructions.innerHTML = `
                    <h3>🌐 Public Network - Local Setup Required</h3>
                    <p><strong>Set up your local development environment:</strong></p>
                    <ol>
                        <li>Install Python 3.11+</li>
                        <li>Clone the repository</li>
                        <li>Install dependencies per module requirements</li>
                        <li>Configure your own LLM API keys</li>
                    </ol>
                `;
            }
        }
    }

    function initializeNetworkDetection() {
        // Add CSS for smooth transitions and ensure BMW content is hidden by default on public sites
        const style = document.createElement('style');
        const hostname = window.location.hostname;
        const isPublicSite = hostname.includes('github.io') || hostname.includes('fwornle');
        
        style.textContent = `
            .bmw-corporate-only, .bmw-public-alternative {
                transition: opacity 0.3s ease-in-out;
            }
            .bmw-corporate-only.corporate-network-detected {
                animation: fadeIn 0.5s ease-in-out;
            }
            .bmw-public-alternative.public-network-detected {
                animation: fadeIn 0.5s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            /* Ensure setup instructions are visible */
            .setup-instructions {
                min-height: 100px;
            }
            /* Force hide BMW content on public sites */
            ${isPublicSite ? '.bmw-corporate-only { display: none !important; } .bmw-public-alternative { display: block !important; }' : ''}
        `;
        document.head.appendChild(style);

        // Default to public content but allow corporate override
        if (isPublicSite) {
            console.log('GitHub Pages detected - defaulting to public content, but checking for corporate access');
            hideCorporateContent();
            // Try the internal service check even on GitHub Pages
            // in case someone is accessing from corporate network
            checkInternalService();
            return;
        }

        // Initial network check
        if (isCorporateNetwork()) {
            console.log('Corporate network detected initially');
            showCorporateContent();
        } else {
            console.log('Public network assumed initially');
            hideCorporateContent();
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeNetworkDetection);
    } else {
        initializeNetworkDetection();
    }

})();