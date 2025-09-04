#!/usr/bin/env python3
"""
Fix the remaining 4 files with test issues.
"""

import os
import re

def fix_test_position(file_path):
    """Fix test position to be second-to-last (before Navigation)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Find the test section
        test_match = re.search(r'(## 📝 Multiple Choice Test.*?)(?=## |$)', content, re.DOTALL)
        if not test_match:
            print(f"  No test section found in {os.path.basename(file_path)}")
            return False
        
        test_section = test_match.group(1).strip()
        
        # Find the Navigation section
        nav_match = re.search(r'(## 🧭 Navigation.*)', content, re.DOTALL)
        if not nav_match:
            print(f"  No Navigation section found in {os.path.basename(file_path)}")
            return False
        
        nav_section = nav_match.group(1).strip()
        
        # Remove the existing test section
        content = content.replace(test_match.group(1), '')
        
        # Remove the existing navigation section
        content = content.replace(nav_match.group(1), '')
        
        # Clean up extra dividers and whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'---\s*\n\s*---', '---', content)
        
        # Ensure content ends properly
        content = content.rstrip()
        if not content.endswith('\n'):
            content += '\n'
        
        # Add test section and navigation at the end
        final_content = content + '\n' + test_section + '\n\n---\n\n' + nav_section + '\n'
        
        # Add solution link if missing
        if '[View Solutions →]' not in final_content and 'Multiple Choice Test' in final_content:
            # Extract session number from filename or content
            session_match = re.search(r'Session(\d+)', os.path.basename(file_path))
            if session_match:
                session_num = session_match.group(1)
                solution_link = f'\n[View Solutions →](Session{session_num}_Test_Solutions.md)\n'
                final_content = final_content.replace('---\n\n## 🧭 Navigation', solution_link + '\n---\n\n## 🧭 Navigation')
        
        if final_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def fix_specific_files():
    """Fix the 4 specific files identified"""
    files_to_fix = [
        '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session8_ModuleC_Performance_Production_Validation.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/02_rag/Session5_RAG_Evaluation_Quality_Assessment.md', 
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a/Session3_LangChain_MCP_Integration.md',
        '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/index.md'
    ]
    
    print("=== Fixing Remaining Test Issues ===\n")
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"Fixing {os.path.basename(file_path)}...")
            if fix_test_position(file_path):
                fixed_count += 1
                print(f"  ✅ Fixed test positioning")
            else:
                print(f"  ⚠️  No changes needed")
        else:
            print(f"  ❌ File not found: {file_path}")
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    fix_specific_files()