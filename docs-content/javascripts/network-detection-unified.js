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
            
            // Strict content matching - no fallbacks, clear error messages
            const targetContent = config.primaryContent;
            const contentToInject = decryptedContent[targetContent];
            
            if (!contentToInject) {
                console.error(`❌ CONTENT MISSING: Required file '${targetContent}' not found in encrypted content`);
                console.error('📋 Page configuration:', config);
                console.error('📋 Available encrypted files:', Object.keys(decryptedContent));
                console.error('💡 Solution: Re-run encryption script to include missing file');
                
                // Show error in the UI as well
                this.showContentError(targetContent, Object.keys(decryptedContent));
                return;
            }
            
            console.log(`📄 Injecting corporate content: ${targetContent}`);
            await this.replacePageContent(contentToInject, decryptedContent);
            
            // Set up detailed content switching for coder page if needed
            if (config.detailedContent && decryptedContent[config.detailedContent]) {
                this.setupDetailedContentSwitching(config, decryptedContent);
            }
        }
        
        showContentError(missingFile, availableFiles) {
            const contentArea = document.querySelector('article.md-typeset') || 
                              document.querySelector('.md-content__inner article') || 
                              document.querySelector('.md-content__inner .md-typeset');
            
            if (contentArea) {
                contentArea.innerHTML = `
                    <div style="background: #ff4444; color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h2>🚫 Corporate Content Error</h2>
                        <p><strong>Missing file:</strong> <code>${missingFile}</code></p>
                        <p><strong>Available files:</strong></p>
                        <ul style="margin: 10px 0;">
                            ${availableFiles.map(file => `<li><code>${file}</code></li>`).join('')}
                        </ul>
                        <p><strong>Solution:</strong> Re-run the encryption script to include the missing file.</p>
                    </div>
                `;
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
            const handleHashChange = async () => {
                if (window.location.hash === `#${config.detailHash}`) {
                    console.log('📄 Loading detailed content...');
                    const processedContent = await this.replaceImagesWithBase64(decryptedContent[config.detailedContent], decryptedContent);
                    const htmlContent = this.convertMarkdownToHtml(processedContent, decryptedContent);
                    detailedDiv.innerHTML = htmlContent;
                    detailedDiv.style.display = 'block';
                    detailedDiv.scrollIntoView({ behavior: 'smooth' });
                } else {
                    detailedDiv.style.display = 'none';
                }
            };
            
            window.addEventListener('hashchange', handleHashChange);
            handleHashChange(); // Check current hash
        }
        
        async replaceImagesWithBase64(markdownContent, decryptedContent) {
            let processedContent = markdownContent;
            
            // Find all image references in markdown: ![alt](path)
            const imagePattern = /!\[([^\]]*)\]\(([^)]+)\)/g;
            const matches = [...markdownContent.matchAll(imagePattern)];
            
            for (const match of matches) {
                const [fullMatch, altText, imagePath] = match;
                console.log(`🖼️ Processing image: ${imagePath}`);
                
                // Normalize the image path to match encrypted content keys
                let normalizedPath = this.normalizeImagePath(imagePath);
                
                // Look for the image in encrypted content
                if (decryptedContent[normalizedPath]) {
                    const base64Content = decryptedContent[normalizedPath];
                    const extension = normalizedPath.split('.').pop().toLowerCase();
                    const mimeType = this.getMimeType(extension);
                    const dataUrl = `data:${mimeType};base64,${base64Content}`;
                    
                    // Replace the image reference with base64 data URL
                    processedContent = processedContent.replace(fullMatch, `![${altText}](${dataUrl})`);
                    console.log(`✅ Replaced image ${normalizedPath} with base64 data URL`);
                } else {
                    // If not in encrypted content, it might be a shared image
                    // Keep the original path but adjust for correct web path
                    if (imagePath.includes('../../00_intro/images/')) {
                        // Shared images - adjust path for web access
                        const webPath = imagePath.replace('../../', '/agentic-ai-nano/');
                        processedContent = processedContent.replace(fullMatch, `![${altText}](${webPath})`);
                        console.log(`📷 Using shared image with web path: ${webPath}`);
                    } else if (normalizedPath === 'images/coder-workspaces.png') {
                        // Special case: coder-workspaces.png should use the shared public image
                        const webPath = '/agentic-ai-nano/00_intro/images/coder-workspaces.png';
                        processedContent = processedContent.replace(fullMatch, `![${altText}](${webPath})`);
                        console.log(`📷 Using shared coder-workspaces image with web path: ${webPath}`);
                    } else {
                        console.warn(`❌ Image not found in encrypted content: ${normalizedPath}`);
                        console.log('Available encrypted images:', Object.keys(decryptedContent).filter(key => key.match(/\.(png|jpg|jpeg|gif|svg)$/i)));
                    }
                }
            }
            
            return processedContent;
        }

        normalizeImagePath(imagePath) {
            // Remove leading ../ or ./ and normalize path separators
            let normalized = imagePath.replace(/\\/g, '/');
            
            // Handle different path patterns in corporate content
            if (imagePath.includes('../../corporate-only/')) {
                // Path like ../../corporate-only/images/file.png -> images/file.png
                normalized = imagePath.replace('../../corporate-only/', '');
            } else if (imagePath.startsWith('../images/')) {
                // Path like ../images/file.png -> images/file.png (corporate-only images)
                normalized = imagePath.replace('../images/', 'images/');
            } else if (imagePath.includes('../../00_intro/images/')) {
                // Path like ../../00_intro/images/file.png -> 00_intro/images/file.png (shared images)
                normalized = imagePath.replace('../../', '');
            } else if (imagePath.startsWith('images/')) {
                // Already normalized
                normalized = imagePath;
            }
            
            console.log(`📁 Normalized image path: ${imagePath} -> ${normalized}`);
            return normalized;
        }

        getMimeType(extension) {
            const mimeTypes = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'svg': 'image/svg+xml'
            };
            return mimeTypes[extension] || 'image/png';
        }

        generateHeadingId(title) {
            return title.toLowerCase()
                .replace(/[^a-z0-9\s-]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .replace(/^-|-$/g, '');
        }

        convertMarkdownToHtml(markdown, decryptedContent = null) {
            if (!markdown) return '';
            
            let htmlContent = markdown;
            
            // First handle code blocks to protect them from other processing
            const codeBlocks = [];
            htmlContent = htmlContent.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
                const index = codeBlocks.length;
                codeBlocks.push(`<pre><code class="language-${lang || ''}">${code.trim()}</code></pre>`);
                return `__CODE_BLOCK_${index}__`;
            });
            
            // Handle headings with automatic ID generation for navigation and scroll highlighting
            htmlContent = htmlContent
                .replace(/^# (.+)$/gm, (match, title) => {
                    const id = this.generateHeadingId(title);
                    return `<h1 id="${id}">${title}</h1>`;
                })
                .replace(/^## (.+)$/gm, (match, title) => {
                    const id = this.generateHeadingId(title);
                    return `<h2 id="${id}">${title}</h2>`;
                })
                .replace(/^### (.+)$/gm, (match, title) => {
                    const id = this.generateHeadingId(title);
                    return `<h3 id="${id}">${title}</h3>`;
                })
                .replace(/^#### (.+)$/gm, (match, title) => {
                    const id = this.generateHeadingId(title);
                    return `<h4 id="${id}">${title}</h4>`;
                })
                .replace(/^##### (.+)$/gm, (match, title) => {
                    const id = this.generateHeadingId(title);
                    return `<h5 id="${id}">${title}</h5>`;
                });
            
            // Handle text formatting
            htmlContent = htmlContent
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*([^*]+?)\*/g, '<em>$1</em>')
                .replace(/`([^`]+?)`/g, '<code>$1</code>');
            
            // Handle images and links (images first to avoid conflicts)
            htmlContent = htmlContent
                .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width: 100%; height: auto;">')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
            
            // Handle lists - improved handling
            htmlContent = htmlContent.replace(/^(\s*)-\s+(.+)$/gm, (match, indent, content) => {
                const level = Math.floor(indent.length / 2);
                return `<li data-level="${level}">${content}</li>`;
            });
            
            // Wrap consecutive list items in ul tags
            htmlContent = htmlContent.replace(/(<li[^>]*>.*?<\/li>\s*)+/gs, (match) => {
                return `<ul>${match}</ul>`;
            });
            
            // Handle numbered lists
            htmlContent = htmlContent.replace(/^(\s*)\d+\.\s+(.+)$/gm, (match, indent, content) => {
                const level = Math.floor(indent.length / 2);
                return `<li data-level="${level}">${content}</li>`;
            });
            
            // Convert paragraphs - be more careful about existing HTML
            const lines = htmlContent.split('\n');
            let inList = false;
            let result = [];
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                
                if (!line) {
                    result.push('');
                    continue;
                }
                
                // Check if line is already HTML
                if (line.startsWith('<') || line.includes('__CODE_BLOCK_')) {
                    result.push(line);
                    inList = line.includes('<li') || line.includes('<ul') || line.includes('<ol');
                } else if (!inList) {
                    // Only wrap in paragraph if not already HTML and not in a list
                    result.push(`<p>${line}</p>`);
                } else {
                    result.push(line);
                }
            }
            
            htmlContent = result.join('\n');
            
            // Restore code blocks
            codeBlocks.forEach((block, index) => {
                htmlContent = htmlContent.replace(`__CODE_BLOCK_${index}__`, block);
            });
            
            // Clean up empty paragraphs and fix common issues
            htmlContent = htmlContent
                .replace(/<p><\/p>/g, '')
                .replace(/<p>(<[^>]+>)/g, '$1')  // Remove p tags around block elements
                .replace(/(<\/[^>]+>)<\/p>/g, '$1');  // Remove closing p tags after block elements
            
            return htmlContent;
        }
        
        async replacePageContent(markdownContent, decryptedContent) {
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
            
            // Step 1: Process images first to convert to base64 data URLs
            const processedContent = await this.replaceImagesWithBase64(markdownContent, decryptedContent);
            
            // Step 2: Convert markdown to HTML with sophisticated processing
            const htmlContent = this.convertMarkdownToHtml(processedContent, decryptedContent);
            
            // Step 3: Replace content area
            contentArea.innerHTML = htmlContent;
            
            // Ensure content has proper MkDocs classes for scroll highlighting
            if (!contentArea.classList.contains('md-typeset')) {
                contentArea.classList.add('md-typeset');
            }
            
            console.log('✅ Corporate content successfully injected with proper image processing');
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