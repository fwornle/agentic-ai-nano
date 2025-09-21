#!/bin/bash

# Automated build script that includes corporate content injection
# Usage: ./scripts/build-with-corporate-content.sh

echo "🚀 Building nano-degree site with corporate content..."

# Step 1: Clean build
echo "📦 Building site with MkDocs..."
mkdocs build --clean

# Step 2: Inject encrypted corporate content into HTML files  
echo "🔐 Injecting encrypted corporate content..."
node scripts/inject-corporate-content.js

# Step 3: Verify injection
ENCRYPTED_COUNT=$(find site -name "*.html" -exec grep -l "ENCRYPTED_CORPORATE_CONTENT" {} \; | wc -l)
echo "✅ Corporate content injected into $ENCRYPTED_COUNT HTML files"

# Step 4: Build complete
echo "🎉 Build complete! Site ready for deployment."
echo "📁 Generated site in: $(pwd)/site"

# Optional: Start local server for testing
if [ "$1" = "--serve" ]; then
    echo "🌐 Starting local server on http://localhost:8000"
    cd site && python -m http.server 8000
fi