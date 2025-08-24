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
        const userAgent = navigator.userAgent;
        
        // Corporate network indicators
        const corporateIndicators = [
            // Internal IP ranges (adjust as needed)
            /^10\./,
            /^192\.168\./,
            /^172\.(1[6-9]|2[0-9]|3[01])\./,
            // BMW-specific domains
            /bmw\.com$/,
            /bmwgroup\.com$/,
            // Local development (for testing)
            /localhost/,
            /127\.0\.0\.1/
        ];

        // Check hostname against corporate patterns
        for (const pattern of corporateIndicators) {
            if (pattern.test(hostname) || pattern.test(window.location.host)) {
                return true;
            }
        }

        // Additional check: try to reach BMW internal service
        // This is a non-blocking check that won't delay page load
        checkInternalService();
        
        return false;
    }

    function checkInternalService() {
        // Attempt to reach BMW internal service (non-blocking)
        const img = new Image();
        img.onload = function() {
            // If image loads, we're likely on corporate network
            showCorporateContent();
        };
        img.onerror = function() {
            // If image fails, we're likely on public network
            hideCorporateContent();
        };
        // Use a small internal resource that exists only on corporate network
        img.src = 'http://10.21.202.14/favicon.ico?' + Date.now();
    }

    function showCorporateContent() {
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(element => {
            element.style.display = '';
            element.classList.add('corporate-network-detected');
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(element => {
            element.style.display = 'none';
        });

        // Update any dynamic text content
        updateNetworkSpecificContent(true);
    }

    function hideCorporateContent() {
        const corporateElements = document.querySelectorAll('.bmw-corporate-only');
        corporateElements.forEach(element => {
            element.style.display = 'none';
        });

        const publicElements = document.querySelectorAll('.bmw-public-alternative');
        publicElements.forEach(element => {
            element.style.display = '';
            element.classList.add('public-network-detected');
        });

        // Update any dynamic text content
        updateNetworkSpecificContent(false);
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
        // Initial check
        if (isCorporateNetwork()) {
            showCorporateContent();
        } else {
            hideCorporateContent();
        }

        // Add CSS for smooth transitions
        const style = document.createElement('style');
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
        `;
        document.head.appendChild(style);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeNetworkDetection);
    } else {
        initializeNetworkDetection();
    }

})();