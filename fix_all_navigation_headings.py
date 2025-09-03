#!/usr/bin/env python3
"""
Fix ALL navigation heading-style links across the entire degree.
Convert "## 🧭 Navigation" sections to clean inline navigation.
"""

import os
import re
import glob

def fix_navigation_headings():
    """Remove all heading-style navigation sections and replace with clean inline links."""
    
    # Find all markdown files across entire degree
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern to match navigation heading sections
            # Matches: ## 🧭 Navigation ... Next: [link] ... ---
            nav_pattern = r'## 🧭 Navigation\s*\n\s*(.*?)(?=##|\Z)'
            
            matches = re.finditer(nav_pattern, content, re.DOTALL)
            
            for match in matches:
                nav_section = match.group(0)
                nav_content = match.group(1).strip()
                
                # Extract just the "Next:" link if it exists
                next_link_match = re.search(r'\*\*Next:\*\*\s*(\[.*?\]\(.*?\))', nav_content)
                if next_link_match:
                    next_link = next_link_match.group(1)
                    # Replace the entire navigation section with clean inline link
                    clean_nav = f'\n\n---\n\n**Next:** {next_link}\n\n---\n'
                    content = content.replace(nav_section, clean_nav)
                else:
                    # If no clear next link, just remove the heading but keep content
                    clean_content = re.sub(r'## 🧭 Navigation\s*\n\s*', '\n\n---\n\n', nav_section)
                    content = content.replace(nav_section, clean_content)
            
            # Clean up multiple consecutive separators
            content = re.sub(r'---\s*\n\s*---', '---', content)
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Fixed navigation in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def main():
    """Main function to fix all navigation headings."""
    print("=== Fixing ALL Navigation Headings Across Entire Degree ===\n")
    
    fixed_count = fix_navigation_headings()
    
    print(f"\n✅ Fixed navigation headings in {fixed_count} files")
    print("All navigation is now clean inline format without heading clutter!")

if __name__ == "__main__":
    main()