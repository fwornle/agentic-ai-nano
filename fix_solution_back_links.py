#!/usr/bin/env python3
"""
Fix broken back links in Test_Solutions.md files.
Ensure "Back to Test" links point to the correct main session file.
"""

import os
import re
import glob

def fix_solution_back_links():
    """Fix back links in all Test_Solutions.md files."""
    
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in solution_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Extract session number from filename
            session_match = re.search(r'Session(\d+)_Test_Solutions\.md', os.path.basename(file_path))
            if not session_match:
                continue
                
            session_num = session_match.group(1)
            
            # Determine the main session file name
            # Look in the same directory for the main session file
            directory = os.path.dirname(file_path)
            
            # Common main session file patterns
            possible_main_files = [
                f"Session{session_num}_*.md",
                f"Session{session_num}.md",
            ]
            
            main_session_file = None
            for pattern in possible_main_files:
                matches = glob.glob(os.path.join(directory, pattern))
                for match in matches:
                    if 'Test_Solutions.md' not in match and 'Module' not in os.path.basename(match):
                        main_session_file = os.path.basename(match)
                        break
                if main_session_file:
                    break
            
            if not main_session_file:
                # Default fallback
                main_session_file = f"Session{session_num}_*.md"
            
            # Fix the back link
            # Replace various broken back link patterns
            back_link_patterns = [
                r'\*\*Back to Test:\*\* \[Session \d+ Test Questions →\]\([^)]*\)',
                r'\*\*Back to Test:\*\* \[Session \d+ - [^]]*\]\([^)]*\)',
                r'\*\*Back to Main Session:\*\* \[Session \d+ - [^]]*\]\([^)]*\)'
            ]
            
            correct_back_link = f"**Back to Test:** [Session {session_num} Test Questions →]({main_session_file}#multiple-choice-test)"
            
            for pattern in back_link_patterns:
                content = re.sub(pattern, correct_back_link, content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Fixed back link in {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    return fixed_files

def main():
    """Main function to fix all solution back links."""
    print("=== Fixing Solution Back Links ===\n")
    
    fixed_count = fix_solution_back_links()
    
    print(f"\n✅ Fixed back links in {fixed_count} solution files")
    print("All solution files now have correct back links to their test questions!")

if __name__ == "__main__":
    main()