/**
 * Network Detection and Conditional Content Display
 * Shows BMW-specific content only when accessed from corporate network
 * Updated: Removed all manual corporate mode switching capabilities
 */

(function() {
    'use strict';
    
    // CONFIGURATION: Define which pages get corporate content treatment
    const CORPORATE_CONTENT_PAGES = {
        // Session 10 page - FIXED: Correct path!
        '/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/': {
            enabled: true,
            hashTriggers: ['session10-corporate-only', 'session10-corporate-content'],
            contentFile: '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'
        },
        // Session 9 page - for navigation triggers
        '/03_mcp-acp-a2a/Session9_Production_Agent_Deployment/': {
            enabled: true,
            hashTriggers: ['session10-corporate-only', 'session10-corporate-content'],
            contentFile: '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'
        },
        // Coder setup page  
        '/00_intro/coder/': {
            enabled: true,
            hashTriggers: [],
            contentFile: '00_intro/coder-detailed.md'
        },
        // LLM API setup page
        '/00_intro/llmapi/': {
            enabled: true,
            hashTriggers: [],
            contentFile: '00_intro/llmapi-detailed.md'
        }
    };
    
    // Check if current page is configured for corporate content
    function isPageConfiguredForCorporateContent() {
        const currentPath = window.location.pathname;
        const currentHash = window.location.hash;
        
        console.log('🔍 Checking if page is configured for corporate content');
        console.log('🔍 Current path:', currentPath);
        console.log('🔍 Current hash:', currentHash);
        
        for (const [path, config] of Object.entries(CORPORATE_CONTENT_PAGES)) {
            if (!config.enabled) continue;
            
            console.log(`🔍 Checking against configured path: ${path}`);
            
            // Check if current path matches
            if (currentPath.includes(path)) {
                console.log(`✅ Path match found: ${path}`);
                return true;
            }
            
            // Check if hash triggers match
            if (config.hashTriggers && config.hashTriggers.length > 0) {
                for (const trigger of config.hashTriggers) {
                    if (currentHash.includes(trigger)) {
                        console.log(`✅ Hash trigger match found: ${trigger}`);
                        return true;
                    }
                }
            }
        }
        
        console.log('❌ No corporate content configuration found for current page');
        return false;
    }
    
    // Early exit if not on a corporate content page - ZERO interference
    if (!isPageConfiguredForCorporateContent()) {
        console.log('✅ Regular page detected - corporate content system disabled');
        return; // Exit completely - no event listeners, no functions, nothing
    }
    
    console.log('🏢 Corporate content page detected - initializing enhanced navigation');
    
    // Global variable to track corporate network status - MUST be on window object
    window.isCorporateNetworkDetected = false;
    
    // Debounce mechanism to prevent multiple simultaneous detection cycles
    let detectionInProgress = false;
    let detectionTimeout = null;

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
        window.isCorporateNetworkDetected = true;
        
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        console.log(`Found ${corporateElements.length} corporate elements to show`);
        corporateElements.forEach((element) => {
            element.classList.add('show-corporate');
            element.classList.add('corporate-network-detected');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        console.log(`Found ${publicElements.length} public elements to hide`);
        publicElements.forEach((element) => {
            element.classList.add('hide-public');
        });

        // Hide public navigation items and show corporate ones
        hidePublicNavigationItems();
        showCorporateNavigationItems();

        console.log('🏢 Corporate mode: BMW content enabled');
        
        // Only load encrypted corporate content if the current page actually needs it
        if (window.CorporateContentLoader && window.CorporateContentLoader.isCorporateContentNeeded()) {
            try {
                const loaded = await window.CorporateContentLoader.load();
                if (loaded) {
                    console.log('✅ Corporate content decrypted and loaded');
                } else {
                    console.log('📋 Corporate content not needed for current page');
                }
            } catch (error) {
                console.warn('⚠️ Corporate content not available:', error.message);
            }
        } else {
            console.log('📋 Corporate content not needed for current page');
        }

        // Update any dynamic text content
        updateNetworkSpecificContent(true);
        
        // Update network status indicator
        updateNetworkStatusIndicator('corporate');
    }

    function hideCorporateContent() {
        console.log('🌐 Showing public content');
        
        // Clear global flag to allow MutationObserver to hide BMW content
        window.isCorporateNetworkDetected = false;
        
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
        // Session 10 should ALWAYS be visible - it's a static navigation item

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

    function cleanupNavigationState() {
        // Clean up any previous navigation state
        // We're on a corporate page, so just reset for fresh setup
        if (window.corporateScrollListener) {
            window.removeEventListener('scroll', window.corporateScrollListener);
            window.corporateScrollListener = null;
            console.log('🧹 Cleaned up previous corporate scroll listener');
        }
    }

    // Initialize when DOM is ready and on every page load
    function runDetection() {
        // Prevent multiple simultaneous detections
        if (detectionInProgress) {
            console.log('🔄 Detection already in progress, skipping...');
            return;
        }
        
        // Clear any pending detection
        if (detectionTimeout) {
            clearTimeout(detectionTimeout);
        }
        
        // Aggressive debounce to prevent rapid successive calls from different event sources
        detectionTimeout = setTimeout(() => {
            // Double-check as detection might have been triggered by another source
            if (detectionInProgress) {
                console.log('🔄 Detection started by another trigger, skipping...');
                return;
            }
            
            detectionInProgress = true;
            console.log('🔄 Starting fresh network detection...');
            
            // Clean up navigation state first
            cleanupNavigationState();
            
            try {
                initializeNetworkDetection();
            } finally {
                // Reset detection flag after longer delay to prevent rapid re-runs
                setTimeout(() => {
                    detectionInProgress = false;
                    console.log('✅ Network detection cycle complete, ready for next run');
                }, 5000); // Increased from 2000 to 5000ms
            }
        }, 300); // Increased from 100 to 300ms debounce delay
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
            
            // Reset Session 10 loaded flag when navigating to different pages
            if (!url.includes('session10-corporate') && !url.includes('Session10_Enterprise_Integration')) {
                session10Loaded = false;
            }
            
            // No cleanup needed - if we navigate away, the page will reload
            // and our early exit will prevent this code from running
            
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
        
        // Reset Session 10 loaded flag when navigating back/forward
        const url = location.href;
        if (!url.includes('session10-corporate') && !url.includes('Session10_Enterprise_Integration')) {
            session10Loaded = false;
        }
        
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
        
        // Session 10 should already be in static navigation from mkdocs.yml
    }

    function addSession10Navigation() {
        // Find Session 9 in Module 03 navigation and add Session 10 after it
        const session9Link = document.querySelector('a[href*="Session9_Production_Agent_Deployment"]');
        if (session9Link) {
            const session9Item = session9Link.closest('.md-nav__item');
            
            // Check for ANY existing Session 10 navigation items - not just corporate ones
            const existingSession10 = document.querySelector('a[href*="session10"], a[href*="Session10"], .bmw-corporate-nav-item, a[href*="Enterprise_Integration"]');
            
            if (session9Item && !existingSession10) {
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
            } else if (existingSession10) {
                console.log('📄 Session 10 navigation already exists, skipping creation');
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

    // Track if Session 10 content is currently loaded to prevent multiple loads
    let session10Loaded = false;
    
    window.loadCorporateSession10 = async function() {
        console.log('🔐 Loading corporate Session 10 content...');
        
        // Prevent multiple loads of Session 10 content
        if (session10Loaded) {
            console.log('📄 Session 10 already loaded, skipping...');
            return true;
        }
        
        // Retry mechanism for improved reliability
        const maxRetries = 3;
        let retryCount = 0;
        
        while (retryCount < maxRetries) {
            try {
                console.log(`🔄 Attempt ${retryCount + 1}/${maxRetries} to load Session 10...`);
                
                // Check if corporate content loader exists
                if (!window.CorporateContentLoader) {
                    console.warn('⚠️ Corporate content loader not available, waiting...');
                    await new Promise(resolve => setTimeout(resolve, 500));
                    retryCount++;
                    continue;
                }
                
                // If content is not loaded yet, try to load it first
                if (!window.CorporateContentLoader.loadedContent) {
                    console.log('📥 Corporate content not loaded yet, loading now...');
                    const loaded = await window.CorporateContentLoader.load();
                    if (!loaded) {
                        console.warn('⚠️ Failed to load corporate content, retrying...');
                        retryCount++;
                        await new Promise(resolve => setTimeout(resolve, 1000));
                        continue;
                    }
                    console.log('✅ Corporate content loaded successfully');
                }
                
                // Now check for Session 10 content
                const session10Content = window.CorporateContentLoader.loadedContent['03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'];
                if (session10Content) {
                    console.log('📄 Found Session 10 content, replacing page...');
                    session10Loaded = true;
                    
                    // Update page title
                    document.title = 'Session 10: Enterprise Integration & Production Deployment | Agentic AI Nano-Degree';
                    
                    // Update URL without causing page reload - use hash instead of path to avoid 404s
                    if (history.pushState) {
                        // Use hash-based navigation to avoid creating non-existent paths
                        const baseUrl = window.location.pathname.replace(/#.*$/, '');
                        const newUrl = baseUrl + '#session10-corporate-content';
                        history.pushState({page: 'session10'}, '', newUrl);
                    }
                    
                    // Replace page content
                    await window.CorporateContentLoader.replacePageContent(session10Content);
                    
                    // Wait a bit for content to be injected, then update navigation
                    setTimeout(async () => {
                        await updateMkDocsNavigationForCorporateContent(session10Content);
                    }, 100);
                    
                    // Instantly jump to top of the page after content is loaded
                    setTimeout(() => {
                        window.scrollTo(0, 0);
                        console.log('📍 Jumped to top of Session 10 content');
                    }, 200);
                    
                    console.log('✅ Session 10 corporate content loaded successfully');
                    return true;
                    
                } else {
                    console.warn('⚠️ Session 10 content not found in encrypted data, retrying...');
                    console.log('Available content keys:', Object.keys(window.CorporateContentLoader.loadedContent || {}));
                    retryCount++;
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    continue;
                }
                
            } catch (error) {
                console.warn(`⚠️ Error loading Session 10 (attempt ${retryCount + 1}):`, error);
                retryCount++;
                if (retryCount < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }
        }
        
        console.error('❌ Failed to load Session 10 after all retries');
        return false;
    }

    async function updateMkDocsNavigationForCorporateContent(contentMarkdown) {
        console.log('🔧 Updating MkDocs navigation for corporate content...');
        
        // No guard needed - we're already on a corporate content page if this runs
        
        try {
            // Extract metadata from the content itself
            const contentMetadata = extractContentMetadata(contentMarkdown);
            console.log('📄 Detected content metadata:', contentMetadata);
            
            // Wait for MkDocs navigation to be ready (retry mechanism)
            let attempts = 0;
            const maxAttempts = 5;
            let corporateNavItem = null;
            
            while (!corporateNavItem && attempts < maxAttempts) {
                if (attempts > 0) {
                    await new Promise(resolve => setTimeout(resolve, 200 * attempts)); // Progressive delay
                }
                
                // Debug: List all navigation links on first attempt
                if (attempts === 0) {
                    const allNavLinks = document.querySelectorAll('.md-nav__link');
                    console.log('🔍 Debug - All navigation links found:', allNavLinks.length);
                    console.log('🔍 Navigation structure:', Array.from(allNavLinks).slice(0, 10).map(link => ({
                        href: link.getAttribute('href'),
                        text: link.textContent.trim(),
                        active: link.classList.contains('md-nav__link--active')
                    })));
                }
                
                // First try to find current active navigation item
                corporateNavItem = document.querySelector('.md-nav__link--active')?.closest('.md-nav__item');
                
                if (!corporateNavItem) {
                    // Try specific Session 9 patterns
                    const session9Selectors = [
                        'a[href*="Session9_Production_Agent_Deployment"]',
                        'a[href*="Session9"]',
                        'a[href*="Production_Agent_Deployment"]'
                    ];
                    
                    for (const selector of session9Selectors) {
                        corporateNavItem = document.querySelector(selector)?.closest('.md-nav__item');
                        if (corporateNavItem) {
                            console.log(`🎯 Found via selector: ${selector}`);
                            break;
                        }
                    }
                }
                
                if (!corporateNavItem) {
                    // Fallback: try any MCP/ACP section navigation item
                    corporateNavItem = document.querySelector([
                        'a[href*="03_mcp-acp-a2a"]',
                        'a[href*="mcp-acp-a2a"]'
                    ].join(', '))?.closest('.md-nav__item');
                }
                
                attempts++;
                console.log(`🔍 Navigation search attempt ${attempts}/${maxAttempts}, found:`, !!corporateNavItem);
                
                if (corporateNavItem) {
                    const navLink = corporateNavItem.querySelector('.md-nav__link');
                    console.log('🔍 Found navigation item:', {
                        href: navLink?.getAttribute('href'),
                        text: navLink?.textContent?.trim(),
                        outerHTML: corporateNavItem.outerHTML.substring(0, 200) + '...'
                    });
                }
            }
            
            if (corporateNavItem) {
                // Remove active state from all navigation items
                document.querySelectorAll('.md-nav__item').forEach(item => {
                    item.classList.remove('md-nav__item--active');
                    const link = item.querySelector('.md-nav__link');
                    if (link) {
                        link.classList.remove('md-nav__link--active');
                    }
                });
                
                // Activate corporate content navigation item
                corporateNavItem.classList.add('md-nav__item--active');
                const corporateLink = corporateNavItem.querySelector('.md-nav__link');
                if (corporateLink) {
                    corporateLink.classList.add('md-nav__link--active');
                    // Update the link text to match current content
                    if (contentMetadata.title) {
                        corporateLink.textContent = contentMetadata.title;
                    }
                }
                
                // Create corporate content sub-navigation based on content structure
                createCorporateContentSubNavigation(corporateNavItem, contentMetadata);
                
                // Scroll corporate content item into view in sidebar
                corporateNavItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                
                console.log(`✅ MkDocs navigation updated for ${contentMetadata.title || 'corporate content'}`);
            } else {
                console.warn('⚠️ Corporate content navigation item not found');
            }
            
            // Fix potential sidebar styling conflicts
            fixSidebarStylingConflicts();
            
        } catch (error) {
            console.error('❌ Failed to update MkDocs navigation for corporate content:', error);
        }
    }

    function extractContentMetadata(markdownContent) {
        const metadata = {
            title: null,
            sections: [],
            type: 'corporate-content'
        };
        
        if (!markdownContent) return metadata;
        
        // Extract title from first H1
        const titleMatch = markdownContent.match(/^#\s+(.+)$/m);
        if (titleMatch) {
            metadata.title = titleMatch[1].trim();
        }
        
        // Extract sections from H2 and H3 headings
        const headingMatches = markdownContent.match(/^#{2,3}\s+(.+)$/gm);
        if (headingMatches) {
            metadata.sections = headingMatches.map(heading => {
                const level = (heading.match(/#/g) || []).length;
                const title = heading.replace(/^#+\s+/, '').trim();
                const id = title.toLowerCase()
                    .replace(/[^a-z0-9\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .replace(/^-|-$/g, '');
                
                return {
                    level,
                    title,
                    id: id || title.toLowerCase().replace(/\s+/g, '-'),
                    href: `#${id || title.toLowerCase().replace(/\s+/g, '-')}`
                };
            });
        }
        
        // Detect content type from title or content
        if (metadata.title) {
            if (metadata.title.includes('Session')) {
                metadata.type = 'session';
                // Extract session number if present
                const sessionMatch = metadata.title.match(/Session\s*(\d+)/i);
                if (sessionMatch) {
                    metadata.sessionNumber = parseInt(sessionMatch[1]);
                }
            } else if (metadata.title.includes('Enterprise') || metadata.title.includes('Production')) {
                metadata.type = 'enterprise-content';
            }
        }
        
        return metadata;
    }


    function createCorporateContentSubNavigation(navItem, contentMetadata) {
        console.log(`🔧 Creating sub-navigation for ${contentMetadata.title || 'corporate content'}...`);
        
        // Remove any existing sub-navigation to rebuild with current content
        const existingSubNav = navItem.querySelector('.md-nav');
        if (existingSubNav) {
            existingSubNav.remove();
        }
        
        // Debug content metadata
        console.log('🔍 Content metadata for sub-navigation:', contentMetadata);
        console.log('🔍 Available sections:', contentMetadata.sections);
        
        // Only create sub-navigation if we have sections
        if (contentMetadata.sections && contentMetadata.sections.length > 0) {
            // Create sub-navigation structure
            const subNav = document.createElement('nav');
            subNav.className = 'md-nav md-nav--secondary';
            subNav.setAttribute('aria-label', `${contentMetadata.title || 'Corporate Content'} Navigation`);
            
            const subNavList = document.createElement('ul');
            subNavList.className = 'md-nav__list';
            
            // Create navigation items from content sections
            contentMetadata.sections.forEach(section => {
                const listItem = document.createElement('li');
                listItem.className = 'md-nav__item';
                
                const link = document.createElement('a');
                link.href = section.href;
                link.className = 'md-nav__link';
                link.textContent = section.title;
                
                // Add appropriate nesting class for H3 items
                if (section.level === 3) {
                    listItem.classList.add('md-nav__item--nested');
                }
                
                // Add smooth scroll behavior for anchor links
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = section.id;
                    const targetElement = document.getElementById(targetId) || 
                                         document.querySelector(`h${section.level}[id="${targetId}"]`) ||
                                         findHeadingByText(section.title);
                    
                    if (targetElement) {
                        targetElement.scrollIntoView({ behavior: 'smooth' });
                        // Update URL hash
                        history.pushState(null, '', section.href);
                        
                        // Update active state in sub-navigation
                        subNavList.querySelectorAll('.md-nav__link').forEach(l => l.classList.remove('md-nav__link--active'));
                        link.classList.add('md-nav__link--active');
                    }
                });
                
                listItem.appendChild(link);
                subNavList.appendChild(listItem);
            });
            
            subNav.appendChild(subNavList);
            navItem.appendChild(subNav);
            
            console.log(`✅ Sub-navigation created with ${contentMetadata.sections.length} sections`);
            
            // Set up scroll spy for corporate content - we're already on a corporate page
            setupCorporateContentScrollSpy(subNavList, contentMetadata.sections);
        }
        
        // Mark as corporate content for scroll spy detection
        document.body.classList.add('corporate-content-active');
        console.log('🔧 Marked page as corporate content');
        
        // Expand the navigation and ensure visibility
        navItem.classList.add('md-nav__item--nested', 'md-nav__item--active', 'corporate-nav-item');
        
        // Make sure the navigation item is visible and expanded
        const navInput = navItem.querySelector('input[type="checkbox"]');
        if (navInput) {
            navInput.checked = true;
        }
        
        // Add explicit CSS to ensure visibility and prevent removal
        navItem.style.display = 'block !important';
        navItem.setAttribute('data-corporate-nav', 'true');
        const subNav = navItem.querySelector('.md-nav');
        if (subNav) {
            subNav.style.display = 'block !important';
            subNav.style.visibility = 'visible';
            subNav.setAttribute('data-corporate-subnav', 'true');
        }
        
        // Prevent navigation from being hidden by other scripts
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    const target = mutation.target;
                    if (target.hasAttribute('data-corporate-nav') || target.hasAttribute('data-corporate-subnav')) {
                        if (target.style.display === 'none' || target.style.visibility === 'hidden') {
                            console.log('🔧 Preventing corporate navigation from being hidden');
                            target.style.display = 'block';
                            target.style.visibility = 'visible';
                        }
                    }
                }
            });
        });
        
        observer.observe(navItem, { attributes: true, subtree: true });
        if (subNav) {
            observer.observe(subNav, { attributes: true, subtree: true });
        }
        
        console.log('🔧 Navigation item expanded and protected from hiding');
    }

    function findHeadingByText(text) {
        // Helper function to find headings by text content
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        for (const heading of headings) {
            if (heading.textContent.trim().toLowerCase().includes(text.toLowerCase())) {
                return heading;
            }
        }
        return null;
    }

    function setupCorporateContentScrollSpy(navList, sections) {
        console.log('🔍 Setting up scroll spy for corporate content navigation...');
        
        let ticking = false;
        let lastActiveSection = null;
        let scrollSpyActive = false;
        
        function updateActiveNavigation() {
            if (!navList || !sections) return;
            
            // Find which section is currently visible
            let activeSection = null;
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Check each section to find the currently visible one
            for (let i = sections.length - 1; i >= 0; i--) {
                const section = sections[i];
                const targetElement = document.getElementById(section.id) || 
                                   document.querySelector(`h${section.level}[id="${section.id}"]`) ||
                                   findHeadingByText(section.title);
                
                if (targetElement) {
                    const rect = targetElement.getBoundingClientRect();
                    const elementTop = rect.top + scrollTop;
                    
                    // Consider element active if it's within the viewport or just passed
                    if (elementTop <= scrollTop + 100) {
                        activeSection = section;
                        break;
                    }
                }
            }
            
            // Update navigation highlighting if section changed
            if (activeSection && activeSection.id !== lastActiveSection) {
                // ONLY remove active state from corporate sub-navigation links, not main nav
                navList.querySelectorAll('.md-nav__link').forEach(link => {
                    link.classList.remove('md-nav__link--active');
                });
                
                // Add active state to current section's nav link
                const activeLink = navList.querySelector(`a[href="#${activeSection.id}"]`);
                if (activeLink) {
                    activeLink.classList.add('md-nav__link--active');
                    console.log(`🔍 Corporate active section: ${activeSection.title}`);
                }
                
                lastActiveSection = activeSection.id;
            }
            
            ticking = false;
        }
        
        function onScroll() {
            if (!ticking) {
                requestAnimationFrame(updateActiveNavigation);
                ticking = true;
            }
        }
        
        // Clean up any existing scroll listeners for corporate content
        if (window.corporateScrollListener) {
            window.removeEventListener('scroll', window.corporateScrollListener);
        }
        
        // Set up scroll listener for corporate content
        window.corporateScrollListener = onScroll;
        window.addEventListener('scroll', onScroll, { passive: true });
        console.log('✅ Corporate scroll listener activated');
        
        // Initial check
        updateActiveNavigation();
        
        console.log('✅ Corporate content scroll spy setup complete');
    }

    function fixSidebarStylingConflicts() {
        console.log('🔧 Fixing sidebar styling conflicts...');
        
        // Ensure sidebar scrolling works properly
        const sidebar = document.querySelector('.md-sidebar--primary .md-sidebar__scrollwrap');
        if (sidebar) {
            sidebar.style.overflowY = 'auto';
            sidebar.style.height = 'calc(100vh - 2.4rem)';
        }
        
        // Fix potential z-index conflicts
        const sidebarContainer = document.querySelector('.md-sidebar--primary');
        if (sidebarContainer) {
            sidebarContainer.style.zIndex = '3';
        }
        
        // Ensure bottom navigation doesn't overlap
        const bottomNav = document.querySelector('.md-footer');
        if (bottomNav) {
            bottomNav.style.position = 'relative';
            bottomNav.style.zIndex = '1';
        }
        
        // Fix any content overflow issues
        const contentArea = document.querySelector('.md-content');
        if (contentArea) {
            contentArea.style.overflow = 'visible';
        }
        
        console.log('✅ Sidebar styling conflicts fixed');
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
        // Remove ALL Session 10 navigation items when in public mode
        const session10Selectors = [
            'a[href*="Session10_Enterprise_Integration"]',
            'a[href*="session10-corporate"]',
            'a[href*="Enterprise_Integration"]',
            '.bmw-corporate-nav-item',
            'a[href*="session10"]',
            'a[href*="Session10"]'
        ];
        
        session10Selectors.forEach(selector => {
            const session10Links = document.querySelectorAll(selector);
            session10Links.forEach(element => {
                const listItem = element.closest('.md-nav__item');
                if (listItem) {
                    console.log('🗑️ Removing Session 10 navigation item:', element.textContent?.trim() || selector);
                    listItem.remove();
                }
            });
        });
        
        // Reset Session 10 loaded flag when switching to public mode
        session10Loaded = false;
        
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