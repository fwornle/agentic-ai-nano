#!/usr/bin/env python3
"""
Find files with actual test questions that don't have solution links
"""

import re
from pathlib import Path

def find_tests_needing_links():
    """Find files with test questions but no solution links"""
    base_dir = Path('docs-content')
    
    tests_without_links = []
    
    for md_file in base_dir.rglob('*.md'):
        if 'Test_Solutions' in md_file.name:
            continue
            
        content = md_file.read_text()
        
        # Check if it has test questions
        has_questions = 'Question 1' in content and ('Question 2' in content or 'Question 3' in content)
        
        # Check if it already has solution links
        has_solution_link = 'View Solutions' in content or '[Solutions]' in content or '→](.*Test_Solutions.md)' in content
        
        if has_questions and not has_solution_link:
            relative_path = md_file.relative_to(base_dir)
            tests_without_links.append(str(relative_path))
    
    return tests_without_links

def add_solution_links_to_tests():
    """Add solution links to tests that need them"""
    tests_needing_links = find_tests_needing_links()
    print(f"Found {len(tests_needing_links)} test files needing solution links:")
    
    for test_file in tests_needing_links[:20]:  # Show first 20
        print(f"  {test_file}")
    
    added_count = 0
    
    for test_file in tests_needing_links:
        file_path = Path('docs-content') / test_file
        content = file_path.read_text()
        
        # Determine solution file name
        filename = Path(test_file).name
        solution_filename = filename.replace('.md', '_Test_Solutions.md')
        
        # Check if solution file exists
        solution_path = file_path.parent / solution_filename
        if not solution_path.exists():
            print(f"  Solution file missing: {solution_filename}")
            continue
        
        # Add solution link
        # Look for the last question and add link after it
        last_question_pattern = r'(Question \d+:.*?)(\n\n---|\n\n## 🧭 Navigation|$)'
        
        def add_link(match):
            question_content = match.group(1)
            following_content = match.group(2) if match.group(2) else ''
            
            # Add solution link after the question
            solution_link = f"\n\n[View Solutions →]({solution_filename})"
            return question_content + solution_link + following_content
        
        new_content = re.sub(last_question_pattern, add_link, content, flags=re.DOTALL)
        
        if new_content != content:
            file_path.write_text(new_content)
            print(f"  Added solution link to: {test_file}")
            added_count += 1
        else:
            # Try alternative approach - add before navigation
            nav_pattern = r'(---\s*\n## 🧭 Navigation)'
            
            if re.search(nav_pattern, content):
                solution_link = f"\n\n[View Solutions →]({solution_filename})\n\n---\n\n## 🧭 Navigation"
                content = re.sub(nav_pattern, solution_link, content)
                file_path.write_text(content)
                print(f"  Added solution link before nav: {test_file}")
                added_count += 1
            else:
                print(f"  Could not find insertion point for: {test_file}")
    
    return added_count

def main():
    print("🔍 Finding test files that need solution links...")
    added = add_solution_links_to_tests()
    print(f"\n✅ Added {added} solution links")

if __name__ == "__main__":
    main()