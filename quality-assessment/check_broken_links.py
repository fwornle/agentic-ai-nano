#!/usr/bin/env python3
"""
Comprehensive broken link checker for markdown files
Finds ALL broken links with exact line numbers and context
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse

def find_all_markdown_files():
    """Find all relevant markdown files"""
    base_path = "/Users/q284340/Agentic/nano-degree"
    md_files = []
    
    patterns = ["README.md", "docs/*.md", "docs-content/**/*.md"]
    
    for root, dirs, files in os.walk(base_path):
        # Skip unwanted directories
        if any(skip in root for skip in ['.git', 'node_modules', 'site', '.venv', '__pycache__']):
            continue
            
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                
                # Only include files matching our patterns
                if (rel_path == "README.md" or 
                    rel_path.startswith("docs/") or 
                    rel_path.startswith("docs-content/")):
                    md_files.append({
                        'full_path': full_path,
                        'relative_path': rel_path
                    })
    
    return md_files

def extract_links_from_markdown(file_path):
    """Extract all links from a markdown file with line numbers"""
    links = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return links
    
    # Patterns for different types of links (avoiding code snippets)
    patterns = [
        # Markdown links: [text](url) - but not inside code blocks
        re.compile(r'(?<!`)\[([^\]]*)\]\(([^)]+)\)(?!`)', re.IGNORECASE),
        # HTML img tags: <img src="url" - only actual HTML tags
        re.compile(r'<img\s[^>]*src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE),
        # HTML links: <a href="url" - only actual HTML tags  
        re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE),
        # Direct image references: ![alt](image) - but not inside code blocks
        re.compile(r'(?<!`)\!\[([^\]]*)\]\(([^)]+)\)(?!`)', re.IGNORECASE),
    ]
    
    # Track if we're inside a code block
    in_code_block = False
    code_block_lang = None
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        line_stripped = line.strip()
        
        # Check for code block markers
        if line_stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line_stripped[3:].strip()
            else:
                in_code_block = False
                code_block_lang = None
            continue
        
        # Skip lines inside code blocks or indented code (4+ spaces)
        if in_code_block or line.startswith('    '):
            continue
        
        # Skip lines that look like code (contain function calls, assignments)
        if any(pattern in line for pattern in ['def ', 'class ', ' = ', '()', '[]', 'import ', 'from ']):
            continue
        
        for pattern in patterns:
            for match in pattern.finditer(line):
                # Extract text and URL based on pattern type
                if '\\[' in pattern.pattern and not '\\!' in pattern.pattern:  # [text](url)
                    text = match.group(1)
                    url = match.group(2)
                elif '\\!\\[' in pattern.pattern:  # ![alt](image)
                    text = match.group(1)
                    url = match.group(2)
                else:  # HTML tags
                    url = match.group(1)
                    # Try to extract text from HTML tag
                    if 'href=' in original_line:
                        # Look for text between > and </a>
                        tag_end = original_line.find('>', match.end())
                        if tag_end != -1:
                            close_tag = original_line.find('</a>', tag_end)
                            if close_tag != -1:
                                text = original_line[tag_end+1:close_tag].strip()
                            else:
                                text = ""
                        else:
                            text = ""
                    else:
                        text = ""
                
                links.append({
                    'line_number': line_num,
                    'line_content': original_line.strip(),
                    'link_text': text,
                    'url': url,
                    'match_start': match.start(),
                    'match_end': match.end(),
                    'pattern_type': 'markdown' if '\\[' in pattern.pattern else 'html'
                })
    
    return links

def check_link_validity(url, base_path, current_file_path):
    """Check if a link is valid"""
    # Skip external URLs
    if url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'ftp://')):
        return True, "external"
    
    # Skip anchors
    if url.startswith('#'):
        return True, "anchor"
    
    # Skip data URLs
    if url.startswith('data:'):
        return True, "data"
    
    # Clean the URL
    clean_url = url.split('#')[0].split('?')[0]
    if not clean_url:
        return True, "anchor_only"
    
    # Resolve relative paths
    current_dir = os.path.dirname(current_file_path)
    
    # Try different possible paths
    possible_paths = [
        clean_url,  # As written
        os.path.join(current_dir, clean_url),  # Relative to current file
        os.path.join(base_path, clean_url),  # Relative to base
        os.path.join(base_path, 'docs-content', clean_url),  # In docs-content
    ]
    
    for possible_path in possible_paths:
        normalized_path = os.path.normpath(possible_path)
        if os.path.exists(normalized_path):
            return True, f"found_at_{normalized_path}"
    
    return False, f"tried_{possible_paths}"

def analyze_markdown_files():
    """Analyze all markdown files for broken links"""
    base_path = "/Users/q284340/Agentic/nano-degree"
    md_files = find_all_markdown_files()
    
    all_broken_links = []
    all_links = []
    
    print(f"Analyzing {len(md_files)} markdown files...")
    
    for file_info in md_files:
        file_path = file_info['full_path']
        rel_path = file_info['relative_path']
        
        print(f"Checking: {rel_path}")
        
        links = extract_links_from_markdown(file_path)
        
        for link in links:
            url = link['url']
            is_valid, check_info = check_link_validity(url, base_path, file_path)
            
            link_info = {
                'file_path': rel_path,
                'line_number': link['line_number'],
                'line_content': link['line_content'],
                'link_text': link['link_text'],
                'url': url,
                'is_valid': is_valid,
                'check_info': check_info,
                'pattern_type': link['pattern_type']
            }
            
            all_links.append(link_info)
            
            if not is_valid:
                all_broken_links.append(link_info)
    
    return all_links, all_broken_links

def main():
    print("🔍 Starting comprehensive broken link analysis...")
    print("=" * 60)
    
    all_links, broken_links = analyze_markdown_files()
    
    print(f"\n📊 Analysis Results:")
    print(f"Total links found: {len(all_links)}")
    print(f"Broken links: {len(broken_links)}")
    print(f"Success rate: {((len(all_links) - len(broken_links)) / len(all_links) * 100):.1f}%")
    
    # Group broken links by type
    broken_by_type = {}
    for broken in broken_links:
        url = broken['url']
        if url.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
            link_type = 'image'
        elif url.endswith('.md'):
            link_type = 'markdown'
        else:
            link_type = 'other'
        
        if link_type not in broken_by_type:
            broken_by_type[link_type] = []
        broken_by_type[link_type].append(broken)
    
    print(f"\n📋 Broken Links by Type:")
    for link_type, links in broken_by_type.items():
        print(f"  {link_type}: {len(links)}")
    
    # Save detailed report
    report = {
        'summary': {
            'total_links': len(all_links),
            'broken_links': len(broken_links),
            'success_rate': (len(all_links) - len(broken_links)) / len(all_links) * 100,
            'broken_by_type': {k: len(v) for k, v in broken_by_type.items()}
        },
        'broken_links': broken_links,
        'all_links': all_links[:100]  # Sample to avoid huge files
    }
    
    with open('/Users/q284340/Agentic/nano-degree/broken_links_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Detailed report saved to: broken_links_report.json")
    
    # Show first 10 broken links for immediate review
    if broken_links:
        print(f"\n❌ First 10 Broken Links:")
        for i, broken in enumerate(broken_links[:10], 1):
            print(f"{i}. {broken['file_path']}:{broken['line_number']}")
            print(f"   Text: '{broken['link_text']}'")
            print(f"   URL: '{broken['url']}'")
            print(f"   Context: {broken['line_content'][:80]}...")
            print()

if __name__ == "__main__":
    main()