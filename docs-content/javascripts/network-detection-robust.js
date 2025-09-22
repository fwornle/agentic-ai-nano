/**
 * Robust Network Detection for Corporate Content
 * Fixes: false positives, race conditions, caching issues, flaky detection
 */

(function() {
    'use strict';
    
    // CONFIGURATION: Corporate content pages
    const CORPORATE_CONTENT_PAGES = {
        '/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/': {
            enabled: true,
            contentFile: '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'
        },
        '/03_mcp-acp-a2a/Session9_Production_Agent_Deployment/': {
            enabled: true,
            contentFile: '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md'
        },
        '/00_intro/coder/': {
            enabled: true,
            contentFile: '00_intro/coder-concise.md',
            fallbackFile: '00_intro/coder-detailed.md'  // Fallback if concise missing
        },
        '/00_intro/llmapi/': {
            enabled: true,
            contentFile: '00_intro/llmapi-detailed.md'
        }
    };
    
    // Detection state management
    let detectionState = {
        inProgress: false,
        completed: false,
        result: false,
        timestamp: 0,
        detectionId: null
    };
    
    // Session storage key for detection results
    const DETECTION_CACHE_KEY = 'cnDetectionResult';
    const DETECTION_TIMESTAMP_KEY = 'cnDetectionTimestamp';
    const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
    
    // Check if current page needs corporate content
    function isPageConfiguredForCorporateContent() {
        const currentPath = window.location.pathname;
        console.log('🔍 Checking CN page configuration for:', currentPath);
        
        for (const [path, config] of Object.entries(CORPORATE_CONTENT_PAGES)) {
            if (config.enabled && currentPath.includes(path)) {
                console.log('✅ Corporate content page detected:', path);
                return true;
            }
        }
        
        console.log('📄 Regular page - no CN content needed');
        return false;
    }
    
    // Early exit for non-corporate pages
    if (!isPageConfiguredForCorporateContent()) {
        console.log('🚫 Not a corporate content page - CN detection disabled');
        return;
    }
    
    console.log('🏢 Corporate content page - initializing robust CN detection');
    
    // Global variable for CN status
    window.isCorporateNetworkDetected = false;
    
    // Enhanced CN detection with multiple validation methods
    async function detectCorporateNetwork() {
        const detectionId = Date.now().toString();
        detectionState.detectionId = detectionId;
        
        console.log(`🔍 Starting robust CN detection [${detectionId}]`);
        
        // Method 1: Check for cached result first
        const cachedResult = checkCachedDetection();
        if (cachedResult !== null) {
            console.log('💾 Using cached CN detection result:', cachedResult);
            return cachedResult;
        }
        
        // Method 2: Quick hostname check
        const hostnameResult = checkHostnameIndicators();
        if (hostnameResult !== null) {
            console.log('🏠 CN detected via hostname:', hostnameResult);
            setCachedDetection(hostnameResult);
            return hostnameResult;
        }
        
        // Method 3: Enhanced IP detection with validation
        try {
            const ipResult = await checkCorporateIP();
            if (ipResult !== null) {
                console.log('🌐 CN detected via IP validation:', ipResult);
                setCachedDetection(ipResult);
                return ipResult;
            }
        } catch (error) {
            console.log('⚠️ IP detection failed:', error.message);
        }
        
        // Method 4: Internal service connectivity test
        try {
            const serviceResult = await checkInternalServices();
            console.log('🔗 CN detected via service check:', serviceResult);
            setCachedDetection(serviceResult);
            return serviceResult;
        } catch (error) {
            console.log('❌ Service check failed:', error.message);
            setCachedDetection(false);
            return false;
        }
    }
    
    // Check cached detection result
    function checkCachedDetection() {
        try {
            const timestamp = sessionStorage.getItem(DETECTION_TIMESTAMP_KEY);
            const result = sessionStorage.getItem(DETECTION_CACHE_KEY);
            
            if (timestamp && result !== null) {
                const age = Date.now() - parseInt(timestamp);
                if (age < CACHE_DURATION) {
                    return result === 'true';
                } else {
                    console.log('⏰ Cached result expired, running fresh detection');
                    sessionStorage.removeItem(DETECTION_CACHE_KEY);
                    sessionStorage.removeItem(DETECTION_TIMESTAMP_KEY);
                }
            }
        } catch (error) {
            console.log('📋 No cached detection result available');
        }
        return null;
    }
    
    // Cache detection result
    function setCachedDetection(result) {
        try {
            sessionStorage.setItem(DETECTION_CACHE_KEY, result.toString());
            sessionStorage.setItem(DETECTION_TIMESTAMP_KEY, Date.now().toString());
        } catch (error) {
            console.warn('⚠️ Failed to cache detection result:', error);
        }
    }
    
    // Check hostname for corporate indicators
    function checkHostnameIndicators() {
        const hostname = window.location.hostname;
        
        // Definitive corporate hostnames
        const corporateHosts = [
            /\.bmw\.com$/,
            /\.bmwgroup\.com$/,
            /\.bmw-internal\.com$/,
            /^bmw-/,
            /^contenthub\.bmwgroup/
        ];
        
        // GitHub Pages or localhost - not corporate
        if (hostname.includes('github.io') || hostname === 'localhost' || hostname === '127.0.0.1') {
            return null; // Continue with other detection methods
        }
        
        // Check corporate patterns
        for (const pattern of corporateHosts) {
            if (pattern.test(hostname)) {
                return true;
            }
        }
        
        return null; // Continue with other methods
    }
    
    // Enhanced corporate IP detection with validation
    async function checkCorporateIP() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('IP detection timeout'));
            }, 3000);
            
            fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(data => {
                    clearTimeout(timeout);
                    
                    const ip = data.ip;
                    console.log('🌐 External IP detected:', ip);
                    
                    // More conservative BMW corporate IP patterns
                    // Only include verified corporate ranges
                    const corporateIPPatterns = [
                        /^194\.114\./,      // BMW verified public range
                        /^195\.34\./,       // BMW verified public range  
                        /^212\.204\./,      // BMW verified public range
                        /^10\./,            // Internal network
                        /^172\.(1[6-9]|2[0-9]|3[01])\./,  // Private range
                        /^192\.168\./       // Private range
                    ];
                    
                    // REMOVED: /^160\.46\./ - this was causing false positives
                    // The 160.46.252.60 IP appears to be external, not BMW corporate
                    
                    for (const pattern of corporateIPPatterns) {
                        if (pattern.test(ip)) {
                            console.log(`✅ IP ${ip} matches verified corporate pattern: ${pattern}`);
                            // Additional validation: check if IP is actually reachable from corporate network
                            return validateCorporateIPAccess(ip).then(valid => {
                                resolve(valid ? true : null);
                            });
                        }
                    }
                    
                    console.log(`📍 IP ${ip} not in verified corporate ranges`);
                    resolve(null);
                })
                .catch(error => {
                    clearTimeout(timeout);
                    reject(error);
                });
        });
    }
    
    // Validate that IP actually has corporate network access
    async function validateCorporateIPAccess(ip) {
        try {
            // Quick test of corporate service reachability
            const response = await fetch('https://contenthub.bmwgroup.net/favicon.ico', {
                method: 'HEAD',
                mode: 'no-cors',
                cache: 'no-cache'
            });
            return true; // If we can reach corporate services, IP validation confirmed
        } catch (error) {
            console.log(`⚠️ IP ${ip} cannot reach corporate services`);
            return false;
        }
    }
    
    // Test internal service connectivity
    async function checkInternalServices() {
        const services = [
            'https://contenthub.bmwgroup.net/favicon.ico',
            'https://api.bmw.com/favicon.ico'
        ];
        
        for (const service of services) {
            try {
                console.log(`🔗 Testing corporate service: ${service}`);
                
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => reject(new Error('timeout')), 2000);
                    
                    const img = new Image();
                    img.onload = () => {
                        clearTimeout(timeout);
                        resolve();
                    };
                    img.onerror = () => {
                        clearTimeout(timeout);
                        reject(new Error('service unreachable'));
                    };
                    
                    img.src = service + '?' + Date.now();
                });
                
                console.log(`✅ Corporate service reachable: ${service}`);
                return true;
            } catch (error) {
                console.log(`❌ Corporate service failed: ${service} - ${error.message}`);
            }
        }
        
        return false;
    }
    
    // Apply CN detection result
    async function applyCNResult(isCorporate) {
        window.isCorporateNetworkDetected = isCorporate;
        
        if (isCorporate) {
            console.log('🏢 Corporate network confirmed - enabling CN content');
            
            // Show corporate content
            showCorporateContent();
            
            // Load encrypted corporate content if available
            if (window.CorporateContentLoader && window.CorporateContentLoader.isCorporateContentNeeded()) {
                try {
                    const loaded = await window.CorporateContentLoader.load();
                    if (loaded) {
                        console.log('✅ Corporate content loaded successfully');
                    } else {
                        console.log('📋 Corporate content not needed for current page');
                    }
                } catch (error) {
                    console.warn('⚠️ Corporate content loading failed:', error.message);
                    
                    // Handle missing coder-concise.md gracefully
                    if (error.message.includes('coder-concise.md')) {
                        console.log('🔄 Falling back to detailed coder content');
                        // This will be handled by the CorporateContentLoader fallback logic
                    }
                }
            }
        } else {
            console.log('🌐 Public network detected - showing public content');
            showPublicContent();
        }
    }
    
    // Show corporate content
    function showCorporateContent() {
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(el => {
            el.classList.add('show-corporate');
            el.classList.add('corporate-network-detected');
        });
        
        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(el => el.classList.add('hide-public'));
        
        hidePublicNavigationItems();
        showCorporateNavigationItems();
    }
    
    // Show public content
    function showPublicContent() {
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(el => {
            el.classList.remove('show-corporate');
            el.classList.remove('corporate-network-detected');
        });
        
        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(el => el.classList.remove('hide-public'));
        
        showPublicNavigationItems();
        hideCorporateNavigationItems();
    }
    
    // Navigation management functions
    function hidePublicNavigationItems() {
        document.querySelectorAll('.md-nav__item').forEach(item => {
            const link = item.querySelector('.md-nav__link');
            if (link && isPublicNavigationItem(link.textContent)) {
                item.style.display = 'none';
                console.log('🏢 Hiding public nav item:', link.textContent);
            }
        });
    }
    
    function showPublicNavigationItems() {
        document.querySelectorAll('.md-nav__item').forEach(item => {
            const link = item.querySelector('.md-nav__link');
            if (link && isPublicNavigationItem(link.textContent)) {
                item.style.display = '';
                console.log('🌐 Showing public nav item:', link.textContent);
            }
        });
    }
    
    function showCorporateNavigationItems() {
        // Implementation for showing corporate nav items
    }
    
    function hideCorporateNavigationItems() {
        // Implementation for hiding corporate nav items
    }
    
    function isPublicNavigationItem(text) {
        const publicItems = [
            'Local Development Environment Setup',
            'Setup Steps',
            'Testing Your Setup',
            'Local LLM Options'
        ];
        return publicItems.some(item => text.includes(item));
    }
    
    // Main detection execution with proper synchronization
    async function runRobustDetection() {
        // Prevent concurrent executions
        if (detectionState.inProgress) {
            console.log('🔄 Detection already in progress, waiting...');
            
            // Wait for current detection to complete
            while (detectionState.inProgress) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            console.log('✅ Using result from concurrent detection:', detectionState.result);
            return detectionState.result;
        }
        
        // Check if we have a recent result
        if (detectionState.completed && (Date.now() - detectionState.timestamp) < CACHE_DURATION) {
            console.log('📋 Using recent detection result:', detectionState.result);
            return detectionState.result;
        }
        
        detectionState.inProgress = true;
        
        try {
            console.log('🚀 Starting robust corporate network detection');
            
            const result = await detectCorporateNetwork();
            
            detectionState.result = result;
            detectionState.completed = true;
            detectionState.timestamp = Date.now();
            
            await applyCNResult(result);
            
            console.log('✅ Robust CN detection complete:', result);
            return result;
        } catch (error) {
            console.error('❌ Robust CN detection failed:', error);
            
            // Force page reload on persistent failures to clear cache
            if (window.location.search.includes('cn-reload')) {
                console.log('🔄 Second reload attempt failed, using public mode');
                await applyCNResult(false);
                return false;
            } else {
                console.log('🔄 Detection failed, forcing page reload to clear cache');
                const url = new URL(window.location);
                url.searchParams.set('cn-reload', '1');
                window.location.href = url.toString();
                return false;
            }
        } finally {
            detectionState.inProgress = false;
        }
    }
    
    // Initialize detection on page load
    function initializeDetection() {
        console.log('🎯 Initializing robust CN detection for corporate page');
        
        // Clear any stale reload parameters
        if (window.location.search.includes('cn-reload')) {
            const url = new URL(window.location);
            url.searchParams.delete('cn-reload');
            window.history.replaceState({}, '', url.toString());
        }
        
        // Run detection
        runRobustDetection();
    }
    
    // Set up page load detection
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDetection);
    } else {
        // Page already loaded, run immediately
        setTimeout(initializeDetection, 100);
    }
    
    // Set up navigation detection
    let lastUrl = location.href;
    const urlObserver = new MutationObserver(() => {
        const currentUrl = location.href;
        if (currentUrl !== lastUrl) {
            lastUrl = currentUrl;
            console.log('📍 URL changed, checking if CN detection needed');
            
            // Only run detection if we're still on a corporate content page
            if (isPageConfiguredForCorporateContent()) {
                console.log('🔄 Running CN detection for new page');
                setTimeout(runRobustDetection, 200);
            }
        }
    });
    
    urlObserver.observe(document.body || document.documentElement, {
        subtree: true,
        childList: true
    });
    
    // Listen for navigation events
    window.addEventListener('popstate', () => {
        console.log('⬅️ Browser navigation detected');
        if (isPageConfiguredForCorporateContent()) {
            setTimeout(runRobustDetection, 200);
        }
    });
    
    console.log('🛡️ Robust CN detection system initialized');
})();