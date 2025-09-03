#!/usr/bin/env python3
"""
Final verification of all test-solution consistency and links.
"""

import os
import re
import glob
from pathlib import Path

def verify_all_test_solution_pairs():
    """Verify all test-solution pairs for consistency."""
    print("=== Final Test-Solution Verification ===\n")
    
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    verified_pairs = 0
    issues = []
    perfect_pairs = []
    
    for solution_file in solution_files:
        solution_path = Path(solution_file)
        base_name = solution_path.stem.replace('_Test_Solutions', '')
        
        print(f"Checking {base_name}...")
        
        # Read solution file
        with open(solution_file, 'r', encoding='utf-8') as f:
            solution_content = f.read()
        
        # Count questions in solution
        solution_questions = len(re.findall(r'\*\*Question \d+:', solution_content))
        
        # Look for corresponding test files
        possible_test_files = [
            solution_path.parent / f"{base_name}_Practice_Test.md",
            solution_path.parent / f"{base_name}.md"
        ]
        
        test_file_found = None
        test_questions = 0
        
        for test_file in possible_test_files:
            if test_file.exists():
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                test_q_count = len(re.findall(r'\*\*Question \d+:', test_content))
                if test_q_count > 0:
                    test_file_found = str(test_file)
                    test_questions = test_q_count
                    break
        
        if test_file_found:
            verified_pairs += 1
            
            # Check for bidirectional links
            test_filename = os.path.basename(test_file_found)
            solution_filename = os.path.basename(solution_file)
            
            with open(test_file_found, 'r', encoding='utf-8') as f:
                test_content = f.read()
            
            has_test_to_solution = solution_filename in test_content
            has_solution_to_test = test_filename in solution_content
            
            # Report status
            status_parts = []
            if test_questions == solution_questions:
                status_parts.append("✅ Q-match")
            else:
                status_parts.append(f"❌ Q-mismatch ({test_questions}≠{solution_questions})")
                issues.append(f"{base_name}: {test_questions} test questions ≠ {solution_questions} solution questions")
            
            if has_test_to_solution:
                status_parts.append("✅ T→S link")
            else:
                status_parts.append("❌ T→S link")
                issues.append(f"{base_name}: Missing test→solution link")
            
            if has_solution_to_test:
                status_parts.append("✅ S→T link")
            else:
                status_parts.append("❌ S→T link")
                issues.append(f"{base_name}: Missing solution→test link")
            
            status = " | ".join(status_parts)
            print(f"  {status}")
            
            if "❌" not in status:
                perfect_pairs.append(base_name)
            
        else:
            print(f"  ❌ No corresponding test file found")
            issues.append(f"{base_name}: No test file found")
    
    # Summary
    print(f"\n=== FINAL SUMMARY ===")
    print(f"✅ Verified {verified_pairs} test-solution pairs")
    print(f"✅ Perfect pairs: {len(perfect_pairs)}")
    print(f"{'❌' if issues else '✅'} Issues found: {len(issues)}")
    
    if perfect_pairs:
        print(f"\n🎉 Perfect Test-Solution Pairs:")
        for pair in perfect_pairs:
            print(f"  • {pair}")
    
    if issues:
        print(f"\n❌ Remaining Issues:")
        for issue in issues:
            print(f"  • {issue}")
    
    return len(issues) == 0

def main():
    """Main verification function."""
    all_good = verify_all_test_solution_pairs()
    
    if all_good:
        print(f"\n🎉 ALL TEST-SOLUTION PAIRS ARE PERFECT! 🎉")
    else:
        print(f"\n⚠️  Some issues remain - see details above")

if __name__ == "__main__":
    main()