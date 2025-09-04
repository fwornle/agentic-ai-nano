#!/usr/bin/env python3
"""
Clean and verify file tail structures.
Focus on removing clutter before tests and ensuring proper Test -> Navigation order.
"""

import os
import re
import glob

def read_file_tail(file_path, lines=50):
    """Read the last N lines of a file to analyze structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines_list = content.split('\n')
        tail_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list
        
        return content, '\n'.join(tail_lines)
    except Exception as e:
        return None, f"Error: {e}"

def clean_clutter_before_test(content):
    """Remove clutter sections that appear before Multiple Choice Test."""
    
    # Find the Multiple Choice Test section
    test_match = re.search(r'## 📝 Multiple Choice Test', content)
    if not test_match:
        return content
    
    test_start = test_match.start()
    before_test = content[:test_start]
    test_and_after = content[test_start:]
    
    # Remove clutter patterns from before_test section
    clutter_patterns = [
        # Remove test-related clutter sections
        r'## Test Your Knowledge.*?(?=##|$)',
        r'### Test Your Knowledge.*?(?=##|$)',
        r'## Knowledge Assessment.*?(?=##|$)', 
        r'### Knowledge Assessment.*?(?=##|$)',
        r'## Quick Understanding Check.*?(?=##|$)',
        r'### Quick Understanding Check.*?(?=##|$)',
        r'## Complete Assessment.*?(?=##|$)',
        r'### Complete Assessment.*?(?=##|$)',
        
        # Remove learning path recommendation sections
        r'### Complete Learning Path Recommendations.*?(?=##|$)',
        r'## Complete Learning Path Recommendations.*?(?=##|$)',
        
        # Remove observer/participant/implementer question blocks
        r'\*\*🎯 Observer Level Questions:\*\*.*?(?=\*\*📝|\*\*⚙️|##|$)',
        r'\*\*📝 Participant Level Questions:\*\*.*?(?=\*\*⚙️|##|$)', 
        r'\*\*⚙️ Implementer Level Questions:\*\*.*?(?=##|$)',
        
        # Remove test continuation headers
        r'## 📝 Multiple Choice Test.*?& Continuation.*?\n',
        
        # Remove standalone test links
        r'- \*\*\[📝 Test Your Knowledge.*?\n',
        r'- \*\*\[📖 Next Session.*?\n'
    ]
    
    for pattern in clutter_patterns:
        before_test = re.sub(pattern, '', before_test, flags=re.DOTALL)
    
    # Clean up excessive whitespace
    before_test = re.sub(r'\n{3,}', '\n\n', before_test)
    before_test = before_test.rstrip() + '\n\n'
    
    return before_test + test_and_after

def analyze_and_fix_file(file_path):
    """Analyze a file and fix any structural issues."""
    
    content, tail = read_file_tail(file_path)
    if content is None:
        return {'error': tail}
    
    original_content = content
    issues = []
    
    # Check if file has both test and navigation
    has_test = '## 📝 Multiple Choice Test' in content
    has_navigation = '## 🧭 Navigation' in content
    
    if not has_test and not has_navigation:
        return {'status': 'no_test_nav', 'issues': []}
    
    if has_test:
        # Clean clutter before test
        content = clean_clutter_before_test(content)
        
        # Verify test comes before navigation
        if has_navigation:
            test_pos = content.find('## 📝 Multiple Choice Test')
            nav_pos = content.find('## 🧭 Navigation')
            
            if test_pos > nav_pos:
                issues.append('Test appears after Navigation')
            elif nav_pos - test_pos > 2000:  # Too far apart
                issues.append('Test and Navigation too far apart')
    
    # Check tail structure
    tail_lines = tail.split('\n')
    section_headers = [line for line in tail_lines if line.startswith('## ')]
    
    if len(section_headers) >= 2:
        last_header = section_headers[-1]
        second_last_header = section_headers[-2]
        
        if not last_header.startswith('## 🧭 Navigation'):
            issues.append(f'Last section is "{last_header}", not Navigation')
            
        if has_test and not second_last_header.startswith('## 📝 Multiple Choice Test'):
            issues.append(f'Second-last section is "{second_last_header}", not Multiple Choice Test')
    
    # Save changes if content was modified
    changed = content != original_content
    if changed:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            return {'error': f'Write failed: {e}'}
    
    return {
        'status': 'analyzed',
        'issues': issues,
        'changed': changed,
        'has_test': has_test,
        'has_navigation': has_navigation
    }

def main():
    """Main function to clean all file tails."""
    print("=== Cleaning File Tail Structures ===\n")
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    md_files = [f for f in md_files if 'BACKUP' not in f and 'ORIGINAL' not in f]
    
    print(f"Processing {len(md_files)} files...")
    
    cleaned_files = []
    issue_files = []
    
    for file_path in md_files:
        result = analyze_and_fix_file(file_path)
        
        if result.get('changed'):
            cleaned_files.append(os.path.basename(file_path))
            print(f"✅ Cleaned {os.path.basename(file_path)}")
        
        if result.get('issues'):
            issue_files.append({
                'file': os.path.basename(file_path),
                'issues': result['issues']
            })
    
    print(f"\n=== Summary ===")
    print(f"✅ Cleaned clutter in {len(cleaned_files)} files")
    
    if issue_files:
        print(f"❌ {len(issue_files)} files still have structural issues:")
        for issue_file in issue_files[:10]:  # Show first 10
            print(f"  {issue_file['file']}: {', '.join(issue_file['issues'])}")
        if len(issue_files) > 10:
            print(f"  ... and {len(issue_files) - 10} more")
    else:
        print("✅ All files have proper tail structure!")
    
    print(f"\nCleanup complete! Removed clutter and verified Test → Navigation order.")

if __name__ == "__main__":
    main()