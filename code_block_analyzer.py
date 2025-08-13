#!/usr/bin/env python3
"""
Comprehensive Code Block Length Analyzer for 01_frameworks Session Files

This script analyzes ALL Session*.md files to identify and report on code block lengths,
specifically highlighting code blocks over 20 lines that need to be broken up.

Usage:
    python code_block_analyzer.py

Output:
    - Detailed report of all code blocks and their lengths
    - Summary statistics
    - Specific recommendations for blocks that need attention
"""

import os
import re
import glob
from typing import List, Dict, Tuple, NamedTuple
from pathlib import Path

class CodeBlock(NamedTuple):
    """Represents a code block found in a markdown file"""
    file_path: str
    start_line: int
    end_line: int
    language: str
    line_count: int
    content_preview: str

class CodeBlockAnalyzer:
    """Analyzes code blocks in markdown files"""
    
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.long_block_threshold = 20
        
    def find_session_files(self) -> List[Path]:
        """Find all Session*.md files in the directory"""
        pattern = str(self.directory / "Session*.md")
        files = glob.glob(pattern)
        # Sort to ensure consistent ordering
        return sorted([Path(f) for f in files])
    
    def extract_code_blocks(self, file_path: Path) -> List[CodeBlock]:
        """Extract all code blocks from a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        code_blocks = []
        in_code_block = False
        start_line = 0
        current_language = ""
        block_lines = []
        
        for i, line in enumerate(lines, 1):
            # Check for code block start
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a new code block
                    in_code_block = True
                    start_line = i
                    # Extract language from ```language
                    language_match = re.match(r'^```(\w+)?', line.strip())
                    current_language = language_match.group(1) if language_match and language_match.group(1) else "unknown"
                    block_lines = []
                else:
                    # Ending a code block
                    in_code_block = False
                    end_line = i
                    line_count = len(block_lines)
                    
                    # Create preview (first 100 chars)
                    content = '\n'.join(block_lines)
                    preview = content[:100].replace('\n', ' ') + ('...' if len(content) > 100 else '')
                    
                    code_block = CodeBlock(
                        file_path=str(file_path),
                        start_line=start_line,
                        end_line=end_line,
                        language=current_language,
                        line_count=line_count,
                        content_preview=preview
                    )
                    code_blocks.append(code_block)
            elif in_code_block:
                # Inside a code block, collect the line
                block_lines.append(line.rstrip())
        
        return code_blocks
    
    def analyze_all_files(self) -> Dict[str, List[CodeBlock]]:
        """Analyze all session files and return code blocks by file"""
        session_files = self.find_session_files()
        results = {}
        
        for file_path in session_files:
            print(f"Analyzing {file_path.name}...")
            code_blocks = self.extract_code_blocks(file_path)
            results[str(file_path)] = code_blocks
            
        return results
    
    def generate_report(self, analysis_results: Dict[str, List[CodeBlock]]) -> str:
        """Generate a comprehensive report of the analysis"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("CODE BLOCK LENGTH ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Summary statistics
        total_files = len(analysis_results)
        total_blocks = sum(len(blocks) for blocks in analysis_results.values())
        long_blocks = []
        
        # Collect all blocks and identify long ones
        all_blocks = []
        for file_path, blocks in analysis_results.items():
            for block in blocks:
                all_blocks.append(block)
                if block.line_count > self.long_block_threshold:
                    long_blocks.append(block)
        
        # Calculate statistics
        if all_blocks:
            avg_length = sum(block.line_count for block in all_blocks) / len(all_blocks)
            max_length = max(block.line_count for block in all_blocks)
            min_length = min(block.line_count for block in all_blocks)
        else:
            avg_length = max_length = min_length = 0
        
        # Summary section
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total files analyzed: {total_files}")
        report_lines.append(f"Total code blocks found: {total_blocks}")
        report_lines.append(f"Code blocks over {self.long_block_threshold} lines: {len(long_blocks)}")
        report_lines.append(f"Average block length: {avg_length:.1f} lines")
        report_lines.append(f"Longest block: {max_length} lines")
        report_lines.append(f"Shortest block: {min_length} lines")
        report_lines.append("")
        
        # Detailed file analysis
        report_lines.append("DETAILED ANALYSIS BY FILE")
        report_lines.append("-" * 40)
        
        for file_path, blocks in analysis_results.items():
            file_name = Path(file_path).name
            report_lines.append(f"\n📁 {file_name}")
            report_lines.append(f"   Total code blocks: {len(blocks)}")
            
            if not blocks:
                report_lines.append("   No code blocks found")
                continue
            
            # Count long blocks in this file
            file_long_blocks = [b for b in blocks if b.line_count > self.long_block_threshold]
            if file_long_blocks:
                report_lines.append(f"   ⚠️  Blocks over {self.long_block_threshold} lines: {len(file_long_blocks)}")
            else:
                report_lines.append(f"   ✅ All blocks under {self.long_block_threshold} lines")
            
            # Show block details
            for i, block in enumerate(blocks, 1):
                status = "⚠️ " if block.line_count > self.long_block_threshold else "✅"
                report_lines.append(f"   {status} Block {i}: {block.line_count} lines ({block.language}) - Line {block.start_line}")
                if block.line_count > self.long_block_threshold:
                    report_lines.append(f"       Preview: {block.content_preview}")
        
        # Long blocks that need attention
        if long_blocks:
            report_lines.append("\n" + "=" * 80)
            report_lines.append("BLOCKS REQUIRING ATTENTION (OVER {} LINES)".format(self.long_block_threshold))
            report_lines.append("=" * 80)
            
            # Sort by length (longest first)
            long_blocks.sort(key=lambda x: x.line_count, reverse=True)
            
            for i, block in enumerate(long_blocks, 1):
                file_name = Path(block.file_path).name
                report_lines.append(f"\n🚨 #{i} - {block.line_count} lines")
                report_lines.append(f"   File: {file_name}")
                report_lines.append(f"   Location: Lines {block.start_line}-{block.end_line}")
                report_lines.append(f"   Language: {block.language}")
                report_lines.append(f"   Preview: {block.content_preview}")
                report_lines.append(f"   ⚡ RECOMMENDATION: Break this {block.line_count}-line block into smaller chunks")
        
        # Recommendations section
        report_lines.append("\n" + "=" * 80)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 80)
        
        if long_blocks:
            report_lines.append(f"\n🔧 IMMEDIATE ACTION REQUIRED:")
            report_lines.append(f"   - {len(long_blocks)} code blocks exceed {self.long_block_threshold} lines")
            report_lines.append(f"   - These blocks should be broken into smaller, focused examples")
            report_lines.append(f"   - Consider splitting into:")
            report_lines.append(f"     • Conceptual examples (5-10 lines)")
            report_lines.append(f"     • Implementation chunks (10-15 lines)")  
            report_lines.append(f"     • Complete examples (separate files with references)")
            
            # File-specific recommendations
            file_counts = {}
            for block in long_blocks:
                file_name = Path(block.file_path).name
                file_counts[file_name] = file_counts.get(file_name, 0) + 1
            
            report_lines.append(f"\n📂 FILES NEEDING MOST ATTENTION:")
            for file_name, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"   • {file_name}: {count} long blocks")
        else:
            report_lines.append(f"\n✅ EXCELLENT! No code blocks exceed {self.long_block_threshold} lines.")
            report_lines.append(f"   All code examples are appropriately sized for learning.")
        
        # Best practices
        report_lines.append(f"\n💡 BEST PRACTICES FOR CODE BLOCKS:")
        report_lines.append(f"   • Keep examples focused on single concepts")
        report_lines.append(f"   • Use progressive disclosure (simple → complex)")
        report_lines.append(f"   • Include comments explaining key concepts")
        report_lines.append(f"   • Reference complete examples in separate files")
        report_lines.append(f"   • Break long examples into logical steps")
        
        return "\n".join(report_lines)

def main():
    """Main function to run the analysis"""
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    frameworks_dir = script_dir / "01_frameworks"
    
    if not frameworks_dir.exists():
        print(f"Error: Directory {frameworks_dir} not found!")
        print("Please run this script from the nano-degree root directory.")
        return
    
    print("Starting comprehensive code block analysis...")
    print(f"Analyzing directory: {frameworks_dir}")
    print()
    
    # Create analyzer and run analysis
    analyzer = CodeBlockAnalyzer(frameworks_dir)
    results = analyzer.analyze_all_files()
    
    # Generate and display report
    report = analyzer.generate_report(results)
    print(report)
    
    # Also save report to file
    report_file = script_dir / "code_block_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_file}")
    print(f"\nAnalysis complete! Use this report to systematically fix all long code blocks.")

if __name__ == "__main__":
    main()