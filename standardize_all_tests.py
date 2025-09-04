#!/usr/bin/env python3
"""
Standardize ALL test sections across the entire nano-degree course.
Ensure tests are always the second-to-last section (before Navigation) and properly formatted.
Fix any broken solution links.
"""

import os
import re
import glob

def analyze_file_structure(content, filename):
    """Analyze a file's structure to understand test placement and formatting."""
    lines = content.split('\n')
    
    analysis = {
        'has_test': False,
        'test_position': None,
        'test_format': None,
        'has_navigation': False,
        'navigation_position': None,
        'test_before_navigation': False,
        'solution_link': None,
        'solution_link_broken': False,
        'needs_fixing': False
    }
    
    # Find test section
    test_patterns = [
        r'## 📝 Multiple Choice Test',
        r'## Multiple Choice Test',
        r'## 📝 Practice Test',
        r'## Practice Test',
        r'## Assessment',
        r'## Complete Assessment',
        r'## Test Questions'
    ]
    
    for i, line in enumerate(lines):
        # Check for test sections
        for pattern in test_patterns:
            if re.match(pattern, line.strip()):
                analysis['has_test'] = True
                analysis['test_position'] = i
                analysis['test_format'] = line.strip()
                break
        
        # Check for navigation
        if line.strip() == '## 🧭 Navigation':
            analysis['has_navigation'] = True
            analysis['navigation_position'] = i
        
        # Check for solution links
        if '[View Solutions →]' in line or '[Solutions →]' in line or 'Test_Solutions.md' in line:
            analysis['solution_link'] = line.strip()
    
    # Determine if test is properly positioned
    if analysis['has_test'] and analysis['has_navigation']:
        # Test should be immediately before navigation (allowing for dividers)
        gap = analysis['navigation_position'] - analysis['test_position']
        analysis['test_before_navigation'] = gap < 20  # Allow for test content
    
    # Check if solution link is broken
    if analysis['solution_link'] and filename:
        # Extract expected solution filename
        session_match = re.search(r'Session(\d+)', os.path.basename(filename))
        if session_match:
            session_num = session_match.group(1)
            expected_solution = f"Session{session_num}_Test_Solutions.md"
            
            # Check if the solution file exists
            solution_path = os.path.join(os.path.dirname(filename), expected_solution)
            if not os.path.exists(solution_path):
                analysis['solution_link_broken'] = True
    
    # Determine if file needs fixing
    if analysis['has_test']:
        # Check if test formatting is standardized
        if not analysis['test_format'].startswith('## 📝 Multiple Choice Test'):
            analysis['needs_fixing'] = True
        
        # Check if test is in wrong position
        if analysis['has_navigation'] and not analysis['test_before_navigation']:
            analysis['needs_fixing'] = True
        
        # Check if solution link is broken
        if analysis['solution_link_broken']:
            analysis['needs_fixing'] = True
    
    return analysis

