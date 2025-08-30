#!/usr/bin/env python3
"""
Markdown Code Block Formatting Checker

This script identifies and fixes common markdown formatting issues in course materials:
- Unclosed code blocks (missing closing ```)
- Missing opening code blocks (orphaned closing ```)
- Improperly formatted code block markers
- Missing language specifiers

Usage:
    python check-markdown-formatting.py file.md
    python check-markdown-formatting.py directory/ --fix
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

def check_code_block_formatting(content: str) -> Dict:
    """Check for markdown formatting issues in code blocks."""
    
    lines = content.split('\n')
    issues = []
    in_code_block = False
    block_start_line = 0
    block_language = ""
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                # Starting a new code block
                in_code_block = True
                block_start_line = i
                block_language = stripped[3:].strip()
                
                # Check if language is specified for python blocks
                if not block_language and i < len(lines):
                    # Look ahead to see if this looks like Python code
                    next_few_lines = '\n'.join(lines[i:i+3])
                    if any(keyword in next_few_lines for keyword in ['import ', 'def ', 'class ', 'async ', 'await ']):
                        issues.append({
                            'type': 'missing_language_specifier',
                            'line': i,
                            'message': f'Code block at line {i} appears to be Python but lacks language specifier',
                            'suggestion': f'Change "```" to "```python"'
                        })
            else:
                # Ending current code block
                in_code_block = False
                block_start_line = 0
                block_language = ""
        
        # Check for orphaned closing markers
        elif stripped == '```' and not in_code_block:
            issues.append({
                'type': 'orphaned_closing_marker',
                'line': i,
                'message': f'Found closing ``` at line {i} without matching opening marker',
                'suggestion': 'Remove this line or add matching opening ```'
            })
    
    # Check if file ends with unclosed code block
    if in_code_block:
        issues.append({
            'type': 'unclosed_code_block',
            'line': block_start_line,
            'message': f'Code block starting at line {block_start_line} is never closed',
            'suggestion': 'Add closing ``` marker'
        })
    
    return {
        'total_issues': len(issues),
        'issues': issues,
        'needs_fixing': len(issues) > 0
    }

def fix_code_block_formatting(content: str) -> Tuple[str, Dict]:
    """Fix common code block formatting issues."""
    
    lines = content.split('\n')
    fixed_lines = []
    fixes_applied = []
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                # Starting code block
                in_code_block = True
                language = stripped[3:].strip()
                
                # Auto-detect Python and add language specifier
                if not language and i + 1 < len(lines):
                    next_few_lines = '\n'.join(lines[i+1:i+4])
                    if any(keyword in next_few_lines for keyword in ['import ', 'def ', 'class ', 'async ', 'await ', 'from ']):
                        fixed_lines.append('```python')
                        fixes_applied.append({
                            'type': 'added_python_specifier',
                            'line': i + 1,
                            'original': line,
                            'fixed': '```python'
                        })
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                # Ending code block
                in_code_block = False
                fixed_lines.append(line)
        
        elif stripped == '```' and not in_code_block:
            # Skip orphaned closing markers
            fixes_applied.append({
                'type': 'removed_orphaned_marker',
                'line': i + 1,
                'original': line,
                'fixed': '(removed)'
            })
            # Skip this line
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Add closing marker if needed
    if in_code_block:
        fixed_lines.append('```')
        fixes_applied.append({
            'type': 'added_closing_marker',
            'line': len(fixed_lines),
            'original': '(missing)',
            'fixed': '```'
        })
    
    return '\n'.join(fixed_lines), {
        'fixes_applied': len(fixes_applied),
        'fixes': fixes_applied
    }

def analyze_file(file_path: str, fix: bool = False) -> Dict:
    """Analyze and optionally fix a markdown file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'issues': []
        }
    
    # Check for issues
    check_result = check_code_block_formatting(content)
    
    result = {
        'file': file_path,
        'total_issues': check_result['total_issues'],
        'issues': check_result['issues'],
        'needs_fixing': check_result['needs_fixing']
    }
    
    if fix and check_result['needs_fixing']:
        fixed_content, fix_result = fix_code_block_formatting(content)
        
        # Write fixed content back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            result['fixes_applied'] = fix_result['fixes_applied']
            result['fixes'] = fix_result['fixes']
            result['status'] = 'fixed'
            
        except Exception as e:
            result['fix_error'] = str(e)
            result['status'] = 'fix_failed'
    
    return result

def analyze_directory(directory: str, fix: bool = False) -> List[Dict]:
    """Analyze all markdown files in a directory."""
    
    results = []
    for md_file in Path(directory).rglob('*.md'):
        if 'Test_Solutions' not in str(md_file):  # Skip test solution files
            result = analyze_file(str(md_file), fix)
            results.append(result)
    
    return results

def print_summary(results: List[Dict]):
    """Print summary of formatting issues."""
    
    total_files = len(results)
    files_with_issues = sum(1 for r in results if r.get('needs_fixing', False))
    total_issues = sum(r.get('total_issues', 0) for r in results)
    
    print(f"\n📋 MARKDOWN FORMATTING ANALYSIS")
    print(f"=" * 50)
    print(f"Files analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total formatting issues: {total_issues}")
    
    if files_with_issues > 0:
        print(f"\n🚨 FILES WITH FORMATTING ISSUES:")
        print(f"-" * 40)
        
        for result in results:
            if result.get('needs_fixing', False):
                file_name = os.path.basename(result['file'])
                issue_count = result['total_issues']
                print(f"📄 {file_name}: {issue_count} issues")
                
                for issue in result['issues']:
                    issue_type = issue['type'].replace('_', ' ').title()
                    print(f"   ⚠️  Line {issue['line']}: {issue_type}")
                    print(f"      {issue['suggestion']}")
    
    else:
        print(f"\n✅ All markdown files have proper formatting!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python check-markdown-formatting.py <file_or_directory> [--fix]")
        sys.exit(1)
    
    target = sys.argv[1]
    fix = '--fix' in sys.argv
    
    if fix:
        print("🔧 Fix mode enabled - will automatically fix issues")
    
    if os.path.isfile(target):
        result = analyze_file(target, fix)
        results = [result]
    elif os.path.isdir(target):
        results = analyze_directory(target, fix)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    # Print detailed results
    for result in results:
        if result.get('error'):
            print(f"❌ Error analyzing {result['file']}: {result['error']}")
            continue
            
        if result.get('needs_fixing', False) or result.get('fixes_applied', 0) > 0:
            file_name = os.path.basename(result['file'])
            print(f"\n📄 {file_name}")
            
            if result.get('fixes_applied', 0) > 0:
                print(f"✅ Applied {result['fixes_applied']} fixes:")
                for fix in result.get('fixes', []):
                    print(f"  - Line {fix['line']}: {fix['type'].replace('_', ' ').title()}")
            
            elif result.get('needs_fixing', False):
                print(f"⚠️  {result['total_issues']} formatting issues found")
    
    # Print summary
    print_summary(results)
    
    # Save JSON report
    output_file = 'markdown-formatting-report.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_files': len(results),
                'files_with_issues': sum(1 for r in results if r.get('needs_fixing', False)),
                'total_issues': sum(r.get('total_issues', 0) for r in results)
            },
            'files': results
        }, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {output_file}")

if __name__ == "__main__":
    main()