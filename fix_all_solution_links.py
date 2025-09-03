#!/usr/bin/env python3
"""
Fix ALL test solution link variations across the entire degree.
Standardize to consistent format: [View Solutions →]
"""

import os
import re
import glob

def fix_all_solution_links():
    """Fix all variations of solution links to standard format."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Comprehensive list of all solution link variations to standardize
            variations = [
                # Bold variations with icons
                r'\[\*\*🗂️ View Test Solutions →\*\*\]\(([^)]*Test_Solutions\.md)\)',
                r'\[\*\*🗂️ View Complete Test & Solutions →\*\*\]\(([^)]*Test_Solutions\.md)\)',
                r'\[\*\*📝 View Test Solutions →\*\*\]\(([^)]*Test_Solutions\.md)\)',
                r'\[\*\*View Test Solutions →\*\*\]\(([^)]*Test_Solutions\.md)\)',
                r'\[\*\*Test Solutions →\*\*\]\(([^)]*Test_Solutions\.md)\)',
                
                # Icon variations
                r'\[🗂️ View Test Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[📝 View Test Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[📝 View Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                
                # Text variations
                r'\[View Test Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[Check Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[Test Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[Solutions →\]\(([^)]*Test_Solutions\.md)\)',
                r'\[Click here for solutions\]\(([^)]*Test_Solutions\.md)\)',
                r'\[Check your answers.*?\]\(([^)]*Test_Solutions\.md)\)',
                
                # Already correct format (to ensure consistency)
                r'\[View Solutions →\]\(([^)]*Test_Solutions\.md)\)'
            ]
            
            # Replace all variations with standard format
            for pattern in variations:
                content = re.sub(pattern, r'[View Solutions →](\1)', content)
            
            # Handle special cases like links in list items or other contexts
            content = re.sub(r'- \*\*\[📝 Comprehensive Assessment\]\(([^)]*Test_Solutions\.md)\)\*\* - .*', 
                           r'[View Solutions →](\1)', content)
            
            # Remove any remaining heading-style solution sections
            content = re.sub(r'##+ .*?Solutions?.*?\n', '', content)
            
            # Clean up commented-out solution links
            content = re.sub(r'#\[View Solutions →\]\(([^)]*Test_Solutions\.md)\)', r'[View Solutions →](\1)', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Standardized {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def main():
    """Main function."""
    print("=== Fixing ALL Solution Link Variations ===\n")
    
    fixed_count = fix_all_solution_links()
    
    print(f"\n✅ Standardized solution links in {fixed_count} files")
    print("All solution links now use consistent format: [View Solutions →]")

if __name__ == "__main__":
    main()