#!/usr/bin/env python3
"""
Fix GitHub-style anchor links to work properly.
GitHub converts headers to anchors by: lowercase, spaces->dashes, remove special chars.
"""

import os
import re
import glob

def create_github_anchor(header_text):
    """Convert header text to GitHub-style anchor."""
    # Remove the ## prefix and clean up
    text = header_text.replace('## ', '').strip()
    
    # Convert to lowercase
    anchor = text.lower()
    
    # Replace spaces with dashes
    anchor = anchor.replace(' ', '-')
    
    # Remove special characters (keep letters, numbers, dashes)
    anchor = re.sub(r'[^a-z0-9\-]', '', anchor)
    
    # Remove multiple consecutive dashes
    anchor = re.sub(r'-+', '-', anchor)
    
    # Remove leading/trailing dashes
    anchor = anchor.strip('-')
    
    return anchor

def fix_back_to_test_links():
    """Fix all back-to-test anchor links to use proper GitHub anchors."""
    
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    fixed_count = 0
    
    for file_path in solution_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Extract session number
            session_match = re.search(r'Session(\d+)', os.path.basename(file_path))
            if not session_match:
                continue
                
            session_num = session_match.group(1)
            
            # The header would be "## 📝 Multiple Choice Test - Session X"
            header_text = f"📝 Multiple Choice Test - Session {session_num}"
            correct_anchor = create_github_anchor(header_text)
            
            # Find and fix back-to-test links
            back_link_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\(([^)]+\.md)(#[^)]*)\)'
            
            def fix_anchor_link(match):
                file_ref = match.group(1)
                return f"**Back to Test:** [Session {session_num} Test Questions →]({file_ref}#{correct_anchor})"
            
            content = re.sub(back_link_pattern, fix_anchor_link, content)
            
            # Also fix links without anchors
            simple_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\(([^)]+\.md)\)'
            
            def add_correct_anchor(match):
                file_ref = match.group(1)
                return f"**Back to Test:** [Session {session_num} Test Questions →]({file_ref}#{correct_anchor})"
            
            content = re.sub(simple_pattern, add_correct_anchor, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                print(f"✅ Fixed anchor in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_count

def main():
    """Main function to fix GitHub anchor links."""
    print("=== Fixing GitHub Anchor Links ===\n")
    
    # Test the anchor generation
    test_header = "## 📝 Multiple Choice Test - Session 7"
    test_anchor = create_github_anchor(test_header)
    print(f"Example: '{test_header}' → '#{test_anchor}'")
    
    fixed_count = fix_back_to_test_links()
    
    print(f"\n✅ Fixed GitHub anchors in {fixed_count} files")
    print("All back-to-test links now use proper GitHub-style anchors!")

if __name__ == "__main__":
    main()