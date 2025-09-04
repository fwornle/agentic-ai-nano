#!/usr/bin/env python3
"""
Comprehensive Course Structure Analyzer
Analyzes all markdown files to detect:
- Chapter structure and hierarchy
- Navigation inconsistencies  
- Link integrity
- Duplicate sections
- Emoji usage patterns
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse
import sys

def extract_headers(content):
    """Extract all headers with their line numbers and levels."""
    headers = []
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            headers.append({
                'line': i,
                'level': level,
                'text': text,
                'raw': line.strip()
            })
    return headers

def extract_links(content):
    """Extract all markdown links."""
    # Pattern for markdown links [text](url)
    link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    links = []
    for match in re.finditer(link_pattern, content):
        text = match.group(1)
        url = match.group(2)
        links.append({
            'text': text,
            'url': url,
            'full_match': match.group(0)
        })
    return links

def categorize_link(url):
    """Categorize link type."""
    if url.startswith('http'):
        return 'external'
    elif url.startswith('#'):
        return 'anchor'
    elif url.endswith('.md'):
        return 'internal_file'
    elif '/' in url:
        return 'path'
    else:
        return 'other'

def extract_emojis(text):
    """Extract emojis from text."""
    # Simple emoji pattern - can be expanded
    emoji_pattern = r'[🎯📝⚙️🧭📋🏠⬅️➡️🔄🚀💡⭐🎨🔧📊🌟🎭🎪🎨🔮🎬🎰🎲🎸🎺🎻🥁🎤🎧🎵🎶🎼🎹]'
    return re.findall(emoji_pattern, text)

def analyze_file(file_path):
    """Analyze a single markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    relative_path = str(file_path).replace('/Users/q284340/Agentic/nano-degree/docs-content/', '')
    
    headers = extract_headers(content)
    links = extract_links(content)
    
    # Analyze structure
    navigation_sections = [h for h in headers if 'navigation' in h['text'].lower()]
    test_sections = [h for h in headers if any(term in h['text'].lower() for term in ['test', 'quiz', 'assessment'])]
    discussion_sections = [h for h in headers if 'discussion' in h['text'].lower()]
    
    # Analyze emojis in headers
    emoji_usage = {}
    for header in headers:
        emojis = extract_emojis(header['text'])
        if emojis:
            emoji_usage[header['text']] = emojis
    
    # Categorize links
    link_categories = defaultdict(list)
    for link in links:
        category = categorize_link(link['url'])
        link_categories[category].append(link)
    
    # Check for potential issues
    issues = []
    
    # Multiple navigation sections
    if len(navigation_sections) > 1:
        issues.append({
            'type': 'duplicate_navigation',
            'count': len(navigation_sections),
            'sections': [{'line': n['line'], 'text': n['text']} for n in navigation_sections]
        })
    
    # Inconsistent navigation emojis
    nav_emojis = []
    for nav in navigation_sections:
        emojis = extract_emojis(nav['text'])
        nav_emojis.extend(emojis)
    
    if len(set(nav_emojis)) > 1:
        issues.append({
            'type': 'inconsistent_navigation_emojis',
            'emojis': list(set(nav_emojis))
        })
    
    # Test without solution link
    has_test = len(test_sections) > 0
    has_solution_link = any('solution' in link['text'].lower() for link in links)
    
    if has_test and not has_solution_link:
        issues.append({
            'type': 'test_without_solution_link'
        })
    
    return {
        'file_path': relative_path,
        'headers': headers,
        'header_count': len(headers),
        'links': links,
        'link_count': len(links),
        'link_categories': dict(link_categories),
        'navigation_sections': navigation_sections,
        'test_sections': test_sections,
        'discussion_sections': discussion_sections,
        'emoji_usage': emoji_usage,
        'issues': issues,
        'structure_summary': {
            'has_navigation': len(navigation_sections) > 0,
            'has_test': has_test,
            'has_discussion': len(discussion_sections) > 0,
            'navigation_count': len(navigation_sections)
        }
    }

