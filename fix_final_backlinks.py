#!/usr/bin/env python3
"""
Fix the final 5 back link issues by finding the correct test files.
"""

import os
import re
import glob

def find_correct_test_file(session_num, module_path):
    """Find the correct file containing the test for a session"""
    # Get all files in the directory
    all_files = glob.glob(os.path.join(module_path, f"Session{session_num}*.md"))
    all_files = [f for f in all_files if "_Test_Solutions.md" not in f]
    
    # Check each file for the test
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if f'Multiple Choice Test - Session {session_num}' in content:
                return os.path.basename(file_path)
        except:
            continue
    
    return None

def fix_remaining_issues():
    """Fix the remaining 5 back link issues"""
    issues = [
        '/Users/q284340/Agentic/nano-degree/docs-content/02_rag/Session7_Test_Solutions.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a/Session6_Test_Solutions.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a/Session5_Test_Solutions.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a/Session8_Test_Solutions.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a/Session7_Test_Solutions.md'
    ]
    
    fixed = 0
    
    for solution_file in issues:
        if not os.path.exists(solution_file):
            print(f"⚠️  File not found: {solution_file}")
            continue
            
        try:
            # Extract session info
            dir_path = os.path.dirname(solution_file)
            filename = os.path.basename(solution_file)
            
            session_match = re.search(r'Session(\d+)', filename)
            if not session_match:
                continue
            
            session_num = session_match.group(1)
            
            # Find correct test file
            correct_file = find_correct_test_file(session_num, dir_path)
            
            if not correct_file:
                print(f"⚠️  No test file found for Session {session_num} in {os.path.basename(dir_path)}")
                continue
            
            # Read and fix solution file
            with open(solution_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix the back link
            back_link_pattern = r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\([^)]+\)'
            correct_anchor = f"multiple-choice-test-session-{session_num}"
            new_back_link = f"**Back to Test:** [Session {session_num} Test Questions →]({correct_file}#{correct_anchor})"
            
            content = re.sub(back_link_pattern, new_back_link, content)
            
            if content != original_content:
                with open(solution_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed += 1
                print(f"✅ Fixed {filename} → {correct_file}")
                
        except Exception as e:
            print(f"❌ Error processing {solution_file}: {e}")
    
    return fixed

def main():
    """Main function"""
    print("=== Fixing Final Back Link Issues ===\n")
    
    fixed = fix_remaining_issues()
    print(f"\n✅ Fixed {fixed} remaining back link issues")

if __name__ == "__main__":
    main()