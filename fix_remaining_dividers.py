#!/usr/bin/env python3
"""
Fix remaining complex divider spacing issues in specific problematic files.
"""

import os
import re

def fix_complex_dividers():
    """Fix complex divider patterns in the problematic file."""
    
    file_path = '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session9_Implementation_Guide.md'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check if current line is any type of divider (3 or more dashes)
            if re.match(r'^-{3,}$', line.strip()):
                # Check if previous line exists and is not empty
                if i > 0 and lines[i-1].strip() != '':
                    # Add empty line before divider
                    fixed_lines.append('')
            
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ Fixed remaining dividers in {os.path.basename(file_path)}")
            return True
        else:
            print(f"No changes needed in {os.path.basename(file_path)}")
            return False
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix remaining divider issues."""
    print("=== Fixing Remaining Divider Issues ===\n")
    
    success = fix_complex_dividers()
    
    if success:
        print("✅ All remaining divider spacing issues have been fixed!")
    else:
        print("✅ No additional fixes were needed.")

if __name__ == "__main__":
    main()