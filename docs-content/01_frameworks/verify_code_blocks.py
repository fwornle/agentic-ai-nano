#!/usr/bin/env python3
"""
Script to verify code block sizes in markdown files
"""
import sys
import re

def analyze_code_blocks(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all code blocks
    code_block_pattern = r'```[\w]*\n(.*?)\n```'
    blocks = re.findall(code_block_pattern, content, re.DOTALL)
    
    large_blocks = []
    block_sizes = []
    
    for i, block in enumerate(blocks):
        lines = block.strip().split('\n')
        line_count = len(lines)
        block_sizes.append(line_count)
        
        if line_count > 20:
            large_blocks.append((i + 1, line_count))
    
    print(f"\n=== CODE BLOCK ANALYSIS ===")
    print(f"File: {file_path}")
    print(f"Total code blocks: {len(blocks)}")
    print(f"Large blocks (>20 lines): {len(large_blocks)}")
    
    if large_blocks:
        print(f"\nLARGE CODE BLOCKS:")
        for block_num, size in large_blocks:
            print(f"  Block {block_num}: {size} lines")
    
    # Calculate statistics
    if block_sizes:
        avg_size = sum(block_sizes) / len(block_sizes)
        max_size = max(block_sizes)
        min_size = min(block_sizes)
        
        print(f"\nSTATISTICS:")
        print(f"  Average block size: {avg_size:.1f} lines")
        print(f"  Largest block: {max_size} lines")
        print(f"  Smallest block: {min_size} lines")
    
    # Success metrics
    small_blocks = len([s for s in block_sizes if s <= 20])
    if len(blocks) > 0:
        compliance_rate = (small_blocks / len(blocks)) * 100
        print(f"  Compliance rate (≤20 lines): {compliance_rate:.1f}%")
        
        if compliance_rate >= 70:
            print(f"  ✅ GOOD: {compliance_rate:.1f}% compliance rate")
        else:
            print(f"  ❌ NEEDS IMPROVEMENT: {compliance_rate:.1f}% compliance rate")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_code_blocks.py <markdown_file>")
        sys.exit(1)
    
    analyze_code_blocks(sys.argv[1])