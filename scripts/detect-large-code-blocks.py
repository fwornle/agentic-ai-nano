#!/usr/bin/env python3
"""
Standalone Code Block Detector for Course Materials

This script analyzes markdown files to identify code blocks that are too large (>20 lines)
and need to be broken down for better educational value.

Usage:
    python detect-large-code-blocks.py file.md
    python detect-large-code-blocks.py directory/
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

def detect_code_blocks(content: str) -> List[Dict]:
    """Detect all code blocks and their sizes in markdown content."""
    
    code_blocks = []
    lines = content.split('\n')
    in_code_block = False
    current_block = {
        'start_line': 0,
        'end_line': 0,
        'language': '',
        'content': [],
        'line_count': 0
    }
    
    for i, line in enumerate(lines, 1):
        # Detect start of code block
        if line.strip().startswith('```'):
            if not in_code_block:
                # Starting a new code block
                in_code_block = True
                language = line.strip()[3:].strip()
                current_block = {
                    'start_line': i,
                    'end_line': 0,
                    'language': language,
                    'content': [],
                    'line_count': 0
                }
            else:
                # Ending current code block
                in_code_block = False
                current_block['end_line'] = i
                current_block['line_count'] = len(current_block['content'])
                code_blocks.append(current_block.copy())
        elif in_code_block:
            # Inside a code block, collect content
            current_block['content'].append(line)
    
    return code_blocks

def analyze_file(file_path: str) -> Dict:
    """Analyze a single markdown file for large code blocks."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'code_blocks': [],
            'large_blocks': []
        }
    
    code_blocks = detect_code_blocks(content)
    large_blocks = [block for block in code_blocks if block['line_count'] > 20]
    
    return {
        'file': file_path,
        'total_code_blocks': len(code_blocks),
        'large_blocks_count': len(large_blocks),
        'code_blocks': code_blocks,
        'large_blocks': large_blocks,
        'needs_refactoring': len(large_blocks) > 0
    }

def analyze_directory(directory: str) -> List[Dict]:
    """Analyze all markdown files in a directory."""
    
    results = []
    for md_file in Path(directory).rglob('*.md'):
        if 'Test_Solutions' not in str(md_file):  # Skip test solution files
            result = analyze_file(str(md_file))
            results.append(result)
    
    return results

def print_summary(results: List[Dict]):
    """Print a summary of analysis results."""
    
    total_files = len(results)
    files_needing_refactoring = sum(1 for r in results if r.get('needs_refactoring', False))
    total_large_blocks = sum(r.get('large_blocks_count', 0) for r in results)
    
    print(f"\n📊 CODE BLOCK ANALYSIS SUMMARY")
    print(f"=" * 50)
    print(f"Files analyzed: {total_files}")
    print(f"Files needing refactoring: {files_needing_refactoring}")
    print(f"Total large code blocks (>20 lines): {total_large_blocks}")
    
    if files_needing_refactoring > 0:
        print(f"\n🚨 FILES WITH LARGE CODE BLOCKS:")
        print(f"-" * 40)
        
        for result in results:
            if result.get('needs_refactoring', False):
                file_name = os.path.basename(result['file'])
                large_count = result['large_blocks_count']
                print(f"📄 {file_name}: {large_count} large blocks")
                
                for block in result['large_blocks']:
                    lines = block['line_count']
                    start = block['start_line']
                    end = block['end_line']
                    lang = block['language'] or 'text'
                    print(f"   ⚠️  Lines {start}-{end}: {lines} lines ({lang})")
        
        print(f"\n✅ RECOMMENDATION:")
        print(f"Use course-material-refactorer agent on these {files_needing_refactoring} files")
    else:
        print(f"\n✅ All files have appropriately sized code blocks!")

def main():
    if len(sys.argv) != 2:
        print("Usage: python detect-large-code-blocks.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        result = analyze_file(target)
        results = [result]
    elif os.path.isdir(target):
        results = analyze_directory(target)
    else:
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    # Print detailed results for each file
    for result in results:
        if result.get('error'):
            print(f"❌ Error analyzing {result['file']}: {result['error']}")
            continue
            
        if result.get('needs_refactoring', False):
            file_name = os.path.basename(result['file'])
            print(f"\n📄 {file_name}")
            print(f"Large blocks: {result['large_blocks_count']}")
            
            for i, block in enumerate(result['large_blocks'], 1):
                print(f"  Block {i}: Lines {block['start_line']}-{block['end_line']} ({block['line_count']} lines, {block['language'] or 'text'})")
    
    # Print summary
    print_summary(results)
    
    # Output JSON for programmatic use
    json_output = {
        'summary': {
            'total_files': len(results),
            'files_needing_refactoring': sum(1 for r in results if r.get('needs_refactoring', False)),
            'total_large_blocks': sum(r.get('large_blocks_count', 0) for r in results)
        },
        'files': results
    }
    
    # Save JSON report
    output_file = 'code-block-analysis.json'
    with open(output_file, 'w') as f:
        json.dump(json_output, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {output_file}")

if __name__ == "__main__":
    main()