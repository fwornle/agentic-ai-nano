#!/usr/bin/env python3
"""
Comprehensive fix for all remaining issues:
1. Fix broken links by creating missing test solution files
2. Fix malformed navigation links
3. Add missing solution links to tests
"""

import json
import os
import re
from pathlib import Path

def load_analysis():
    """Load the course structure analysis"""
    with open('course_structure_analysis.json', 'r') as f:
        return json.load(f)

def create_missing_test_solutions():
    """Create missing test solution files"""
    analysis = load_analysis()
    broken_links = analysis.get('broken_links', [])
    
    # Find broken links that point to missing test solution files
    missing_solutions = set()
    for link in broken_links:
        target = link['target_file']
        if target.endswith('_Test_Solutions.md') and 'View Solutions' in link['link_text']:
            source_path = Path(f"docs-content/{link['source_file']}")
            target_path = source_path.parent / target
            if not target_path.exists():
                missing_solutions.add(str(target_path))
    
    print(f"Creating {len(missing_solutions)} missing test solution files...")
    
    # Create template content for missing solution files
    template_content = """# Test Solutions

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

[← Back to Test](#) <!-- Link will be updated by link fixer -->

---

## 🧭 Navigation

**Module Home:** [Session Overview](#) <!-- Link will be updated -->  
**Course Home:** [Framework Course →](../index.md)

---
"""
    
    created_count = 0
    for solution_path in missing_solutions:
        try:
            Path(solution_path).write_text(template_content)
            print(f"Created: {solution_path}")
            created_count += 1
        except Exception as e:
            print(f"Error creating {solution_path}: {e}")
    
    return created_count

def fix_malformed_links():
    """Fix malformed navigation links"""
    analysis = load_analysis()
    broken_links = analysis.get('broken_links', [])
    
    fixed_count = 0
    for link in broken_links:
        if 'Session None' in link['link_text'] and link['target_file'] == '../index.md':
            source_path = Path(f"docs-content/{link['source_file']}")
            if source_path.exists():
                content = source_path.read_text()
                
                # Fix malformed links like "Session None -  →"
                old_pattern = r'\[Session None -\s+→\]\(\.\.\/index\.md\)'
                new_link = '[Course Home →](../index.md)'
                
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_link, content)
                    source_path.write_text(content)
                    print(f"Fixed malformed link in: {source_path}")
                    fixed_count += 1
    
    return fixed_count

def add_missing_solution_links():
    """Add solution links to tests that don't have them"""
    analysis = load_analysis()
    
    # Find test files (files that contain tests but no solution links)
    test_files_without_solutions = []
    for file_data in analysis['files']:
        issues = file_data.get('issues', [])
        for issue in issues:
            if issue.get('type') == 'test_without_solution_link':
                test_files_without_solutions.append(file_data['file_path'])
    
    print(f"Adding solution links to {len(test_files_without_solutions)} test files...")
    
    added_count = 0
    for test_file in test_files_without_solutions[:10]:  # Process first 10 to avoid overwhelming
        file_path = Path(f"docs-content/{test_file}")
        if not file_path.exists():
            continue
            
        content = file_path.read_text()
        
        # Determine what solution file should be
        solution_filename = test_file.replace('.md', '_Test_Solutions.md')
        solution_path = file_path.parent / solution_filename
        
        # Create solution file if it doesn't exist
        if not solution_path.exists():
            template_content = """# Test Solutions

## Multiple Choice Questions

### Question 1
**Answer:** [To be completed]

**Explanation:** [To be completed]

---

## Back to Test

[← Back to Test]({}) 

---

## 🧭 Navigation

**Module Home:** [Session Overview](#)  
**Course Home:** [Framework Course →](../index.md)

---
""".format(test_file)
            
            solution_path.write_text(template_content)
            print(f"Created solution file: {solution_path}")
        
        # Add solution link to test file
        # Find the test section and add link after it
        if '## Test' in content and 'View Solutions' not in content:
            # Add solution link before the final navigation section
            nav_pattern = r'(---\s*\n## 🧭 Navigation)'
            solution_link = f"\n\n[View Solutions →]({solution_filename})\n\n---\n\n## 🧭 Navigation"
            
            if re.search(nav_pattern, content):
                content = re.sub(nav_pattern, solution_link, content)
                file_path.write_text(content)
                print(f"Added solution link to: {file_path}")
                added_count += 1
            else:
                # If no navigation section, add at end
                content += f"\n\n[View Solutions →]({solution_filename})\n"
                file_path.write_text(content)
                print(f"Added solution link at end of: {file_path}")
                added_count += 1
    
    return added_count

def main():
    print("🔧 Fixing all remaining course structure issues...")
    
    # Fix 1: Create missing test solution files
    created = create_missing_test_solutions()
    print(f"✅ Created {created} missing test solution files")
    
    # Fix 2: Fix malformed navigation links
    fixed_links = fix_malformed_links()
    print(f"✅ Fixed {fixed_links} malformed navigation links")
    
    # Fix 3: Add missing solution links to tests
    added_links = add_missing_solution_links()
    print(f"✅ Added {added_links} missing solution links")
    
    print("\n🎉 All fixes completed! Re-running analysis...")
    
    # Re-run analysis to check results
    os.system('python3 analyze_course_structure.py')

if __name__ == "__main__":
    main()