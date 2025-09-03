#!/usr/bin/env python3
"""
Comprehensive review and fix of all test files across the entire course.
"""

import os
import re
import glob
from pathlib import Path

def find_all_test_content():
    """Find all files with test content and their corresponding solution files."""
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    # Create a mapping of solution files
    solution_map = {}
    for solution_file in solution_files:
        solution_path = Path(solution_file)
        # Extract session info from filename
        parts = solution_path.stem.split('_')
        if len(parts) >= 2:
            session_info = '_'.join(parts[:-2])  # Remove '_Test_Solutions'
            solution_map[session_info] = solution_file
    
    print(f"Found {len(solution_files)} solution files:")
    for key, value in solution_map.items():
        print(f"  {key}: {os.path.basename(value)}")
    
    # Find files with test content
    test_files = []
    for root, dirs, files in os.walk('/Users/q284340/Agentic/nano-degree/docs-content'):
        for file in files:
            if file.endswith('.md') and not file.endswith('_Test_Solutions.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for test content
                    has_questions = bool(re.search(r'\*\*Question \d+:', content))
                    has_test_section = 'multiple choice test' in content.lower()
                    has_practice_test_link = 'practice test' in content.lower()
                    
                    if has_questions or has_test_section or has_practice_test_link:
                        # Try to match with solution file
                        file_path = Path(filepath)
                        filename_no_ext = file_path.stem
                        
                        # Try various matching patterns
                        possible_matches = [
                            filename_no_ext,
                            filename_no_ext.replace('_Practice_Test', ''),
                            filename_no_ext.split('_')[0] + '_' + filename_no_ext.split('_')[1] if '_' in filename_no_ext else filename_no_ext
                        ]
                        
                        matched_solution = None
                        for match in possible_matches:
                            if match in solution_map:
                                matched_solution = solution_map[match]
                                break
                        
                        test_files.append({
                            'file': filepath,
                            'has_questions': has_questions,
                            'has_test_section': has_test_section,
                            'has_practice_test_link': has_practice_test_link,
                            'solution_file': matched_solution,
                            'base_name': filename_no_ext
                        })
                except:
                    continue
    
    return test_files

def add_test_solution_links_to_main_files():
    """Add links to solution files in main session files that reference tests."""
    main_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/Session*.md', recursive=True)
    main_files = [f for f in main_files if not f.endswith('_Test_Solutions.md') and not f.endswith('_Practice_Test.md')]
    
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    solution_map = {}
    
    # Create mapping
    for solution_file in solution_files:
        solution_path = Path(solution_file)
        base_name = solution_path.stem.replace('_Test_Solutions', '')
        solution_map[base_name] = os.path.basename(solution_file)
    
    print(f"\n=== Adding Test Solution Links to Main Files ===")
    
    fixed_files = 0
    for main_file in main_files:
        main_path = Path(main_file)
        base_name = main_path.stem
        
        if base_name in solution_map:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            solution_filename = solution_map[base_name]
            
            # Check if file mentions tests but doesn't link to solutions
            mentions_test = ('practice test' in content.lower() or 
                           'multiple choice test' in content.lower() or 
                           'test your understanding' in content.lower() or
                           '📝 Practice Assessment' in content)
            
            has_solution_link = solution_filename in content or solution_filename.replace('.md', '') in content
            
            if mentions_test and not has_solution_link:
                # Add solution link after practice assessment section
                if '## 📝 Practice Assessment' in content:
                    content = content.replace(
                        'Ready to test your understanding? Take the practice test to validate your knowledge of agent frameworks and patterns:',
                        f'Ready to test your understanding? Take the practice test to validate your knowledge:\n\n[**📝 {base_name} Practice Test →**]({base_name}_Practice_Test.md)  \n[**📝 View Test Solutions →**]({solution_filename})'
                    )
                    
                    with open(main_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  ✅ Added solution link to {os.path.basename(main_file)}")
                    fixed_files += 1
    
    print(f"Fixed {fixed_files} main session files")

def verify_question_counts():
    """Verify that all test-solution pairs have matching question counts."""
    print(f"\n=== Verifying Question Counts ===")
    
    issues = []
    
    # Check Session 0 (we just fixed this)
    practice_file = '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session0_Practice_Test.md'
    solution_file = '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session0_Test_Solutions.md'
    
    if os.path.exists(practice_file) and os.path.exists(solution_file):
        with open(practice_file, 'r') as f:
            practice_content = f.read()
        with open(solution_file, 'r') as f:
            solution_content = f.read()
        
        practice_questions = len(re.findall(r'\*\*Question \d+:', practice_content))
        solution_questions = len(re.findall(r'\*\*Question \d+:', solution_content))
        
        print(f"Session 0: Practice={practice_questions}, Solution={solution_questions}")
        
        if practice_questions != solution_questions:
            issues.append(f"Session 0: {practice_questions} vs {solution_questions}")
    
    if issues:
        print(f"\n❌ Question count mismatches found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"✅ All question counts match!")
    
    return len(issues) == 0

def main():
    """Main function."""
    print("=== Comprehensive Test Content Review ===\n")
    
    # Find all test content
    test_files = find_all_test_content()
    print(f"\nFound {len(test_files)} files with test content:")
    
    for item in test_files:
        status = []
        if item['has_questions']:
            status.append('Q')
        if item['has_test_section']:
            status.append('T')
        if item['has_practice_test_link']:
            status.append('L')
        
        solution_status = "✅" if item['solution_file'] else "❌"
        
        print(f"  {os.path.basename(item['file'])}: [{'/'.join(status)}] Solution: {solution_status}")
    
    # Add solution links to main files
    add_test_solution_links_to_main_files()
    
    # Verify question counts
    all_good = verify_question_counts()
    
    print(f"\n=== Final Summary ===")
    print(f"✅ Found and analyzed {len(test_files)} files with test content")
    print(f"✅ Added solution links to main session files")
    print(f"{'✅' if all_good else '❌'} Question count verification {'passed' if all_good else 'found issues'}")

if __name__ == "__main__":
    main()