/**
 * Corporate Content Loader
 * 
 * Handles loading and decrypting corporate content when accessed from 
 * BMW corporate network. Works with content encrypted by encrypt-corporate-content.js
 */

(function() {
    'use strict';

    // Corporate content loader class
    // Cache buster: 2025-09-20T20:18:00Z - Fixed: content.encrypted.json now in site root
    class CorporateContentLoader {
        constructor() {
            // Use absolute path for GitHub Pages deployment - content in site root
            this.encryptedContentPath = '/agentic-ai-nano/content.encrypted.json';
            console.log('🔍 Corporate content path configured:', this.encryptedContentPath);
            console.log('🔍 Current pathname:', window.location.pathname);
            console.log('🔍 Current hostname:', window.location.hostname);
            this.corporateKey = 'bmw-corporate-network-2024-secure'; // Same as encryption script
            this.loadedContent = null;
            this._isReplacingContent = false; // Flag to prevent duplicate content replacement
        }

        /**
         * Derives the same key used for encryption
         */
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

        /**
         * Decrypts content using AES-GCM
         */
        async decryptContent(encryptedData, key) {
            try {
                const iv = this.base64ToArrayBuffer(encryptedData.iv);
                const authTag = this.base64ToArrayBuffer(encryptedData.authTag);
                const encrypted = this.base64ToArrayBuffer(encryptedData.encrypted);
                
                // Combine encrypted data with auth tag for AES-GCM
                const ciphertext = new Uint8Array(encrypted.byteLength + authTag.byteLength);
                ciphertext.set(new Uint8Array(encrypted), 0);
                ciphertext.set(new Uint8Array(authTag), encrypted.byteLength);

                const decrypted = await crypto.subtle.decrypt(
                    {
                        name: 'AES-GCM',
                        iv: iv,
                        tagLength: 128
                    },
                    key,
                    ciphertext
                );

                return new TextDecoder().decode(decrypted);
            } catch (error) {
                console.error('Decryption failed:', error);
                throw new Error('Failed to decrypt corporate content');
            }
        }

        /**
         * Converts base64 string to ArrayBuffer
         */
        base64ToArrayBuffer(base64) {
            const binaryString = atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            return bytes.buffer;
        }

        /**
         * Checks if corporate content is needed for the current page
         */
        isCorporateContentNeeded() {
            const currentPath = window.location.pathname;
            const needsCorporateContent = 
                currentPath.includes('/00_intro/coder/') ||
                currentPath.includes('/00_intro/llmapi/') ||
                currentPath.includes('/03_mcp-acp-a2a/Session10') ||
                currentPath.includes('/03_mcp-acp-a2a/') ||  // Module index where Session 10 nav gets added
                currentPath.includes('session10') ||
                window.location.hash.includes('session10');
            
            console.log(`🔍 Corporate content needed for ${currentPath}: ${needsCorporateContent}`);
            return needsCorporateContent;
        }

        /**
         * Loads and decrypts corporate content
         */
        async load() {
            try {
                // If content is already loaded, check if current page needs content replacement
                if (this.loadedContent) {
                    console.log('🔐 Corporate content already loaded, checking if page needs replacement...');
                    await this.injectDecryptedContent();
                    return true;
                }
                
                // Check if corporate content is actually needed for this page
                if (!this.isCorporateContentNeeded()) {
                    console.log('🔐 Corporate content not needed for current page, skipping...');
                    return false;
                }
                
                console.log('🔐 Loading encrypted corporate content...');
                console.log('🔍 Fetching from path:', this.encryptedContentPath);
                
                // Use the correct path for GitHub Pages deployment with cache busting
                const cacheBuster = `?v=${Date.now()}`;
                const fullPath = this.encryptedContentPath + cacheBuster;
                console.log('🔍 Full URL with cache buster:', fullPath);
                const response = await fetch(fullPath);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch encrypted content: ${response.status} ${response.statusText}`);
                }
                
                console.log(`✅ Found content at: ${this.encryptedContentPath}`);

                const manifest = await response.json();
                console.log(`📦 Found ${manifest.files.length} encrypted files`);

                // Derive decryption key
                const key = await this.deriveKey(this.corporateKey);

                // Decrypt all content
                const decryptedContent = {};
                for (const [filePath, encryptedData] of Object.entries(manifest.content)) {
                    try {
                        console.log(`🔓 Decrypting: ${filePath}`);
                        decryptedContent[filePath] = await this.decryptContent(encryptedData, key);
                    } catch (error) {
                        console.error(`Failed to decrypt ${filePath}:`, error);
                    }
                }

                this.loadedContent = decryptedContent;
                
                // Inject decrypted content into DOM
                await this.injectDecryptedContent();

                console.log('✅ Corporate content decrypted and loaded successfully');
                return true;
            } catch (error) {
                console.error('❌ Failed to load corporate content:', error);
                return false;
            }
        }

        /**
         * Injects decrypted content into the DOM by replacing placeholders
         */
        async injectDecryptedContent() {
            if (!this.loadedContent) {
                console.warn('No decrypted content available to inject');
                return;
            }

            // Determine which corporate content to load based on current page
            const currentPath = window.location.pathname;
            console.log('🔍 Current path:', currentPath);
            
            // Corporate content mapping - only exact matches to prevent mismatches
            const contentMapping = {
                '/00_intro/coder/': '00_intro/coder-detailed.md',
                '/00_intro/llmapi/': '00_intro/llmapi-detailed.md'
            };
            
            let targetFile = null;
            
            // Check for exact path matches first
            for (const [path, file] of Object.entries(contentMapping)) {
                if (currentPath.includes(path)) {
                    targetFile = file;
                    console.log(`📄 Matched ${path} - will load corporate content: ${file}`);
                    break;
                }
            }
            
            // Special handling for Session 10 - create virtual page navigation
            if (!targetFile && window.location.hash.includes('session10')) {
                targetFile = '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md';
                console.log('📄 Virtual Session 10 page requested via hash - will load corporate content');
                // Navigate to proper Session 10 URL to maintain consistency
                this.navigateToVirtualPage('/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/', targetFile);
                return; // Exit early, navigation will trigger reload
            }
            
            if (!targetFile) {
                console.log('📄 No corporate content mapping for path:', currentPath);
            }
            
            if (targetFile) {
                if (this.loadedContent[targetFile]) {
                    console.log(`🔄 Replacing page content with corporate version: ${targetFile}`);
                    await this.replacePageContent(this.loadedContent[targetFile]);
                } else {
                    console.log(`❌ Target file ${targetFile} not found in loaded content`);
                    console.log('Available files:', Object.keys(this.loadedContent));
                }
            }

            // Handle image content
            for (const [filePath, content] of Object.entries(this.loadedContent)) {
                if (filePath.match(/\.(png|jpg|jpeg|gif|svg)$/i)) {
                    await this.injectImageContent(filePath, content);
                }
            }
        }

        /**
         * Creates a virtual page navigation for Session 10
         */
        navigateToVirtualPage(virtualPath, contentFile) {
            try {
                console.log('🔄 Navigating to virtual page:', virtualPath);
                
                // Update browser URL without reload
                const newUrl = `${window.location.origin}${virtualPath}`;
                history.pushState({corporateContent: contentFile}, '', newUrl);
                
                // Replace content immediately
                if (this.loadedContent[contentFile]) {
                    this.replacePageContent(this.loadedContent[contentFile]);
                    // Update navigation to match the new content
                    this.updateNavigationState(contentFile);
                }
                
                console.log('✅ Virtual navigation completed');
            } catch (error) {
                console.error('❌ Failed to navigate to virtual page:', error);
            }
        }

        /**
         * Replaces only the article content, preserving MkDocs navigation structure
         */
        async replacePageContent(markdownContent) {
            try {
                // Prevent duplicate content replacement
                if (this._isReplacingContent) {
                    console.log('🔄 Content replacement already in progress, skipping duplicate call');
                    return;
                }
                this._isReplacingContent = true;
                
                // Target only the actual article content, not the entire content area
                const selectors = [
                    'article.md-typeset',                       // Direct article with content
                    '.md-content__inner article',               // Article within content
                    '.md-typeset > *',                          // Direct children of typeset
                    '.md-content__inner .md-typeset'            // Fallback to typeset area
                ];
                
                let contentArea = null;
                for (const selector of selectors) {
                    contentArea = document.querySelector(selector);
                    if (contentArea) {
                        console.log('✅ Found content area using selector:', selector);
                        break;
                    }
                }
                
                if (!contentArea) {
                    console.error('❌ Could not find any content area to replace');
                    return;
                }
                
                console.log('🔄 Replacing minimal content area:', contentArea.tagName);
                
                // First, replace image references with base64 data URLs
                let processedContent = await this.replaceImagesWithBase64(markdownContent);
                
                // Enhanced markdown to HTML conversion with better structure handling
                // IMPORTANT: Process images BEFORE links to avoid conflicts
                let htmlContent = processedContent;
                
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
                
                // Replace the content while preserving essential structure
                contentArea.innerHTML = htmlContent;
                
                // Ensure content has proper MkDocs classes for scroll highlighting
                if (!contentArea.classList.contains('md-typeset')) {
                    contentArea.classList.add('md-typeset');
                }
                
                // Fix navigation links within the injected content
                this.fixNavigationLinks(contentArea);
                
                // Update page title based on content
                this.updatePageTitle(markdownContent);
                
                // Update navigation state to match corporate content
                const contentFile = this.getCurrentContentFile();
                this.updateNavigationState(contentFile);
                
                console.log('✅ Corporate content successfully injected with preserved structure');
                
            } catch (error) {
                console.error('❌ Failed to replace page content:', error);
            } finally {
                // Always reset the flag to allow future content replacements
                this._isReplacingContent = false;
            }
        }

        /**
         * Triggers MkDocs navigation update for scroll highlighting
         */
        updateNavigationState(contentFile) {
            try {
                console.log('🔄 Updating navigation state for:', contentFile);
                
                // Update sidebar highlighting based on content
                this.updateSidebarForContent(contentFile);
                
                // Simple scroll highlighting re-initialization without breaking MkDocs
                setTimeout(() => {
                    // Just trigger a scroll event to activate any existing highlighting
                    window.dispatchEvent(new Event('scroll', { bubbles: true }));
                }, 100);
                
                console.log('✅ Navigation state updated');
            } catch (error) {
                console.warn('⚠️ Could not update navigation state:', error);
            }
        }

        /**
         * Updates sidebar highlighting based on corporate content
         */
        updateSidebarForContent(contentFile) {
            try {
                // First, ensure sidebar is visible (especially important for coder page)
                this.ensureSidebarVisible();
                
                // Remove any existing active states
                document.querySelectorAll('.md-nav__link--active, .md-nav__item--active').forEach(el => {
                    el.classList.remove('md-nav__link--active', 'md-nav__item--active');
                });
                
                // Determine which sidebar item should be highlighted
                let targetText = '';
                if (contentFile.includes('coder-detailed.md')) {
                    targetText = 'Development Environment';
                    // For the coder page, ensure we're in the correct navigation context
                    this.ensureCoderPageNavigation();
                } else if (contentFile.includes('Session10_Enterprise_Integration_Production_Deployment.md')) {
                    targetText = 'Enterprise Integration';
                    // For Session 10, also create/update the navigation item
                    this.ensureSession10Navigation();
                }
                
                // Find and highlight the appropriate navigation item
                if (targetText) {
                    const navLinks = document.querySelectorAll('.md-nav__link');
                    navLinks.forEach(link => {
                        if (link.textContent.includes(targetText)) {
                            link.classList.add('md-nav__link--active');
                            const item = link.closest('.md-nav__item');
                            if (item) {
                                item.classList.add('md-nav__item--active');
                            }
                        }
                    });
                }
                
                console.log('✅ Sidebar highlighting updated for:', targetText);
            } catch (error) {
                console.warn('⚠️ Could not update sidebar highlighting:', error);
            }
        }
        
        /**
         * Ensures the sidebar is visible and properly displayed
         */
        ensureSidebarVisible() {
            try {
                // Log current sidebar state for debugging
                const sidebar = document.querySelector('.md-sidebar.md-sidebar--primary');
                if (sidebar) {
                    console.log('🔍 Current sidebar state:', {
                        display: sidebar.style.display || 'default',
                        visibility: sidebar.style.visibility || 'default',
                        classes: sidebar.className,
                        offsetWidth: sidebar.offsetWidth,
                        offsetHeight: sidebar.offsetHeight
                    });
                    
                    // Force visibility with multiple approaches
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.opacity = '1';
                    sidebar.style.transform = '';
                    sidebar.style.left = '';
                    sidebar.style.marginLeft = '';
                    sidebar.classList.remove('md-sidebar--hidden');
                    
                    // Apply force CSS with !important
                    const forceStyle = 'display: block !important; visibility: visible !important; opacity: 1 !important; position: fixed !important; left: 0 !important;';
                    sidebar.setAttribute('style', forceStyle);
                    
                    // Ensure drawer toggle is properly set
                    const drawerToggle = document.querySelector('[data-md-toggle="drawer"]');
                    if (drawerToggle && drawerToggle.type === 'checkbox') {
                        console.log('🔍 Drawer toggle state:', drawerToggle.checked);
                        drawerToggle.checked = false; // Unchecked shows sidebar
                        drawerToggle.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    
                    // Force layout recalculation
                    sidebar.offsetHeight; // Trigger reflow
                    
                    console.log('✅ Sidebar visibility forced - checking dimensions:', {
                        offsetWidth: sidebar.offsetWidth,
                        offsetHeight: sidebar.offsetHeight,
                        computed: window.getComputedStyle(sidebar).display
                    });
                } else {
                    console.warn('⚠️ Primary sidebar not found in DOM');
                }
                
                // Force show secondary sidebar (TOC)
                const secondarySidebar = document.querySelector('.md-sidebar.md-sidebar--secondary');
                if (secondarySidebar) {
                    const forceSecondaryStyle = 'display: block !important; visibility: visible !important; opacity: 1 !important;';
                    secondarySidebar.setAttribute('style', forceSecondaryStyle);
                }
                
                // Try to reinitialize Material theme if possible
                setTimeout(() => {
                    try {
                        if (window.app && window.app.drawer) {
                            window.app.drawer.reset();
                        }
                        // Force body class update to ensure proper layout
                        document.body.classList.remove('md-sidebar--hidden');
                        document.documentElement.classList.remove('md-sidebar--hidden');
                    } catch (e) {
                        console.log('Could not reinitialize Material theme:', e);
                    }
                }, 100);
                
            } catch (error) {
                console.warn('⚠️ Could not ensure sidebar visibility:', error);
            }
        }
        
        /**
         * Ensures proper navigation context for the coder page
         */
        ensureCoderPageNavigation() {
            try {
                // Find the "Setup & Environment" section in navigation
                const setupSection = Array.from(document.querySelectorAll('.md-nav__link')).find(link =>
                    link.textContent.includes('Setup & Environment') || 
                    link.textContent.includes('Getting Started')
                );
                
                if (setupSection) {
                    // Expand the parent section if needed
                    const parentItem = setupSection.closest('.md-nav__item');
                    if (parentItem) {
                        const toggle = parentItem.querySelector('[data-md-toggle]');
                        if (toggle && toggle.type === 'checkbox') {
                            toggle.checked = true; // Expand the section
                        }
                    }
                }
                
                console.log('✅ Coder page navigation context set');
            } catch (error) {
                console.warn('⚠️ Could not set coder page navigation:', error);
            }
        }

        /**
         * Ensures Session 10 appears in navigation when showing Session 10 content
         */
        ensureSession10Navigation() {
            try {
                // Check if Session 10 nav item already exists
                const existingSession10 = Array.from(document.querySelectorAll('.md-nav__link')).find(link => 
                    link.textContent.includes('Session 10') || link.textContent.includes('Enterprise Integration')
                );
                
                if (!existingSession10) {
                    // Find the Module 03 navigation area
                    const module03Section = document.querySelector('[data-md-level="1"]:has(.md-nav__link[href*="mcp-acp-a2a"])');
                    if (module03Section) {
                        // Create Session 10 navigation item
                        const session10Item = document.createElement('li');
                        session10Item.className = 'md-nav__item md-nav__item--active';
                        session10Item.innerHTML = `
                            <a href="#" class="md-nav__link md-nav__link--active">
                                <span class="md-ellipsis">Session 10 - Enterprise Integration</span>
                            </a>
                        `;
                        
                        // Add after other sessions
                        const sessionItems = module03Section.querySelectorAll('.md-nav__item');
                        if (sessionItems.length > 0) {
                            sessionItems[sessionItems.length - 1].insertAdjacentElement('afterend', session10Item);
                        }
                        
                        console.log('✅ Added Session 10 to navigation');
                    }
                }
            } catch (error) {
                console.warn('⚠️ Could not ensure Session 10 navigation:', error);
            }
        }


        /**
         * Gets the current content file being displayed
         */
        getCurrentContentFile() {
            const currentPath = window.location.pathname;
            
            if (currentPath.includes('/00_intro/coder/')) {
                return '00_intro/coder-detailed.md';
            } else if (currentPath.includes('/00_intro/llmapi/')) {
                return '00_intro/llmapi-detailed.md';
            } else if (currentPath.includes('/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/') || 
                       window.location.hash.includes('session10')) {
                return '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md';
            }
            
            return null;
        }

        /**
         * Updates page title and header based on content
         */
        updatePageTitle(content) {
            try {
                // Extract first H1 heading from content for dynamic title
                const h1Match = content.match(/^#\s+(.+)$/m);
                if (h1Match) {
                    const pageTitle = h1Match[1].trim();
                    document.title = `${pageTitle} - Agentic AI Nano-Degree`;
                    
                    // Update header title if available
                    const headerTopic = document.querySelector('.md-header__topic[data-md-component="header-topic"] .md-ellipsis');
                    if (headerTopic) {
                        headerTopic.textContent = pageTitle;
                    }
                    
                    console.log('✅ Page title updated:', pageTitle);
                }
            } catch (error) {
                console.warn('⚠️ Could not update page title:', error);
            }
        }


        /**
         * Replaces image references in markdown with base64 data URLs from encrypted content
         */
        async replaceImagesWithBase64(markdownContent) {
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
                if (this.loadedContent[normalizedPath]) {
                    const base64Content = this.loadedContent[normalizedPath];
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
                    } else {
                        console.warn(`❌ Image not found in encrypted content: ${normalizedPath}`);
                        console.log('Available encrypted images:', Object.keys(this.loadedContent).filter(key => key.match(/\.(png|jpg|jpeg|gif|svg)$/i)));
                    }
                }
            }
            
            return processedContent;
        }

        /**
         * Normalizes image paths to match encrypted content structure
         */
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

        /**
         * Injects decrypted markdown content (legacy method, kept for compatibility)
         */
        async injectMarkdownContent(filePath, content) {
            // Look for elements that reference this file path
            const selector = `[href*="${filePath}"], [src*="${filePath}"]`;
            const elements = document.querySelectorAll(selector);
            
            if (elements.length > 0) {
                console.log(`💉 Injecting markdown content for ${filePath}`);
                // Convert markdown to HTML and inject
                // This would require a markdown parser or server-side rendering
                // For now, just log that content is available
                console.log(`📄 Content available for ${filePath} (${content.length} chars)`);
            }
        }

        /**
         * Injects decrypted image content
         */
        async injectImageContent(filePath, base64Content) {
            // Find img elements with src pointing to this file
            const images = document.querySelectorAll(`img[src*="${filePath}"]`);
            
            images.forEach(img => {
                try {
                    // Determine image type from file extension
                    const extension = filePath.split('.').pop().toLowerCase();
                    const mimeType = this.getMimeType(extension);
                    
                    // Create data URL from base64 content
                    const dataUrl = `data:${mimeType};base64,${base64Content}`;
                    
                    console.log(`🖼️ Injecting image: ${filePath}`);
                    img.src = dataUrl;
                } catch (error) {
                    console.error(`Failed to inject image ${filePath}:`, error);
                }
            });
        }

        /**
         * Generates consistent heading IDs for navigation
         */
        generateHeadingId(title) {
            return title.toLowerCase()
                .replace(/[^a-z0-9\s-]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .replace(/^-|-$/g, '');
        }

        /**
         * Gets MIME type for image extensions
         */
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

        /**
         * Fixes navigation links within injected corporate content
         */
        fixNavigationLinks(contentArea) {
            try {
                console.log('🔧 Fixing navigation links in corporate content...');
                
                // Find all links in the injected content
                const links = contentArea.querySelectorAll('a[href]');
                console.log(`Found ${links.length} links to process`);
                
                links.forEach((link, index) => {
                    const href = link.getAttribute('href');
                    console.log(`Processing link ${index}: ${href}`);
                    
                    // Handle different types of links
                    if (href.startsWith('#')) {
                        // Hash links - keep as is
                        console.log(`  Hash link - keeping as is: ${href}`);
                    } else if (href.startsWith('http://') || href.startsWith('https://')) {
                        // External links - keep as is
                        console.log(`  External link - keeping as is: ${href}`);
                    } else if (href.includes('Session9_Production_Agent_Deployment') || href.includes('Session9')) {
                        // Session 9 navigation - fix to work with current structure
                        // Use the correct HTML path
                        const session9Url = '/agentic-ai-nano/03_mcp-acp-a2a/Session9_Production_Agent_Deployment/';
                        link.setAttribute('href', session9Url);
                        console.log(`  Fixed Session 9 link: ${href} -> ${session9Url}`);
                    } else if (href.includes('Session8')) {
                        // Session 8 navigation - ensure correct path
                        const session8Url = '/agentic-ai-nano/03_mcp-acp-a2a/Session8_Advanced_Agent_Workflows/';
                        link.setAttribute('href', session8Url);
                        console.log(`  Fixed Session 8 link: ${href} -> ${session8Url}`);
                    } else if (href.startsWith('../') || href.startsWith('./')) {
                        // Relative links - convert to absolute based on site structure
                        let absoluteHref = href;
                        
                        if (href.startsWith('../')) {
                            // Go up from current module (03_mcp-acp-a2a)
                            absoluteHref = href.replace(/^\.\.\//, '/agentic-ai-nano/');
                        } else if (href.startsWith('./')) {
                            // Stay in current module
                            absoluteHref = href.replace(/^\.\//, '/agentic-ai-nano/03_mcp-acp-a2a/');
                        }
                        
                        link.setAttribute('href', absoluteHref);
                        console.log(`  Fixed relative link: ${href} -> ${absoluteHref}`);
                    } else if (!href.startsWith('/')) {
                        // Relative links without ./ prefix - assume current module
                        const absoluteHref = `/agentic-ai-nano/03_mcp-acp-a2a/${href}`;
                        link.setAttribute('href', absoluteHref);
                        console.log(`  Fixed unqualified link: ${href} -> ${absoluteHref}`);
                    }
                });
                
                console.log('✅ Navigation links fixed');
                
            } catch (error) {
                console.error('❌ Failed to fix navigation links:', error);
            }
        }

        /**
         * Test decryption with the test file
         */
        async testDecryption() {
            try {
                const basePath = window.location.pathname.includes('/agentic-ai-nano/') ? 
                    '/agentic-ai-nano/corporate-only/' : '../corporate-only/';
                const response = await fetch(basePath + 'test.encrypted.json');
                if (!response.ok) {
                    throw new Error('Test file not found');
                }

                const encryptedTest = await response.json();
                const key = await this.deriveKey(this.corporateKey);
                const decrypted = await this.decryptContent(encryptedTest, key);
                const testData = JSON.parse(decrypted);
                
                console.log('🧪 Decryption test result:', testData);
                return testData.test === true;
            } catch (error) {
                console.error('🧪 Decryption test failed:', error);
                return false;
            }
        }
    }

    // Make CorporateContentLoader available globally
    window.CorporateContentLoader = new CorporateContentLoader();

    // Auto-test decryption when loaded
    document.addEventListener('DOMContentLoaded', async () => {
        // Only test on corporate networks
        const hostname = window.location.hostname;
        if (!hostname.includes('github.io') && !hostname.includes('fwornle')) {
            console.log('🧪 Testing corporate content decryption...');
            const testResult = await window.CorporateContentLoader.testDecryption();
            console.log('🧪 Decryption test:', testResult ? 'PASSED' : 'FAILED');
        }
    });

})();