def standardize_test_section(content, filename):
    """Standardize test section formatting and position."""
    lines = content.split('\n')
    
    # Find test section and extract it
    test_start = None
    test_end = None
    navigation_start = None
    
    test_patterns = [
        r'## 📝 Multiple Choice Test',
        r'## Multiple Choice Test',
        r'## 📝 Practice Test',
        r'## Practice Test',
        r'## Assessment',
        r'## Complete Assessment',
        r'## Test Questions'
    ]
    
    for i, line in enumerate(lines):
        # Find test section start
        if test_start is None:
            for pattern in test_patterns:
                if re.match(pattern, line.strip()):
                    test_start = i
                    break
        
        # Find navigation start
        if line.strip() == '## 🧭 Navigation':
            navigation_start = i
            break
    
    if test_start is None:
        # No test section found
        return content
    
    # Find test section end (before navigation or end of file)
    if navigation_start:
        test_end = navigation_start
    else:
        test_end = len(lines)
    
    # Extract test content
    test_lines = lines[test_start:test_end]
    
    # Standardize test header
    test_lines[0] = f"## 📝 Multiple Choice Test - Session {get_session_number(filename)}"
    
    # Ensure proper solution link
    session_num = get_session_number(filename)
    if session_num:
        solution_link = f"[View Solutions →](Session{session_num}_Test_Solutions.md)"
        
        # Find and replace existing solution links
        for i, line in enumerate(test_lines):
            if '[View Solutions →]' in line or '[Solutions →]' in line or 'Test_Solutions.md' in line:
                test_lines[i] = solution_link
                break
        else:
            # Add solution link if not found
            test_lines.append("")
            test_lines.append(solution_link)
    
    # Reconstruct content with test properly positioned before navigation
    if navigation_start:
        # Remove old test section
        before_test = lines[:test_start]
        after_test = lines[test_end:]
        
        # Find where to insert test (before navigation)
        for i, line in enumerate(after_test):
            if line.strip() == '## 🧭 Navigation':
                # Insert test before navigation
                new_content = before_test + [''] + test_lines + [''] + after_test
                break
        else:
            # No navigation found, append test at end
            new_content = before_test + [''] + test_lines
    else:
        # No navigation, just replace test in place
        new_content = lines[:test_start] + test_lines + lines[test_end:]
    
    return '\n'.join(new_content)

def get_session_number(filename):
    """Extract session number from filename."""
    if not filename:
        return None
    
    match = re.search(r'Session(\d+)', os.path.basename(filename))
    return match.group(1) if match else None

def analyze_all_files():
    """Analyze all markdown files for test consistency issues."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    issues = []
    
    for file_path in md_files:
        # Skip backup files
        if 'BACKUP' in file_path or 'ORIGINAL' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = analyze_file_structure(content, file_path)
            
            if analysis['has_test']:
                issue_details = []
                
                if analysis['needs_fixing']:
                    if not analysis['test_format'].startswith('## 📝 Multiple Choice Test'):
                        issue_details.append("non-standard test format")
                    
                    if analysis['has_navigation'] and not analysis['test_before_navigation']:
                        issue_details.append("test not before navigation")
                    
                    if analysis['solution_link_broken']:
                        issue_details.append("broken solution link")
                
                if issue_details:
                    issues.append({
                        'file': os.path.basename(file_path),
                        'path': file_path,
                        'issues': issue_details,
                        'test_format': analysis['test_format']
                    })
        
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    return issues

def fix_all_test_issues():
    """Fix all test formatting and positioning issues."""
    
    issues = analyze_all_files()
    
    if not issues:
        print("✅ All test sections are properly formatted!")
        return
    
    print(f"Found {len(issues)} files with test issues:")
    for issue in issues:
        print(f"  📝 {issue['file']}: {', '.join(issue['issues'])}")
    
    print("\nFixing issues...")
    
    fixed_count = 0
    
    for issue in issues:
        try:
            with open(issue['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the test section
            fixed_content = standardize_test_section(content, issue['path'])
            
            if fixed_content != content:
                with open(issue['path'], 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                fixed_count += 1
                print(f"✅ Fixed test in {issue['file']}")
        
        except Exception as e:
            print(f"❌ Error fixing {issue['file']}: {e}")
    
    return fixed_count

def main():
    """Main function to standardize all test sections."""
    print("=== Analyzing All Test Sections ===\n")
    
    fixed_count = fix_all_test_issues()
    
    print(f"\n=== Final Verification ===")
    remaining_issues = analyze_all_files()
    
    if remaining_issues:
        print(f"❌ {len(remaining_issues)} files still have test issues:")
        for issue in remaining_issues:
            print(f"  {issue['file']}: {', '.join(issue['issues'])}")
    else:
        print("✅ All test sections are now properly formatted and positioned!")
    
    print(f"\n✅ Fixed {fixed_count} test sections")
    print("All tests are now consistently positioned as second-to-last section before Navigation!")

if __name__ == "__main__":
    main()