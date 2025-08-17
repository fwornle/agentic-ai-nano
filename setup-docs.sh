#!/bin/bash

# Setup script for Material for MkDocs documentation site

echo "🚀 Setting up Material for MkDocs for Agentic AI Nano-Degree..."

# Create virtual environment if it doesn't exist
if [ ! -d "docs-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv docs-env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source docs-env/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p docs/stylesheets
mkdir -p docs/javascripts
mkdir -p includes

echo "✅ Setup complete!"
echo ""
echo "🏃 To run the documentation locally:"
echo "  1. Activate the environment: source docs-env/bin/activate"
echo "  2. Start the dev server: mkdocs serve"
echo "  3. Open your browser to: http://localhost:8000"
echo ""
echo "🚀 To deploy to GitHub Pages:"
echo "  1. Push your changes to the main branch"
echo "  2. GitHub Actions will automatically build and deploy"
echo "  3. Enable GitHub Pages in your repository settings"
echo ""
echo "📝 Don't forget to:"
echo "  - Update 'yourusername' in mkdocs.yml with your GitHub username"
echo "  - Update site_url with your actual GitHub Pages URL"
echo "  - Enable GitHub Pages in repository settings -> Pages -> GitHub Actions"