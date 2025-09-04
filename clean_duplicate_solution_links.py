#!/usr/bin/env python3
"""
Clean up duplicate solution links created by the auto-fixer
"""

import os
import re
from pathlib import Path

def clean_duplicate_solution_links(content):
    """Remove duplicate solution links, keeping the more specific ones."""
    lines = content.split('\n')
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is a solution link
        if '[View Solutions →]' in line:
            # Look ahead for another solution link
            next_solution_found = False
            j = i + 1
            while j < len(lines) and j < i + 5:  # Look within next 5 lines
                if '[View Solutions →]' in lines[j]:
                    next_solution_found = True
                    # Keep the more specific link (not the wildcard one)
                    if 'Session*_Test_Solutions.md' in line and 'Session*_Test_Solutions.md' not in lines[j]:
                        # Skip current line (wildcard), keep the specific one
                        i = j
                        break
                    elif 'Session*_Test_Solutions.md' in lines[j] and 'Session*_Test_Solutions.md' not in line:
                        # Keep current line (specific), skip the wildcard one later
                        cleaned_lines.append(line)
                        i += 1
                        # Skip the wildcard line when we get to it
                        skip_next_solution = True
                        break
                j += 1
            
            if not next_solution_found:
                cleaned_lines.append(line)
                i += 1
        else:
            cleaned_lines.append(line)
            i += 1
    
    return '\n'.join(cleaned_lines)

def process_file(file_path):
    """Process a single file to clean duplicate links."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False
    
    original_content = content
    content = clean_duplicate_solution_links(content)
    
    # Also fix specific wildcard pattern issues
    content = re.sub(r'\[View Solutions →\]\(Session\*_Test_Solutions\.md\)', 
                    lambda m: '', content)
    
    # Clean up extra empty lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
    
    return False

def main():
    print("🧹 Cleaning duplicate solution links...")
    
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    fixed_count = 0
    
    # Process all solution files 
    for md_file in base_dir.rglob('*Test_Solutions.md'):
        if process_file(md_file):
            print(f"✅ Cleaned: {md_file}")
            fixed_count += 1
    
    print(f"\n📊 Cleaned {fixed_count} solution files")

if __name__ == "__main__":
    main()