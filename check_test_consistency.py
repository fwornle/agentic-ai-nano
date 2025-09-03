#!/usr/bin/env python3
"""
Script to check consistency between test files and their corresponding solution files.
Verifies:
1. Question/answer matching
2. Bidirectional navigation links
3. File pair completeness
"""

import os
import re
import glob
from pathlib import Path

def extract_questions_from_test(content):
    """Extract questions from a test section in markdown content."""
    questions = []
    
    # Find multiple choice test sections
    test_sections = re.findall(r'## Multiple Choice Test.*?(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
    
    for section in test_sections:
        # Extract numbered questions
        question_matches = re.findall(r'\*\*(\d+)\.\s*(.*?)\*\*\s*\n(.*?)(?=\*\*\d+\.|$)', section, re.DOTALL)
        for match in question_matches:
            question_num = match[0]
            question_text = match[1].strip()
            options = match[2].strip()
            questions.append({
                'number': question_num,
                'text': question_text,
                'options': options
            })
    
    return questions

def extract_answers_from_solution(content):
    """Extract answers from a solution file."""
    answers = {}
    
    # Look for answer patterns like "1. A)" or "Question 1: A"
    answer_patterns = [
        r'(\d+)\.\s*([A-D])\)',
        r'Question\s+(\d+):\s*([A-D])',
        r'\*\*(\d+)\.\s*([A-D])\*\*',
        r'(\d+)\)\s*([A-D])'
    ]
    
    for pattern in answer_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            answers[match[0]] = match[1].upper()
    
    return answers

def check_navigation_links(test_file, solution_file):
    """Check for bidirectional navigation links between test and solution files."""
    with open(test_file, 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    with open(solution_file, 'r', encoding='utf-8') as f:
        solution_content = f.read()
    
    # Extract filenames for link checking
    test_filename = os.path.basename(test_file)
    solution_filename = os.path.basename(solution_file)
    
    # Check if test file links to solution
    test_to_solution = solution_filename in test_content or solution_filename.replace('.md', '') in test_content
    
    # Check if solution file links to test
    solution_to_test = test_filename in solution_content or test_filename.replace('.md', '') in solution_content
    
    return test_to_solution, solution_to_test

def find_test_files_with_questions():
    """Find all files containing test sections."""
    test_files = []
    
    for root, dirs, files in os.walk('/Users/q284340/Agentic/nano-degree/docs-content'):
        for file in files:
            if file.endswith('.md') and not file.endswith('_Test_Solutions.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'multiple choice test' in content.lower():
                            test_files.append(filepath)
                except:
                    continue
    
    return test_files

def main():
    """Main analysis function."""
    print("=== Test-Solution Consistency Analysis ===\n")
    
    # Find all solution files
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    print(f"Found {len(solution_files)} solution files")
    
    # Find all test files with questions
    test_files = find_test_files_with_questions()
    print(f"Found {len(test_files)} files with test sections\n")
    
    issues = []
    checked_pairs = 0
    
    # Check each solution file for corresponding test file
    for solution_file in solution_files:
        solution_path = Path(solution_file)
        solution_name = solution_path.stem
        
        # Try to find corresponding test file
        base_name = solution_name.replace('_Test_Solutions', '')
        test_candidates = []
        
        # Look for matching test files
        for test_file in test_files:
            test_path = Path(test_file)
            if base_name in test_path.stem:
                test_candidates.append(test_file)
        
        if not test_candidates:
            issues.append(f"❌ No test file found for solution: {solution_file}")
            continue
        
        # Check each candidate
        for test_file in test_candidates:
            checked_pairs += 1
            print(f"Checking pair {checked_pairs}:")
            print(f"  Test: {test_file}")
            print(f"  Solution: {solution_file}")
            
            # Read files
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                with open(solution_file, 'r', encoding='utf-8') as f:
                    solution_content = f.read()
            except Exception as e:
                issues.append(f"❌ Error reading files: {e}")
                continue
            
            # Extract questions and answers
            questions = extract_questions_from_test(test_content)
            answers = extract_answers_from_solution(solution_content)
            
            print(f"  Questions found: {len(questions)}")
            print(f"  Answers found: {len(answers)}")
            
            # Check question-answer matching
            if len(questions) != len(answers):
                issues.append(f"❌ Question/Answer count mismatch in {test_file} vs {solution_file}: {len(questions)} questions, {len(answers)} answers")
            
            # Check if all questions have answers
            for q in questions:
                if q['number'] not in answers:
                    issues.append(f"❌ Missing answer for question {q['number']} in {solution_file}")
            
            # Check navigation links
            test_to_solution, solution_to_test = check_navigation_links(test_file, solution_file)
            
            if not test_to_solution:
                issues.append(f"❌ No link from test to solution: {test_file} → {solution_file}")
            
            if not solution_to_test:
                issues.append(f"❌ No link from solution to test: {solution_file} → {test_file}")
            
            print(f"  Links: Test→Solution: {'✅' if test_to_solution else '❌'}, Solution→Test: {'✅' if solution_to_test else '❌'}")
            print()
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Checked {checked_pairs} test-solution pairs")
    print(f"Found {len(issues)} issues\n")
    
    if issues:
        print("=== ISSUES FOUND ===")
        for issue in issues:
            print(issue)
    else:
        print("✅ All tests and solutions are consistent!")
    
    # Save detailed report
    with open('/Users/q284340/Agentic/nano-degree/test_consistency_report.txt', 'w') as f:
        f.write("Test-Solution Consistency Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Checked {checked_pairs} test-solution pairs\n")
        f.write(f"Found {len(issues)} issues\n\n")
        
        if issues:
            f.write("Issues Found:\n")
            for issue in issues:
                f.write(f"{issue}\n")
        else:
            f.write("✅ All tests and solutions are consistent!\n")
    
    print(f"\nDetailed report saved to: test_consistency_report.txt")

if __name__ == "__main__":
    main()