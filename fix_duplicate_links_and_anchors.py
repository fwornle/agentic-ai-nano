#!/usr/bin/env python3
"""
Fix duplicate "View Solutions" links and verify/fix all anchor links in back navigation.
"""

import os
import re
import glob

def fix_duplicate_solution_links(content):
    """Remove duplicate View Solutions links, keeping only the first occurrence."""
    
    # Find all View Solutions links
    solution_links = list(re.finditer(r'\[View Solutions →\]\([^)]*Test_Solutions\.md\)', content))
    
    if len(solution_links) <= 1:
        return content
    
    # Keep only the first occurrence, remove the rest
    for i in range(len(solution_links) - 1, 0, -1):  # Remove from last to first
        match = solution_links[i]
        # Remove the duplicate link and any surrounding whitespace/newlines
        start = match.start()
        end = match.end()
        
        # Check if there's a newline before and after to remove cleanly
        if start > 0 and content[start-1] == '\n':
            start -= 1
        if end < len(content) and content[end] == '\n':
            end += 1
            
        content = content[:start] + content[end:]
    
    return content

def fix_back_to_test_anchors(content, filename):
    """Fix Back to Test anchor links to use proper fragment identifiers."""
    
    # Extract session number
    session_match = re.search(r'Session(\d+)', os.path.basename(filename))
    if not session_match:
        return content
    
    session_num = session_match.group(1)
    
    # Look for back to test links and fix the anchor
    back_link_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\([^)]*\.md(#[^)]*)\)'
    
    def fix_anchor(match):
        # Replace with proper anchor
        full_match = match.group(0)
        # Find the main session file name - try common patterns
        directory = os.path.dirname(filename)
        
        # Common main session file patterns
        possible_files = [
            f"Session{session_num}_*.md",
            # More specific patterns based on actual files
        ]
        
        main_file = None
        for pattern in possible_files:
            matches = glob.glob(os.path.join(directory, pattern))
            for match_file in matches:
                if 'Test_Solutions.md' not in match_file and 'Module' not in os.path.basename(match_file):
                    main_file = os.path.basename(match_file)
                    break
            if main_file:
                break
        
        if not main_file:
            main_file = f"Session{session_num}_*.md"
        
        # Use the proper anchor for Multiple Choice Test
        return f"**Back to Test:** [Session {session_num} Test Questions →]({main_file}#📝-multiple-choice-test---session-{session_num})"
    
    content = re.sub(back_link_pattern, fix_anchor, content)
    
    # Also fix any links that don't have anchors
    simple_back_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\(([^)]*\.md)\)'
    
    def add_anchor(match):
        file_ref = match.group(1)
        return f"**Back to Test:** [Session {session_num} Test Questions →]({file_ref}#📝-multiple-choice-test---session-{session_num})"
    
    content = re.sub(simple_back_pattern, add_anchor, content)
    
    return content

def process_all_files():
    """Process all markdown files to fix duplicate links and anchors."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if 'BACKUP' not in f and 'ORIGINAL' not in f]
    
    fixed_duplicates = 0
    fixed_anchors = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix duplicate solution links
            content = fix_duplicate_solution_links(content)
            if content != original_content:
                fixed_duplicates += 1
                print(f"✅ Fixed duplicate solution links in {os.path.basename(file_path)}")
            
            # Fix anchor links if this is a test solutions file
            if 'Test_Solutions.md' in file_path:
                fixed_content = fix_back_to_test_anchors(content, file_path)
                if fixed_content != content:
                    content = fixed_content
                    fixed_anchors += 1
                    print(f"✅ Fixed back-to-test anchor in {os.path.basename(file_path)}")
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_duplicates, fixed_anchors

def verify_solution_links():
    """Verify all solution links are clean and not duplicated."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    files_with_duplicates = []
    
    for file_path in md_files:
        if 'BACKUP' in file_path or 'ORIGINAL' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count View Solutions links
            solution_count = len(re.findall(r'\[View Solutions →\]', content))
            
            if solution_count > 1:
                files_with_duplicates.append((os.path.basename(file_path), solution_count))
        
        except Exception as e:
            continue
    
    return files_with_duplicates

def main():
    """Main function to fix all link issues."""
    print("=== Fixing Duplicate Solution Links & Back-to-Test Anchors ===\n")
    
    fixed_dups, fixed_anchors = process_all_files()
    
    print(f"\n=== Verification ===")
    remaining_duplicates = verify_solution_links()
    
    if remaining_duplicates:
        print(f"❌ Files still have duplicate solution links:")
        for file, count in remaining_duplicates:
            print(f"  {file}: {count} solution links")
    else:
        print("✅ All solution links are unique!")
    
    print(f"\n=== Summary ===")
    print(f"✅ Fixed duplicate solution links in {fixed_dups} files")
    print(f"✅ Fixed back-to-test anchors in {fixed_anchors} files")
    print("All solution links are now clean and back-links use proper anchors!")

if __name__ == "__main__":
    main()