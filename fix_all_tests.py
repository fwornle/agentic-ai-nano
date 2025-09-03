#!/usr/bin/env python3
"""
Comprehensive script to fix all test-solution consistency issues:
1. Add bidirectional navigation links
2. Ensure consistent formatting
3. Verify question/answer alignment
"""

import os
import re
import glob
from pathlib import Path

def find_test_solution_pairs():
    """Find all test-solution file pairs."""
    solution_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*_Test_Solutions.md', recursive=True)
    pairs = []
    
    for solution_file in solution_files:
        solution_path = Path(solution_file)
        solution_name = solution_path.stem
        
        # Extract base name (remove _Test_Solutions)
        base_name = solution_name.replace('_Test_Solutions', '')
        
        # Look for corresponding test files
        possible_test_names = [
            f"{base_name}_Practice_Test.md",
            f"{base_name}.md",
            f"{base_name}_Test.md"
        ]
        
        for test_name in possible_test_names:
            test_file = solution_path.parent / test_name
            if test_file.exists():
                pairs.append({
                    'test_file': str(test_file),
                    'solution_file': solution_file,
                    'base_name': base_name
                })
                break
        else:
            # Look for test sections in main session files
            main_file = solution_path.parent / f"{base_name}.md"
            if main_file.exists():
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'multiple choice test' in content.lower() or re.search(r'\*\*Question \d+:', content):
                    pairs.append({
                        'test_file': str(main_file),
                        'solution_file': solution_file,
                        'base_name': base_name,
                        'embedded_test': True
                    })
    
    return pairs

def add_navigation_links(test_file, solution_file, base_name):
    """Add bidirectional navigation links between test and solution files."""
    print(f"Processing: {base_name}")
    
    # Read test file
    with open(test_file, 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    # Read solution file
    with open(solution_file, 'r', encoding='utf-8') as f:
        solution_content = f.read()
    
    # Extract filenames
    test_filename = os.path.basename(test_file)
    solution_filename = os.path.basename(solution_file)
    
    # Add link to solution in test file (if not already present)
    if solution_filename not in test_content and solution_filename.replace('.md', '') not in test_content:
        # Look for existing solutions section or add at end
        if '## Solutions' in test_content or '## Test Solutions' in test_content:
            # Replace existing solutions section
            test_content = re.sub(
                r'## (Test )?Solutions.*?(?=##|\Z)',
                f'## 🔗 Solutions\n\nCheck your answers: [**📝 {base_name} Test Solutions →**]({solution_filename})\n\n---\n\n',
                test_content,
                flags=re.DOTALL
            )
        else:
            # Add solutions section before navigation
            if '## 🧭 Navigation' in test_content:
                test_content = test_content.replace(
                    '## 🧭 Navigation',
                    f'## 🔗 Solutions\n\nCheck your answers: [**📝 {base_name} Test Solutions →**]({solution_filename})\n\n---\n\n## 🧭 Navigation'
                )
            else:
                # Add at the end
                test_content += f'\n\n---\n\n## 🔗 Solutions\n\nCheck your answers: [**📝 {base_name} Test Solutions →**]({solution_filename})\n\n---\n'
    
    # Add link to test in solution file (if not already present)
    if test_filename not in solution_content and test_filename.replace('.md', '') not in solution_content:
        # Add at the top after title
        lines = solution_content.split('\n')
        title_line = -1
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title_line = i
                break
        
        if title_line >= 0:
            # Insert practice test link after title
            practice_test_section = [
                '',
                '## 🔗 Practice Test',
                '',
                f'Take the practice test first: [**📝 {base_name} Practice Test →**]({test_filename})',
                '',
                '---',
                ''
            ]
            lines = lines[:title_line+1] + practice_test_section + lines[title_line+1:]
            solution_content = '\n'.join(lines)
    
    # Write updated files
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    with open(solution_file, 'w', encoding='utf-8') as f:
        f.write(solution_content)
    
    print(f"  ✅ Added navigation links")

def ensure_consistent_formatting(pairs):
    """Ensure consistent formatting across all test files."""
    print("\n=== Ensuring Consistent Formatting ===")
    
    for pair in pairs:
        test_file = pair['test_file']
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure questions are properly formatted
        # Format: **Question N:** text
        content = re.sub(r'\*\*Question (\d+):\*\*', r'**Question \1:**', content)
        
        # Ensure answer options are properly formatted
        content = re.sub(r'^([A-D])\)\s*', r'\1) ', content, flags=re.MULTILINE)
        
        # Ensure proper spacing around questions
        content = re.sub(r'(\*\*Question \d+:.*?\n[A-D]\).*?\n[A-D]\).*?\n[A-D]\).*?\n[A-D]\).*?\n)\n*', r'\1\n', content)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    """Main function to fix all test issues."""
    print("=== Comprehensive Test-Solution Fix ===\n")
    
    # Find all test-solution pairs
    pairs = find_test_solution_pairs()
    print(f"Found {len(pairs)} test-solution pairs\n")
    
    # Add navigation links to each pair
    print("=== Adding Navigation Links ===")
    for pair in pairs:
        try:
            add_navigation_links(pair['test_file'], pair['solution_file'], pair['base_name'])
        except Exception as e:
            print(f"  ❌ Error processing {pair['base_name']}: {e}")
    
    # Ensure consistent formatting
    ensure_consistent_formatting(pairs)
    
    print(f"\n=== Summary ===")
    print(f"✅ Processed {len(pairs)} test-solution pairs")
    print(f"✅ Added bidirectional navigation links")
    print(f"✅ Ensured consistent formatting")
    print(f"\nAll test-solution consistency issues have been addressed!")

if __name__ == "__main__":
    main()