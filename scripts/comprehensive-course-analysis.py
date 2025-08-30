#!/usr/bin/env python3
"""
Comprehensive Course Material Quality Analysis

This master script combines all quality checks:
- Large code blocks (>20 lines) detection
- Markdown formatting issues
- Insufficient explanations
- Overall course material quality assessment

Usage:
    python comprehensive-course-analysis.py directory/
    python comprehensive-course-analysis.py file.md --detailed
"""

import sys
import os
import subprocess
from pathlib import Path
import json
from typing import Dict, List

def run_analysis_script(script_path: str, target: str) -> Dict:
    """Run an analysis script and return its JSON output."""
    
    try:
        # Run the script
        result = subprocess.run([
            'python3', script_path, target
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': result.stderr,
                'script': script_path
            }
        
        # Try to read the JSON output file
        script_name = Path(script_path).stem
        json_files = {
            'detect-large-code-blocks': 'code-block-analysis.json',
            'check-markdown-formatting': 'markdown-formatting-report.json',
            'detect-insufficient-explanations': 'explanation-quality-report.json'
        }
        
        json_file = json_files.get(script_name)
        if json_file and os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            # Clean up temp file
            os.remove(json_file)
            return {
                'success': True,
                'data': data,
                'script': script_path
            }
        
        return {
            'success': True,
            'data': {'summary': 'No JSON output available'},
            'script': script_path
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Script timeout after 300 seconds',
            'script': script_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'script': script_path
        }

def comprehensive_analysis(target: str) -> Dict:
    """Run comprehensive analysis on target directory or file."""
    
    script_dir = Path(__file__).parent
    scripts = [
        script_dir / 'detect-large-code-blocks.py',
        script_dir / 'check-markdown-formatting.py', 
        script_dir / 'detect-insufficient-explanations.py'
    ]
    
    results = {}
    
    print("🔍 Running comprehensive course material analysis...")
    print(f"Target: {target}")
    print("=" * 60)
    
    for script in scripts:
        script_name = script.stem.replace('-', '_')
        print(f"\n📊 Running {script.name}...")
        
        result = run_analysis_script(str(script), target)
        results[script_name] = result
        
        if result['success']:
            print(f"✅ {script.name} completed successfully")
        else:
            print(f"❌ {script.name} failed: {result['error']}")
    
    return results

def calculate_overall_quality_score(analysis_results: Dict) -> Dict:
    """Calculate overall quality metrics from all analysis results."""
    
    metrics = {
        'total_files': 0,
        'code_block_score': 0,
        'formatting_score': 0,
        'explanation_score': 0,
        'overall_score': 0,
        'critical_issues': 0,
        'total_issues': 0
    }
    
    # Extract metrics from each analysis
    if analysis_results['detect_large_code_blocks']['success']:
        data = analysis_results['detect_large_code_blocks']['data']
        summary = data.get('summary', {})
        
        total_files = summary.get('total_files', 0)
        large_blocks = summary.get('total_large_blocks', 0)
        
        metrics['total_files'] = total_files
        metrics['code_block_score'] = max(0, (total_files * 20 - large_blocks) / max(1, total_files * 20)) * 100
        metrics['critical_issues'] += large_blocks
    
    if analysis_results['check_markdown_formatting']['success']:
        data = analysis_results['check_markdown_formatting']['data']
        summary = data.get('summary', {})
        
        formatting_issues = summary.get('total_issues', 0)
        metrics['formatting_score'] = max(0, (metrics['total_files'] * 5 - formatting_issues) / max(1, metrics['total_files'] * 5)) * 100
        metrics['total_issues'] += formatting_issues
    
    if analysis_results['detect_insufficient_explanations']['success']:
        data = analysis_results['detect_insufficient_explanations']['data']
        summary = data.get('summary', {})
        
        explanation_score = summary.get('average_quality_score', 0)
        explanation_issues = summary.get('total_issues', 0)
        
        metrics['explanation_score'] = explanation_score
        metrics['total_issues'] += explanation_issues
    
    # Calculate overall score (weighted average)
    metrics['overall_score'] = (
        metrics['code_block_score'] * 0.4 +  # 40% weight - most important
        metrics['explanation_score'] * 0.4 +  # 40% weight - equally important
        metrics['formatting_score'] * 0.2     # 20% weight - least critical
    )
    
    return metrics

def print_comprehensive_summary(analysis_results: Dict, metrics: Dict):
    """Print comprehensive summary of all analyses."""
    
    print(f"\n" + "="*60)
    print(f"📋 COMPREHENSIVE COURSE MATERIAL ANALYSIS SUMMARY")
    print(f"="*60)
    
    print(f"\n🎯 OVERALL QUALITY METRICS:")
    print(f"Overall Score: {metrics['overall_score']:.1f}%")
    print(f"Files Analyzed: {metrics['total_files']}")
    print(f"Critical Issues: {metrics['critical_issues']}")
    print(f"Total Issues: {metrics['total_issues']}")
    
    print(f"\n📊 DETAILED SCORES:")
    print(f"Code Block Quality: {metrics['code_block_score']:.1f}%")
    print(f"Explanation Quality: {metrics['explanation_score']:.1f}%") 
    print(f"Formatting Quality: {metrics['formatting_score']:.1f}%")
    
    # Quality assessment
    if metrics['overall_score'] >= 90:
        quality_status = "🟢 EXCELLENT"
    elif metrics['overall_score'] >= 75:
        quality_status = "🟡 GOOD" 
    elif metrics['overall_score'] >= 60:
        quality_status = "🟠 NEEDS IMPROVEMENT"
    else:
        quality_status = "🔴 POOR - URGENT ACTION REQUIRED"
    
    print(f"\n📈 QUALITY ASSESSMENT: {quality_status}")
    
    # Specific recommendations
    print(f"\n✅ PRIORITY RECOMMENDATIONS:")
    
    if metrics['code_block_score'] < 80:
        large_blocks = analysis_results['detect_large_code_blocks']['data']['summary'].get('total_large_blocks', 0)
        print(f"1. 🚨 HIGH: Break down {large_blocks} large code blocks (>20 lines)")
    
    if metrics['explanation_score'] < 75:
        print(f"2. 🚨 HIGH: Improve code block explanations (current: {metrics['explanation_score']:.1f}%)")
    
    if metrics['formatting_score'] < 90:
        formatting_issues = analysis_results['check_markdown_formatting']['data']['summary'].get('total_issues', 0)
        print(f"3. 🔧 MEDIUM: Fix {formatting_issues} markdown formatting issues")
    
    print(f"\n🛠️  RECOMMENDED ACTION:")
    if metrics['overall_score'] < 70:
        print(f"Use course-material-refactorer agent immediately on all flagged files")
    else:
        print(f"Focus on files with lowest quality scores first")

def generate_prioritized_file_list(analysis_results: Dict) -> List[Dict]:
    """Generate prioritized list of files that need refactoring."""
    
    priority_files = []
    
    # Get file-level data from each analysis
    code_block_files = {}
    if analysis_results['detect_large_code_blocks']['success']:
        for file_data in analysis_results['detect_large_code_blocks']['data'].get('files', []):
            if file_data.get('needs_refactoring', False):
                file_path = file_data['file']
                code_block_files[file_path] = {
                    'large_blocks': file_data.get('large_blocks_count', 0),
                    'total_blocks': file_data.get('total_code_blocks', 0)
                }
    
    explanation_files = {}
    if analysis_results['detect_insufficient_explanations']['success']:
        for file_data in analysis_results['detect_insufficient_explanations']['data'].get('files', []):
            if file_data.get('needs_improvement', False):
                file_path = file_data['file']
                explanation_files[file_path] = {
                    'quality_score': file_data.get('quality_score', 0),
                    'issues': file_data.get('total_issues', 0)
                }
    
    # Combine and prioritize
    all_files = set(code_block_files.keys()) | set(explanation_files.keys())
    
    for file_path in all_files:
        file_name = os.path.basename(file_path)
        
        priority_score = 0
        issues = []
        
        if file_path in code_block_files:
            large_blocks = code_block_files[file_path]['large_blocks']
            priority_score += large_blocks * 10  # High weight for large blocks
            issues.append(f"{large_blocks} large code blocks")
        
        if file_path in explanation_files:
            quality_score = explanation_files[file_path]['quality_score']
            priority_score += (100 - quality_score) / 5  # Weight by poor quality
            issues.append(f"{quality_score:.1f}% explanation quality")
        
        priority_files.append({
            'file': file_path,
            'file_name': file_name,
            'priority_score': priority_score,
            'issues': issues
        })
    
    # Sort by priority (highest first)
    priority_files.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return priority_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python comprehensive-course-analysis.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    detailed = '--detailed' in sys.argv
    
    if not (os.path.isfile(target) or os.path.isdir(target)):
        print(f"Error: {target} is not a valid file or directory")
        sys.exit(1)
    
    # Run comprehensive analysis
    analysis_results = comprehensive_analysis(target)
    
    # Calculate metrics
    metrics = calculate_overall_quality_score(analysis_results)
    
    # Print summary
    print_comprehensive_summary(analysis_results, metrics)
    
    # Generate prioritized file list
    priority_files = generate_prioritized_file_list(analysis_results)
    
    if priority_files:
        print(f"\n📋 PRIORITIZED REFACTORING LIST:")
        print(f"-" * 50)
        
        for i, file_info in enumerate(priority_files[:10], 1):  # Top 10
            print(f"{i:2d}. {file_info['file_name']} (Score: {file_info['priority_score']:.1f})")
            for issue in file_info['issues']:
                print(f"     - {issue}")
    
    # Save comprehensive report
    output_data = {
        'analysis_timestamp': str(Path(__file__).stat().st_mtime),
        'target': target,
        'overall_metrics': metrics,
        'detailed_results': analysis_results,
        'priority_files': priority_files
    }
    
    output_file = 'comprehensive-course-analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n📋 Comprehensive report saved to: {output_file}")
    
    # Exit with appropriate code
    if metrics['overall_score'] < 60:
        sys.exit(1)  # Poor quality
    elif metrics['critical_issues'] > 0:
        sys.exit(2)  # Has critical issues
    else:
        sys.exit(0)  # Good quality

if __name__ == "__main__":
    main()