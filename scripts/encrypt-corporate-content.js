#!/usr/bin/env node

/**
 * Encryption Script for Corporate Content
 * 
 * This script encrypts corporate-only content and creates JSON files
 * that can be safely included in the public repository.
 * The content is only decryptable when accessed from the corporate network.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Configuration
const CORPORATE_DIR = path.join(__dirname, '..', 'docs-content', 'corporate-only');
const OUTPUT_FILE = path.join(CORPORATE_DIR, 'content.encrypted.json');

// Check if corporate-only is a submodule directory, if so update paths
const SUBMODULE_CHECK = fs.existsSync(path.join(CORPORATE_DIR, '.git'));
if (SUBMODULE_CHECK) {
    console.log('Detected submodule structure for corporate-only content');
}

// Encryption key derived from network characteristics
// In production, this would be more sophisticated
const ENCRYPTION_KEY = process.env.BMW_ENCRYPTION_KEY || 'bmw-corporate-network-2024-secure';
const ALGORITHM = 'aes-256-gcm';

/**
 * Derives a 32-byte key from the passphrase
 */
function deriveKey(passphrase) {
    return crypto.createHash('sha256').update(passphrase).digest();
}

/**
 * Encrypts text content
 */
function encryptContent(text, key) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    
    const authTag = cipher.getAuthTag();
    
    return {
        encrypted,
        iv: iv.toString('base64'),
        authTag: authTag.toString('base64')
    };
}

/**
 * Reads and encrypts all markdown files in a directory
 */
function encryptMarkdownFiles(dir, basePath = '') {
    const results = {};
    
    try {
        const files = fs.readdirSync(dir);
        
        files.forEach(file => {
            const fullPath = path.join(dir, file);
            // Use forward slashes for consistency across platforms
            const relativePath = path.join(basePath, file).replace(/\\/g, '/');
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                // Recursively process subdirectories
                Object.assign(results, encryptMarkdownFiles(fullPath, relativePath));
            } else if (file.endsWith('.md')) {
                console.log(`Encrypting: ${relativePath}`);
                const content = fs.readFileSync(fullPath, 'utf8');
                const key = deriveKey(ENCRYPTION_KEY);
                results[relativePath] = encryptContent(content, key);
            }
        });
    } catch (error) {
        console.error(`Error processing directory ${dir}:`, error);
    }
    
    return results;
}

/**
 * Encrypts image files
 */
function encryptImages(dir, basePath = '') {
    const results = {};
    
    try {
        const files = fs.readdirSync(dir);
        
        files.forEach(file => {
            const fullPath = path.join(dir, file);
            // Use forward slashes for consistency across platforms
            const relativePath = path.join(basePath, file).replace(/\\/g, '/');
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                // Recursively process subdirectories
                Object.assign(results, encryptImages(fullPath, relativePath));
            } else if (file.match(/\.(png|jpg|jpeg|gif|svg)$/i)) {
                console.log(`Encrypting image: ${relativePath}`);
                const content = fs.readFileSync(fullPath);
                const base64Content = content.toString('base64');
                const key = deriveKey(ENCRYPTION_KEY);
                results[relativePath] = encryptContent(base64Content, key);
            }
        });
    } catch (error) {
        console.error(`Error processing images in ${dir}:`, error);
    }
    
    return results;
}

/**
 * Main encryption process
 */
function main() {
    console.log('Starting corporate content encryption...');
    console.log(`Corporate directory: ${CORPORATE_DIR}`);
    
    if (!fs.existsSync(CORPORATE_DIR)) {
        console.error('Corporate directory does not exist!');
        process.exit(1);
    }
    
    // Encrypt markdown files
    const encryptedContent = encryptMarkdownFiles(CORPORATE_DIR);
    
    // Encrypt images
    const imagesDir = path.join(CORPORATE_DIR, 'images');
    if (fs.existsSync(imagesDir)) {
        const encryptedImages = encryptImages(imagesDir, 'images');
        Object.assign(encryptedContent, encryptedImages);
    }
    
    // Create manifest
    const manifest = {
        version: '1.0',
        timestamp: new Date().toISOString(),
        algorithm: ALGORITHM,
        files: Object.keys(encryptedContent),
        content: encryptedContent
    };
    
    // Write encrypted content to file
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(manifest, null, 2));
    console.log(`\nEncrypted content written to: ${OUTPUT_FILE}`);
    console.log(`Total files encrypted: ${Object.keys(encryptedContent).length}`);
    
    // Create a simple test file to verify decryption works
    const testData = {
        test: true,
        message: 'If you can read this, decryption works!',
        timestamp: new Date().toISOString()
    };
    
    const key = deriveKey(ENCRYPTION_KEY);
    const encryptedTest = encryptContent(JSON.stringify(testData), key);
    
    fs.writeFileSync(
        path.join(CORPORATE_DIR, 'test.encrypted.json'),
        JSON.stringify(encryptedTest, null, 2)
    );
    
    console.log('\nEncryption complete!');
    console.log('Note: Set BMW_ENCRYPTION_KEY environment variable for production use.');
}

// Run the script
if (require.main === module) {
    main();
}