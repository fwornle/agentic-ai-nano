#!/usr/bin/env python3
"""
Fix the analysis bug - the script excludes solution files but then flags links to them as broken
"""

import json
import os
from pathlib import Path

def get_all_existing_files():
    """Get all actual existing files in the docs-content directory"""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    existing_files = []
    
    for md_file in base_dir.rglob('*.md'):
        relative_path = str(md_file.relative_to(base_dir))
        existing_files.append(relative_path)
    
    return set(existing_files)

def fix_broken_links_analysis():
    """Re-analyze broken links against actual file system"""
    with open('course_structure_analysis.json', 'r') as f:
        data = json.load(f)
    
    existing_files = get_all_existing_files()
    print(f"Found {len(existing_files)} existing files")
    
    broken_links = data.get('broken_links', [])
    actually_broken = []
    
    for link in broken_links:
        source_file = link['source_file']
        target_file = link['target_file']
        
        # Handle different path scenarios
        target_exists = False
        
        # Direct match
        if target_file in existing_files:
            target_exists = True
        
        # Same directory
        source_dir = os.path.dirname(source_file)
        if source_dir:
            full_target = os.path.join(source_dir, target_file).replace('\\', '/')
            if full_target in existing_files:
                target_exists = True
        
        # Check if it's a relative path like ../index.md
        if target_file.startswith('../'):
            # Resolve relative path
            source_dir = os.path.dirname(source_file)
            resolved_path = os.path.normpath(os.path.join(source_dir, target_file)).replace('\\', '/')
            if resolved_path in existing_files:
                target_exists = True
        
        if not target_exists:
            actually_broken.append(link)
    
    print(f"Original broken links: {len(broken_links)}")
    print(f"Actually broken links: {len(actually_broken)}")
    print(f"False positives: {len(broken_links) - len(actually_broken)}")
    
    # Show samples of actually broken links
    print("\nActually broken links (first 10):")
    for link in actually_broken[:10]:
        print(f"  {link['source_file']} -> {link['target_file']} ('{link['link_text']}')")
    
    # Update the analysis data
    data['broken_links'] = actually_broken
    data['analysis_summary']['total_broken_links'] = len(actually_broken)
    
    with open('course_structure_analysis.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    return len(actually_broken)

if __name__ == "__main__":
    actually_broken_count = fix_broken_links_analysis()
    print(f"\n✅ Fixed analysis! Actual broken links: {actually_broken_count}")