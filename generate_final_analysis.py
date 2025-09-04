#!/usr/bin/env python3
"""
Generate comprehensive final analysis report of course structure
"""

import json
import os
from collections import defaultdict, Counter
from pathlib import Path

def generate_final_analysis():
    """Generate final comprehensive analysis."""
    
    # Load the analysis data
    with open('/Users/q284340/Agentic/nano-degree/course_structure_analysis.json', 'r') as f:
        data = json.load(f)
    
    # Categorize files by type and structure
    categorized_files = {
        'main_sessions': [],
        'module_files': [],
        'solution_files': [],
        'index_files': [],
        'other_files': []
    }
    
    chapter_structures = defaultdict(list)
    emoji_usage = Counter()
    navigation_consistency = defaultdict(list)
    
    for file_data in data['files']:
        file_path = file_data['file_path']
        
        # Categorize file type
        if 'Test_Solutions.md' in file_path:
            categorized_files['solution_files'].append(file_data)
        elif 'Module' in file_path and 'Session' in file_path:
            categorized_files['module_files'].append(file_data)
        elif file_path.endswith('index.md'):
            categorized_files['index_files'].append(file_data)
        elif 'Session' in file_path and not any(x in file_path for x in ['Module', 'Test_Solutions']):
            categorized_files['main_sessions'].append(file_data)
        else:
            categorized_files['other_files'].append(file_data)
        
        # Analyze chapter structure
        headers = file_data['headers']
        structure = [{'level': h['level'], 'text': h['text']} for h in headers]
        chapter_structures[file_path] = structure
        
        # Count emoji usage
        for header in headers:
            text = header['text']
            if '🧭' in text:
                emoji_usage['🧭'] += 1
                navigation_consistency['🧭'].append(file_path)
            elif '📝' in text and 'Navigation' in text:
                emoji_usage['📝_nav'] += 1
                navigation_consistency['📝_nav'].append(file_path)
            elif '🔗' in text and 'Navigation' in text:
                emoji_usage['🔗_nav'] += 1
                navigation_consistency['🔗_nav'].append(file_path)
    
    # Analyze link patterns
    broken_links_by_type = defaultdict(list)
    for broken_link in data['broken_links']:
        if '*.md' in broken_link['target_file']:
            broken_links_by_type['wildcard_patterns'].append(broken_link)
        elif 'Test_Solutions.md' in broken_link['target_file']:
            broken_links_by_type['solution_links'].append(broken_link)
        else:
            broken_links_by_type['other'].append(broken_link)
    
    # Calculate structure quality metrics
    quality_metrics = {
        'total_files': len(data['files']),
        'navigation_standardization': {
            'standard_navigation': len(navigation_consistency['🧭']),
            'non_standard_navigation': len(navigation_consistency['📝_nav']) + len(navigation_consistency['🔗_nav']),
            'standardization_rate': len(navigation_consistency['🧭']) / max(1, len(navigation_consistency['🧭']) + len(navigation_consistency['📝_nav']) + len(navigation_consistency['🔗_nav']))
        },
        'link_quality': {
            'total_broken_links': len(data['broken_links']),
            'wildcard_issues': len(broken_links_by_type['wildcard_patterns']),
            'solution_link_issues': len(broken_links_by_type['solution_links'])
        },
        'content_organization': {
            'files_with_tests': len([f for f in data['files'] if f['structure_summary']['has_test']]),
            'files_with_discussion': len([f for f in data['files'] if f['structure_summary']['has_discussion']]),
            'files_with_proper_navigation': len([f for f in data['files'] if f['structure_summary']['has_navigation']])
        }
    }
    
    # Generate recommendations
    recommendations = []
    
    if quality_metrics['navigation_standardization']['standardization_rate'] < 0.95:
        recommendations.append({
            'priority': 'high',
            'issue': 'Navigation emoji inconsistency',
            'description': f"Only {quality_metrics['navigation_standardization']['standardization_rate']:.1%} of navigation sections use the standard 🧭 emoji",
            'action': 'Standardize all navigation sections to use 🧭 emoji'
        })
    
    if quality_metrics['link_quality']['wildcard_issues'] > 50:
        recommendations.append({
            'priority': 'medium',
            'issue': 'High number of wildcard link patterns',
            'description': f"{quality_metrics['link_quality']['wildcard_issues']} broken wildcard patterns found",
            'action': 'Replace Session*.md patterns with specific file names'
        })
    
    if quality_metrics['link_quality']['solution_link_issues'] > 20:
        recommendations.append({
            'priority': 'high',
            'issue': 'Broken solution links',
            'description': f"{quality_metrics['link_quality']['solution_link_issues']} solution links pointing to non-existent files",
            'action': 'Verify all solution files exist and are properly named'
        })
    
    # Create final analysis structure
    final_analysis = {
        'metadata': {
            'analysis_date': '2024-12-19',
            'total_files_analyzed': len(data['files']),
            'analysis_version': '2.0'
        },
        'file_categorization': {
            'main_sessions': len(categorized_files['main_sessions']),
            'module_files': len(categorized_files['module_files']),
            'solution_files': len(categorized_files['solution_files']),
            'index_files': len(categorized_files['index_files']),
            'other_files': len(categorized_files['other_files'])
        },
        'structure_quality': quality_metrics,
        'emoji_standardization': {
            'usage_counts': dict(emoji_usage),
            'navigation_consistency': {k: len(v) for k, v in navigation_consistency.items()}
        },
        'link_analysis': {
            'total_broken_links': len(data['broken_links']),
            'broken_by_type': {k: len(v) for k, v in broken_links_by_type.items()},
            'sample_broken_links': data['broken_links'][:10]
        },
        'recommendations': recommendations,
        'detailed_files': categorized_files,
        'chapter_structures': dict(chapter_structures)
    }
    
    return final_analysis

