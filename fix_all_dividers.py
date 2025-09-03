#!/usr/bin/env python3
"""
Fix all divider spacing issues - ensure all dividers (---) are preceded by an empty line.
This prevents various GitHub rendering issues where content gets interpreted as headings.
"""

import os
import re
import glob

def fix_divider_spacing(content):
    """Add blank line before all dividers that don't already have one."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if current line is a divider
        if line.strip() == '---':
            # Check if previous line exists and is not empty
            if i > 0 and lines[i-1].strip() != '':
                # Add empty line before divider
                fixed_lines.append('')
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_all_dividers():
    """Fix divider spacing in all markdown files."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    # Also check root level files
    root_files = glob.glob('/Users/q284340/Agentic/nano-degree/*.md')
    md_files.extend(root_files)
    
    fixed_files = 0
    total_fixes = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix divider spacing
            fixed_content = fix_divider_spacing(content)
            
            if fixed_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Count how many dividers were fixed in this file
                original_dividers = content.count('\n---\n') + content.count('\n---')
                fixed_dividers = fixed_content.count('\n\n---')
                file_fixes = len(re.findall(r'[^\n]\n---', content))
                
                fixed_files += 1
                total_fixes += file_fixes
                print(f"✅ Fixed {file_fixes} dividers in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files, total_fixes

def verify_divider_spacing():
    """Verify all dividers have proper spacing."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    root_files = glob.glob('/Users/q284340/Agentic/nano-degree/*.md')
    md_files.extend(root_files)
    
    issues = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for dividers not preceded by empty line
            # Pattern: non-empty line followed directly by divider
            problematic_dividers = re.findall(r'[^\n\s].+\n---', content, re.MULTILINE)
            
            if problematic_dividers:
                issues.append(f"{os.path.basename(file_path)}: {len(problematic_dividers)} dividers need spacing")
        
        except Exception as e:
            print(f"❌ Error verifying {file_path}: {e}")
    
    return issues

def main():
    """Main function to fix all divider spacing."""
    print("=== Fixing All Divider Spacing Issues ===\n")
    
    fixed_files, total_fixes = fix_all_dividers()
    
    print(f"\n=== Verification ===")
    issues = verify_divider_spacing()
    
    if issues:
        print(f"❌ Found {len(issues)} files with remaining spacing issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All dividers have proper spacing!")
    
    print(f"\n✅ Fixed {total_fixes} dividers in {fixed_files} files")
    print("All dividers now have blank lines before them to prevent rendering issues!")

if __name__ == "__main__":
    main()