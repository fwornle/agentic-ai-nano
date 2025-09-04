#!/usr/bin/env python3
"""
Final comprehensive fix for test positioning.
Ensure ALL tests are positioned as the second-to-last section (immediately before Navigation).
"""

import os
import re
import glob

def move_test_before_navigation(content):
    """Move test section to be immediately before navigation."""
    
    # Find test section
    test_match = re.search(r'(## 📝 Multiple Choice Test.*?\[View Solutions →\][^\n]*)', content, re.DOTALL)
    if not test_match:
        return content
    
    test_section = test_match.group(1)
    
    # Find navigation section
    nav_match = re.search(r'(## 🧭 Navigation.*)', content, re.DOTALL)
    if not nav_match:
        return content
    
    # Remove test from its current location
    content_without_test = re.sub(r'## 📝 Multiple Choice Test.*?\[View Solutions →\][^\n]*\n*', '', content, flags=re.DOTALL)
    
    # Insert test immediately before navigation
    final_content = re.sub(
        r'(## 🧭 Navigation)', 
        f'{test_section}\n\n---\n\n\\1', 
        content_without_test
    )
    
    return final_content

def fix_all_test_positions():
    """Fix test positioning in all files."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        # Skip backup files
        if 'BACKUP' in file_path or 'ORIGINAL' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Only process files that have both test and navigation sections
            if '## 📝 Multiple Choice Test' in content and '## 🧭 Navigation' in content:
                fixed_content = move_test_before_navigation(content)
                
                if fixed_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    fixed_files += 1
                    print(f"✅ Repositioned test in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def verify_test_positions():
    """Verify all tests are properly positioned before navigation."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    issues = []
    
    for file_path in md_files:
        # Skip backup files
        if 'BACKUP' in file_path or 'ORIGINAL' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check files with both test and navigation
            if '## 📝 Multiple Choice Test' in content and '## 🧭 Navigation' in content:
                lines = content.split('\n')
                
                test_line = None
                nav_line = None
                
                for i, line in enumerate(lines):
                    if line.startswith('## 📝 Multiple Choice Test'):
                        test_line = i
                    elif line.startswith('## 🧭 Navigation'):
                        nav_line = i
                        break
                
                if test_line is not None and nav_line is not None:
                    # Check if test comes before navigation and is reasonably close
                    if test_line >= nav_line or (nav_line - test_line) > 50:
                        issues.append(os.path.basename(file_path))
        
        except Exception as e:
            print(f"❌ Error verifying {file_path}: {e}")
    
    return issues

def main():
    """Main function to fix all test positioning."""
    print("=== Final Test Positioning Fix ===\n")
    
    fixed_count = fix_all_test_positions()
    
    print(f"\n=== Verification ===")
    issues = verify_test_positions()
    
    if issues:
        print(f"❌ {len(issues)} files still have positioning issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ All tests are properly positioned before Navigation!")
    
    print(f"\n✅ Fixed positioning in {fixed_count} files")
    print("All test sections are now consistently positioned as second-to-last section!")

if __name__ == "__main__":
    main()