#!/usr/bin/env python3
"""
Fix the 13 actually broken links
"""

import json
import re
from pathlib import Path

def fix_broken_links():
    """Fix the 13 broken links"""
    fixes = [
        # Session6 Agent Communication Protocols -> use Atomic Agents main file
        {
            'files': ['01_frameworks/Session4_ModuleA_Advanced_CrewAI_Flows.md', '01_frameworks/Session4_ModuleB_Enterprise_Team_Patterns.md'],
            'old_target': 'Session6_Agent_Communication_Protocols.md',
            'new_target': 'Session6_Atomic_Agents_Modular_Architecture.md',
            'old_text': 'Agent Communication Protocols',
            'new_text': 'Atomic Agents & Modular Architecture'
        },
        # Session9 Observer -> use Multi Agent Patterns file
        {
            'files': ['01_frameworks/Session9_Practical_Coordination.md', '01_frameworks/Session9_Implementation_Guide.md'],
            'old_target': 'Session9_Multi_Agent_Patterns_Observer.md',
            'new_target': 'Session9_Multi_Agent_Patterns.md',
            'old_text': ['Session9_Multi_Agent_Patterns_Observer.md', 'Observer Path'],
            'new_text': 'Multi-Agent Patterns'
        },
        # Session9 Advanced Framework Patterns -> Advanced Coordination
        {
            'files': ['01_frameworks/Session8_ModuleD_Security_Compliance.md'],
            'old_target': 'Session9_Advanced_Framework_Patterns.md',
            'new_target': 'Session9_Advanced_Coordination.md',
            'old_text': 'Session 9 - Advanced Framework Patterns',
            'new_text': 'Session 9 - Advanced Coordination'
        },
        # MCP Enterprise File Operations -> remove or comment out as doesn't exist
        {
            'files': ['03_mcp-acp-a2a/Session2_FileSystem_MCP_Server.md'],
            'old_target': 'Session2_Enterprise_File_Operations.md',
            'new_target': None,  # Will comment out
            'old_text': 'Enterprise File Operations',
            'new_text': None
        }
    ]
    
    fixed_count = 0
    
    for fix in fixes:
        for file_path in fix['files']:
            full_path = Path('docs-content') / file_path
            if not full_path.exists():
                continue
                
            content = full_path.read_text()
            
            # Handle old_text as list or string
            old_texts = fix['old_text'] if isinstance(fix['old_text'], list) else [fix['old_text']]
            
            for old_text in old_texts:
                old_link = f"[{old_text}]({fix['old_target']})"
                
                if fix['new_target'] is None:
                    # Comment out the link
                    new_link = f"<!-- [{old_text}]({fix['old_target']}) (Link disabled - target file not found) -->"
                else:
                    new_link = f"[{fix['new_text']}]({fix['new_target']})"
                
                if old_link in content:
                    content = content.replace(old_link, new_link)
                    full_path.write_text(content)
                    print(f"Fixed link in {file_path}: {old_text} -> {fix['new_text'] or 'commented out'}")
                    fixed_count += 1
    
    return fixed_count

def fix_rag_index_links():
    """Fix the RAG index.md links to correct Session files"""
    rag_index = Path('docs-content/02_rag/index.md')
    if not rag_index.exists():
        return 0
        
    content = rag_index.read_text()
    
    # Find actual Session files in 02_rag
    rag_sessions = []
    rag_dir = Path('docs-content/02_rag')
    for f in rag_dir.glob('Session*.md'):
        if 'Test_Solutions' not in f.name and f.name != 'index.md':
            rag_sessions.append(f.name)
    
    rag_sessions.sort()
    print(f"Found RAG sessions: {rag_sessions[:10]}")  # Show first 10
    
    # Map broken links to actual files
    link_fixes = {
        'Session1_RAG_Fundamentals_Vector_Databases.md': 'Session1_Basic_RAG_Implementation.md',
        'Session2_Advanced_Chunking_Query_Processing.md': 'Session2_Advanced_Chunking_Preprocessing.md',
        'Session3_RAG_Search_Enhancement_Query_Expansion.md': 'Session3_RAG_Search_Enhancement.md',
        'Session4_Advanced_Context_RAG_Routing.md': 'Session4_Query_Enhancement_Context_Augmentation.md'
    }
    
    fixed_count = 0
    for old_target, new_target in link_fixes.items():
        if new_target in [s for s in rag_sessions]:
            # Find and replace the link
            old_pattern = f'\\[\\*\\*Start Session \\d+ →\\*\\*\\]\\({re.escape(old_target)}\\)'
            # Extract session number from old target
            session_num = re.search(r'Session(\d+)', old_target)
            if session_num:
                new_link = f'[**Start Session {session_num.group(1)} →**]({new_target})'
                content = re.sub(old_pattern, new_link, content)
                print(f"Fixed RAG index link: {old_target} -> {new_target}")
                fixed_count += 1
    
    if fixed_count > 0:
        rag_index.write_text(content)
    
    return fixed_count

def fix_session4_module_links():
    """Fix Session4 module links to non-existent files"""
    session4_file = Path('docs-content/02_rag/Session4_Query_Enhancement_Context_Augmentation.md')
    if not session4_file.exists():
        return 0
    
    content = session4_file.read_text()
    
    # Comment out links to non-existent module files
    module_links = [
        ('Session4_Advanced_HyDE_Systems.md', 'Advanced HyDE Systems'),
        ('Session4_Multi_Query_Systems.md', 'Multi-Query Systems'),
        ('Session4_Advanced_Context_Systems.md', 'Advanced Context Systems')
    ]
    
    fixed_count = 0
    for target, text in module_links:
        old_link = f'[{text}]({target})'
        new_link = f'<!-- [{text}]({target}) (Module not yet implemented) -->'
        
        if old_link in content:
            content = content.replace(old_link, new_link)
            print(f"Commented out link in Session4: {text}")
            fixed_count += 1
    
    if fixed_count > 0:
        session4_file.write_text(content)
    
    return fixed_count

def main():
    print("🔧 Fixing 13 broken links...")
    
    fixed1 = fix_broken_links()
    fixed2 = fix_rag_index_links()
    fixed3 = fix_session4_module_links()
    
    total_fixed = fixed1 + fixed2 + fixed3
    print(f"✅ Fixed {total_fixed} broken links")
    
    # Re-run analysis
    print("\n🔍 Re-analyzing...")
    import os
    os.system('python3 fix_analysis_bug.py')

if __name__ == "__main__":
    main()