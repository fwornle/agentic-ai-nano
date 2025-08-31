#!/usr/bin/env python3
"""
Fix test formatting in markdown files:
- Ensure 2 spaces at the end of each question
- Ensure 2 spaces at the end of each answer option
- Ensure first answer follows immediately after question (no blank line)
"""

import sys
import re
from pathlib import Path

def fix_test_formatting(content: str) -> str:
    """Fix formatting of multiple choice tests in markdown content."""
    
    lines = content.split('\n')
    fixed_lines = []
    in_test_section = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if we're entering a test section
        if re.match(r'^#+.*(?:Multiple Choice Test|Test Questions|Module Test)', line, re.IGNORECASE):
            in_test_section = True
            fixed_lines.append(line)
            i += 1
            continue
        
        # Check if we're leaving the test section
        if in_test_section and (line.startswith('---') or re.match(r'^#+.*(?:Navigation|Summary)', line)):
            in_test_section = False
        
        if in_test_section:
            # Handle question lines
            if re.match(r'^\*\*Question \d+:', line):
                # Ensure 2 spaces at the end of question line
                if not line.endswith('  '):
                    line = line.rstrip() + '  '
                fixed_lines.append(line)
                
                # Skip any blank lines between question and first answer
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                
                # Add the first answer directly after question (no blank line)
                if j < len(lines):
                    i = j - 1  # Will be incremented at end of loop
            
            # Handle answer option lines
            elif re.match(r'^[A-Z]\)', line):
                # Ensure 2 spaces at the end of answer option
                if not line.endswith('  '):
                    line = line.rstrip() + '  '
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def process_file(file_path: Path) -> bool:
    """Process a single markdown file to fix test formatting."""
    
    try:
        content = file_path.read_text(encoding='utf-8')
        fixed_content = fix_test_formatting(content)
        
        if content != fixed_content:
            file_path.write_text(fixed_content, encoding='utf-8')
            print(f"✅ Fixed: {file_path.name}")
            return True
        else:
            print(f"✓ Already correct: {file_path.name}")
            return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix-test-formatting.py <file_or_directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if target.is_file():
        process_file(target)
    elif target.is_dir():
        fixed_count = 0
        total_count = 0
        
        # Process all markdown files
        for md_file in sorted(target.glob('**/*.md')):
            # Skip test solution files (we'll process those separately if needed)
            if 'Test_Solutions' not in str(md_file):
                total_count += 1
                if process_file(md_file):
                    fixed_count += 1
        
        print(f"\n📊 Summary: Fixed {fixed_count}/{total_count} files")
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)

if __name__ == "__main__":
    main()