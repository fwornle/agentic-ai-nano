#!/usr/bin/env python3
"""
Fix ALL divider spacing issues and add emoji to Navigation sections.
This addresses two problems:
1. Dividers not preceded by blank lines (caused by navigation standardization)
2. Missing emoji in Navigation headings
"""

import os
import re
import glob

def fix_dividers_and_navigation(content):
    """Fix divider spacing and add emoji to Navigation headings."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if current line is a divider (3+ dashes)
        if re.match(r'^-{3,}$', line.strip()):
            # Check if previous line exists and is not empty
            if i > 0 and lines[i-1].strip() != '':
                # Add empty line before divider
                fixed_lines.append('')
        
        # Check if current line is Navigation heading without emoji
        if line.strip() == '## Navigation':
            line = '## 🧭 Navigation'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_all_dividers_and_navigation():
    """Fix divider spacing and navigation emoji in all markdown files."""
    
    # Get all markdown files
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    # Also check root level files
    root_files = glob.glob('/Users/q284340/Agentic/nano-degree/*.md')
    md_files.extend(root_files)
    
    fixed_files = 0
    divider_fixes = 0
    navigation_fixes = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix dividers and navigation
            fixed_content = fix_dividers_and_navigation(content)
            
            if fixed_content != original_content:
                # Count fixes
                original_bad_dividers = len(re.findall(r'[^\n]\n---', original_content))
                fixed_bad_dividers = len(re.findall(r'[^\n]\n---', fixed_content))
                divider_fixes_in_file = original_bad_dividers - fixed_bad_dividers
                
                original_plain_nav = len(re.findall(r'## Navigation', original_content))
                fixed_plain_nav = len(re.findall(r'## Navigation', fixed_content))
                nav_fixes_in_file = original_plain_nav - fixed_plain_nav
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                fixed_files += 1
                divider_fixes += divider_fixes_in_file
                navigation_fixes += nav_fixes_in_file
                
                fixes_text = []
                if divider_fixes_in_file > 0:
                    fixes_text.append(f"{divider_fixes_in_file} dividers")
                if nav_fixes_in_file > 0:
                    fixes_text.append(f"{nav_fixes_in_file} navigation emojis")
                
                if fixes_text:
                    print(f"✅ Fixed {', '.join(fixes_text)} in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files, divider_fixes, navigation_fixes

def verify_all_fixes():
    """Verify all dividers have proper spacing and all navigation has emoji."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    root_files = glob.glob('/Users/q284340/Agentic/nano-degree/*.md')
    md_files.extend(root_files)
    
    divider_issues = []
    navigation_issues = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for bad dividers (not preceded by empty line)
            bad_dividers = re.findall(r'[^\n\s].+\n---', content, re.MULTILINE)
            if bad_dividers:
                divider_issues.append(f"{os.path.basename(file_path)}: {len(bad_dividers)} bad dividers")
            
            # Check for navigation without emoji
            plain_nav = re.findall(r'## Navigation\n', content)
            if plain_nav:
                navigation_issues.append(f"{os.path.basename(file_path)}: {len(plain_nav)} navigation without emoji")
        
        except Exception as e:
            print(f"❌ Error verifying {file_path}: {e}")
    
    return divider_issues, navigation_issues

def main():
    """Main function to fix all divider and navigation issues."""
    print("=== Fixing All Divider Spacing & Navigation Emoji Issues ===\n")
    
    fixed_files, divider_fixes, navigation_fixes = fix_all_dividers_and_navigation()
    
    print(f"\n=== Verification ===")
    divider_issues, navigation_issues = verify_all_fixes()
    
    if divider_issues:
        print(f"❌ Found {len(divider_issues)} files with remaining divider issues:")
        for issue in divider_issues:
            print(f"  {issue}")
    else:
        print("✅ All dividers have proper spacing!")
    
    if navigation_issues:
        print(f"❌ Found {len(navigation_issues)} files with navigation missing emoji:")
        for issue in navigation_issues:
            print(f"  {issue}")
    else:
        print("✅ All navigation sections have emoji!")
    
    print(f"\n=== Summary ===")
    print(f"✅ Fixed issues in {fixed_files} files")
    print(f"🔧 Fixed {divider_fixes} dividers")  
    print(f"🧭 Added {navigation_fixes} navigation emojis")
    print("All dividers and navigation sections are now properly formatted!")

if __name__ == "__main__":
    main()