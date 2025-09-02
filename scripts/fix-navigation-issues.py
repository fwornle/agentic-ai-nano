#!/usr/bin/env python3
"""
Navigation Cleanup Script

This script fixes common formatting issues from the navigation standardization:
1. Removes "No newline at end of file" issues
2. Removes duplicate navigation sections
3. Ensures proper line endings
"""

import os
import re
from pathlib import Path
from typing import List

def clean_file_content(content: str) -> str:
    """Clean up common formatting issues in file content."""
    
    # Remove "No newline at end of file" artifacts
    content = re.sub(r'\s*No newline at end of file\s*', '', content)
    
    # Remove duplicate navigation sections
    # Keep only the last navigation section
    nav_sections = list(re.finditer(r'---\s*\n\n## 🧭 Navigation.*?(?=\n---\s*$|\Z)', content, re.DOTALL | re.MULTILINE))
    
    if len(nav_sections) > 1:
        # Remove all but the last navigation section
        for nav_match in nav_sections[:-1]:
            content = content[:nav_match.start()] + content[nav_match.end():]
            # Recalculate positions after removal
            nav_sections = list(re.finditer(r'---\s*\n\n## 🧭 Navigation.*?(?=\n---\s*$|\Z)', content, re.DOTALL | re.MULTILINE))
    
    # Ensure proper line endings and remove excessive whitespace
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip completely empty lines at the end, but preserve intentional spacing
        cleaned_lines.append(line.rstrip())
    
    # Remove trailing empty lines
    while cleaned_lines and cleaned_lines[-1] == '':
        cleaned_lines.pop()
    
    # Ensure file ends with single newline
    content = '\n'.join(cleaned_lines) + '\n'
    
    # Fix any double dashes at the end
    content = re.sub(r'\n---\s*\n--\s*$', '\n---\n', content)
    
    return content

def process_file(file_path: Path) -> bool:
    """Process a single file to fix navigation issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        cleaned_content = clean_file_content(content)
        
        # Only write if changes were made
        if cleaned_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all markdown files."""
    base_dir = Path("/Users/q284340/Agentic/nano-degree/docs-content")
    
    processed_count = 0
    
    # Process all markdown files
    for md_file in base_dir.rglob("*.md"):
        # Skip certain directories
        if 'docs-env' in str(md_file) or '.git' in str(md_file):
            continue
            
        if process_file(md_file):
            processed_count += 1
            print(f"  Cleaned: {md_file.name}")
    
    print(f"\nCleaned {processed_count} files total.")

if __name__ == "__main__":
    main()