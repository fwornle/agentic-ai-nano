/**
 * Network Detection and Conditional Content Display
 * Shows BMW-specific content only when accessed from corporate network
 */

(function() {
    'use strict';
    
    // Global variable to track corporate network status
    let isCorporateNetworkDetected = false;

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
        
        // Show initial status
        updateNetworkStatusIndicator('checking');
        
        // Try multiple detection methods
        let detectionComplete = false;
        
        // Method 1: Check if user manually wants to enable corporate mode (for testing)
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('corporate') === 'true') {
            console.log('🔧 Corporate mode forced via URL parameter');
            showCorporateContent();
            return;
        }
        
        // Method 2: Direct internal service check (faster, no external API calls)
        console.log('🔍 Checking internal BMW services for corporate network access');
        tryInternalServiceCheck();
            
        function tryInternalServiceCheck() {
            if (detectionComplete) return;
            
            // Try internal service check with multiple BMW internal services
            const testUrls = [
                'https://contenthub.bmwgroup.net/favicon.ico',  // BMW Content Hub (most reliable)
                'https://10.21.202.14/favicon.ico',             // Coder instance HTTPS
                'http://10.21.202.14/favicon.ico'               // Coder instance HTTP fallback
            ];
            
            let urlIndex = 0;
            
            function testNextUrl() {
                if (urlIndex >= testUrls.length || detectionComplete) {
                    // All URLs failed
                    if (!detectionComplete) {
                        console.log('❌ All internal service checks failed - showing public content');
                        hideCorporateContent();
                        detectionComplete = true;
                    }
                    return;
                }
                
                const testUrl = testUrls[urlIndex];
                console.log(`🔍 Trying internal service: ${testUrl}`);
                
                const img = new Image();
                img.onload = function() {
                    if (!detectionComplete) {
                        console.log('✅ Internal service reachable - showing corporate content');
                        showCorporateContent();
                        detectionComplete = true;
                    }
                };
                img.onerror = function() {
                    console.log(`❌ Failed to reach: ${testUrl}`);
                    urlIndex++;
                    setTimeout(testNextUrl, 500); // Try next URL after short delay
                };
                
                img.src = testUrl + '?' + Date.now();
            }
            
            testNextUrl();
        }
        
        // Set a timeout to ensure we don't wait forever  
        setTimeout(() => {
            if (!detectionComplete) {
                console.log('⏱️ BMW service check timed out after 3s - defaulting to public content');
                console.log('💡 If you are on BMW network, try manual override by clicking the status indicator');
                hideCorporateContent();
                detectionComplete = true;
            }
        }, 3000);
    }

    function showCorporateContent() {
        console.log('🏢 Showing BMW corporate content');
        
        // Set global flag to prevent MutationObserver from re-hiding content
        isCorporateNetworkDetected = true;
        
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        console.log(`Found ${corporateElements.length} corporate elements to show`);
        corporateElements.forEach((element, index) => {
            console.log(`Corporate element ${index}:`, element.tagName, element.className);
            element.classList.add('show-corporate');
            element.classList.add('corporate-network-detected');
            // Force display with inline style as backup
            element.style.setProperty('display', 'block', 'important');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        console.log(`Found ${publicElements.length} public elements to hide`);
        publicElements.forEach((element, index) => {
            console.log(`Public element ${index}:`, element.tagName, element.className);
            element.classList.add('hide-public');
            // Force hide with inline style as backup  
            element.style.setProperty('display', 'none', 'important');
        });

        // Show BMW-specific navigation items in corporate mode
        showNavigationItems([
            'BMW Cloud Development Environment with Coder',
            'BMW Cloud Development Environment',
            'Overview: Developing in the BMW Cloud',
            'Why BMW Cloud Development',
            'Cluster Resources',
            'Traditional Challenges in Corporate Environments',
            'The Cloud Development Solution',
            'How to Work with Coder',
            'Workspace Lifecycle',
            'Dev Containers: The Foundation',
            'Nano-Degree Specific Setup',
            'Working with AI Assistants'
        ]);

        // Update any dynamic text content
        updateNetworkSpecificContent(true);
        
        // Update network status indicator
        updateNetworkStatusIndicator('corporate');
    }

    function hideCorporateContent() {
        console.log('🌐 Showing public content');
        
        // Clear global flag to allow MutationObserver to hide BMW content
        isCorporateNetworkDetected = false;
        
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        console.log(`Found ${corporateElements.length} corporate elements to hide`);
        corporateElements.forEach(element => {
            element.classList.remove('show-corporate');
            element.classList.remove('corporate-network-detected');
            // Clear inline style and let default CSS take over
            element.style.removeProperty('display');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        console.log(`Found ${publicElements.length} public elements to show`);
        publicElements.forEach(element => {
            element.classList.remove('hide-public');
            element.classList.add('public-network-detected');
            // Clear inline style and let default CSS take over
            element.style.removeProperty('display');
        });

        // Hide BMW-specific navigation items in public mode
        hideNavigationItems([
            'BMW Cloud Development Environment with Coder',
            'BMW Cloud Development Environment',
            'Overview: Developing in the BMW Cloud',
            'Why BMW Cloud Development',
            'Cluster Resources',
            'Traditional Challenges in Corporate Environments',
            'The Cloud Development Solution',
            'How to Work with Coder',
            'Workspace Lifecycle',
            'Dev Containers: The Foundation',
            'Nano-Degree Specific Setup',
            'Working with AI Assistants'
        ]);

        // Update any dynamic text content
        updateNetworkSpecificContent(false);
        
        // Update network status indicator
        updateNetworkStatusIndicator('public');
    }

    function hideNavigationItems(itemTexts) {
        // Wait for navigation to load and repeatedly check (since ToC might load later)
        let attempts = 0;
        const maxAttempts = 10;
        
        function hideItems() {
            let found = false;
            
            // Target both main nav and table of contents
            const selectors = [
                '.md-nav__item',
                '.md-nav__list .md-nav__item',
                '.md-sidebar__scrollwrap .md-nav__item',
                '.md-nav--secondary .md-nav__item'
            ];
            
            selectors.forEach(selector => {
                const navItems = document.querySelectorAll(selector);
                navItems.forEach(item => {
                    const link = item.querySelector('.md-nav__link');
                    if (link) {
                        const linkText = link.textContent.trim();
                        if (itemTexts.some(text => linkText.includes(text) || linkText.toLowerCase().includes(text.toLowerCase()))) {
                            item.style.display = 'none';
                            found = true;
                            console.log('Hiding navigation item:', linkText);
                        }
                    }
                });
            });
            
            attempts++;
            if (!found && attempts < maxAttempts) {
                setTimeout(hideItems, 200);
            }
        }
        
        hideItems();
    }

    function showNavigationItems(itemTexts) {
        // Show navigation items immediately and with retries
        let attempts = 0;
        const maxAttempts = 10;
        
        function showItems() {
            let found = false;
            
            // Target both main nav and table of contents
            const selectors = [
                '.md-nav__item',
                '.md-nav__list .md-nav__item',
                '.md-sidebar__scrollwrap .md-nav__item',
                '.md-nav--secondary .md-nav__item'
            ];
            
            selectors.forEach(selector => {
                const navItems = document.querySelectorAll(selector);
                navItems.forEach(item => {
                    const link = item.querySelector('.md-nav__link');
                    if (link) {
                        const linkText = link.textContent.trim();
                        if (itemTexts.some(text => linkText.includes(text) || linkText.toLowerCase().includes(text.toLowerCase()))) {
                            item.style.setProperty('display', 'block', 'important');
                            found = true;
                            console.log('Showing navigation item:', linkText);
                        }
                    }
                });
            });
            
            attempts++;
            if (!found && attempts < maxAttempts) {
                setTimeout(showItems, 200);
            }
        }
        
        showItems();
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

    function updateNetworkStatusIndicator(networkType) {
        // Remove any existing status indicator
        const existingIndicator = document.querySelector('.network-status-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Create new status indicator
        const indicator = document.createElement('div');
        indicator.className = 'network-status-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${networkType === 'corporate' ? '#0066cc' : '#28a745'};
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        `;
        
        if (networkType === 'corporate') {
            indicator.innerHTML = `
                🏢 BMW Corporate Network
                <div style="font-size: 10px; font-weight: normal; margin-top: 2px;">
                    Cloud Dev Environment Available
                </div>
            `;
        } else if (networkType === 'checking') {
            indicator.innerHTML = `
                🔍 Detecting Network...
                <div style="font-size: 10px; font-weight: normal; margin-top: 2px;">
                    Checking corporate access
                </div>
            `;
            indicator.style.background = '#ffa500';
        } else {
            indicator.innerHTML = `
                🌐 Public Network
                <div style="font-size: 10px; font-weight: normal; margin-top: 2px;">
                    Local Setup Required
                </div>
            `;
        }

        // Make indicator clickable for manual override
        if (networkType === 'public') {
            indicator.style.cursor = 'pointer';
            indicator.title = 'Click to manually enable corporate mode for testing';
            indicator.addEventListener('click', () => {
                if (confirm('Enable BMW corporate mode? This will show internal BMW content.')) {
                    console.log('🔧 Manual override: Enabling corporate mode');
                    showCorporateContent();
                }
            });
        }

        document.body.appendChild(indicator);

        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.style.opacity = '0.7';
                indicator.style.transition = 'opacity 0.3s ease';
            }
        }, 10000);
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
            /* Default to public content on public sites but allow override */
            ${isPublicSite ? '.bmw-corporate-only { display: none !important; } .bmw-public-alternative { display: block !important; }' : ''}
            /* Corporate override styles */
            .bmw-corporate-only.show-corporate { display: block !important; }
            .bmw-public-alternative.hide-public { display: none !important; }
        `;
        document.head.appendChild(style);

        // Default to public content but allow corporate override
        if (isPublicSite) {
            console.log('GitHub Pages detected - checking for corporate access');
            // Don't immediately hide corporate content, let the service check determine it
            // Try the internal service check on GitHub Pages
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

    // Initialize when DOM is ready and on every page load
    function runDetection() {
        // Reset detection state for fresh detection on each page
        isCorporateNetworkDetected = false;
        console.log('🔄 Starting fresh network detection...');
        initializeNetworkDetection();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runDetection);
    } else {
        runDetection();
    }
    
    // Also run detection on navigation changes (for SPA behavior)
    window.addEventListener('popstate', runDetection);

    // Also observe for navigation changes (Material theme dynamic loading)
    const observer = new MutationObserver(() => {
        const hostname = window.location.hostname;
        // Only hide BMW content on public sites AND when corporate network is NOT detected
        if ((hostname.includes('github.io') || hostname.includes('fwornle')) && !isCorporateNetworkDetected) {
            console.log('🔍 MutationObserver: Re-hiding BMW content on public site (corporate not detected)');
            hideNavigationItems([
                'BMW Cloud Development Environment with Coder',
                'BMW Cloud Development Environment',
                'Overview: Developing in the BMW Cloud',
                'Why BMW Cloud Development',
                'Cluster Resources',
                'Traditional Challenges in Corporate Environments',
                'The Cloud Development Solution',
                'How to Work with Coder',
                'Workspace Lifecycle',
                'Dev Containers: The Foundation',
                'Nano-Degree Specific Setup',
                'Working with AI Assistants'
            ]);
        } else if (isCorporateNetworkDetected) {
            console.log('🏢 MutationObserver: Corporate network detected, ensuring BMW content is visible');
            // Make sure corporate content is still visible after navigation changes
            showNavigationItems([
                'BMW Cloud Development Environment with Coder',
                'BMW Cloud Development Environment',
                'Overview: Developing in the BMW Cloud',
                'Why BMW Cloud Development',
                'Cluster Resources',
                'Traditional Challenges in Corporate Environments',
                'The Cloud Development Solution',
                'How to Work with Coder',
                'Workspace Lifecycle',
                'Dev Containers: The Foundation',
                'Nano-Degree Specific Setup',
                'Working with AI Assistants'
            ]);
        }
    });

    // Start observing once DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            observer.observe(document.body, { childList: true, subtree: true });
        });
    } else {
        observer.observe(document.body, { childList: true, subtree: true });
    }

})();