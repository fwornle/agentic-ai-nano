#!/usr/bin/env python3
"""
Fix solution link spacing issues - add blank line between solution links and dividers.
This prevents GitHub from rendering the solution link as a heading.
"""

import os
import re
import glob

def fix_solution_link_spacing():
    """Add blank line between solution links and dividers to prevent heading rendering."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern: Solution link immediately followed by divider (causes heading rendering)
            # Fix: Add blank line between them
            pattern = r'(\[View Solutions →\]\([^)]*Test_Solutions\.md\))\n---'
            replacement = r'\1\n\n---'
            content = re.sub(pattern, replacement, content)
            
            # Also handle cases where there might already be some whitespace but not enough
            pattern2 = r'(\[View Solutions →\]\([^)]*Test_Solutions\.md\))\s*\n\s*---'
            replacement2 = r'\1\n\n---'
            content = re.sub(pattern2, replacement2, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Fixed spacing in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def verify_solution_link_spacing():
    """Verify all solution links have proper spacing."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    issues = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for solution links immediately followed by dividers
            if re.search(r'\[View Solutions →\]\([^)]*Test_Solutions\.md\)\s*\n\s*---', content):
                # Check if there's a blank line
                if not re.search(r'\[View Solutions →\]\([^)]*Test_Solutions\.md\)\s*\n\s*\n\s*---', content):
                    issues.append(f"{os.path.basename(file_path)}: Solution link needs blank line before divider")
        
        except Exception as e:
            print(f"❌ Error verifying {file_path}: {e}")
    
    return issues

def main():
    """Main function to fix solution link spacing."""
    print("=== Fixing Solution Link Spacing Issues ===\n")
    
    fixed_count = fix_solution_link_spacing()
    
    print(f"\n=== Verification ===")
    issues = verify_solution_link_spacing()
    
    if issues:
        print(f"❌ Found {len(issues)} remaining spacing issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All solution links have proper spacing!")
    
    print(f"\n✅ Fixed spacing in {fixed_count} files")
    print("All solution links now have blank lines before dividers to prevent heading rendering!")

if __name__ == "__main__":
    main()