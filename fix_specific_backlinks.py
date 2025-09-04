#!/usr/bin/env python3
"""
Fix specific back link issues where the test is in a different file than expected.
Based on user feedback that Session0_Test_Solutions should point to Session0_Introduction_to_RAG_Architecture.md
"""

import os
import re
import glob

def create_test_location_mapping():
    """Create a mapping of which files actually contain tests"""
    test_locations = {}
    
    # Search all markdown files for test sections
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if '_Test_Solutions.md' not in f and 'history' not in f]
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for test sections
            if 'Multiple Choice Test - Session' in content:
                # Extract session number
                session_match = re.search(r'Multiple Choice Test - Session (\d+)', content)
                if session_match:
                    session_num = session_match.group(1)
                    module_dir = os.path.basename(os.path.dirname(file_path))
                    filename = os.path.basename(file_path)
                    
                    key = f"{module_dir}/Session{session_num}"
                    if key not in test_locations:
                        test_locations[key] = []
                    test_locations[key].append(filename)
                    
        except Exception as e:
            continue
    
    return test_locations

def fix_solution_backlinks_with_mapping(test_locations):
    """Fix solution back links using the actual test location mapping"""
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    fixed_count = 0
    
    for solution_file in solution_files:
        try:
            # Extract session info
            dir_path = os.path.dirname(solution_file)
            filename = os.path.basename(solution_file)
            module_dir = os.path.basename(dir_path)
            
            session_match = re.search(r'Session(\d+)', filename)
            if not session_match:
                continue
            
            session_num = session_match.group(1)
            
            # Find the correct test file
            key = f"{module_dir}/Session{session_num}"
            
            # Special case handling for Session0 RAG
            if session_num == '0' and module_dir == '02_rag':
                correct_file = 'Session0_Introduction_to_RAG_Architecture.md'
            elif key in test_locations:
                # Use the first (primary) file that contains the test
                correct_file = test_locations[key][0]
            else:
                print(f"⚠️  No test location found for {filename}")
                continue
            
            # Read solution file
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
                fixed_count += 1
                print(f"✅ Fixed {filename} → {correct_file}")
            
        except Exception as e:
            print(f"❌ Error processing {solution_file}: {e}")
    
    return fixed_count

def main():
    """Main function"""
    print("=== Fixing Specific Back Link Issues ===\n")
    
    print("1. Mapping actual test locations...")
    test_locations = create_test_location_mapping()
    
    print(f"Found tests in {len(test_locations)} session/module combinations")
    for key, files in test_locations.items():
        if len(files) > 1:
            print(f"  {key}: {files} (multiple files)")
        else:
            print(f"  {key}: {files[0]}")
    
    print("\n2. Fixing solution back links with correct mapping...")
    fixed_count = fix_solution_backlinks_with_mapping(test_locations)
    
    print(f"\n✅ Fixed {fixed_count} solution files with correct test locations")

if __name__ == "__main__":
    main()