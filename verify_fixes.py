#!/usr/bin/env python3
"""
Verify both sidebar and back link fixes are working correctly.
"""

import os
import re
import glob

def check_empty_headers():
    """Check for any remaining empty headers that break sidebar"""
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if 'history' not in f]
    
    empty_header_files = []
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for empty headers
            if re.search(r'^#\s*$', content, re.MULTILINE):
                empty_header_files.append(file_path)
                
        except Exception as e:
            continue
    
    return empty_header_files

def verify_backlink_accuracy():
    """Verify that solution back links point to files that actually contain the tests"""
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    issues = []
    verified = []
    
    for solution_file in solution_files:
        try:
            with open(solution_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract back link
            back_link_match = re.search(r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\(([^)#]+)(#[^)]+)?\)', content)
            if not back_link_match:
                issues.append(f"No back link found in {os.path.basename(solution_file)}")
                continue
            
            target_file = back_link_match.group(1)
            anchor = back_link_match.group(2) if back_link_match.group(2) else ""
            
            # Check if target file exists
            target_path = os.path.join(os.path.dirname(solution_file), target_file)
            if not os.path.exists(target_path):
                issues.append(f"{os.path.basename(solution_file)} → {target_file} (FILE NOT FOUND)")
                continue
            
            # Check if target file actually contains a test
            with open(target_path, 'r', encoding='utf-8') as f:
                target_content = f.read()
            
            if 'Multiple Choice Test' not in target_content:
                issues.append(f"{os.path.basename(solution_file)} → {target_file} (NO TEST FOUND)")
                continue
            
            # Extract session number from solution file
            session_match = re.search(r'Session(\d+)', os.path.basename(solution_file))
            if session_match:
                session_num = session_match.group(1)
                expected_test_header = f"Multiple Choice Test - Session {session_num}"
                if expected_test_header in target_content:
                    verified.append(f"{os.path.basename(solution_file)} → {target_file} ✅")
                else:
                    issues.append(f"{os.path.basename(solution_file)} → {target_file} (WRONG SESSION)")
            else:
                issues.append(f"{os.path.basename(solution_file)} → {target_file} (NO SESSION NUMBER)")
                
        except Exception as e:
            issues.append(f"Error processing {os.path.basename(solution_file)}: {e}")
    
    return verified, issues

def main():
    """Main verification function"""
    print("=== Verifying Sidebar and Back Link Fixes ===\n")
    
    # Check sidebar issues
    print("1. Checking for empty headers that break sidebar...")
    empty_headers = check_empty_headers()
    
    if empty_headers:
        print(f"❌ Found {len(empty_headers)} files with empty headers:")
        for file_path in empty_headers:
            print(f"  - {os.path.basename(file_path)}")
    else:
        print("✅ No empty headers found - sidebar should work correctly")
    
    # Check back link accuracy
    print("\n2. Verifying back link accuracy...")
    verified, issues = verify_backlink_accuracy()
    
    print(f"\n✅ Verified {len(verified)} correct back links:")
    for item in verified[:5]:  # Show first 5 examples
        print(f"  - {item}")
    if len(verified) > 5:
        print(f"  ... and {len(verified) - 5} more")
    
    if issues:
        print(f"\n❌ Found {len(issues)} back link issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ All back links are accurate!")
    
    print(f"\n=== SUMMARY ===")
    print(f"Empty headers: {len(empty_headers)} (should be 0)")
    print(f"Correct back links: {len(verified)}")
    print(f"Back link issues: {len(issues)} (should be 0)")
    
    if len(empty_headers) == 0 and len(issues) == 0:
        print("\n🎉 ALL ISSUES RESOLVED!")
        print("✅ Sidebar navigation will show complete chapter structure")
        print("✅ All solution back links point to correct test locations")
    else:
        print(f"\n⚠️  {len(empty_headers) + len(issues)} issues remaining")

if __name__ == "__main__":
    main()