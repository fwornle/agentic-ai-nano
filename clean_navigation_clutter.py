#!/usr/bin/env python3
"""
Remove clunky heading-style navigation links and replace with clean inline links.
"""

import os
import re
import glob

def clean_navigation_clutter():
    """Remove heading-style navigation links from all files."""
    
    # Find all markdown files
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove clunky heading-style navigation sections
            patterns_to_remove = [
                r'## 🔗 Practice Test\s*\n\s*Take the practice test first:.*?\n\s*---\s*\n',
                r'## 🔗 Practice Questions\s*\n\s*Review the questions first:.*?\n\s*---\s*\n',
                r'## 🔗 Solutions\s*\n\s*Check your answers:.*?\n\s*---\s*\n',
                r'## 🔗 Test Solutions\s*\n\s*\[.*?\]\(.*?\)\s*\n\s*---\s*\n'
            ]
            
            for pattern in patterns_to_remove:
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            # Clean up multiple consecutive line breaks
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files += 1
                print(f"✅ Cleaned {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n✅ Cleaned {fixed_files} files")

def consolidate_practice_tests():
    """Move separate practice test content back into main session files."""
    
    # Find practice test files
    practice_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Practice_Test.md', recursive=True)
    
    for practice_file in practice_files:
        try:
            # Extract session info
            practice_path = Path(practice_file)
            base_name = practice_path.stem.replace('_Practice_Test', '')
            session_file = practice_path.parent / f"{base_name}.md"
            
            if not session_file.exists():
                print(f"❌ No corresponding session file for {practice_path.name}")
                continue
            
            # Read practice test content
            with open(practice_file, 'r', encoding='utf-8') as f:
                practice_content = f.read()
            
            # Extract just the questions (remove navigation and headers)
            questions_match = re.search(r'(\*\*Question 1:.*?)(?=---|\Z)', practice_content, re.DOTALL)
            if not questions_match:
                print(f"❌ No questions found in {practice_path.name}")
                continue
            
            questions = questions_match.group(1).strip()
            
            # Read session file
            with open(session_file, 'r', encoding='utf-8') as f:
                session_content = f.read()
            
            # Add questions before the final navigation section
            if '## 🧭 Navigation' in session_content:
                # Insert before navigation
                test_section = f'\n\n## 📝 Practice Assessment\n\nReady to test your understanding? Take the practice test to validate your knowledge:\n\n{questions}\n\n---\n\n'
                session_content = session_content.replace('## 🧭 Navigation', test_section + '## 🧭 Navigation')
            else:
                # Add at the end
                test_section = f'\n\n---\n\n## 📝 Practice Assessment\n\nReady to test your understanding? Take the practice test to validate your knowledge:\n\n{questions}\n\n---\n'
                session_content += test_section
            
            # Write updated session file
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(session_content)
            
            print(f"✅ Consolidated {practice_path.name} into {session_file.name}")
            
        except Exception as e:
            print(f"❌ Error consolidating {practice_file}: {e}")

def main():
    """Main cleanup function."""
    print("=== Cleaning Navigation Clutter ===\n")
    
    clean_navigation_clutter()
    
    print(f"\n✅ Navigation cleanup complete!")
    print("Files now have clean, minimal navigation without heading clutter.")

if __name__ == "__main__":
    from pathlib import Path
    main()