#!/usr/bin/env python3
"""
Fix list formatting across all markdown files in the nano-degree course.
Adds two trailing spaces to:
1. Sentences that introduce lists (ending with :)
2. All list items (starting with -, *, or numbers)
"""

import os
import re
from pathlib import Path

def fix_list_formatting(content):
    """Fix list formatting in markdown content."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines and code blocks
        if not line.strip():
            fixed_lines.append(line)
            continue
            
        # Skip lines that are in code blocks (between ``` markers)
        in_code_block = False
        for j in range(i):
            if lines[j].strip().startswith('```'):
                in_code_block = not in_code_block
        
        if in_code_block:
            fixed_lines.append(line)
            continue
            
        # Skip inline code
        if '`' in line and line.count('`') >= 2:
            fixed_lines.append(line)
            continue
            
        original_line = line
        
        # Check if this line introduces a list (next line is a list item)
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and (next_line.startswith('- ') or next_line.startswith('* ') or 
                             re.match(r'^\d+\. ', next_line)):
                # This line introduces a list
                if line.endswith(':') and not line.endswith('  '):
                    line = line + '  '
                elif not line.endswith('  ') and not line.endswith(':::'):
                    line = line + '  '
        
        # Fix list items themselves
        if re.match(r'^(\s*)[-*] ', line):  # Unordered list items
            if not line.endswith('  '):
                line = line + '  '
        elif re.match(r'^(\s*)\d+\. ', line):  # Numbered list items
            if not line.endswith('  '):
                line = line + '  '
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_list_formatting(content)
        
        if content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all markdown files in the course."""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    
    if not base_dir.exists():
        print(f"Base directory not found: {base_dir}")
        return
    
    total_files = 0
    fixed_files = 0
    
    # Find all markdown files
    for md_file in base_dir.rglob('*.md'):
        # Skip certain directories
        if any(skip in str(md_file) for skip in ['venv', 'node_modules', '.git']):
            continue
            
        total_files += 1
        if process_file(md_file):
            fixed_files += 1
    
    print(f"\nProcessed {total_files} files, fixed {fixed_files} files")

if __name__ == '__main__':
    main()