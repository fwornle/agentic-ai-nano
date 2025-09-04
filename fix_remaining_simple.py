#!/usr/bin/env python3
"""
Simple fix for remaining issues - create missing test solution files
"""

import json
import re
from pathlib import Path

def load_analysis():
    with open('course_structure_analysis.json', 'r') as f:
        return json.load(f)

def fix_broken_solution_links():
    """Fix broken solution links by creating missing files or fixing paths"""
    analysis = load_analysis()
    broken_links = analysis.get('broken_links', [])
    
    fixed_count = 0
    created_count = 0
    
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

[← Back to Test](#)

---

## 🧭 Navigation

**Course Home:** [Framework Course →](../index.md)

---
"""
    
    for link in broken_links:
        if 'View Solutions' in link['link_text'] and link['target_file'].endswith('_Test_Solutions.md'):
            source_file = link['source_file']
            target_file = link['target_file']
            
            # Construct proper paths
            source_path = Path('docs-content') / source_file
            target_path = source_path.parent / target_file
            
            if not target_path.exists():
                try:
                    target_path.write_text(template_content)
                    print(f"Created: {target_path}")
                    created_count += 1
                except Exception as e:
                    print(f"Error creating {target_path}: {e}")
    
    # Fix malformed navigation links
    for link in broken_links:
        if 'Session None' in link['link_text']:
            source_path = Path('docs-content') / link['source_file']
            if source_path.exists():
                try:
                    content = source_path.read_text()
                    old_pattern = r'\[Session None -\s+→\]\(\.\.\/index\.md\)'
                    new_link = '[Course Home →](../index.md)'
                    
                    if re.search(old_pattern, content):
                        content = re.sub(old_pattern, new_link, content)
                        source_path.write_text(content)
                        print(f"Fixed malformed link in: {source_path}")
                        fixed_count += 1
                except Exception as e:
                    print(f"Error fixing {source_path}: {e}")
    
    return created_count, fixed_count

def main():
    print("🔧 Fixing remaining broken links...")
    
    created, fixed = fix_broken_solution_links()
    print(f"✅ Created {created} missing test solution files")
    print(f"✅ Fixed {fixed} malformed navigation links")
    
    print("\n🔍 Re-analyzing structure...")
    import os
    os.system('python3 analyze_course_structure.py')

if __name__ == "__main__":
    main()