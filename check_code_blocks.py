#!/usr/bin/env python3

import os
import re
from pathlib import Path

def analyze_code_blocks(file_path):
    """Analyze code blocks in a markdown file and return those over 20 lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    code_blocks = []
    in_code_block = False
    start_line = 0
    block_count = 0
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```') and not in_code_block:
            # Start of code block
            in_code_block = True
            start_line = i
            block_count += 1
        elif line.strip().startswith('```') and in_code_block:
            # End of code block
            in_code_block = False
            block_length = i - start_line - 1
            
            if block_length > 20:
                # Get context around the code block
                context_start = max(0, start_line - 3)
                context_lines = lines[context_start:start_line]
                context = ''.join(context_lines).strip()
                
                code_blocks.append({
                    'block_number': block_count,
                    'start_line': start_line,
                    'end_line': i,
                    'length': block_length,
                    'context': context[-100:] if context else 'No context'
                })
    
    return code_blocks

def main():
    mcp_dir = Path('03_mcp-adk-a2a')
    
    print("=== CODE BLOCK ANALYSIS FOR MODULE 03 (MCP-ADK-A2A) ===\n")
    
    all_long_blocks = []
    
    for i in range(10):  # Sessions 0-9
        session_files = list(mcp_dir.glob(f'Session{i}_*.md'))
        session_files = [f for f in session_files if 'Test_Solutions' not in f.name and 'solution' not in f.name]
        
        if not session_files:
            continue
            
        session_file = session_files[0]  # Take the first match
        
        print(f"📄 {session_file.name}")
        print("-" * 50)
        
        long_blocks = analyze_code_blocks(session_file)
        
        if long_blocks:
            for block in long_blocks:
                print(f"  🔴 Block #{block['block_number']}: Lines {block['start_line']}-{block['end_line']} ({block['length']} lines)")
                print(f"     Context: {block['context']}")
                print()
                all_long_blocks.append((session_file.name, block))
        else:
            print("  ✅ All code blocks are 20 lines or fewer")
        
        print()
    
    print(f"\n=== SUMMARY ===")
    print(f"Total sessions with long code blocks: {len(set(item[0] for item in all_long_blocks))}")
    print(f"Total long code blocks: {len(all_long_blocks)}")
    
    if all_long_blocks:
        print("\n🚨 SESSIONS NEEDING FIXES:")
        for session_name, block in all_long_blocks:
            print(f"  - {session_name}: Block #{block['block_number']} ({block['length']} lines)")

if __name__ == '__main__':
    main()