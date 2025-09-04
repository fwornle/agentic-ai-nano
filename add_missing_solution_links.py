#!/usr/bin/env python3
"""
Add solution links to tests that don't have them
"""

import json
import re
from pathlib import Path

def get_tests_without_solutions():
    """Get list of test files without solution links"""
    with open('course_structure_analysis.json', 'r') as f:
        data = json.load(f)
    
    test_files = []
    for file_data in data['files']:
        issues = file_data.get('issues', [])
        for issue in issues:
            if issue.get('type') == 'test_without_solution_link':
                test_files.append(file_data['file_path'])
    
    return test_files

def add_solution_links():
    """Add solution links to test files"""
    test_files = get_tests_without_solutions()
    print(f"Adding solution links to {len(test_files)} test files...")
    
    added_count = 0
    
    for test_file in test_files:
        file_path = Path('docs-content') / test_file
        if not file_path.exists():
            continue
        
        content = file_path.read_text()
        
        # Skip if it already has a solution link (false positive)
        if 'View Solutions' in content or 'solution' in content.lower():
            continue
        
        # Determine solution filename
        if 'ModuleA' in test_file:
            solution_file = test_file.replace('.md', '_Test_Solutions.md')
        elif 'ModuleB' in test_file:
            solution_file = test_file.replace('.md', '_Test_Solutions.md')
        elif 'ModuleC' in test_file:
            solution_file = test_file.replace('.md', '_Test_Solutions.md')
        elif 'ModuleD' in test_file:
            solution_file = test_file.replace('.md', '_Test_Solutions.md')
        else:
            # Main session file - look for corresponding test solution
            base_name = test_file.replace('.md', '')
            solution_file = f"{base_name}_Test_Solutions.md"
        
        # Check if solution file exists
        solution_path = file_path.parent / solution_file
        if not solution_path.exists():
            # Create basic solution file
            template_content = f"""# {base_name.replace('_', ' ')} - Test Solutions

## Multiple Choice Questions

### Question 1
**Answer:** [To be completed]

**Explanation:** [To be completed]

### Question 2
**Answer:** [To be completed]

**Explanation:** [To be completed]

### Question 3
**Answer:** [To be completed]

**Explanation:** [To be completed]

---

## Back to Test

[← Back to Test]({Path(test_file).name})

---

## 🧭 Navigation

**Course Home:** [Course Overview →](../index.md)

---
"""
            solution_path.write_text(template_content)
            print(f"Created solution file: {solution_path}")
        
        # Add solution link to test file
        # Look for test section and add link before navigation
        if '## Test' in content or '## 📝' in content:
            # Find navigation section and add solution link before it
            nav_pattern = r'(---\s*\n## 🧭 Navigation)'
            
            if re.search(nav_pattern, content):
                solution_link = f"\n\n[View Solutions →]({Path(solution_file).name})\n\n---\n\n## 🧭 Navigation"
                content = re.sub(nav_pattern, solution_link, content)
            else:
                # Add at end if no navigation
                content += f"\n\n[View Solutions →]({Path(solution_file).name})\n"
            
            file_path.write_text(content)
            print(f"Added solution link to: {test_file}")
            added_count += 1
        else:
            # File might not actually contain tests
            print(f"Skipped (no test section found): {test_file}")
    
    return added_count

def main():
    print("📝 Adding missing solution links to tests...")
    
    added = add_solution_links()
    print(f"✅ Added {added} solution links")
    
    print("\n🔍 Re-analyzing course structure...")
    import os
    os.system('python3 analyze_course_structure.py')
    os.system('python3 fix_analysis_bug.py')

if __name__ == "__main__":
    main()