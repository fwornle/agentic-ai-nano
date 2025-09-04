#!/usr/bin/env python3
"""
Create missing solution files and add links
"""

import re
from pathlib import Path

def create_solutions_and_links():
    """Create missing solution files and add links to tests"""
    
    # Files that need solution files and links
    test_files = [
        '03_mcp-acp-a2a/Session2_FileSystem_MCP_Server.md',
        '03_mcp-acp-a2a/Session3_ModuleB_Advanced_Workflows.md', 
        '03_mcp-acp-a2a/Session3_ModuleA_Enterprise_Patterns.md',
        '02_rag/Session9_Production_RAG_Enterprise_Integration.md',
        '02_rag/Session1_Basic_RAG_Implementation.md',
        '02_rag/Session8_MultiModal_Advanced_RAG.md',
        '02_rag/src/session5/Session6_Atomic_Agents_Modular_Architecture.md'
    ]
    
    created_count = 0
    linked_count = 0
    
    for test_file in test_files:
        file_path = Path('docs-content') / test_file
        if not file_path.exists():
            print(f"Test file not found: {test_file}")
            continue
            
        content = file_path.read_text()
        
        # Create solution filename
        filename = Path(test_file).name
        solution_filename = filename.replace('.md', '_Test_Solutions.md')
        solution_path = file_path.parent / solution_filename
        
        # Create solution file if it doesn't exist
        if not solution_path.exists():
            # Extract session name from filename for title
            session_name = filename.replace('_', ' ').replace('.md', '')
            
            solution_content = f"""# {session_name} - Test Solutions

## Multiple Choice Questions

### Question 1
**Answer:** [To be completed]

**Explanation:** [To be completed]

### Question 2
**Answer:** [To be completed]

**Explanation:** [To be completed]

### Question 3
**Answer:** [To be completed]

**Explanation:** [To be completed]

---

## Back to Test

[← Back to Test]({filename})

---

## 🧭 Navigation

**Course Home:** [Course Overview →](../index.md)

---
"""
            
            solution_path.write_text(solution_content)
            print(f"Created: {solution_path}")
            created_count += 1
        
        # Add solution link to test file if it doesn't exist
        if 'View Solutions' not in content:
            # Try to add before navigation
            nav_pattern = r'(---\s*\n## 🧭 Navigation)'
            
            if re.search(nav_pattern, content):
                solution_link = f"\n\n[View Solutions →]({solution_filename})\n\n---\n\n## 🧭 Navigation"
                content = re.sub(nav_pattern, solution_link, content)
                file_path.write_text(content)
                print(f"Added solution link to: {test_file}")
                linked_count += 1
            else:
                # Add at end
                content += f"\n\n[View Solutions →]({solution_filename})\n"
                file_path.write_text(content)
                print(f"Added solution link at end: {test_file}")
                linked_count += 1
    
    return created_count, linked_count

def main():
    print("📝 Creating missing solution files and adding links...")
    created, linked = create_solutions_and_links()
    print(f"✅ Created {created} solution files")
    print(f"✅ Added {linked} solution links")

if __name__ == "__main__":
    main()