#!/usr/bin/env python3
"""
Quality Assurance Analysis Script for Test-Solution Consistency
Analyzes all test files and their corresponding solution files for consistency.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

def find_all_test_files(docs_dir: str) -> Dict[str, List[str]]:
    """Find all files with test content and their corresponding solution files."""
    
    # Pattern to match files that might have tests (ending with view test solutions link)
    test_files = []
    solution_files = []
    
    docs_path = Path(docs_dir)
    
    # Find all markdown files
    for md_file in docs_path.rglob("*.md"):
        if "Test_Solutions" in md_file.name:
            solution_files.append(str(md_file))
        else:
            # Check if file has test content
            try:
                content = md_file.read_text(encoding='utf-8')
                if "View Test Solutions" in content or "**Question" in content:
                    test_files.append(str(md_file))
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
    
    return {"test_files": test_files, "solution_files": solution_files}

def extract_questions_from_file(file_path: str) -> Tuple[List[Dict], Optional[str]]:
    """Extract questions from a file and find the solution link."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [], f"Error reading file: {e}"
    
    questions = []
    solution_link = None
    
    # Extract questions using various patterns
    question_patterns = [
        r'\*\*Question (\d+)\*\*:?\s*(.+?)(?=\*\*Question \d+\*\*|\*\*Answers?\*\*|$)',
        r'Question (\d+):\s*(.+?)(?=Question \d+:|$)',
        r'(\d+)\.\s*(.+?)(?=\d+\.\s|$)',
    ]
    
    for pattern in question_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            for num, question_text in matches:
                # Extract answer choices
                choices = re.findall(r'[A-D]\)\s*([^A-D\n]+)', question_text)
                questions.append({
                    "number": int(num),
                    "text": question_text.strip(),
                    "choices": choices
                })
            break
    
    # Find solution link
    solution_match = re.search(r'\[.*?View Test Solutions.*?\]\(([^)]+)\)', content, re.IGNORECASE)
    if solution_match:
        solution_link = solution_match.group(1)
    
    return questions, solution_link

def extract_solutions_from_file(file_path: str) -> Tuple[List[Dict], Optional[str]]:
    """Extract solutions from a solution file and find the back link."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [], f"Error reading file: {e}"
    
    solutions = []
    back_link = None
    
    # Extract questions and answers from solution file
    question_patterns = [
        r'\*\*Question (\d+)\*\*:?\s*(.+?)(?=\*\*Question \d+\*\*|$)',
        r'Question (\d+):\s*(.+?)(?=Question \d+:|$)',
    ]
    
    for pattern in question_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            for num, question_text in matches:
                # Extract answer choices and correct answer
                choices = re.findall(r'[A-D]\)\s*([^A-D\n]+)', question_text)
                answer_match = re.search(r'\*\*Answer:\s*([A-D])\*\*', question_text, re.IGNORECASE)
                correct_answer = answer_match.group(1) if answer_match else None
                
                solutions.append({
                    "number": int(num),
                    "text": question_text.strip(),
                    "choices": choices,
                    "correct_answer": correct_answer
                })
            break
    
    # Find back link to main session
    back_link_patterns = [
        r'\[.*?←.*?\]\(([^)]+)\)',
        r'\[.*?Back.*?\]\(([^)]+)\)',
        r'← \[([^]]+)\]'
    ]
    
    for pattern in back_link_patterns:
        back_match = re.search(pattern, content, re.IGNORECASE)
        if back_match:
            back_link = back_match.group(1)
            break
    
    return solutions, back_link

def analyze_consistency(test_file: str, solution_file: str) -> Dict:
    """Analyze consistency between a test file and its solution file."""
    
    test_questions, solution_link = extract_questions_from_file(test_file)
    solution_questions, back_link = extract_solutions_from_file(solution_file)
    
    issues = []
    
    # Check question count consistency
    if len(test_questions) != len(solution_questions):
        issues.append(f"Question count mismatch: {len(test_questions)} in test vs {len(solution_questions)} in solutions")
    
    # Check individual questions
    for i, (test_q, sol_q) in enumerate(zip(test_questions, solution_questions)):
        if test_q["number"] != sol_q["number"]:
            issues.append(f"Question {i+1}: Number mismatch ({test_q['number']} vs {sol_q['number']})")
        
        if len(test_q["choices"]) != len(sol_q["choices"]):
            issues.append(f"Question {test_q['number']}: Choice count mismatch ({len(test_q['choices'])} vs {len(sol_q['choices'])})")
    
    # Check navigation links
    if not solution_link:
        issues.append("Missing forward link (test → solution)")
    
    if not back_link:
        issues.append("Missing back link (solution → test)")
    
    return {
        "test_file": test_file,
        "solution_file": solution_file,
        "test_question_count": len(test_questions),
        "solution_question_count": len(solution_questions),
        "has_forward_link": bool(solution_link),
        "has_back_link": bool(back_link),
        "forward_link": solution_link,
        "back_link": back_link,
        "issues": issues
    }

def main():
    docs_dir = "/Users/q284340/Agentic/nano-degree/docs-content"
    
    # Find all test and solution files
    files = find_all_test_files(docs_dir)
    
    print(f"Found {len(files['test_files'])} test files")
    print(f"Found {len(files['solution_files'])} solution files")
    
    # Analyze each test file
    analyses = []
    
    for test_file in files['test_files']:
        # Determine corresponding solution file
        base_name = Path(test_file).stem
        
        # Try different solution file patterns
        solution_patterns = [
            f"{base_name}_Test_Solutions.md",
            f"{base_name.replace('_ModuleA', '')}_ModuleA_Test_Solutions.md",
            f"{base_name.replace('_ModuleB', '')}_ModuleB_Test_Solutions.md",
            f"{base_name.replace('_ModuleC', '')}_ModuleC_Test_Solutions.md",
            f"{base_name.replace('_ModuleD', '')}_ModuleD_Test_Solutions.md",
        ]
        
        solution_file = None
        for pattern in solution_patterns:
            candidate = str(Path(test_file).parent / pattern)
            if candidate in files['solution_files']:
                solution_file = candidate
                break
        
        if solution_file:
            analysis = analyze_consistency(test_file, solution_file)
            analyses.append(analysis)
        else:
            analyses.append({
                "test_file": test_file,
                "solution_file": "NOT_FOUND",
                "issues": ["No corresponding solution file found"]
            })
    
    # Save results
    with open("/Users/q284340/Agentic/nano-degree/qa_analysis_results.json", "w") as f:
        json.dump(analyses, f, indent=2)
    
    # Print summary
    total_files = len(analyses)
    files_with_issues = sum(1 for a in analyses if a.get('issues', []))
    
    print(f"\n=== QA ANALYSIS SUMMARY ===")
    print(f"Total test files analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Success rate: {((total_files - files_with_issues) / total_files * 100):.1f}%")
    
    print(f"\n=== ISSUES BY FILE ===")
    for analysis in analyses:
        if analysis.get('issues', []):
            print(f"\n{Path(analysis['test_file']).name}:")
            for issue in analysis['issues']:
                print(f"  - {issue}")

if __name__ == "__main__":
    main()