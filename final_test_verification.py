#!/usr/bin/env python3
"""
Final comprehensive verification of all test formatting across the course.
"""

import os
import re
import glob

def analyze_file_structure(file_path):
    """Analyze a single file's structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = re.findall(r'## ([^#\n]+)', content)
        issues = []
        
        # Check for issues
        if 'Continue Your Journey' in content:
            issues.append('Contains "Continue Your Journey"')
        if re.search(r'## 📝 Multiple Choice Test.*and Testing:', content):
            issues.append('Improper test title format')
        if re.search(r'\[.*Session.*Test.*\]\([^)]*\.md\)', content):
            issues.append('Contains link to test instead of embedded test')
        
        has_test = any('Multiple Choice Test' in section for section in sections)
        has_navigation = any('Navigation' in section for section in sections)
        
        if has_test and len(sections) >= 2:
            test_index = nav_index = -1
            for i, section in enumerate(sections):
                if 'Multiple Choice Test' in section:
                    test_index = i
                if 'Navigation' in section:
                    nav_index = i
            
            if nav_index != -1 and test_index != nav_index - 1:
                issues.append(f'Test not in second-to-last position')
        
        if has_test and not re.search(r'\[View Solutions →\]', content):
            issues.append('Missing solution link')
        
        return {
            'file': file_path,
            'sections': sections,
            'has_test': has_test,
            'issues': issues,
            'last_two_sections': sections[-2:] if len(sections) >= 2 else sections
        }
        
    except Exception as e:
        return {'file': file_path, 'error': str(e), 'issues': [f'Error: {e}']}

def main():
    print("=== Final Test Structure Verification ===\n")
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if '_Test_Solutions.md' not in f and 'history' not in f and 'index.md' not in f]
    
    files_with_issues = 0
    test_files = []
    
    for file_path in sorted(md_files):
        analysis = analyze_file_structure(file_path)
        
        if analysis.get('issues'):
            files_with_issues += 1
            print(f"❌ {os.path.basename(file_path)}")
            for issue in analysis['issues']:
                print(f"   - {issue}")
            print()
        elif analysis.get('has_test'):
            test_files.append(file_path)
    
    print(f"=== RESULTS ===")
    print(f"Total files: {len(md_files)}")
    print(f"Files with tests: {len(test_files)}")
    print(f"Files with issues: {files_with_issues}")
    
    if files_with_issues == 0:
        print("\n✅ ALL FILES PROPERLY STRUCTURED!")
    
    print(f"\n=== SAMPLE CORRECT FILES ===")
    for file_path in test_files[:3]:
        analysis = analyze_file_structure(file_path)
        if not analysis.get('issues'):
            print(f"✅ {os.path.basename(file_path)}: {analysis['last_two_sections']}")

if __name__ == "__main__":
    main()