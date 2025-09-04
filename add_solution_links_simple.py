#!/usr/bin/env python3
"""
Simple approach to add solution links to tests
"""

import json
import re
from pathlib import Path

def main():
    # Get tests without solution links
    with open('course_structure_analysis.json', 'r') as f:
        data = json.load(f)
    
    test_files = []
    for file_data in data['files']:
        issues = file_data.get('issues', [])
        for issue in issues:
            if issue.get('type') == 'test_without_solution_link':
                test_files.append(file_data['file_path'])
    
    print(f"Found {len(test_files)} test files without solution links")
    
    # Process first 10 to avoid overwhelming
    added_count = 0
    
    for test_file in test_files[:15]:
        file_path = Path('docs-content') / test_file
        if not file_path.exists():
            continue
        
        content = file_path.read_text()
        
        # Skip if already has solution link
        if 'View Solutions' in content or '[Solutions]' in content:
            continue
        
        # Skip if no actual test content
        if '## Test' not in content and '## 📝' not in content and 'Question' not in content:
            print(f"Skipped (no test content): {test_file}")
            continue
        
        # Determine solution file name
        filename = Path(test_file).name
        solution_filename = filename.replace('.md', '_Test_Solutions.md')
        
        # Check if solution file exists
        solution_path = file_path.parent / solution_filename
        if solution_path.exists():
            # Add link before navigation
            nav_pattern = r'(---\s*\n## 🧭 Navigation)'
            
            if re.search(nav_pattern, content):
                solution_link = f"\n\n[View Solutions →]({solution_filename})\n\n---\n\n## 🧭 Navigation"
                content = re.sub(nav_pattern, solution_link, content)
                file_path.write_text(content)
                print(f"Added solution link to: {test_file}")
                added_count += 1
            else:
                # Add at end
                content += f"\n\n[View Solutions →]({solution_filename})\n"
                file_path.write_text(content)
                print(f"Added solution link at end of: {test_file}")
                added_count += 1
        else:
            print(f"Solution file not found for: {test_file}")
    
    print(f"✅ Added {added_count} solution links")

if __name__ == "__main__":
    main()