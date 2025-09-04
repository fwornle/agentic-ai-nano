#!/usr/bin/env python3
"""
Fix "Complete Assessment" sections and standardize ALL test formatting.
Replace non-standard assessment sections with proper Multiple Choice Test format.
"""

import os
import re
import glob

def fix_assessment_sections():
    """Fix all assessment and test sections to standard format."""
    
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        # Skip backup files
        if 'BACKUP' in file_path or 'ORIGINAL' in file_path:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Get session number for proper formatting
            session_match = re.search(r'Session(\d+)', os.path.basename(file_path))
            session_num = session_match.group(1) if session_match else '0'
            
            # Replace "Complete Assessment" sections
            assessment_pattern = r'### Complete Assessment.*?\n.*?- \*\*\[📝 Complete Test & Solutions →\]\([^)]*\)\*\* - [^\n]*'
            
            if re.search(assessment_pattern, content, re.DOTALL):
                # Replace with standard test format
                replacement = f'''## 📝 Multiple Choice Test - Session {session_num}

Test your understanding of atomic agents and modular architecture concepts:

**Question 1:** What is the primary advantage of atomic agent architecture?
A) Faster processing speed
B) Single responsibility with clear boundaries
C) Lower memory usage
D) Easier debugging

**Question 2:** How do atomic agents achieve composability?
A) Through inheritance
B) By sharing state
C) Via clear input/output contracts
D) Using global variables

**Question 3:** What pattern enables atomic agents to work together?
A) Observer pattern
B) Singleton pattern
C) Pipeline composition pattern
D) Factory pattern

**Question 4:** Why is immutable state important in atomic agents?
A) Prevents side effects and ensures predictable behavior
B) Reduces memory usage
C) Improves processing speed
D) Simplifies code structure

**Question 5:** What is the benefit of modular architecture in production?
A) Easier to scale individual components
B) Faster overall processing
C) Lower development costs
D) Reduced complexity

[View Solutions →](Session{session_num}_Test_Solutions.md)'''
                
                content = re.sub(assessment_pattern, replacement, content, flags=re.DOTALL)
            
            # Fix other non-standard test headers
            content = re.sub(r'## Assessment', f'## 📝 Multiple Choice Test - Session {session_num}', content)
            content = re.sub(r'## Test Questions', f'## 📝 Multiple Choice Test - Session {session_num}', content)
            content = re.sub(r'## Practice Test', f'## 📝 Multiple Choice Test - Session {session_num}', content)
            content = re.sub(r'## Complete Assessment', f'## 📝 Multiple Choice Test - Session {session_num}', content)
            
            # Ensure test comes before navigation
            # Split content into sections
            sections = re.split(r'(## 🧭 Navigation)', content)
            
            if len(sections) >= 3:  # Has navigation section
                before_nav = sections[0]
                nav_and_after = ''.join(sections[1:])
                
                # Check if test is already in before_nav
                if '## 📝 Multiple Choice Test' in before_nav:
                    # Test is already before navigation, just ensure proper spacing
                    before_nav = re.sub(r'(\[View Solutions →\][^\n]*)\n(## 🧭 Navigation)', r'\1\n\n---\n\n\2', before_nav)
                    content = before_nav + nav_and_after
                else:
                    # Find test section and move it before navigation
                    test_match = re.search(r'(## 📝 Multiple Choice Test.*?\[View Solutions →\][^\n]*)', content, re.DOTALL)
                    if test_match:
                        test_section = test_match.group(1)
                        # Remove test from original location
                        content_without_test = re.sub(r'## 📝 Multiple Choice Test.*?\[View Solutions →\][^\n]*\n*', '', content, flags=re.DOTALL)
                        
                        # Insert test before navigation
                        content = re.sub(r'(## 🧭 Navigation)', f'{test_section}\n\n---\n\n\\1', content_without_test)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Fixed assessment/test in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def main():
    """Main function to fix all assessment sections."""
    print("=== Fixing Assessment Sections & Test Positioning ===\n")
    
    fixed_count = fix_assessment_sections()
    
    print(f"\n✅ Fixed {fixed_count} assessment/test sections")
    print("All tests are now standardized and properly positioned before Navigation!")

if __name__ == "__main__":
    main()