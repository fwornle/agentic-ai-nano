/**
 * Unified Corporate Network Detection & Content Management System
 * 
 * This replaces the problematic network-detection.js with a robust,
 * event-driven system that eliminates race conditions and provides
 * reliable corporate content loading with visual feedback.
 * 
 * Version: 2025-09-22 - Complete rewrite for reliability
 */

(function() {
    'use strict';
    
    // ===== CONFIGURATION =====
    
    const CORPORATE_PAGES = {
        '/00_intro/coder/': {
            enabled: true,
            primaryContent: '00_intro/coder-concise.md',
            detailedContent: '00_intro/coder-detailed.md',
            detailHash: 'detailed-setup-guide',
            name: 'Coder Setup'
        },
        '/00_intro/llmapi/': {
            enabled: true,
            primaryContent: '00_intro/llmapi-detailed.md',
            name: 'LLM API Setup'
        },
        '/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/': {
            enabled: true,
            primaryContent: '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md',
            name: 'Session 10 - Enterprise Integration'
        }
    };
    
    const BMW_IP_PATTERNS = [
        /^160\.46\./,    // Working BMW IP range
        /^194\.114\./,   // BMW public IP range
        /^195\.34\./,    // BMW public IP range
        /^212\.204\./    // BMW public IP range
    ];
    
    const BMW_INTERNAL_SERVICES = [
        'https://contenthub.bmwgroup.net/favicon.ico'
    ];
    
    // ===== CORPORATE NETWORK MANAGER =====
    
    class CorporateNetworkManager {
        constructor() {
            this.state = {
                isDetecting: false,
                isCorporateNetwork: false,
                contentLoaded: false,
                currentPage: null,
                detectionMethod: null,
                lastDetection: null
            };
            
            this.eventListeners = new Map();
            this.detectionPromise = null;
            this.contentLoader = null;
            
            // Initialize backward compatibility flag for old corporate-content-loader.js
            window.isCorporateNetworkDetected = false;
            
            console.log('🏢 Corporate Network Manager initialized');
        }
        
        // Event system for state changes
        on(eventType, callback) {
            if (!this.eventListeners.has(eventType)) {
                this.eventListeners.set(eventType, []);
            }
            this.eventListeners.get(eventType).push(callback);
        }
        
        off(eventType, callback) {
            if (this.eventListeners.has(eventType)) {
                const callbacks = this.eventListeners.get(eventType);
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        }
        
        emit(eventType, data = {}) {
            console.log(`📡 Emitting event: ${eventType}`, data);
            if (this.eventListeners.has(eventType)) {
                this.eventListeners.get(eventType).forEach(callback => {
                    try {
                        callback(data);
                    } catch (error) {
                        console.error(`Error in event listener for ${eventType}:`, error);
                    }
                });
            }
        }
        
        // Check if current page is a corporate content page
        getCurrentPageConfig() {
            const currentPath = window.location.pathname;
            
            for (const [path, config] of Object.entries(CORPORATE_PAGES)) {
                if (currentPath.includes(path)) {
                    return { path, config };
                }
            }
            return null;
        }
        
        // Main detection method - returns Promise
        async detectCorporateNetwork() {
            // Prevent multiple simultaneous detections
            if (this.detectionPromise) {
                console.log('🔄 Detection already in progress, waiting for result...');
                return this.detectionPromise;
            }
            
            this.detectionPromise = this._performDetection();
            return this.detectionPromise;
        }
        
        async _performDetection() {
            this.state.isDetecting = true;
            this.emit('detection:started');
            
            try {
                console.log('🔍 Starting corporate network detection...');
                
                // Method 1: Check external IP first (fastest for corporate users)
                const ipResult = await this._checkExternalIP();
                if (ipResult.isCorporate) {
                    return this._setDetectionResult(true, `IP: ${ipResult.method}`, ipResult.ip);
                }
                
                // Method 2: Check internal services
                const serviceResult = await this._checkInternalServices();
                if (serviceResult.isCorporate) {
                    return this._setDetectionResult(true, `Service: ${serviceResult.method}`, serviceResult.service);
                }
                
                // All methods failed - public network
                return this._setDetectionResult(false, 'All checks failed', 'public');
                
            } catch (error) {
                console.error('❌ Detection failed with error:', error);
                return this._setDetectionResult(false, 'Error', error.message);
            } finally {
                this.detectionPromise = null;
            }
        }
        
        async _checkExternalIP() {
            try {
                console.log('🌐 Checking external IP...');
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000);
                
                const response = await fetch('https://api.ipify.org?format=json', {
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                
                if (!response.ok) throw new Error(`IP service returned ${response.status}`);
                
                const data = await response.json();
                const ip = data.ip;
                
                console.log(`🌐 External IP: ${ip}`);
                
                for (const pattern of BMW_IP_PATTERNS) {
                    if (pattern.test(ip)) {
                        console.log(`✅ IP ${ip} matches BMW pattern: ${pattern}`);
                        return { isCorporate: true, method: pattern.toString(), ip };
                    }
                }
                
                return { isCorporate: false, method: 'IP check', ip };
                
            } catch (error) {
                console.log('❌ External IP check failed:', error.message);
                return { isCorporate: false, method: 'IP check failed', ip: null };
            }
        }
        
        async _checkInternalServices() {
            console.log('🔍 Checking internal services...');
            
            for (const serviceUrl of BMW_INTERNAL_SERVICES) {
                try {
                    const result = await this._pingService(serviceUrl);
                    if (result.success) {
                        console.log(`✅ Internal service reachable: ${serviceUrl}`);
                        return { isCorporate: true, method: 'Internal service', service: serviceUrl };
                    }
                } catch (error) {
                    console.log(`❌ Service check failed for ${serviceUrl}:`, error.message);
                }
            }
            
            return { isCorporate: false, method: 'Service check', service: null };
        }
        
        _pingService(url) {
            return new Promise((resolve) => {
                const img = new Image();
                const timeout = setTimeout(() => {
                    resolve({ success: false, error: 'Timeout' });
                }, 2000);
                
                img.onload = () => {
                    clearTimeout(timeout);
                    resolve({ success: true });
                };
                
                img.onerror = () => {
                    clearTimeout(timeout);
                    resolve({ success: false, error: 'Connection failed' });
                };
                
                img.src = `${url}?${Date.now()}`;
            });
        }
        
        _setDetectionResult(isCorporate, method, details) {
            const oldState = this.state.isCorporateNetwork;
            
            this.state.isDetecting = false;
            this.state.isCorporateNetwork = isCorporate;
            this.state.detectionMethod = method;
            this.state.lastDetection = new Date();
            
            // Set backward compatibility flag for old corporate-content-loader.js
            window.isCorporateNetworkDetected = isCorporate;
            
            console.log(`🎯 Detection complete: ${isCorporate ? 'CORPORATE' : 'PUBLIC'} (${method})`);
            console.log(`🔄 Set window.isCorporateNetworkDetected = ${isCorporate} for backward compatibility`);
            
            // Emit events
            this.emit('detection:completed', {
                isCorporate,
                method,
                details,
                changed: oldState !== isCorporate
            });
            
            if (oldState !== isCorporate) {
                this.emit('network:changed', {
                    from: oldState,
                    to: isCorporate
                });
            }
            
            return { isCorporate, method, details };
        }
        
        // Get current state
        getState() {
            return { ...this.state };
        }
        
        // Force re-detection (for debugging/manual triggers)
        async forceDetection() {
            this.detectionPromise = null;
            return this.detectCorporateNetwork();
        }
    }
    
    // ===== VISUAL INDICATOR MANAGER =====
    
    class VisualIndicatorManager {
        constructor(networkManager) {
            this.networkManager = networkManager;
            this.currentIndicator = null;
            this.isOnCorporatePage = false;
            
            // Listen to network manager events
            this.networkManager.on('detection:started', () => this.showDetectionIndicator());
            this.networkManager.on('detection:completed', (data) => this.showResultIndicator(data));
            this.networkManager.on('network:changed', (data) => this.showNetworkChangeIndicator(data));
            
            console.log('📊 Visual Indicator Manager initialized');
        }
        
        checkIfCorporatePage() {
            const pageConfig = this.networkManager.getCurrentPageConfig();
            this.isOnCorporatePage = pageConfig !== null;
            return this.isOnCorporatePage;
        }
        
        showDetectionIndicator() {
            if (!this.checkIfCorporatePage()) return;
            
            this.removeCurrentIndicator();
            
            const indicator = this.createIndicator('🔍 Detecting Network...', '#ffa500', {
                subtitle: 'Checking corporate access'
            });
            
            this.currentIndicator = indicator;
            document.body.appendChild(indicator);
        }
        
        showResultIndicator(data) {
            if (!this.checkIfCorporatePage()) return;
            
            this.removeCurrentIndicator();
            
            const isCorporate = data.isCorporate;
            const color = isCorporate ? '#0066cc' : '#28a745';
            const icon = isCorporate ? '🏢' : '🌐';
            const title = isCorporate ? 'BMW Corporate Network' : 'Public Network';
            const subtitle = isCorporate ? 'Corporate Content Available' : 'Local Setup Required';
            
            const indicator = this.createIndicator(`${icon} ${title}`, color, {
                subtitle,
                duration: 1500 // 1.5 seconds as requested
            });
            
            this.currentIndicator = indicator;
            document.body.appendChild(indicator);
            
            // Auto-hide after duration
            setTimeout(() => {
                this.hideIndicator();
            }, 1500);
        }
        
        showNetworkChangeIndicator(data) {
            if (!this.checkIfCorporatePage()) return;
            
            const fromText = data.from ? 'Corporate' : 'Public';
            const toText = data.to ? 'Corporate' : 'Public';
            
            console.log(`📊 Network changed from ${fromText} to ${toText}`);
            
            // Show the new state immediately
            this.showResultIndicator({
                isCorporate: data.to,
                method: 'Network change'
            });
        }
        
        createIndicator(text, backgroundColor, options = {}) {
            const indicator = document.createElement('div');
            indicator.className = 'network-status-indicator';
            indicator.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${backgroundColor};
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                max-width: 280px;
                transition: opacity 0.3s ease;
            `;
            
            let content = text;
            if (options.subtitle) {
                content += `<div style="font-size: 11px; font-weight: normal; margin-top: 4px; opacity: 0.9;">${options.subtitle}</div>`;
            }
            
            indicator.innerHTML = content;
            
            return indicator;
        }
        
        hideIndicator() {
            if (this.currentIndicator) {
                this.currentIndicator.style.transition = 'opacity 0.5s ease';
                this.currentIndicator.style.opacity = '0';
                setTimeout(() => {
                    this.removeCurrentIndicator();
                }, 500);
            }
        }
        
        removeCurrentIndicator() {
            if (this.currentIndicator && this.currentIndicator.parentNode) {
                this.currentIndicator.remove();
            }
            this.currentIndicator = null;
        }
    }
    
    // ===== CONTENT MANAGER =====
    
    class CorporateContentManager {
        constructor(networkManager) {
            this.networkManager = networkManager;
            this.loadedContent = null;
            this.isProcessingContent = false;
            
            // Listen to network detection events
            this.networkManager.on('detection:completed', (data) => {
                if (data.isCorporate) {
                    this.loadAndInjectContent();
                } else {
                    this.showPublicContent();
                }
            });
            
            console.log('📄 Corporate Content Manager initialized');
        }
        
        async loadAndInjectContent() {
            if (this.isProcessingContent) {
                console.log('📄 Content processing already in progress');
                return;
            }
            
            const pageConfig = this.networkManager.getCurrentPageConfig();
            if (!pageConfig) {
                console.log('📄 Not a corporate content page, skipping content load');
                return;
            }
            
            this.isProcessingContent = true;
            
            try {
                console.log('📄 Starting independent content decryption and injection...');
                
                // Step 1: Load and decrypt content independently
                const decryptedContent = await this.loadAndDecryptContent();
                if (!decryptedContent) {
                    console.error('❌ Failed to decrypt content');
                    return;
                }
                
                // Step 2: Inject content for current page independently
                await this.injectContentForCurrentPage(pageConfig, decryptedContent);
                
                this.networkManager.state.contentLoaded = true;
                this.networkManager.emit('content:loaded', { source: 'unified-system' });
                console.log('✅ Corporate content loaded and injected successfully');
                
            } catch (error) {
                console.error('❌ Failed to load and inject content:', error);
            } finally {
                this.isProcessingContent = false;
            }
        }
        
        async loadAndDecryptContent() {
            console.log('🔓 Loading and decrypting corporate content...');
            
            // Get encrypted content from HTML comments
            const htmlContent = document.documentElement.outerHTML;
            const encryptedMatch = htmlContent.match(/ENCRYPTED_CORPORATE_CONTENT_START\s*([\s\S]*?)\s*ENCRYPTED_CORPORATE_CONTENT_END/);
            
            if (!encryptedMatch) {
                console.log('❌ No encrypted content found in HTML');
                return null;
            }
            
            try {
                const manifest = JSON.parse(encryptedMatch[1].trim());
                console.log('✅ Parsed encrypted manifest with', Object.keys(manifest.content || {}).length, 'files');
                
                // Decrypt all content
                const decryptedContent = {};
                const corporateKey = 'bmw-corporate-network-2024-secure';
                const key = await this.deriveKey(corporateKey);
                
                if (manifest.files && manifest.content) {
                    for (const [filePath, encryptedData] of Object.entries(manifest.content)) {
                        try {
                            decryptedContent[filePath] = await this.decryptContent(encryptedData, key);
                            console.log(`🔓 Decrypted: ${filePath}`);
                        } catch (error) {
                            console.error(`❌ Failed to decrypt ${filePath}:`, error);
                        }
                    }
                }
                
                return decryptedContent;
                
            } catch (error) {
                console.error('❌ Failed to parse or decrypt content:', error);
                return null;
            }
        }
        
        async deriveKey(passphrase) {
            const encoder = new TextEncoder();
            const data = encoder.encode(passphrase);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            return await crypto.subtle.importKey(
                'raw',
                hashBuffer,
                { name: 'AES-GCM' },
                false,
                ['decrypt']
            );
        }
        
        async decryptContent(encryptedData, key) {
            const iv = this.base64ToArrayBuffer(encryptedData.iv);
            const authTag = this.base64ToArrayBuffer(encryptedData.authTag);
            const encrypted = this.base64ToArrayBuffer(encryptedData.encrypted);
            
            // Combine encrypted data with auth tag for AES-GCM
            const combinedBuffer = new Uint8Array(encrypted.byteLength + authTag.byteLength);
            combinedBuffer.set(new Uint8Array(encrypted), 0);
            combinedBuffer.set(new Uint8Array(authTag), encrypted.byteLength);
            
            const decrypted = await crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: iv
                },
                key,
                combinedBuffer
            );
            
            return new TextDecoder().decode(decrypted);
        }
        
        base64ToArrayBuffer(base64) {
            const binaryString = atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            return bytes.buffer;
        }
        
        async injectContentForCurrentPage(pageConfig, decryptedContent) {
            const { config } = pageConfig;
            console.log(`📄 Injecting content for page:`, config);
            
            // Determine which content to use (primary first, fallback if needed)
            let targetContent = config.primaryContent;
            let contentToInject = decryptedContent[targetContent];
            
            if (!contentToInject && config.fallbackContent) {
                console.log(`⚠️ Primary content ${targetContent} not found, trying fallback...`);
                targetContent = config.fallbackContent;
                contentToInject = decryptedContent[targetContent];
            }
            
            if (!contentToInject) {
                console.error(`❌ No content found for ${targetContent}`);
                console.log('Available content files:', Object.keys(decryptedContent));
                return;
            }
            
            console.log(`📄 Injecting corporate content: ${targetContent}`);
            await this.replacePageContent(contentToInject);
            
            // Set up detailed content switching for coder page if needed
            if (config.detailedContent && decryptedContent[config.detailedContent]) {
                this.setupDetailedContentSwitching(config, decryptedContent);
            }
        }
        
        setupDetailedContentSwitching(config, decryptedContent) {
            const detailedDiv = document.getElementById(config.detailHash);
            if (!detailedDiv) {
                console.log(`⚠️ Detailed content div #${config.detailHash} not found`);
                return;
            }
            
            console.log(`🔗 Setting up detailed content switching for #${config.detailHash}`);
            
            // Set up hash change listener
            const handleHashChange = () => {
                if (window.location.hash === `#${config.detailHash}`) {
                    console.log('📄 Loading detailed content...');
                    detailedDiv.innerHTML = this.convertMarkdownToHtml(decryptedContent[config.detailedContent]);
                    detailedDiv.style.display = 'block';
                    detailedDiv.scrollIntoView({ behavior: 'smooth' });
                } else {
                    detailedDiv.style.display = 'none';
                }
            };
            
            window.addEventListener('hashchange', handleHashChange);
            handleHashChange(); // Check current hash
        }
        
        convertMarkdownToHtml(markdown) {
            if (!markdown) return '';
            
            // Enhanced markdown conversion with better formatting
            let html = markdown;
            
            // Headers
            html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
            html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
            
            // Code blocks
            html = html.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
            html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Bold and italic
            html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            // Links with better handling
            html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
            
            // Images
            html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto;">');
            
            // Lists
            html = html.replace(/^\* (.+)$/gm, '<li>$1</li>');
            html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
            html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
            
            // Checkboxes
            html = html.replace(/- \[x\] (.+)/g, '<li style="list-style: none;"><input type="checkbox" checked disabled> $1</li>');
            html = html.replace(/- \[ \] (.+)/g, '<li style="list-style: none;"><input type="checkbox" disabled> $1</li>');
            
            // Paragraphs
            html = html.replace(/\n\n/g, '</p><p>');
            html = html.replace(/\n/g, '<br>');
            
            // Wrap in paragraph if not already wrapped
            if (!html.startsWith('<')) {
                html = `<p>${html}</p>`;
            }
            
            return html;
        }
        
        async replacePageContent(markdownContent) {
            // Find the main content area
            const contentSelectors = [
                'article.md-typeset',
                '.md-content__inner article',
                '.md-content__inner .md-typeset'
            ];
            
            let contentArea = null;
            for (const selector of contentSelectors) {
                contentArea = document.querySelector(selector);
                if (contentArea) break;
            }
            
            if (!contentArea) {
                console.error('❌ Could not find content area to replace');
                return;
            }
            
            console.log('🔄 Replacing page content with decrypted corporate content...');
            const htmlContent = this.convertMarkdownToHtml(markdownContent);
            contentArea.innerHTML = htmlContent;
            
            // Process images to ensure they load correctly
            this.processImages(contentArea);
        }
        
        processImages(contentArea) {
            const images = contentArea.querySelectorAll('img');
            images.forEach(img => {
                // Fix relative image paths
                if (img.src.startsWith('../')) {
                    const basePath = window.location.pathname.includes('/agentic-ai-nano/') ? 
                        '/agentic-ai-nano/' : '/';
                    img.src = basePath + img.src.replace('../', '');
                }
                
                // Add error handling
                img.onerror = function() {
                    console.warn(`⚠️ Failed to load image: ${this.src}`);
                    this.style.display = 'none';
                };
                
                console.log(`🖼️ Processing image: ${img.src}`);
            });
        }
        
        
        showPublicContent() {
            console.log('🌐 Showing public content');
            // Remove any corporate content classes/indicators
            document.querySelectorAll('.bmw-corporate-only').forEach(el => {
                el.style.display = 'none';
            });
            
            document.querySelectorAll('.bmw-public-alternative').forEach(el => {
                el.style.display = 'block';
            });
        }
    }
    
    // ===== MAIN CONTROLLER =====
    
    class UnifiedCorporateNetworkController {
        constructor() {
            this.networkManager = new CorporateNetworkManager();
            this.visualManager = new VisualIndicatorManager(this.networkManager);
            this.contentManager = new CorporateContentManager(this.networkManager);
            
            this.isInitialized = false;
            
            // Disable the old corporate content loader to prevent conflicts
            this.disableOldContentLoader();
            
            console.log('🚀 Unified Corporate Network Controller initialized');
        }
        
        disableOldContentLoader() {
            // Completely disable the old corporate content loader to prevent any conflicts
            // We now handle everything independently
            
            // Prevent the old loader from auto-initializing
            if (window.CorporateContentLoader) {
                console.log('🔧 Completely disabling old corporate content loader');
                
                // Override all methods to prevent execution
                const noop = () => {
                    console.log('🔄 Old corporate content loader disabled - using unified system');
                    return Promise.resolve(false);
                };
                
                window.CorporateContentLoader.load = noop;
                window.CorporateContentLoader.init = noop;
                window.CorporateContentLoader.autoDetectionDisabled = true;
            }
            
            // Also prevent the auto-initialization script from running
            const scripts = document.querySelectorAll('script[src*="corporate-content-loader"]');
            scripts.forEach(script => {
                script.disabled = true;
                console.log('🔧 Disabled corporate content loader script');
            });
            
            console.log('✅ Old corporate content loader completely disabled');
        }
        
        async initialize() {
            if (this.isInitialized) {
                console.log('⚠️ Already initialized, skipping...');
                return;
            }
            
            // Check if this is a corporate page
            const pageConfig = this.networkManager.getCurrentPageConfig();
            if (!pageConfig) {
                console.log('📄 Not a corporate page, exiting...');
                return;
            }
            
            console.log(`🏢 Initializing for corporate page: ${pageConfig.config.name}`);
            this.networkManager.state.currentPage = pageConfig;
            
            // Start detection
            try {
                await this.networkManager.detectCorporateNetwork();
                this.isInitialized = true;
                console.log('✅ Initialization complete');
            } catch (error) {
                console.error('❌ Initialization failed:', error);
            }
        }
        
        // Public API for debugging
        getState() {
            return this.networkManager.getState();
        }
        
        async forceDetection() {
            return this.networkManager.forceDetection();
        }
    }
    
    // ===== GLOBAL INITIALIZATION =====
    
    // Disable old corporate content loader IMMEDIATELY to prevent conflicts
    document.addEventListener('DOMContentLoaded', () => {
        // Override the old auto-loading behavior completely
        if (window.CorporateContentLoader && window.CorporateContentLoader.isCorporateContentNeeded) {
            window.CorporateContentLoader.isCorporateContentNeeded = () => false;
            console.log('🔧 Disabled old corporate content auto-loading');
        }
    });
    
    // Create global instance
    window.CorporateNetworkController = new UnifiedCorporateNetworkController();
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // Delay initialization slightly to ensure old loader is disabled
            setTimeout(() => {
                window.CorporateNetworkController.initialize();
            }, 100);
        });
    } else {
        setTimeout(() => {
            window.CorporateNetworkController.initialize();
        }, 100);
    }
    
    // Handle navigation
    let lastUrl = location.href;
    const observer = new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            console.log('🔄 URL changed, reinitializing...');
            
            // Reset and reinitialize
            window.CorporateNetworkController.isInitialized = false;
            setTimeout(() => {
                window.CorporateNetworkController.initialize();
            }, 100);
        }
    });
    
    observer.observe(document.body, {
        subtree: true,
        childList: true
    });
    
    console.log('🎯 Unified Corporate Network Detection System loaded');
    
})();