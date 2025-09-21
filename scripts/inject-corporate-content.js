#!/usr/bin/env node

/**
 * Post-build script to inject encrypted corporate content into HTML files
 * This ensures the corporate content loader can find the encrypted data
 */

const fs = require('fs');
const path = require('path');

const SITE_DIR = path.join(__dirname, '..', 'site');
const ENCRYPTED_CONTENT_PATH = path.join(__dirname, '..', 'docs-content', 'corporate-only', 'content.encrypted.json');

console.log('🔐 Injecting encrypted corporate content into HTML files...');

// Read encrypted content
let encryptedContent;
try {
    encryptedContent = fs.readFileSync(ENCRYPTED_CONTENT_PATH, 'utf8');
    console.log('✅ Loaded encrypted content from:', ENCRYPTED_CONTENT_PATH);
} catch (error) {
    console.error('❌ Failed to load encrypted content:', error.message);
    process.exit(1);
}

// Function to inject content into HTML file
function injectContentIntoHtml(filePath) {
    try {
        let htmlContent = fs.readFileSync(filePath, 'utf8');
        
        // Check if already injected to avoid duplicates
        if (htmlContent.includes('ENCRYPTED_CORPORATE_CONTENT_START')) {
            console.log('⏭️  Already injected:', path.relative(SITE_DIR, filePath));
            return;
        }
        
        // Create injection comment
        const injectionComment = `
<!-- ENCRYPTED_CORPORATE_CONTENT_START
${encryptedContent}
ENCRYPTED_CORPORATE_CONTENT_END -->`;
        
        // Inject before closing body tag
        if (htmlContent.includes('</body>')) {
            htmlContent = htmlContent.replace('</body>', `${injectionComment}\n</body>`);
            fs.writeFileSync(filePath, htmlContent, 'utf8');
            console.log('✅ Injected into:', path.relative(SITE_DIR, filePath));
        } else {
            console.log('⚠️  No </body> tag found in:', path.relative(SITE_DIR, filePath));
        }
    } catch (error) {
        console.error('❌ Failed to inject into', filePath, ':', error.message);
    }
}

// Define which HTML files need corporate content injection
const CORPORATE_PAGES = [
    '00_intro/coder/index.html',
    '00_intro/llmapi/index.html',
    '03_mcp-acp-a2a/Session10_Enterprise_Integration_Production_Deployment/index.html'
];

// Start processing
if (!fs.existsSync(SITE_DIR)) {
    console.error('❌ Site directory not found:', SITE_DIR);
    console.log('💡 Run "mkdocs build" first to generate the site');
    process.exit(1);
}

console.log('🔍 Processing corporate-specific HTML files in:', SITE_DIR);

// Only process the specific files that need corporate content
for (const relativePath of CORPORATE_PAGES) {
    const fullPath = path.join(SITE_DIR, relativePath);
    
    if (fs.existsSync(fullPath)) {
        injectContentIntoHtml(fullPath);
    } else {
        console.log('⚠️  Corporate page not found:', relativePath);
    }
}

console.log('🎉 Corporate content injection complete!');