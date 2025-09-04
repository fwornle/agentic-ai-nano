#!/usr/bin/env python3
"""Extract specific issue details from the analysis."""

import json

def main():
    with open('/Users/q284340/Agentic/nano-degree/course_structure_analysis.json', 'r') as f:
        data = json.load(f)
    
    print("🔄 Files with duplicate navigation:")
    for file_data in data['files']:
        for issue in file_data.get('issues', []):
            if issue['type'] == 'duplicate_navigation':
                print(f"\n📁 {file_data['file_path']}")
                print(f"   Found {issue['count']} navigation sections:")
                for section in issue['sections']:
                    print(f"   - Line {section['line']}: {section['text']}")
    
    print("\n🎭 Files with emoji inconsistencies:")
    for file_data in data['files']:
        for issue in file_data.get('issues', []):
            if issue['type'] == 'inconsistent_navigation_emojis':
                print(f"\n📁 {file_data['file_path']}")
                print(f"   Mixed emojis: {issue['emojis']}")
    
    print(f"\n🔗 Sample broken links (showing first 20 of {len(data['broken_links'])}):")
    for i, broken_link in enumerate(data['broken_links'][:20]):
        print(f"{i+1:2d}. {broken_link['source_file']} → {broken_link['target_file']}")
        print(f"    Link text: '{broken_link['link_text']}'")

if __name__ == "__main__":
    main()