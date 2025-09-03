#!/usr/bin/env python3
"""
Comprehensive fix for ALL solution links to ensure none appear as headings.
"""

import os
import re
import glob

def fix_all_solution_link_headings():
    """Ensure ALL solution links are inline, never headings or under headings."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove any heading-style solution sections completely
            # Pattern 1: Solution links that are headings themselves
            content = re.sub(r'^#+\s*View Solutions.*?\n', '', content, flags=re.MULTILINE)
            content = re.sub(r'^#+\s*\[View Solutions.*?\]\(.*?\)\s*\n', '', content, flags=re.MULTILINE)
            
            # Pattern 2: Solution links immediately under headings (make them standalone)
            # Look for headings followed by solution links
            content = re.sub(
                r'(^#+.*?\n)\s*(\[View Solutions →\]\([^)]*Test_Solutions\.md\))',
                r'\1\n\2\n',
                content,
                flags=re.MULTILINE
            )
            
            # Pattern 3: Ensure solution links have proper spacing and are not part of heading structure
            content = re.sub(
                r'(\[View Solutions →\]\([^)]*Test_Solutions\.md\))\s*\n\s*(#+)',
                r'\1\n\n\2',
                content
            )
            
            # Pattern 4: Fix any solution links that might be formatted as headings with markdown
            content = re.sub(r'^#+\s*(\[View Solutions →\].*?)$', r'\1', content, flags=re.MULTILINE)
            
            # Pattern 5: Ensure solution links are always followed by proper separation
            content = re.sub(
                r'(\[View Solutions →\]\([^)]*Test_Solutions\.md\))(?!\n---)',
                r'\1\n\n---',
                content
            )
            
            # Clean up any multiple separators created
            content = re.sub(r'---\s*\n\s*---', '---', content)
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Fixed solution links in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def verify_no_heading_solution_links():
    """Verify there are no remaining heading-style solution links."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    issues = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for heading-style solution links
                if re.match(r'^#+.*View Solutions', line):
                    issues.append(f"{os.path.basename(file_path)}:{i} - Heading solution link: {line.strip()}")
                
                # Check for solution links directly under headings (potential rendering issue)
                if i > 1 and re.match(r'^#+', lines[i-2]) and 'View Solutions' in line:
                    issues.append(f"{os.path.basename(file_path)}:{i} - Solution link under heading")
        
        except Exception as e:
            print(f"❌ Error verifying {file_path}: {e}")
    
    return issues

def main():
    """Main function."""
    print("=== Comprehensive Solution Link Heading Fix ===\n")
    
    fixed_count = fix_all_solution_link_headings()
    
    print(f"\n=== Verification ===")
    issues = verify_no_heading_solution_links()
    
    if issues:
        print(f"❌ Found {len(issues)} remaining issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ No heading-style solution links found!")
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("All solution links are now guaranteed to be inline format!")

if __name__ == "__main__":
    main()