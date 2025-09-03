#!/usr/bin/env python3
"""
Fix key session files that have test content but missing or broken solution links.
Focus on main session files first.
"""

import os
import re
from pathlib import Path

def fix_session_test_links():
    """Fix test solution links for key session files."""
    
    # Key session files that need fixing
    key_sessions = [
        {
            'session_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session1_Bare_Metal_Agents.md',
            'solution_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session1_Test_Solutions.md',
            'session_name': 'Session1'
        },
        {
            'session_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session2_LangChain_Foundations.md',
            'solution_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session2_Test_Solutions.md',
            'session_name': 'Session2'
        },
        {
            'session_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session3_LangGraph_Multi_Agent_Workflows.md',
            'solution_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session3_Test_Solutions.md',
            'session_name': 'Session3'
        },
        {
            'session_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session4_CrewAI_Team_Orchestration.md',
            'solution_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session4_Test_Solutions.md',
            'session_name': 'Session4'
        },
        {
            'session_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session5_PydanticAI_Type_Safe_Agents.md',
            'solution_file': '/Users/q284340/Agentic/nano-degree/docs-content/01_frameworks/Session5_Test_Solutions.md',
            'session_name': 'Session5'
        }
    ]
    
    print("=== Fixing Key Session Test Links ===\n")
    
    for session in key_sessions:
        session_file = session['session_file']
        solution_file = session['solution_file']
        session_name = session['session_name']
        
        if not os.path.exists(session_file):
            print(f"❌ {session_name}: Session file not found")
            continue
            
        if not os.path.exists(solution_file):
            print(f"❌ {session_name}: Solution file not found")
            continue
        
        print(f"Processing {session_name}...")
        
        # Read session file
        with open(session_file, 'r', encoding='utf-8') as f:
            session_content = f.read()
        
        # Read solution file
        with open(solution_file, 'r', encoding='utf-8') as f:
            solution_content = f.read()
        
        # Check if session file has test content
        has_questions = bool(re.search(r'\*\*Question \d+:', session_content))
        has_test_section = 'multiple choice test' in session_content.lower()
        
        if not (has_questions or has_test_section):
            print(f"  ℹ️  No test content found in session file")
            continue
        
        # Add solution link to session file if missing
        solution_filename = os.path.basename(solution_file)
        if solution_filename not in session_content:
            # Look for test sections and add solution link
            if '## Multiple Choice Test' in session_content:
                # Add solution link after the test section
                test_pattern = r'(## Multiple Choice Test.*?)(?=##|\Z)'
                match = re.search(test_pattern, session_content, re.DOTALL)
                if match:
                    test_section = match.group(1)
                    new_test_section = test_section + f'\n\n## 🔗 Test Solutions\n\n[**📝 View Test Solutions →**]({solution_filename})\n\n---\n'
                    session_content = session_content.replace(test_section, new_test_section)
            
            # Write updated session file
            with open(session_file, 'w', encoding='utf-8') as f:
                f.write(session_content)
            
            print(f"  ✅ Added solution link to session file")
        else:
            print(f"  ✅ Solution link already exists")
        
        # Add back-link to solution file if missing
        session_filename = os.path.basename(session_file)
        if session_filename not in solution_content:
            # Add practice test link at the top
            lines = solution_content.split('\n')
            title_line = -1
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    title_line = i
                    break
            
            if title_line >= 0:
                practice_test_section = [
                    '',
                    '## 🔗 Practice Questions',
                    '',
                    f'Review the questions first: [**📝 {session_name} Questions →**]({session_filename})',
                    '',
                    '---',
                    ''
                ]
                lines = lines[:title_line+1] + practice_test_section + lines[title_line+1:]
                solution_content = '\n'.join(lines)
                
                # Write updated solution file
                with open(solution_file, 'w', encoding='utf-8') as f:
                    f.write(solution_content)
                
                print(f"  ✅ Added back-link to solution file")
            else:
                print(f"  ❌ Could not find title in solution file")
        else:
            print(f"  ✅ Back-link already exists")
        
        print()

def main():
    """Main function."""
    print("=== Key Session Test Links Fix ===\n")
    fix_session_test_links()
    print("✅ Completed fixing key session test links!")

if __name__ == "__main__":
    main()