def main():
    analysis = generate_final_analysis()
    
    # Save final analysis
    output_file = '/Users/q284340/Agentic/nano-degree/final_course_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print("📋 Final Course Structure Analysis")
    print("=" * 50)
    print(f"📁 Total files: {analysis['metadata']['total_files_analyzed']}")
    print(f"📖 Main sessions: {analysis['file_categorization']['main_sessions']}")
    print(f"📚 Module files: {analysis['file_categorization']['module_files']}")
    print(f"✅ Solution files: {analysis['file_categorization']['solution_files']}")
    print(f"🏠 Index files: {analysis['file_categorization']['index_files']}")
    
    print(f"\n🧭 Navigation Standardization:")
    print(f"   Standard (🧭): {analysis['emoji_standardization']['navigation_consistency'].get('🧭', 0)}")
    print(f"   Non-standard: {analysis['emoji_standardization']['navigation_consistency'].get('📝_nav', 0) + analysis['emoji_standardization']['navigation_consistency'].get('🔗_nav', 0)}")
    print(f"   Rate: {analysis['structure_quality']['navigation_standardization']['standardization_rate']:.1%}")
    
    print(f"\n🔗 Link Quality:")
    print(f"   Total broken: {analysis['link_analysis']['total_broken_links']}")
    print(f"   Wildcard issues: {analysis['link_analysis']['broken_by_type'].get('wildcard_patterns', 0)}")
    print(f"   Solution issues: {analysis['link_analysis']['broken_by_type'].get('solution_links', 0)}")
    
    print(f"\n📈 Content Organization:")
    print(f"   Files with tests: {analysis['structure_quality']['content_organization']['files_with_tests']}")
    print(f"   Files with discussion: {analysis['structure_quality']['content_organization']['files_with_discussion']}")
    print(f"   Files with navigation: {analysis['structure_quality']['content_organization']['files_with_proper_navigation']}")
    
    print(f"\n🎯 Recommendations ({len(analysis['recommendations'])}):")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"   {i}. [{rec['priority'].upper()}] {rec['issue']}")
        print(f"      → {rec['action']}")
    
    print(f"\n💾 Complete analysis saved to: {output_file}")

if __name__ == "__main__":
    main()