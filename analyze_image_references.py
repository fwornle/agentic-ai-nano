#!/usr/bin/env python3
"""
Comprehensive analysis of image references in the nano-degree course structure
Identifies broken links, unused images, and structural issues
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

def find_all_image_files(base_path):
    """Find all image files in the project"""
    image_files = []
    image_extensions = {'.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp'}
    
    for root, dirs, files in os.walk(base_path):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'docs-env']):
            continue
            
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)
                image_files.append({
                    'filename': file,
                    'full_path': full_path,
                    'relative_path': rel_path,
                    'directory': os.path.dirname(rel_path)
                })
    
    return image_files

def find_image_references_in_markdown(base_path):
    """Find all image references in markdown files"""
    references = []
    markdown_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+\.(png|svg|jpg|jpeg|gif|webp))\)', re.IGNORECASE)
    src_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+\.(png|svg|jpg|jpeg|gif|webp))["\']', re.IGNORECASE)
    
    for root, dirs, files in os.walk(base_path):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'docs-env']):
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, base_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # Find markdown image references
                        for i, line in enumerate(lines, 1):
                            for match in markdown_pattern.finditer(line):
                                alt_text = match.group(1)
                                image_path = match.group(2)
                                references.append({
                                    'type': 'markdown',
                                    'file': rel_file_path,
                                    'line': i,
                                    'alt_text': alt_text,
                                    'image_path': image_path,
                                    'full_line': line.strip()
                                })
                            
                            # Find HTML img tag references
                            for match in src_pattern.finditer(line):
                                image_path = match.group(1)
                                references.append({
                                    'type': 'html',
                                    'file': rel_file_path,
                                    'line': i,
                                    'alt_text': '',
                                    'image_path': image_path,
                                    'full_line': line.strip()
                                })
                                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return references

def analyze_session2_structure(base_path):
    """Analyze Session 2 document structure and relationships"""
    session2_files = []
    frameworks_path = os.path.join(base_path, 'docs-content', '01_frameworks')
    
    if not os.path.exists(frameworks_path):
        return {"error": "Frameworks directory not found"}
    
    for file in os.listdir(frameworks_path):
        if file.startswith('Session2') and file.endswith('.md'):
            file_path = os.path.join(frameworks_path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract learning path indicators
                    learning_paths = []
                    if '🎯' in content or 'Observer' in content:
                        learning_paths.append('Observer')
                    if '📝' in content or 'Participant' in content:
                        learning_paths.append('Participant')
                    if '⚙️' in content or 'Implementer' in content:
                        learning_paths.append('Implementer')
                    
                    # Find prerequisites references
                    prereq_pattern = re.compile(r'Prerequisites?[^\n]*?\[([^\]]+)\]\(([^)]+)\)', re.IGNORECASE)
                    prerequisites = []
                    for match in prereq_pattern.finditer(content):
                        prerequisites.append({
                            'text': match.group(1),
                            'file': match.group(2)
                        })
                    
                    # Get file size and creation info
                    stat = os.stat(file_path)
                    
                    session2_files.append({
                        'filename': file,
                        'size': stat.st_size,
                        'learning_paths': learning_paths,
                        'prerequisites': prerequisites,
                        'has_implementer_marker': '⚙️ IMPLEMENTER PATH CONTENT' in content,
                        'word_count': len(content.split()),
                        'line_count': len(content.split('\n'))
                    })
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
    
    return session2_files

def find_navigation_links(base_path):
    """Find all navigation links between documents"""
    links = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)', re.IGNORECASE)
    
    for root, dirs, files in os.walk(base_path):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'docs-env']):
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, base_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for match in link_pattern.finditer(content):
                            link_text = match.group(1)
                            target_file = match.group(2)
                            links.append({
                                'source_file': rel_file_path,
                                'link_text': link_text,
                                'target_file': target_file
                            })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return links

def main():
    base_path = "/Users/q284340/Agentic/nano-degree"
    
    print("🔍 Analyzing nano-degree course structure...")
    print("=" * 60)
    
    # Find all actual image files
    print("Finding all image files...")
    image_files = find_all_image_files(base_path)
    
    # Find all image references
    print("Finding all image references...")
    image_references = find_image_references_in_markdown(base_path)
    
    # Analyze Session 2 structure
    print("Analyzing Session 2 structure...")
    session2_analysis = analyze_session2_structure(base_path)
    
    # Find navigation links
    print("Finding navigation links...")
    navigation_links = find_navigation_links(base_path)
    
    # Analysis: Check for broken image references
    print("\n🔍 BROKEN IMAGE REFERENCE ANALYSIS")
    print("=" * 50)
    
    broken_references = []
    existing_images = {img['relative_path'] for img in image_files}
    
    for ref in image_references:
        # Normalize path separators and check various possible paths
        image_path = ref['image_path'].replace('\\', '/')
        
        # Try different path combinations
        possible_paths = [
            image_path,  # As specified
            image_path.lstrip('./'),  # Remove leading ./
            f"docs-content/{image_path}" if not image_path.startswith('docs-content') else image_path,
        ]
        
        found = False
        for possible_path in possible_paths:
            if possible_path in existing_images:
                found = True
                break
        
        if not found:
            # Look for similar named files
            image_name = os.path.basename(image_path)
            similar_files = [img for img in image_files if img['filename'] == image_name]
            
            broken_references.append({
                'reference': ref,
                'possible_paths_tried': possible_paths,
                'similar_named_files': similar_files
            })
    
    # Analysis: Find unused images
    print("\n📁 UNUSED IMAGE ANALYSIS")
    print("=" * 50)
    
    referenced_images = set()
    for ref in image_references:
        image_path = ref['image_path'].replace('\\', '/')
        # Try to match with actual files
        for img in image_files:
            if img['relative_path'].endswith(os.path.basename(image_path)):
                referenced_images.add(img['relative_path'])
    
    unused_images = []
    for img in image_files:
        if img['relative_path'] not in referenced_images:
            # Additional check: see if the filename appears in any reference
            filename_referenced = any(
                os.path.basename(ref['image_path']) == img['filename']
                for ref in image_references
            )
            if not filename_referenced:
                unused_images.append(img)
    
    # Create comprehensive report
    report = {
        'summary': {
            'total_image_files': len(image_files),
            'total_image_references': len(image_references),
            'broken_references': len(broken_references),
            'unused_images': len(unused_images)
        },
        'image_files_by_directory': {},
        'broken_references': broken_references,
        'unused_images': unused_images,
        'session2_analysis': session2_analysis,
        'navigation_links': navigation_links
    }
    
    # Group images by directory
    for img in image_files:
        directory = img['directory']
        if directory not in report['image_files_by_directory']:
            report['image_files_by_directory'][directory] = []
        report['image_files_by_directory'][directory].append(img['filename'])
    
    # Print summary
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print(f"Total image files found: {len(image_files)}")
    print(f"Total image references: {len(image_references)}")
    print(f"Broken references: {len(broken_references)}")
    print(f"Unused images: {len(unused_images)}")
    
    print(f"\n📁 IMAGE FILES BY MODULE:")
    for directory, files in sorted(report['image_files_by_directory'].items()):
        if 'docs-content' in directory:
            print(f"  {directory}: {len(files)} files")
    
    print(f"\n📄 SESSION 2 STRUCTURE:")
    if isinstance(session2_analysis, list):
        for doc in session2_analysis:
            paths = "/".join(doc['learning_paths']) if doc['learning_paths'] else "None"
            print(f"  {doc['filename']}: {paths} ({doc['word_count']} words)")
    
    print(f"\n❌ BROKEN REFERENCES SAMPLE:")
    for i, broken in enumerate(broken_references[:5]):  # Show first 5
        ref = broken['reference']
        print(f"  {i+1}. {ref['file']}:{ref['line']} -> {ref['image_path']}")
        if broken['similar_named_files']:
            similar = broken['similar_named_files'][0]
            print(f"     Possible match: {similar['relative_path']}")
    
    if len(broken_references) > 5:
        print(f"     ... and {len(broken_references) - 5} more")
    
    # Save detailed report
    output_file = os.path.join(base_path, 'image_analysis_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {output_file}")

if __name__ == "__main__":
    main()