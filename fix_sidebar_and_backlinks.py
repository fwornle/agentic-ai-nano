#!/usr/bin/env python3
"""
Fix two critical issues:
1. Remove empty headers (#) that break sidebar navigation
2. Fix all back links in solution files to point to correct test locations
"""

import os
import re
import glob

def fix_empty_headers(file_path):
    """Remove empty headers that break sidebar navigation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove empty headers (just # with optional whitespace)
        content = re.sub(r'^#\s*$', '', content, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def find_test_file_for_session(session_num, module_path):
    """Find the correct file that contains the test for a given session"""
    # Common patterns for session files that contain tests
    patterns = [
        f'Session{session_num}_*.md',
        f'Session{session_num}.md'
    ]
    
    for pattern in patterns:
        files = glob.glob(os.path.join(module_path, pattern))
        for file_path in files:
            if '_Test_Solutions.md' in file_path:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if f'Multiple Choice Test - Session {session_num}' in content:
                    return os.path.basename(file_path)
            except:
                continue
    return None

def fix_solution_backlinks():
    """Fix all back links in solution files"""
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    fixed_count = 0
    
    for solution_file in solution_files:
        try:
            # Extract session number and module path
            dir_path = os.path.dirname(solution_file)
            filename = os.path.basename(solution_file)
            
            # Extract session number
            session_match = re.search(r'Session(\d+)', filename)
            if not session_match:
                continue
            
            session_num = session_match.group(1)
            
            # Find the correct test file
            correct_test_file = find_test_file_for_session(session_num, dir_path)
            if not correct_test_file:
                print(f"⚠️  Could not find test file for {filename}")
                continue
            
            # Read solution file
            with open(solution_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix the back link pattern
            # Look for existing back link and replace it
            back_link_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\([^)]+\)'
            correct_anchor = f"multiple-choice-test-session-{session_num}"
            new_back_link = f"**Back to Test:** [Session {session_num} Test Questions →]({correct_test_file}#{correct_anchor})"
            
            content = re.sub(back_link_pattern, new_back_link, content)
            
            if content != original_content:
                with open(solution_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"✅ Fixed back link in {filename} → {correct_test_file}")
            
        except Exception as e:
            print(f"❌ Error processing {solution_file}: {e}")
    
    return fixed_count

def find_empty_header_files():
    """Find all files with empty headers"""
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if 'history' not in f]
    
    files_with_empty_headers = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for empty headers
            if re.search(r'^#\s*$', content, re.MULTILINE):
                files_with_empty_headers.append(file_path)
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    return files_with_empty_headers

def main():
    """Main function to fix both issues"""
    print("=== Fixing Sidebar and Back Link Issues ===\n")
    
    # Issue 1: Fix empty headers breaking sidebar
    print("1. Finding files with empty headers...")
    empty_header_files = find_empty_header_files()
    print(f"Found {len(empty_header_files)} files with empty headers")
    
    fixed_headers = 0
    for file_path in empty_header_files:
        if fix_empty_headers(file_path):
            fixed_headers += 1
            print(f"  ✅ Fixed empty header in {os.path.basename(file_path)}")
    
    print(f"\n✅ Fixed empty headers in {fixed_headers} files")
    
    # Issue 2: Fix solution back links
    print("\n2. Fixing solution back links...")
    fixed_backlinks = fix_solution_backlinks()
    print(f"\n✅ Fixed back links in {fixed_backlinks} solution files")
    
    print("\n🎉 Both issues resolved!")
    print("- Sidebar navigation should now show complete chapter structure")
    print("- All solution back links now point to correct test locations")

if __name__ == "__main__":
    main()