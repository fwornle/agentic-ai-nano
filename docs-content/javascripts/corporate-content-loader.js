/**
 * Corporate Content Loader
 * 
 * Handles loading and decrypting corporate content when accessed from 
 * BMW corporate network. Works with content encrypted by encrypt-corporate-content.js
 */

(function() {
    'use strict';

    // Corporate content loader class
    class CorporateContentLoader {
        constructor() {
            // Adjust path based on site structure
            const basePath = window.location.pathname.includes('/agentic-ai-nano/') ? 
                '/agentic-ai-nano/corporate-only/' : '../corporate-only/';
            this.encryptedContentPath = basePath + 'content.encrypted.json';
            console.log('🔍 Corporate content path:', this.encryptedContentPath);
            console.log('🔍 Current pathname:', window.location.pathname);
            this.corporateKey = 'bmw-corporate-network-2024-secure'; // Same as encryption script
            this.loadedContent = null;
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
         * Loads and decrypts corporate content
         */
        async load() {
            try {
                console.log('🔐 Loading encrypted corporate content...');
                
                // Try multiple potential paths for encrypted content
                const potentialPaths = [
                    this.encryptedContentPath,
                    '/agentic-ai-nano/corporate-only/content.encrypted.json',
                    'corporate-only/content.encrypted.json',
                    '../corporate-only/content.encrypted.json'
                ];
                
                let response = null;
                let workingPath = null;
                
                for (const path of potentialPaths) {
                    try {
                        console.log(`🔍 Trying path: ${path}`);
                        response = await fetch(path);
                        if (response.ok) {
                            workingPath = path;
                            console.log(`✅ Found content at: ${path}`);
                            break;
                        } else {
                            console.log(`❌ Failed ${path}: ${response.status}`);
                        }
                    } catch (e) {
                        console.log(`❌ Error ${path}:`, e.message);
                    }
                }
                
                if (!response || !response.ok) {
                    throw new Error(`Failed to fetch encrypted content from any path. Tried: ${potentialPaths.join(', ')}`);
                }

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
            
            let targetFile = null;
            if (currentPath.includes('/00_intro/coder/')) {
                targetFile = '00_intro/coder-detailed.md';
                console.log('📄 Matched coder page - will load corporate content');
            } else if (currentPath.includes('/00_intro/llmapi/')) {
                targetFile = '00_intro/llmapi-detailed.md';
                console.log('📄 Matched llmapi page - will load corporate content');
            } else if (currentPath.includes('/03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/') || 
                       currentPath.includes('session10-corporate-only') ||
                       currentPath.includes('Session9_Production_Agent_Deployment/Session10') ||
                       window.location.hash.includes('session10')) {
                targetFile = '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment.md';
                console.log('📄 Matched Session10 page - will load corporate content');
            } else {
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
         * Replaces the main page content with corporate markdown content
         */
        async replacePageContent(markdownContent) {
            try {
                // Find the main content area - be more specific to preserve sidebar
                const contentArea = document.querySelector('.md-content__inner article') || 
                                   document.querySelector('.md-content__inner') || 
                                   document.querySelector('article') ||
                                   document.querySelector('main');
                
                if (!contentArea) {
                    console.error('Could not find main content area to replace');
                    return;
                }
                
                console.log('🔄 Replacing main content area with corporate content');
                
                // First, replace image references with base64 data URLs
                let processedContent = await this.replaceImagesWithBase64(markdownContent);
                
                // Simple markdown to HTML conversion for key elements
                // IMPORTANT: Process images BEFORE links to avoid conflicts
                let htmlContent = processedContent
                    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
                    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
                    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
                    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.+?)\*/g, '<em>$1</em>')
                    .replace(/`(.+?)`/g, '<code>$1</code>')
                    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">')  // Images first
                    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')       // Then links
                    .replace(/^- (.+)$/gm, '<li>$1</li>')
                    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
                    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
                    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
                    .replace(/\n\n/g, '</p><p>')
                    .replace(/^(?!<[h1-6]|<ul|<ol|<pre|<script)(.+)$/gm, '<p>$1</p>')
                    .replace(/<p><\/p>/g, '');
                
                // Replace the content
                contentArea.innerHTML = htmlContent;
                
                console.log('✅ Corporate content successfully injected into page');
                
            } catch (error) {
                console.error('❌ Failed to replace page content:', error);
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