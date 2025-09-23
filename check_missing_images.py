#!/usr/bin/env python3
"""
Find missing images referenced in markdown files
"""
import os
import re
import json
from pathlib import Path

def find_missing_images():
    """Find all missing image references in markdown files"""
    base_path = "/Users/q284340/Agentic/nano-degree"
    missing_images = []
    
    # Find all markdown files
    for root, dirs, files in os.walk(base_path):
        if any(skip in root for skip in ['.git', 'node_modules', '__pycache__']):
            continue
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                except Exception as e:
                    continue
                
                # Find image references
                for line_num, line in enumerate(lines, 1):
                    # Skip code blocks
                    if line.strip().startswith('```'):
                        continue
                    
                    # Find image patterns
                    img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+\.(png|jpg|jpeg|svg|webp))\)', re.IGNORECASE)
                    
                    for match in img_pattern.finditer(line):
                        alt_text = match.group(1)
                        img_url = match.group(2)
                        
                        # Skip external URLs
                        if img_url.startswith(('http://', 'https://')):
                            continue
                        
                        # Check if image exists
                        possible_paths = [
                            os.path.join(os.path.dirname(file_path), img_url),
                            os.path.join(base_path, img_url),
                            os.path.join(base_path, 'docs-content', img_url),
                            os.path.join(base_path, 'docs-content', 'corporate-only', img_url)
                        ]
                        
                        image_exists = False
                        for possible_path in possible_paths:
                            if os.path.exists(os.path.normpath(possible_path)):
                                image_exists = True
                                break
                        
                        if not image_exists:
                            missing_images.append({
                                'file': rel_path,
                                'line': line_num,
                                'line_content': line.strip(),
                                'alt_text': alt_text,
                                'image_url': img_url,
                                'tried_paths': [os.path.normpath(p) for p in possible_paths]
                            })
    
    return missing_images

def main():
    print("🔍 Finding missing images...")
    missing = find_missing_images()
    
    print(f"\n📊 Results:")
    print(f"Missing images: {len(missing)}")
    
    if missing:
        print(f"\n❌ Missing Images:")
        for i, img in enumerate(missing[:10], 1):  # Show first 10
            print(f"{i}. {img['file']}:{img['line']}")
            print(f"   Alt: '{img['alt_text']}'")
            print(f"   Image: '{img['image_url']}'")
            print(f"   Line: {img['line_content'][:80]}...")
            print()
    
    # Save detailed report
    with open('missing_images_report.json', 'w') as f:
        json.dump(missing, f, indent=2)
    
    print(f"✅ Detailed report saved to: missing_images_report.json")

if __name__ == "__main__":
    main()