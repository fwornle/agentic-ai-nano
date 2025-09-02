#!/usr/bin/env python3
"""
Fix markdown test question formatting by ensuring blank lines between questions and answers.

Pattern to fix:
**Question X:** [question text]  
A) First answer

Should become:
**Question X:** [question text]  

A) First answer
"""

import os
import re
import sys
from pathlib import Path

def fix_question_spacing(content):
    """
    Fix question spacing by adding blank line between question and first answer choice.
    
    Pattern: **Question N:** text  \nA) -> **Question N:** text  \n\nA)
    """
    # Pattern matches:
    # - **Question followed by number and colon
    # - Any text until the end of line with exactly 2 trailing spaces
    # - Newline followed immediately by A)
    pattern = r'(\*\*Question \d+:\*\*.*?  )\n(A\))'
    
    # Replace with question + blank line + answer
    replacement = r'\1\n\n\2'
    
    fixed_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return fixed_content

def count_questions(content):
    """Count total questions in content."""
    pattern = r'^\*\*Question \d+:'
    return len(re.findall(pattern, content, re.MULTILINE))

def count_fixes(original_content, fixed_content):
    """Count how many fixes were applied."""
    original_questions = count_questions(original_content)
    
    # Count questions that now have blank lines
    pattern = r'\*\*Question \d+:.*?  \n\nA\)'
    fixed_questions = len(re.findall(pattern, fixed_content, re.MULTILINE | re.DOTALL))
    
    return original_questions, fixed_questions

def process_file(file_path):
    """Process a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Skip if no questions
        if '**Question ' not in original_content:
            return None
        
        fixed_content = fix_question_spacing(original_content)
        
        # Only write if changes were made
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            original_count, fixed_count = count_fixes(original_content, fixed_content)
            return {
                'file': file_path,
                'total_questions': original_count,
                'fixed_questions': fixed_count,
                'changed': True
            }
        else:
            original_count, fixed_count = count_fixes(original_content, fixed_content)
            return {
                'file': file_path,
                'total_questions': original_count,
                'fixed_questions': fixed_count,
                'changed': False
            }
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix-question-spacing.py <directory_path>")
        sys.exit(1)
    
    base_path = Path(sys.argv[1])
    
    if not base_path.exists():
        print(f"Directory {base_path} does not exist")
        sys.exit(1)
    
    # Find all markdown files
    md_files = list(base_path.rglob('*.md'))
    
    print(f"Processing {len(md_files)} markdown files...")
    
    total_files = 0
    changed_files = 0
    total_questions = 0
    total_fixed = 0
    
    results = []
    
    for md_file in md_files:
        result = process_file(md_file)
        if result:
            results.append(result)
            total_files += 1
            total_questions += result['total_questions']
            total_fixed += result['fixed_questions']
            
            if result['changed']:
                changed_files += 1
                print(f"✓ Fixed {result['file']}: {result['fixed_questions']}/{result['total_questions']} questions")
            else:
                print(f"- Already correct {result['file']}: {result['total_questions']} questions")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {total_files}")
    print(f"Files changed: {changed_files}")
    print(f"Total questions found: {total_questions}")
    print(f"Questions with proper spacing: {total_fixed}")
    
    if total_questions > 0:
        percentage = (total_fixed / total_questions) * 100
        print(f"Success rate: {percentage:.1f}%")
    
    # Show files that still have issues
    problem_files = [r for r in results if r['total_questions'] > r['fixed_questions']]
    if problem_files:
        print(f"\nFiles with remaining issues:")
        for result in problem_files:
            unfixed = result['total_questions'] - result['fixed_questions']
            print(f"  {result['file']}: {unfixed} questions need attention")

if __name__ == '__main__':
    main()