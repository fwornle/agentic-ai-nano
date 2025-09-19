/**
 * Network Detection and Conditional Content Display
 * Shows BMW-specific content only when accessed from corporate network
 * Updated: Removed all manual corporate mode switching capabilities
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

        // For localhost/127.0.0.1 - let the CN detection determine access
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            console.log('Localhost detected - running CN detection to determine access');
            return false; // Let checkInternalService() determine corporate access
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
        
        // Method 1: URL parameter override REMOVED to prevent manual corporate mode switching
        
        // Method 2: Check external IP first, then try internal service
        console.log('🔍 Checking BMW network access');
        console.log('🌍 Current hostname:', window.location.hostname);
        console.log('🌍 Current URL:', window.location.href);
        
        // Check external IP for BMW ranges (this was working before!)
        fetch('https://api.ipify.org?format=json')
            .then(response => response.json())
            .then(data => {
                console.log('🌐 External IP detected:', data.ip);
                // BMW corporate IP ranges
                const corporateIPPatterns = [
                    /^160\.46\./,    // Your working IP range
                    /^194\.114\./,   // BMW public IP range
                    /^195\.34\./,    // BMW public IP range
                    /^212\.204\./    // BMW public IP range
                ];
                
                const isCorporateIP = corporateIPPatterns.some(pattern => {
                    if (pattern.test(data.ip)) {
                        console.log(`✅ IP ${data.ip} matches corporate pattern: ${pattern}`);
                        return true;
                    }
                    return false;
                });
                
                if (isCorporateIP && !detectionComplete) {
                    console.log('✅ Corporate IP range detected - showing corporate content');
                    detectionComplete = true;
                    showCorporateContent();
                } else if (!detectionComplete) {
                    console.log(`📍 IP ${data.ip} not in corporate ranges, trying internal service check`);
                    tryInternalServiceCheck();
                }
            })
            .catch(error => {
                console.log('❌ IP detection failed, trying internal service check:', error);
                tryInternalServiceCheck();
            });
            
        function tryInternalServiceCheck() {
            if (detectionComplete) return;
            
            // Try internal service check with BMW Content Hub only (no 10.x latency)
            const testUrls = [
                'https://contenthub.bmwgroup.net/favicon.ico'  // BMW Content Hub (most reliable, no VPN latency)
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
                console.log('⏱️ BMW ContentHub check timed out after 2s - defaulting to public content');
                hideCorporateContent();
                detectionComplete = true;
            }
        }, 2000);
    }

    async function showCorporateContent() {
        // Corporate content is only shown when CN detection succeeds
        // No hostname restrictions - let the CN detection determine access
        
        console.log('🏢 Showing BMW corporate content');
        
        // Set global flag to prevent MutationObserver from re-hiding content
        isCorporateNetworkDetected = true;
        
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        console.log(`Found ${corporateElements.length} corporate elements to show`);
        corporateElements.forEach((element, index) => {
            console.log(`Corporate element ${index}:`, element.tagName, element.className);
            element.classList.add('show-corporate');
            element.classList.add('corporate-network-detected');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        console.log(`Found ${publicElements.length} public elements to hide`);
        publicElements.forEach((element, index) => {
            console.log(`Public element ${index}:`, element.tagName, element.className);
            element.classList.add('hide-public');
        });

        // Hide public navigation items and show corporate ones
        hidePublicNavigationItems();
        showCorporateNavigationItems();

        console.log('🏢 Corporate mode: BMW content enabled');
        
        // Load encrypted corporate content if available
        if (window.CorporateContentLoader) {
            console.log('🔐 Loading encrypted corporate content...');
            try {
                await window.CorporateContentLoader.load();
                console.log('✅ Corporate content decrypted and loaded');
            } catch (error) {
                console.error('❌ Failed to load encrypted content:', error);
            }
        }

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
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        console.log(`Found ${publicElements.length} public elements to show`);
        publicElements.forEach(element => {
            element.classList.remove('hide-public');
            element.classList.add('public-network-detected');
        });

        // Hide corporate navigation items and show public ones  
        hideCorporateNavigationItems();
        showPublicNavigationItems();
        removeSession10Navigation();

        console.log('📋 Public mode: public content visible');
        

        // Update any dynamic text content
        updateNetworkSpecificContent(false);
        
        // Update network status indicator
        updateNetworkStatusIndicator('public');
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
        // Only show indicator on Setup & Environment pages
        const currentPath = window.location.pathname;
        const isSetupPage = currentPath.includes('00_intro') || 
                           currentPath.includes('setup') || 
                           currentPath.includes('environment') ||
                           currentPath.includes('coder') ||
                           currentPath.includes('llmapi');
        
        // Remove any existing status indicator
        const existingIndicator = document.querySelector('.network-status-indicator');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Don't show indicator if not on setup pages
        if (!isSetupPage) {
            return;
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

        // Remove manual override clickability to prevent switching to corporate network
        // This was causing unwanted CN switching when viewing publicly
        indicator.style.cursor = 'default';
        indicator.title = networkType === 'corporate' ? 
            'BMW Corporate Network - Cloud Development Environment Available' : 
            'Public Network - Local Setup Required';

        document.body.appendChild(indicator);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (indicator && indicator.parentNode) {
                indicator.style.transition = 'opacity 0.5s ease';
                indicator.style.opacity = '0';
                setTimeout(() => {
                    if (indicator && indicator.parentNode) {
                        indicator.remove();
                    }
                }, 500);
            }
        }, 5000);
    }

    function initializeNetworkDetection() {
        // Add CSS for smooth transitions and ensure BMW content is hidden by default on public sites
        const style = document.createElement('style');
        const hostname = window.location.hostname;
        const isPublicSite = hostname.includes('github.io') || hostname.includes('fwornle');
        
        style.textContent = `
            /* Default: hide all conditional content until detection completes */
            .bmw-corporate-only {
                display: none;
                transition: opacity 0.3s ease-in-out;
            }
            .bmw-public-alternative {
                display: none;
                transition: opacity 0.3s ease-in-out;
            }
            /* Show corporate content when detected */
            .bmw-corporate-only.corporate-network-detected {
                display: block;
                animation: fadeIn 0.5s ease-in-out;
            }
            /* Show public content when detected */
            .bmw-public-alternative.public-network-detected {
                display: block;
                animation: fadeIn 0.5s ease-in-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            /* Ensure setup instructions container is visible */
            .setup-instructions {
                min-height: 100px;
            }
        `;
        document.head.appendChild(style);

        // Always run CN detection regardless of hostname
        console.log('Running corporate network detection...');
        
        // Initial quick check, then run full detection
        if (isCorporateNetwork()) {
            console.log('Corporate network detected initially');
            showCorporateContent();
        } else {
            console.log('Public network assumed initially, running full CN detection');
            hideCorporateContent();
            // Always run the comprehensive check for CN access
            checkInternalService();
        }
    }

    // Initialize when DOM is ready and on every page load
    function runDetection() {
        // Reset detection state for fresh detection on each page
        console.log('🔄 Starting fresh network detection...');
        initializeNetworkDetection();
    }
    
    // Initial run
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runDetection);
    } else {
        runDetection();
    }
    
    // Set up navigation listeners immediately (not waiting for DOMContentLoaded)
    console.log('🎯 Setting up navigation listeners');
    
    // Watch for URL changes with MutationObserver
    let lastUrl = location.href;
    const observer = new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            console.log('📍 URL changed to:', url);
            setTimeout(runDetection, 100);
        }
    });
    observer.observe(document.body || document.documentElement, {
        subtree: true, 
        childList: true
    });
    
    // Listen for navigation link clicks (use capturing to catch all clicks)
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link) {
            const href = link.getAttribute('href');
            console.log('🔗 Link clicked:', href);
            if (link.classList.contains('md-nav__link') || 
                link.classList.contains('md-tabs__link') ||
                href?.includes('/00_intro/')) {
                console.log('🔗 Navigation link detected, will re-run detection');
                setTimeout(runDetection, 500);
            }
        }
    }, true); // Use capture phase
    
    // Also listen for popstate
    window.addEventListener('popstate', () => {
        console.log('⬅️ Browser navigation detected');
        runDetection();
    });

    // Navigation control functions
    function hideCorporateNavigationItems() {
        const navigationItems = document.querySelectorAll('.md-nav__link');
        navigationItems.forEach(link => {
            const linkText = link.textContent.trim();
            // Hide items that contain corporate/BMW content indicators
            if (linkText.includes('BMW Gaia LLM API') || 
                linkText.includes('BMW Cloud Development Environment with Coder') ||
                linkText.includes('Quick Setup') ||
                linkText.includes('Testing Your Connection') ||
                linkText.includes('Available Models') ||
                linkText.includes('Using in Code') ||
                linkText.includes('Framework Integration') ||
                linkText.includes('Why Cloud Development?') ||
                linkText.includes('AI Assistant Integration')) {
                const listItem = link.closest('.md-nav__item');
                if (listItem) {
                    console.log('Hiding corporate nav item:', linkText);
                    listItem.style.display = 'none';
                }
            }
        });
    }

    function showCorporateNavigationItems() {
        const navigationItems = document.querySelectorAll('.md-nav__link');
        navigationItems.forEach(link => {
            const linkText = link.textContent.trim();
            // Show items that contain corporate/BMW content indicators
            if (linkText.includes('BMW Gaia LLM API') || 
                linkText.includes('BMW Cloud Development Environment with Coder') ||
                linkText.includes('Quick Setup') ||
                linkText.includes('Testing Your Connection') ||
                linkText.includes('Available Models') ||
                linkText.includes('Using in Code') ||
                linkText.includes('Framework Integration') ||
                linkText.includes('Why Cloud Development?') ||
                linkText.includes('AI Assistant Integration')) {
                const listItem = link.closest('.md-nav__item');
                if (listItem) {
                    console.log('Showing corporate nav item:', linkText);
                    listItem.style.display = '';
                }
            }
        });
        
        // Add Session 10 to Module 03 navigation when in corporate mode
        addSession10Navigation();
    }

    function addSession10Navigation() {
        // Find Session 9 in Module 03 navigation and add Session 10 after it
        const session9Link = document.querySelector('a[href*="Session9_Production_Agent_Deployment"]');
        if (session9Link) {
            const session9Item = session9Link.closest('.md-nav__item');
            if (session9Item && !document.querySelector('.bmw-corporate-nav-item')) {
                console.log('🔧 Adding Session 10 to corporate navigation');
                
                // Create Session 10 navigation item
                const session10Item = document.createElement('li');
                session10Item.className = 'md-nav__item bmw-corporate-nav-item';
                
                const session10Link = document.createElement('a');
                session10Link.href = '#session10-corporate-only';
                session10Link.className = 'md-nav__link bmw-corporate-link';
                session10Link.textContent = 'Session 10 - Enterprise Integration';
                
                // Add click handler to load corporate content
                session10Link.addEventListener('click', (e) => {
                    e.preventDefault();
                    loadCorporateSession10();
                });
                
                session10Item.appendChild(session10Link);
                
                // Insert after Session 9
                session9Item.parentNode.insertBefore(session10Item, session9Item.nextSibling);
                
                console.log('✅ Session 10 added to corporate navigation');
            }
        }
        
        // Also update the "Next" link on Session 9 to point to Session 10
        updateSession9NextLink();
    }

    function updateSession9NextLink() {
        // Find "Next" navigation links and update Session 9 to point to Session 10
        const nextLinks = document.querySelectorAll('.md-footer__link--next');
        nextLinks.forEach(link => {
            if (window.location.pathname.includes('Session9_Production_Agent_Deployment')) {
                const titleDiv = link.querySelector('.md-ellipsis');
                if (titleDiv) {
                    titleDiv.textContent = 'Session 10 - Enterprise Integration';
                    link.href = '#session10-corporate-only';
                    
                    // Add click handler for corporate Session 10
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        loadCorporateSession10();
                    });
                    
                    console.log('🔧 Updated Session 9 next link to point to Session 10');
                }
            }
        });
    }

    function loadCorporateSession10() {
        console.log('🔐 Loading corporate Session 10 content...');
        
        if (window.CorporateContentLoader && window.CorporateContentLoader.loadedContent) {
            const session10Content = window.CorporateContentLoader.loadedContent['03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'];
            if (session10Content) {
                console.log('📄 Found Session 10 content, replacing page...');
                
                // Update page title
                document.title = 'Session 10: Enterprise Integration & Production Deployment | Agentic AI Nano-Degree';
                
                // Update URL without causing page reload
                if (history.pushState) {
                    const newUrl = window.location.pathname.replace(/[^/]*$/, 'Session10_Enterprise_Integration_Production_Deployment/');
                    history.pushState({page: 'session10'}, '', newUrl);
                }
                
                // Replace page content
                window.CorporateContentLoader.replacePageContent(session10Content);
                
                console.log('✅ Session 10 corporate content loaded successfully');
            } else {
                console.error('❌ Session 10 content not found in encrypted data');
            }
        } else {
            console.error('❌ Corporate content loader not available');
            console.log('Debug info:', {
                'CorporateContentLoader exists': !!window.CorporateContentLoader,
                'loadedContent exists': !!(window.CorporateContentLoader && window.CorporateContentLoader.loadedContent),
                'Content keys': window.CorporateContentLoader && window.CorporateContentLoader.loadedContent ? Object.keys(window.CorporateContentLoader.loadedContent) : 'None'
            });
        }
    }

    function hidePublicNavigationItems() {
        const navigationItems = document.querySelectorAll('.md-nav__link');
        navigationItems.forEach(link => {
            const linkText = link.textContent.trim();
            // Hide items that contain public/local content indicators (but NOT main nav items)
            if (linkText.includes('Public LLM API Configuration') || 
                linkText.includes('Local Development Environment Setup') ||
                linkText.includes('Local Setup Requirements') ||
                linkText.includes('Setup Steps') ||
                linkText.includes('OpenAI Setup') ||
                linkText.includes('Anthropic Claude Setup') ||
                linkText.includes('Testing Your Setup') ||
                linkText.includes('Local LLM Options')) {
                const listItem = link.closest('.md-nav__item');
                if (listItem) {
                    console.log('Hiding public nav item:', linkText);
                    listItem.style.display = 'none';
                }
            }
        });
    }

    function removeSession10Navigation() {
        // Remove Session 10 from navigation when in public mode
        const session10Links = document.querySelectorAll('a[href*="Session10_Enterprise_Integration"]');
        session10Links.forEach(link => {
            const listItem = link.closest('.md-nav__item');
            if (listItem && listItem.classList.contains('bmw-corporate-nav-item')) {
                console.log('🗑️ Removing Session 10 from public navigation');
                listItem.remove();
            }
        });
        
        // Update Session 9 next link to not point to Session 10
        const nextLinks = document.querySelectorAll('.md-footer__link--next');
        nextLinks.forEach(link => {
            if (window.location.pathname.includes('Session9_Production_Agent_Deployment')) {
                // Remove the next link entirely for Session 9 in public mode
                const titleDiv = link.querySelector('.md-ellipsis');
                if (titleDiv && titleDiv.textContent.includes('Session 10')) {
                    console.log('🗑️ Removing Session 9 next link to Session 10 in public mode');
                    link.style.display = 'none';
                }
            }
        });
    }

    function showPublicNavigationItems() {
        const navigationItems = document.querySelectorAll('.md-nav__link');
        navigationItems.forEach(link => {
            const linkText = link.textContent.trim();
            // Show items that contain public/local content indicators (but NOT main nav items)
            if (linkText.includes('Public LLM API Configuration') || 
                linkText.includes('Local Development Environment Setup') ||
                linkText.includes('Local Setup Requirements') ||
                linkText.includes('Setup Steps') ||
                linkText.includes('OpenAI Setup') ||
                linkText.includes('Anthropic Claude Setup') ||
                linkText.includes('Testing Your Setup') ||
                linkText.includes('Local LLM Options')) {
                const listItem = link.closest('.md-nav__item');
                if (listItem) {
                    console.log('Showing public nav item:', linkText);
                    listItem.style.display = '';
                }
            }
        });
    }

    // REMOVED: MutationObserver navigation interference
    // Let MkDocs handle navigation structure completely
    // Content visibility is handled by CSS classes only

})();