def analyze_course():
    """Analyze entire course structure."""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    
    all_files = []
    global_stats = {
        'total_files': 0,
        'files_with_issues': 0,
        'total_issues': 0,
        'issue_types': Counter(),
        'emoji_usage': Counter(),
        'navigation_patterns': Counter()
    }
    
    # Find all markdown files
    for md_file in base_dir.rglob('*.md'):
        if 'Test_Solutions' not in str(md_file):  # Analyze solution files separately
            result = analyze_file(md_file)
            if 'error' not in result:
                all_files.append(result)
                
                # Update global stats
                global_stats['total_files'] += 1
                
                if result['issues']:
                    global_stats['files_with_issues'] += 1
                    global_stats['total_issues'] += len(result['issues'])
                    
                    for issue in result['issues']:
                        global_stats['issue_types'][issue['type']] += 1
                
                # Track emoji usage
                for header_text, emojis in result['emoji_usage'].items():
                    for emoji in emojis:
                        global_stats['emoji_usage'][emoji] += 1
                
                # Track navigation patterns
                for nav in result['navigation_sections']:
                    global_stats['navigation_patterns'][nav['text']] += 1
    
    # Analyze cross-file links
    all_internal_links = []
    for file_data in all_files:
        for link in file_data['link_categories'].get('internal_file', []):
            all_internal_links.append({
                'source_file': file_data['file_path'],
                'target_file': link['url'],
                'link_text': link['text']
            })
    
    # Find broken internal links
    existing_files = set(f['file_path'] for f in all_files)
    existing_files.add('Session0_Test_Solutions.md')  # Add common solution files
    
    broken_links = []
    for link in all_internal_links:
        target_path = link['target_file']
        
        # Handle relative paths
        source_dir = os.path.dirname(link['source_file'])
        if source_dir:
            full_target = os.path.join(source_dir, target_path).replace('\\', '/')
        else:
            full_target = target_path
        
        # Check if target exists
        target_exists = any(
            f['file_path'] == full_target or 
            f['file_path'].endswith('/' + target_path) or
            f['file_path'] == target_path
            for f in all_files
        )
        
        if not target_exists:
            broken_links.append(link)
    
    return {
        'files': all_files,
        'global_stats': global_stats,
        'broken_links': broken_links,
        'analysis_summary': {
            'total_files_analyzed': len(all_files),
            'files_with_duplicate_navigation': len([f for f in all_files if any(i['type'] == 'duplicate_navigation' for i in f['issues'])]),
            'files_with_emoji_issues': len([f for f in all_files if any(i['type'] == 'inconsistent_navigation_emojis' for i in f['issues'])]),
            'total_broken_links': len(broken_links)
        }
    }

def main():
    print("🔍 Analyzing course structure...")
    
    analysis = analyze_course()
    
    # Save to JSON
    output_file = '/Users/q284340/Agentic/nano-degree/course_structure_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Analysis complete! Results saved to {output_file}")
    print(f"📁 Total files analyzed: {analysis['analysis_summary']['total_files_analyzed']}")
    print(f"🔄 Files with duplicate navigation: {analysis['analysis_summary']['files_with_duplicate_navigation']}")
    print(f"🎭 Files with emoji issues: {analysis['analysis_summary']['files_with_emoji_issues']}")
    print(f"🔗 Broken internal links found: {analysis['analysis_summary']['total_broken_links']}")
    
    # Print most common issues
    print("\n🚨 Most common issues:")
    for issue_type, count in analysis['global_stats']['issue_types'].most_common(5):
        print(f"  - {issue_type}: {count}")
    
    # Print navigation patterns
    print("\n🧭 Navigation patterns:")
    for pattern, count in analysis['global_stats']['navigation_patterns'].most_common(10):
        print(f"  - '{pattern}': {count}")

if __name__ == "__main__":
    main()