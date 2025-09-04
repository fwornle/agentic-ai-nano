#!/usr/bin/env python3
"""
Course Structure Fixer - Fix navigation consistency and broken links
"""

import os
import re
import json
from pathlib import Path

def standardize_navigation_emoji(content):
    """Standardize all navigation sections to use 🧭 emoji."""
    # Replace various navigation emojis with standard 🧭
    patterns = [
        (r'## 📝 Navigation', '## 🧭 Navigation'),
        (r'## 🔗 Navigation', '## 🧭 Navigation'),
        (r'## 📋 Navigation', '## 🧭 Navigation')
    ]
    
    for old_pattern, new_pattern in patterns:
        content = re.sub(old_pattern, new_pattern, content)
    
    return content

def fix_wildcard_links(content, file_path):
    """Fix Session*.md wildcard links to proper file names."""
    # Common fixes for wildcard patterns
    relative_path = str(file_path).replace('/Users/q284340/Agentic/nano-degree/docs-content/', '')
    
    # Extract session number from filename
    session_match = re.search(r'Session(\d+)', os.path.basename(file_path))
    if not session_match:
        return content
    
    current_session = int(session_match.group(1))
    
    # Fix common wildcard patterns
    fixes = []
    
    # Previous session links
    if current_session > 0:
        prev_session = current_session - 1
        fixes.append((
            rf'Session{current_session - 1}_\*\.md',
            f'Session{prev_session}_*.md'
        ))
    
    # Next session links
    next_session = current_session + 1
    fixes.append((
        rf'Session{next_session}_\*\.md',
        f'Session{next_session}_*.md'  
    ))
    
    for old, new in fixes:
        content = re.sub(old, new, content)
    
    return content

def ensure_solution_links(content):
    """Ensure test sections have solution links."""
    lines = content.split('\n')
    modified = False
    
    # Find test sections
    for i, line in enumerate(lines):
        if re.match(r'## 📝 Multiple Choice Test', line):
            # Look for end of test (next ## header or end of file)
            test_end = len(lines) - 1
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('## '):
                    test_end = j - 1
                    break
            
            # Check if solution link exists in test section
            has_solution = False
            for k in range(i, test_end + 1):
                if 'View Solutions' in lines[k] or 'Solutions →' in lines[k]:
                    has_solution = True
                    break
            
            # Add solution link if missing
            if not has_solution:
                # Insert before the next ## section
                solution_line = "\n[View Solutions →](Session*_Test_Solutions.md)\n"
                lines.insert(test_end + 1, solution_line)
                modified = True
    
    return '\n'.join(lines) if modified else content

def process_file(file_path):
    """Process a single file for fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return
    
    original_content = content
    
    # Apply fixes
    content = standardize_navigation_emoji(content)
    content = fix_wildcard_links(content, file_path)
    content = ensure_solution_links(content)
    
    # Only write if changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
    
    return False

def main():
    print("🔧 Fixing course structure issues...")
    
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    fixed_count = 0
    total_count = 0
    
    # Process all markdown files
    for md_file in base_dir.rglob('*.md'):
        total_count += 1
        if process_file(md_file):
            fixed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Total files processed: {total_count}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Files unchanged: {total_count - fixed_count}")

if __name__ == "__main__":
    main()