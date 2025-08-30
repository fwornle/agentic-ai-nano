#!/usr/bin/env python3
"""
Code Block Explanation Quality Checker

This script identifies code blocks that lack proper educational explanations:
- Code blocks with no explanation (just title)
- Code blocks with insufficient explanation (< 30 words)
- Code blocks missing educational context
- Consecutive code blocks without intermediate explanations

Usage:
    python detect-insufficient-explanations.py file.md
    python detect-insufficient-explanations.py directory/
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

def analyze_explanations(content: str) -> Dict:
    """Analyze the quality of explanations for code blocks."""
    
    lines = content.split('\n')
    issues = []
    
    # Find all code blocks with their surrounding text
    code_blocks = []
    in_code_block = False
    current_block = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            if not in_code_block:
                # Starting new code block
                in_code_block = True
                current_block = {
                    'start_line': i + 1,
                    'end_line': 0,
                    'language': stripped[3:].strip(),
                    'content': [],
                    'preceding_text': [],
                    'following_text': []
                }
                
                # Collect preceding context (up to 5 lines before)
                start_idx = max(0, i - 5)
                for j in range(start_idx, i):
                    if lines[j].strip():
                        current_block['preceding_text'].append(lines[j].strip())
                
            else:
                # Ending code block
                in_code_block = False
                current_block['end_line'] = i + 1
                
                # Collect following context (up to 10 lines after)
                end_idx = min(len(lines), i + 11)
                for j in range(i + 1, end_idx):
                    if lines[j].strip():
                        current_block['following_text'].append(lines[j].strip())
                    # Stop at next code block or major heading
                    if lines[j].strip().startswith('```') or lines[j].strip().startswith('#'):
                        break
                
                code_blocks.append(current_block)
                current_block = None
        
        elif in_code_block and current_block:
            current_block['content'].append(line)
    
    # Analyze each code block for explanation quality
    for block in code_blocks:
        block_size = len([line for line in block['content'] if line.strip()])
        
        # Skip very small code blocks (< 3 lines)
        if block_size < 3:
            continue
        
        following_text = ' '.join(block['following_text'])
        word_count = len(following_text.split())
        
        # Check for various explanation issues
        if not following_text:
            issues.append({
                'type': 'no_explanation',
                'severity': 'high',
                'line': block['end_line'] + 1,
                'code_block_size': block_size,
                'message': f'Code block ({block_size} lines) at line {block["start_line"]} has no explanation',
                'suggestion': 'Add detailed explanation covering what the code does, why it matters, and key insights'
            })
        
        elif word_count < 20:
            issues.append({
                'type': 'insufficient_explanation',
                'severity': 'high',
                'line': block['end_line'] + 1,
                'code_block_size': block_size,
                'word_count': word_count,
                'message': f'Code block ({block_size} lines) at line {block["start_line"]} has insufficient explanation ({word_count} words)',
                'suggestion': 'Expand explanation to at least 30-50 words covering functionality, purpose, and educational insights'
            })
        
        elif word_count < 30 and block_size > 10:
            issues.append({
                'type': 'inadequate_explanation_for_size',
                'severity': 'medium',
                'line': block['end_line'] + 1,
                'code_block_size': block_size,
                'word_count': word_count,
                'message': f'Large code block ({block_size} lines) at line {block["start_line"]} has minimal explanation ({word_count} words)',
                'suggestion': 'Provide more detailed explanation proportional to code complexity'
            })
        
        # Check explanation quality indicators
        explanation_lower = following_text.lower()
        
        # Missing educational context indicators
        if not any(indicator in explanation_lower for indicator in [
            'this', 'these', 'the code', 'this approach', 'this method', 'this function',
            'notice', 'important', 'key', 'essential', 'crucial', 'enables', 'provides',
            'because', 'since', 'as', 'when', 'while', 'ensures', 'prevents'
        ]):
            issues.append({
                'type': 'lacks_educational_context',
                'severity': 'medium',
                'line': block['end_line'] + 1,
                'code_block_size': block_size,
                'message': f'Code block at line {block["start_line"]} explanation lacks educational context',
                'suggestion': 'Add context explaining WHY this approach is used and HOW it benefits the student'
            })
        
        # Check for generic/lazy explanations
        generic_phrases = [
            'here we', 'this code', 'the above', 'as shown', 'as seen',
            'simply', 'just', 'basic', 'standard', 'typical', 'usual'
        ]
        
        if any(phrase in explanation_lower for phrase in generic_phrases) and word_count < 40:
            issues.append({
                'type': 'generic_explanation',
                'severity': 'medium',
                'line': block['end_line'] + 1,
                'code_block_size': block_size,
                'message': f'Code block at line {block["start_line"]} has generic/lazy explanation',
                'suggestion': 'Replace generic phrases with specific, educational explanations'
            })
    
    # Check for consecutive code blocks without explanations
    for i in range(len(code_blocks) - 1):
        current = code_blocks[i]
        next_block = code_blocks[i + 1]
        
        # Check if blocks are consecutive (within 3 lines)
        if next_block['start_line'] - current['end_line'] <= 3:
            issues.append({
                'type': 'consecutive_code_blocks',
                'severity': 'medium',
                'line': current['end_line'],
                'message': f'Consecutive code blocks at lines {current["start_line"]} and {next_block["start_line"]} without intermediate explanation',
                'suggestion': 'Add transitional explanation between code blocks to maintain narrative flow'
            })
    
    return {
        'total_code_blocks': len(code_blocks),
        'total_issues': len(issues),
        'issues': issues,
        'needs_improvement': len(issues) > 0,
        'quality_score': max(0, (len(code_blocks) - len(issues)) / max(1, len(code_blocks))) * 100
    }

def analyze_file(file_path: str) -> Dict:
    """Analyze explanation quality in a single file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'issues': []
        }
    
    analysis = analyze_explanations(content)
    analysis['file'] = file_path
    
    return analysis

