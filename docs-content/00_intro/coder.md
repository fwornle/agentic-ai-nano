# Development Environment Setup

<div id="loading-message">
<p>🔄 Detecting your network environment and loading appropriate setup instructions...</p>
</div>

<div id="setup-content">
<!-- Content will be loaded here by JavaScript -->
</div>

<script>
(function() {
    'use strict';
    
    function detectNetwork() {
        const hostname = window.location.hostname;
        console.log('Detecting network for hostname:', hostname);
        
        // Check for corporate network indicators
        const corporatePatterns = [
            /^10\./,
            /^192\.168\./,
            /^172\.(1[6-9]|2[0-9]|3[01])\./,
            /bmw\.com$/,
            /bmwgroup\.com$/
        ];
        
        // Check hostname for corporate patterns
        for (const pattern of corporatePatterns) {
            if (pattern.test(hostname)) {
                console.log('Corporate network detected via hostname');
                return Promise.resolve(true);
            }
        }
        
        // GitHub Pages should always be public
        if (hostname.includes('github.io') || hostname.includes('fwornle')) {
            console.log('GitHub Pages detected - using public mode');
            return Promise.resolve(false);
        }
        
        // Localhost defaults to corporate for testing
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            console.log('Localhost detected - using corporate mode for testing');
            return Promise.resolve(true);
        }
        
        // Check if we can reach BMW internal service
        return checkInternalService();
    }
    
    function checkInternalService() {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                console.log('BMW internal service reachable - corporate network');
                resolve(true);
            };
            img.onerror = () => {
                console.log('BMW internal service not reachable - public network');
                resolve(false);
            };
            img.src = 'http://10.21.202.14/favicon.ico?' + Date.now();
            
            // Timeout after 2 seconds
            setTimeout(() => {
                console.log('Service check timeout - assuming public network');
                resolve(false);
            }, 2000);
        });
    }
    
    async function loadContent() {
        try {
            const isCorporate = await detectNetwork();
            const targetFile = isCorporate ? 'coder-bmw/' : 'coder-public/';
            
            console.log('Redirecting to:', targetFile);
            
            // Hide loading message
            document.getElementById('loading-message').style.display = 'none';
            
            // Redirect to the appropriate page
            window.location.href = targetFile;
        } catch (error) {
            console.error('Network detection error:', error);
            // Default to public on error
            window.location.href = 'coder-public/';
        }
    }
    
    // Start detection when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadContent);
    } else {
        loadContent();
    }
})();
</script>