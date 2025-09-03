#!/usr/bin/env python3
"""
Standardize ALL test solution links across the entire degree.
- Remove any heading-style solution links
- Use consistent text: [View Solutions →]
- Make all links inline, not headings
"""

import os
import re
import glob

def standardize_solution_links():
    """Standardize all test solution links to consistent inline format."""
    
    # Find all markdown files
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove heading-style solution links
            heading_patterns = [
                r'## 📝 View Test Solutions\s*\n\s*\[.*?\]\(.*?Test_Solutions\.md\)',
                r'## 🔗 Test Solutions\s*\n\s*\[.*?\]\(.*?Test_Solutions\.md\)',
                r'## Test Solutions\s*\n\s*\[.*?\]\(.*?Test_Solutions\.md\)',
                r'### View Solutions\s*\n\s*\[.*?\]\(.*?Test_Solutions\.md\)',
                r'### 📝 Solutions\s*\n\s*\[.*?\]\(.*?Test_Solutions\.md\)'
            ]
            
            for pattern in heading_patterns:
                content = re.sub(pattern, lambda m: extract_link_from_heading(m.group(0)), content, flags=re.DOTALL)
            
            # Standardize all existing solution link texts to consistent format
            # Find all variations of solution links
            solution_link_patterns = [
                (r'\[View Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[View Test Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[📝 View Test Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[🗂️ View Test Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[📝 View Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[\*\*📝 .*? Test Solutions →\*\*\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[Test Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[Check Solutions →\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)'),
                (r'\[Check your answers.*?\]\((.*?Test_Solutions\.md)\)', r'[View Solutions →](\1)')
            ]
            
            for pattern, replacement in solution_link_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Clean up any remaining heading-style solution sections
            content = re.sub(r'## 📝 View Test Solutions\s*→?\s*\n', '', content)
            content = re.sub(r'### 📝 Solutions\s*\n', '', content)
            
            # Clean up multiple line breaks
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Standardized {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def extract_link_from_heading(heading_text):
    """Extract the link from a heading-style solution section and return as inline link."""
    # Find the link in the heading section
    link_match = re.search(r'\[.*?\]\((.*?Test_Solutions\.md)\)', heading_text)
    if link_match:
        filename = link_match.group(1)
        return f'[View Solutions →]({filename})'
    return ''

def main():
    """Main function to standardize all solution links."""
    print("=== Standardizing ALL Test Solution Links ===\n")
    
    fixed_count = standardize_solution_links()
    
    print(f"\n✅ Standardized solution links in {fixed_count} files")
    print("All test solution links now use consistent format: [View Solutions →]")

if __name__ == "__main__":
    main()