def analyze_directory(directory: str) -> List[Dict]:
    """Analyze all markdown files in a directory."""
    
    results = []
    for md_file in Path(directory).rglob('*.md'):
        if 'Test_Solutions' not in str(md_file):  # Skip test solution files
            result = analyze_file(str(md_file))
            results.append(result)
    
    return results

def print_summary(results: List[Dict]):
    """Print summary of explanation quality analysis."""
    
    total_files = len(results)
    files_needing_improvement = sum(1 for r in results if r.get('needs_improvement', False))
    total_issues = sum(r.get('total_issues', 0) for r in results)
    total_code_blocks = sum(r.get('total_code_blocks', 0) for r in results)
    
    avg_quality = sum(r.get('quality_score', 0) for r in results) / max(1, total_files)
    
    print(f"\n📚 CODE BLOCK EXPLANATION ANALYSIS")
    print(f"=" * 50)
    print(f"Files analyzed: {total_files}")
    print(f"Total code blocks: {total_code_blocks}")
    print(f"Files needing improvement: {files_needing_improvement}")
    print(f"Total explanation issues: {total_issues}")
    print(f"Average quality score: {avg_quality:.1f}%")
    
    if files_needing_improvement > 0:
        print(f"\n🚨 FILES NEEDING EXPLANATION IMPROVEMENT:")
        print(f"-" * 45)
        
        # Sort by quality score (worst first)
        sorted_results = sorted([r for r in results if r.get('needs_improvement', False)], 
                              key=lambda x: x.get('quality_score', 0))
        
        for result in sorted_results:
            file_name = os.path.basename(result['file'])
            quality_score = result.get('quality_score', 0)
            issue_count = result['total_issues']
            block_count = result.get('total_code_blocks', 0)
            
            print(f"📄 {file_name}: {quality_score:.1f}% quality ({issue_count} issues, {block_count} blocks)")
            
            # Group issues by severity
            high_issues = [i for i in result['issues'] if i.get('severity') == 'high']
            medium_issues = [i for i in result['issues'] if i.get('severity') == 'medium']
            
            if high_issues:
                print(f"   🔴 High Priority Issues: {len(high_issues)}")
                for issue in high_issues[:3]:  # Show top 3
                    print(f"      Line {issue['line']}: {issue['message']}")
            
            if medium_issues:
                print(f"   🟡 Medium Priority Issues: {len(medium_issues)}")
                for issue in medium_issues[:2]:  # Show top 2
                    print(f"      Line {issue['line']}: {issue['message']}")
        
        print(f"\n✅ RECOMMENDATIONS:")
        print(f"1. Focus on HIGH priority issues first (missing/insufficient explanations)")
        print(f"2. Add 30-50 word explanations for each code block")
        print(f"3. Include educational context: what, why, how")
        print(f"4. Use course-material-refactorer agent to fix systematically")
    
    else:
        print(f"\n✅ All files have adequate code block explanations!")

def main():
    if len(sys.argv) != 2:
        print("Usage: python detect-insufficient-explanations.py <file_or_directory>")
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
    
    # Print detailed results for worst files
    worst_files = sorted([r for r in results if r.get('needs_improvement', False)], 
                        key=lambda x: x.get('quality_score', 100))[:5]
    
    for result in worst_files:
        if result.get('error'):
            print(f"❌ Error analyzing {result['file']}: {result['error']}")
            continue
        
        file_name = os.path.basename(result['file'])
        print(f"\n📄 {file_name} - Quality: {result.get('quality_score', 0):.1f}%")
        print(f"Issues breakdown:")
        
        issue_types = {}
        for issue in result.get('issues', []):
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        for issue_type, issues in issue_types.items():
            print(f"  {issue_type.replace('_', ' ').title()}: {len(issues)} issues")
    
    # Print summary
    print_summary(results)
    
    # Save detailed JSON report
    output_file = 'explanation-quality-report.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total_files': len(results),
                'files_needing_improvement': sum(1 for r in results if r.get('needs_improvement', False)),
                'total_issues': sum(r.get('total_issues', 0) for r in results),
                'average_quality_score': sum(r.get('quality_score', 0) for r in results) / max(1, len(results))
            },
            'files': results
        }, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {output_file}")

if __name__ == "__main__":
    main()