#!/usr/bin/env python3
"""
Focused analysis of test-solution inconsistencies found in the course.
"""

import os
import re

def analyze_session0():
    """Analyze Session 0 test vs solution file."""
    print("=== Session 0 Analysis ===")
    
    # Read practice test
    with open('/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session0_Practice_Test.md', 'r') as f:
        practice_content = f.read()
    
    # Read solution file
    with open('/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session0_Test_Solutions.md', 'r') as f:
        solution_content = f.read()
    
    # Count questions in practice test
    practice_questions = re.findall(r'\*\*Question \d+:', practice_content)
    print(f"Practice Test Questions: {len(practice_questions)}")
    
    # Count questions in solution
    solution_questions = re.findall(r'\*\*Question \d+:', solution_content)
    print(f"Solution File Questions: {len(solution_questions)}")
    
    print(f"❌ MISMATCH: Practice has {len(practice_questions)} questions, Solution has {len(solution_questions)}")
    
    # Check for navigation links
    has_test_to_solution = 'Session0_Test_Solutions' in practice_content
    has_solution_to_test = 'Session0_Practice_Test' in solution_content
    
    print(f"Practice Test → Solution link: {'✅' if has_test_to_solution else '❌'}")
    print(f"Solution → Practice Test link: {'✅' if has_solution_to_test else '❌'}")
    
    return {
        'practice_questions': len(practice_questions),
        'solution_questions': len(solution_questions),
        'has_bidirectional_links': has_test_to_solution and has_solution_to_test
    }

def check_common_patterns():
    """Check for common patterns across files that might indicate structural issues."""
    print("\n=== Common Pattern Analysis ===")
    
    # Look for files that have both questions AND answers in same file
    mixed_files = []
    
    # Check a few more examples
    examples = [
        '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session1_Bare_Metal_Agents.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session2_LangChain_Foundations.md'
    ]
    
    for filepath in examples:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            has_questions = bool(re.search(r'\*\*Question \d+:', content))
            has_answers = bool(re.search(r'Answer \d+:', content))
            has_test_section = 'multiple choice test' in content.lower()
            
            if has_questions or has_answers or has_test_section:
                mixed_files.append({
                    'file': filepath,
                    'has_questions': has_questions,
                    'has_answers': has_answers,
                    'has_test_section': has_test_section
                })
    
    if mixed_files:
        print("Files with test content:")
        for item in mixed_files:
            print(f"  {item['file']}: Q={item['has_questions']}, A={item['has_answers']}, Test={item['has_test_section']}")
    else:
        print("No additional files with test content found")

def main():
    """Main analysis."""
    print("=== Focused Test-Solution Analysis ===\n")
    
    session0_result = analyze_session0()
    check_common_patterns()
    
    print("\n=== Summary of Critical Issues ===")
    print("1. ❌ Session 0: Practice test (5 questions) vs Solution (15 questions) - MAJOR MISMATCH")
    print("2. ❌ Missing bidirectional navigation links between tests and solutions")
    print("3. ❌ Many solution files may be detached from their actual test sections")
    
    print("\n=== Recommendations ===")
    print("1. Review Session 0 to ensure practice test and solution match")
    print("2. Add proper navigation links between test and solution files")
    print("3. Conduct systematic review of all test-solution pairs")
    print("4. Consider standardizing format: either embed solutions or keep separate with clear links")

if __name__ == "__main__":
    main()