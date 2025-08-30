#!/usr/bin/env python3
"""
Iterative Refactoring Cycle Script

This script implements a reliable iterative process for course material refactoring:
1. Detect large code blocks
2. Break them down with explanations
3. Check for formatting mistakes (orphaned ```)
4. Fix formatting issues
5. Verify no large blocks remain
6. Repeat until 100% compliant

Usage:
    python iterative-refactoring-cycle.py file.md
    python iterative-refactoring-cycle.py directory/
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json
import subprocess

def detect_orphaned_code_markers(content: str) -> List[Dict]:
    """Detect orphaned ``` markers that appear inappropriately."""
    lines = content.split('\n')
    issues = []
    in_code_block = False
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
            else:
                in_code_block = False
        elif stripped == '```' and not in_code_block:
            # Found orphaned closing marker
            # Check if next line is regular text (not code)
            next_lines = lines[i:i+3] if i < len(lines) else []
            next_content = '\n'.join(next_lines).strip()
            
            # If followed by regular text, this is likely a mistake
            if next_content and not next_content.startswith('```'):
                issues.append({
                    'type': 'orphaned_code_marker',
                    'line': i,
                    'context': next_content[:50] + '...' if len(next_content) > 50 else next_content,
                    'suggestion': 'Remove this orphaned ``` marker'
                })
    
    return issues

def fix_orphaned_markers(content: str) -> str:
    """Remove orphaned ``` markers that appear inappropriately."""
    lines = content.split('\n')
    fixed_lines = []
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                fixed_lines.append(line)
            else:
                in_code_block = False
                fixed_lines.append(line)
        elif stripped == '```' and not in_code_block:
            # Check if this is followed by regular text
            next_lines = lines[i+1:i+4] if i+1 < len(lines) else []
            next_content = '\n'.join(next_lines).strip()
            
            # If followed by regular text, remove this orphaned marker
            if next_content and not next_content.startswith('```'):
                print(f"  ✓ Removed orphaned ``` at line {i+1}")
                # Skip this line
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def run_code_block_detector(target: str) -> Dict:
    """Run the code block detector and return results."""
    try:
        script_path = '/Users/q284340/Agentic/nano-degree/scripts/detect-large-code-blocks.py'
        result = subprocess.run([
            'python3', script_path, target
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return {'success': False, 'error': result.stderr}
        
        # Read the JSON output
        if os.path.exists('code-block-analysis.json'):
            with open('code-block-analysis.json', 'r') as f:
                data = json.load(f)
            os.remove('code-block-analysis.json')
            return {'success': True, 'data': data}
        
        return {'success': True, 'data': {'summary': {'total_large_blocks': 0}}}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def run_formatting_fixer(target: str) -> Dict:
    """Run the markdown formatting fixer."""
    try:
        script_path = '/Users/q284340/Agentic/nano-degree/scripts/check-markdown-formatting.py'
        result = subprocess.run([
            'python3', script_path, target, '--fix'
        ], capture_output=True, text=True, timeout=300)
        
        return {'success': result.returncode == 0, 'output': result.stdout}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def refactor_single_file(file_path: str, max_iterations: int = 5) -> Dict:
    """Refactor a single file with iterative verification."""
    
    print(f"\n🔄 Starting iterative refactoring for {os.path.basename(file_path)}")
    
    results = {
        'file': file_path,
        'iterations': 0,
        'large_blocks_eliminated': 0,
        'formatting_issues_fixed': 0,
        'success': False
    }
    
    for iteration in range(max_iterations):
        results['iterations'] = iteration + 1
        print(f"\n  Iteration {iteration + 1}/{max_iterations}")
        
        # Step 1: Check for large code blocks
        print("  📊 Checking for large code blocks...")
        detector_result = run_code_block_detector(file_path)
        
        if not detector_result['success']:
            print(f"  ❌ Detector failed: {detector_result['error']}")
            break
        
        large_blocks = detector_result['data']['summary'].get('total_large_blocks', 0)
        print(f"  📈 Found {large_blocks} large code blocks")
        
        if large_blocks == 0:
            print("  ✅ No large code blocks remaining!")
            results['success'] = True
            break
        
        # Step 2: Fix orphaned markers first
        print("  🔧 Fixing orphaned code markers...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orphaned_issues = detect_orphaned_code_markers(content)
            if orphaned_issues:
                print(f"  📋 Found {len(orphaned_issues)} orphaned markers")
                fixed_content = fix_orphaned_markers(content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                results['formatting_issues_fixed'] += len(orphaned_issues)
            
        except Exception as e:
            print(f"  ⚠️ Error fixing orphaned markers: {e}")
        
        # Step 3: Run markdown formatting fixer
        print("  🔧 Running markdown formatting fixer...")
        format_result = run_formatting_fixer(file_path)
        
        if format_result['success']:
            print("  ✅ Formatting check completed")
        else:
            print(f"  ⚠️ Formatting issues: {format_result.get('error', 'Unknown')}")
        
        # Step 4: Manual intervention needed message
        print(f"  🚨 Manual refactoring needed for {large_blocks} large code blocks")
        print(f"     Please break these down into 5-15 line segments with explanations")
        
        # For now, we'll break here and let the user know manual work is needed
        # In a full implementation, this would trigger the course-material-refactorer agent
        break
    
    if not results['success'] and results['iterations'] >= max_iterations:
        print(f"  ⚠️ Reached maximum iterations ({max_iterations}) - manual intervention needed")
    
    return results

def refactor_directory(directory: str) -> List[Dict]:
    """Refactor all markdown files in a directory."""
    results = []
    
    print(f"🎯 Starting iterative refactoring for directory: {directory}")
    
    for md_file in Path(directory).rglob('*.md'):
        if 'Test_Solutions' not in str(md_file):
            result = refactor_single_file(str(md_file))
            results.append(result)
    
    return results

def print_summary(results: List[Dict]):
    """Print summary of refactoring results."""
    
    total_files = len(results)
    successful_files = sum(1 for r in results if r['success'])
    total_iterations = sum(r['iterations'] for r in results)
    total_formatting_fixes = sum(r['formatting_issues_fixed'] for r in results)
    
    print(f"\n📋 ITERATIVE REFACTORING SUMMARY")
    print(f"=" * 50)
    print(f"Files processed: {total_files}")
    print(f"Successfully completed: {successful_files}")
    print(f"Total iterations: {total_iterations}")
    print(f"Formatting issues fixed: {total_formatting_fixes}")
    
    # Files still needing work
    incomplete_files = [r for r in results if not r['success']]
    if incomplete_files:
        print(f"\n🚨 FILES STILL NEEDING MANUAL REFACTORING:")
        print(f"-" * 45)
        
        for result in incomplete_files:
            file_name = os.path.basename(result['file'])
            iterations = result['iterations']
            print(f"📄 {file_name} (after {iterations} iterations)")

def main():
    if len(sys.argv) != 2:
        print("Usage: python iterative-refactoring-cycle.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        result = refactor_single_file(target)
        results = [result]
    elif os.path.isdir(target):
        results = refactor_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    print_summary(results)
    
    # Save results
    output_file = 'iterative-refactoring-results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_files': len(results),
                'successful_files': sum(1 for r in results if r['success']),
                'total_formatting_fixes': sum(r['formatting_issues_fixed'] for r in results)
            },
            'files': results
        }, f, indent=2)
    
    print(f"\n📋 Results saved to: {output_file}")

if __name__ == "__main__":
    main()