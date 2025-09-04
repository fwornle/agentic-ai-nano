#!/usr/bin/env python3
"""
Verify ALL markdown files have proper structure:
(a) Last two sections are Multiple Choice Test and Navigation
(b) Remove any clutter like "Test your knowledge" sections before the test
"""

import os
import re
import glob

def analyze_file_structure(file_path):
    """Analyze a file's tail structure and identify issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    lines = content.split('\n')
    
    # Find all section headers (## headings)
    sections = []
    for i, line in enumerate(lines):
        if line.startswith('## '):
            sections.append({
                'line_num': i,
                'title': line.strip(),
                'content_start': i + 1
            })
    
    if len(sections) < 2:
        return {'error': 'Less than 2 sections found'}
    
    # Check last two sections
    last_section = sections[-1]['title'] if sections else ""
    second_last_section = sections[-2]['title'] if len(sections) >= 2 else ""
    
    issues = []
    
    # Check if last section is Navigation
    if not last_section.startswith('## 🧭 Navigation'):
        issues.append('Last section is not Navigation')
    
    # Check if second-last section is Multiple Choice Test
    if not second_last_section.startswith('## 📝 Multiple Choice Test'):
        # Only flag as issue if file has tests at all
        if '📝 Multiple Choice Test' in content or 'Test' in content:
            issues.append('Second-last section is not Multiple Choice Test')
    
    # Check for clutter sections before test
    clutter_patterns = [
        '## 📝 Multiple Choice Test.*?& Continuation',
        '## Test Your Knowledge',
        '## Complete Assessment',
        '## Knowledge Assessment',
        '## Quick Understanding Check',
        '### Test Your Knowledge',
        '### Complete Assessment',
        '### Knowledge Assessment',
        '### Quick Understanding Check'
    ]
    
    clutter_found = []
    for pattern in clutter_patterns:
        if re.search(pattern, content):
            clutter_found.append(pattern)
    
    if clutter_found:
        issues.append(f'Clutter sections found: {", ".join(clutter_found)}')
    
    return {
        'last_section': last_section,
        'second_last_section': second_last_section,
        'issues': issues,
        'has_test': '📝 Multiple Choice Test' in content,
        'has_navigation': '🧭 Navigation' in content
    }

def clean_file_clutter(file_path):
    """Remove clutter sections from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading: {e}"
    
    original_content = content
    
    # Remove clutter patterns
    clutter_removals = [
        # Remove "Test your knowledge" style sections
        r'## Test Your Knowledge.*?\n(?=[#\n])',
        r'### Test Your Knowledge.*?\n(?=[#\n])',
        r'## Knowledge Assessment.*?\n(?=[#\n])',
        r'### Knowledge Assessment.*?\n(?=[#\n])',
        r'## Quick Understanding Check.*?\n(?=[#\n])',
        r'### Quick Understanding Check.*?\n(?=[#\n])',
        
        # Remove complete assessment clutter
        r'## Complete Assessment.*?\n(?=[#\n])',
        r'### Complete Assessment.*?\n(?=[#\n])',
        
        # Remove continuation clutter from test headers
        r'## 📝 Multiple Choice Test - Session \d+ & Continuation.*?\n',
        
        # Remove sections with links to test/solutions that aren't the actual test
        r'### 📝 Multiple Choice Test.*?- **\[📝 Test Your Knowledge.*?\n',
        r'- \*\*\[📝 Test Your Knowledge.*?\n',
        r'- \*\*\[📖 Next Session.*?\n',
        
        # Remove "Complete Learning Path Recommendations" sections
        r'### Complete Learning Path Recommendations.*?\n(?=##|\n##)',
        r'## Complete Learning Path Recommendations.*?\n(?=##|\n##)',
        
        # Remove observer/participant/implementer question sections before test
        r'\*\*🎯 Observer Level Questions:\*\*.*?\n(?=\*\*📝|\*\*⚙️|##)',
        r'\*\*📝 Participant Level Questions:\*\*.*?\n(?=\*\*⚙️|##)',
        r'\*\*⚙️ Implementer Level Questions:\*\*.*?\n(?=##)',
        
        # Clean up multiple consecutive newlines
        r'\n{3,}',
    ]
    
    for pattern in clutter_removals:
        if pattern == r'\n{3,}':
            content = re.sub(pattern, '\n\n', content, flags=re.DOTALL | re.MULTILINE)
        else:
            content = re.sub(pattern, '\n', content, flags=re.DOTALL | re.MULTILINE)
    
    # Clean up any remaining artifacts
    content = re.sub(r'\n\n+---\n\n+## 📝 Multiple Choice Test', '\n\n## 📝 Multiple Choice Test', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Cleaned successfully"
        except Exception as e:
            return False, f"Error writing: {e}"
    
    return False, "No changes needed"

def verify_all_files():
    """Verify all markdown files and report issues."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    # Skip backup files
    md_files = [f for f in md_files if 'BACKUP' not in f and 'ORIGINAL' not in f]
    
    print(f"Analyzing {len(md_files)} markdown files...\n")
    
    files_with_issues = []
    files_cleaned = []
    
    for file_path in md_files:
        analysis = analyze_file_structure(file_path)
        
        if 'error' in analysis:
            continue
        
        if analysis['issues']:
            files_with_issues.append({
                'file': os.path.basename(file_path),
                'path': file_path,
                'issues': analysis['issues'],
                'last_section': analysis['last_section'],
                'second_last_section': analysis['second_last_section']
            })
            
            # Try to clean the file
            cleaned, message = clean_file_clutter(file_path)
            if cleaned:
                files_cleaned.append(os.path.basename(file_path))
                print(f"✅ Cleaned clutter in {os.path.basename(file_path)}")
    
    return files_with_issues, files_cleaned

def main():
    """Main function to verify and clean all files."""
    print("=== Verifying All File Structures & Cleaning Clutter ===\n")
    
    issues, cleaned = verify_all_files()
    
    print(f"\n=== Summary ===")
    
    if cleaned:
        print(f"✅ Cleaned clutter in {len(cleaned)} files:")
        for file in cleaned[:10]:  # Show first 10
            print(f"  {file}")
        if len(cleaned) > 10:
            print(f"  ... and {len(cleaned) - 10} more files")
    
    # Re-verify after cleaning
    print(f"\n=== Post-Cleanup Verification ===")
    remaining_issues, _ = verify_all_files()
    
    if remaining_issues:
        print(f"❌ {len(remaining_issues)} files still have structural issues:")
        for issue in remaining_issues[:5]:  # Show first 5
            print(f"  {issue['file']}: {', '.join(issue['issues'])}")
        if len(remaining_issues) > 5:
            print(f"  ... and {len(remaining_issues) - 5} more files")
    else:
        print("✅ All files have proper structure: Test → Navigation")
    
    print(f"\nAll markdown files verified and cleaned!")

if __name__ == "__main__":
    main()