#!/usr/bin/env python3
"""
Fix Test_Solutions.md files by removing Answer Summary sections and other clutter.
Ensure proper structure: Test Questions → Navigation (no clutter in between).
"""

import os
import re
import glob

def clean_solution_file(file_path):
    """Clean a test solutions file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading: {e}"
    
    original_content = content
    
    # Remove Answer Summary sections and similar clutter
    clutter_patterns = [
        r'## Answer Summary.*?\n(?=##|\[View Solutions|\n---)',
        r'## Key Concepts Summary.*?\n(?=##|\[View Solutions|\n---)',
        r'## Summary.*?\n(?=##|\[View Solutions|\n---)',
        
        # Remove standalone answer lines like "1. B  2. D  3. A..."
        r'\n\d+\.\s+[A-D]\s+\d+\.\s+[A-D].*?\n',
        
        # Remove duplicate solution links
        r'\[View Solutions →\]\([^)]*Test_Solutions\.md\).*?\n(?=\[View Solutions)',
        
        # Clean up excessive dividers and whitespace
        r'\n---\n\n+\[View Solutions',
        r'\n{3,}',
    ]
    
    for pattern in clutter_patterns:
        if pattern == r'\n{3,}':
            content = re.sub(pattern, '\n\n', content)
        elif pattern == r'\n---\n\n+\[View Solutions':
            content = re.sub(pattern, '\n\n[View Solutions', content)
        else:
            content = re.sub(pattern, '\n', content, flags=re.DOTALL)
    
    # Ensure proper structure before Navigation
    # Remove anything between the last question explanation and Navigation
    nav_match = re.search(r'## 🧭 Navigation', content)
    if nav_match:
        nav_start = nav_match.start()
        before_nav = content[:nav_start]
        nav_section = content[nav_start:]
        
        # Find the last question explanation
        explanation_matches = list(re.finditer(r'\*\*Explanation:\*\*[^\n]*\n', before_nav))
        if explanation_matches:
            last_explanation_end = explanation_matches[-1].end()
            clean_before_nav = before_nav[:last_explanation_end]
            content = clean_before_nav + '\n---\n\n' + nav_section
    
    # Clean up the final structure
    content = re.sub(r'\n+---\n+## 🧭 Navigation', '\n\n---\n\n## 🧭 Navigation', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Cleaned successfully"
        except Exception as e:
            return False, f"Write error: {e}"
    
    return False, "No changes needed"

def main():
    """Main function to clean all solution files."""
    print("=== Cleaning Test Solution Files ===\n")
    
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    solution_files = [f for f in solution_files if 'BACKUP' not in f and 'ORIGINAL' not in f]
    
    print(f"Processing {len(solution_files)} solution files...")
    
    cleaned_count = 0
    
    for file_path in solution_files:
        cleaned, message = clean_solution_file(file_path)
        if cleaned:
            cleaned_count += 1
            print(f"✅ Cleaned {os.path.basename(file_path)}")
    
    print(f"\n✅ Cleaned {cleaned_count} solution files")
    print("All solution files now have clean structure: Test Questions → Navigation")

if __name__ == "__main__":
    main()