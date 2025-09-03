#!/usr/bin/env python3
"""
Detailed Quality Assurance Analysis Script
Focuses on confirmed test-solution pairs with detailed content analysis.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from difflib import SequenceMatcher

def extract_questions_detailed(content: str) -> List[Dict]:
    """Extract questions with all details from content."""
    questions = []
    
    # Split content by Question patterns
    question_blocks = re.split(r'\*\*Question (\d+)\*\*:?\s*', content)[1:]  # Skip first empty element
    
    for i in range(0, len(question_blocks), 2):
        if i + 1 < len(question_blocks):
            question_num = int(question_blocks[i])
            question_content = question_blocks[i + 1]
            
            # Extract question text (everything before the first A)
            question_parts = re.split(r'\n[A-D]\)', question_content, 1)
            question_text = question_parts[0].strip()
            
            # Extract choices
            choices = {}
            choice_matches = re.findall(r'([A-D])\)\s*([^\nA-D]+?)(?=\n[A-D]\)|$)', question_content)
            for letter, choice_text in choice_matches:
                choices[letter] = choice_text.strip()
            
            questions.append({
                "number": question_num,
                "text": question_text,
                "choices": choices
            })
    
    return questions

def extract_solutions_detailed(content: str) -> List[Dict]:
    """Extract solutions with all details from content."""
    solutions = []
    
    # Split content by Question patterns
    question_blocks = re.split(r'\*\*Question (\d+)\*\*:?\s*', content)[1:]
    
    for i in range(0, len(question_blocks), 2):
        if i + 1 < len(question_blocks):
            question_num = int(question_blocks[i])
            question_content = question_blocks[i + 1]
            
            # Extract question text
            question_parts = re.split(r'\n[A-D]\)', question_content, 1)
            question_text = question_parts[0].strip()
            
            # Extract choices and find correct answer
            choices = {}
            correct_answer = None
            choice_matches = re.findall(r'([A-D])\)\s*([^\nA-D✅]+?)(?:\s*✅)?(?=\n[A-D]\)|$)', question_content)
            
            for letter, choice_text in choice_matches:
                choices[letter] = choice_text.strip()
                # Check if this choice has the checkmark
                if '✅' in question_content and f'{letter})' in question_content.split('✅')[0]:
                    # Find the line with this letter that has checkmark
                    lines = question_content.split('\n')
                    for line in lines:
                        if f'{letter})' in line and '✅' in line:
                            correct_answer = letter
                            break
            
            solutions.append({
                "number": question_num,
                "text": question_text,
                "choices": choices,
                "correct_answer": correct_answer
            })
    
    return solutions

def compare_questions(test_q: Dict, sol_q: Dict) -> List[str]:
    """Compare a test question with its solution and return list of issues."""
    issues = []
    
    if test_q["number"] != sol_q["number"]:
        issues.append(f"Question number mismatch: {test_q['number']} vs {sol_q['number']}")
    
    # Compare question text similarity
    similarity = SequenceMatcher(None, test_q["text"], sol_q["text"]).ratio()
    if similarity < 0.9:  # Less than 90% similar
        issues.append(f"Question text differs significantly (similarity: {similarity:.2f})")
    
    # Compare choice counts
    if len(test_q["choices"]) != len(sol_q["choices"]):
        issues.append(f"Different number of choices: {len(test_q['choices'])} vs {len(sol_q['choices'])}")
    
    # Compare choices
    for letter in ['A', 'B', 'C', 'D']:
        if letter in test_q["choices"] and letter in sol_q["choices"]:
            test_choice = test_q["choices"][letter]
            sol_choice = sol_q["choices"][letter]
            choice_similarity = SequenceMatcher(None, test_choice, sol_choice).ratio()
            if choice_similarity < 0.9:
                issues.append(f"Choice {letter} differs: '{test_choice}' vs '{sol_choice}'")
        elif letter in test_q["choices"] or letter in sol_q["choices"]:
            issues.append(f"Choice {letter} missing in one file")
    
    # Check if solution has correct answer marked
    if not sol_q.get("correct_answer"):
        issues.append("No correct answer marked in solution")
    
    return issues

def analyze_pair(test_file: str, solution_file: str) -> Dict:
    """Analyze a test-solution file pair."""
    
    # Read files
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_content = f.read()
    except Exception as e:
        return {"error": f"Cannot read test file: {e}"}
    
    try:
        with open(solution_file, 'r', encoding='utf-8') as f:
            solution_content = f.read()
    except Exception as e:
        return {"error": f"Cannot read solution file: {e}"}
    
    # Extract questions
    test_questions = extract_questions_detailed(test_content)
    solution_questions = extract_solutions_detailed(solution_content)
    
    # Check navigation links
    forward_link = re.search(r'\[.*?View Test Solutions.*?\]\(([^)]+)\)', test_content, re.IGNORECASE)
    back_link_patterns = [
        re.search(r'← \[.*?\]\(([^)]+)\)', solution_content),
        re.search(r'\[.*?←.*?\]\(([^)]+)\)', solution_content),
        re.search(r'\[.*?Back to.*?\]\(([^)]+)\)', solution_content, re.IGNORECASE)
    ]
    back_link = None
    for pattern in back_link_patterns:
        if pattern:
            back_link = pattern
            break
    
    # Analyze consistency
    all_issues = []
    
    # Basic counts
    if len(test_questions) != len(solution_questions):
        all_issues.append(f"Question count mismatch: {len(test_questions)} test vs {len(solution_questions)} solution")
    
    # Compare each question
    question_issues = {}
    for i, (test_q, sol_q) in enumerate(zip(test_questions, solution_questions)):
        q_issues = compare_questions(test_q, sol_q)
        if q_issues:
            question_issues[f"Question {test_q['number']}"] = q_issues
            all_issues.extend([f"Q{test_q['number']}: {issue}" for issue in q_issues])
    
    # Check navigation
    if not forward_link:
        all_issues.append("Missing forward navigation link (test → solution)")
    
    if not back_link:
        all_issues.append("Missing back navigation link (solution → test)")
    
    return {
        "test_file": test_file,
        "solution_file": solution_file,
        "test_question_count": len(test_questions),
        "solution_question_count": len(solution_questions),
        "has_forward_link": bool(forward_link),
        "has_back_link": bool(back_link),
        "forward_link_target": forward_link.group(1) if forward_link else None,
        "back_link_target": back_link.group(1) if back_link else None,
        "all_issues": all_issues,
        "question_issues": question_issues,
        "test_questions": test_questions,
        "solution_questions": solution_questions
    }

def main():
    """Main analysis function."""
    
    # Known test-solution pairs (manually identified)
    pairs = [
        # Module 1 - Agent Frameworks
        ("docs-content/01_frameworks/Session0_ModuleA_Historical_Context_Evolution.md", 
         "docs-content/01_frameworks/Session0_ModuleA_Test_Solutions.md"),
        ("docs-content/01_frameworks/Session0_ModuleB_Advanced_Pattern_Theory.md", 
         "docs-content/01_frameworks/Session0_ModuleB_Test_Solutions.md"),
        
        # Add more pairs as we discover them
    ]
    
    # Auto-discover pairs by looking for solution files and finding their test counterparts
    docs_dir = Path("/Users/q284340/Agentic/nano-degree/docs-content")
    solution_files = list(docs_dir.rglob("*Test_Solutions.md"))
    
    auto_pairs = []
    for sol_file in solution_files:
        # Try to find corresponding test file
        base_name = sol_file.stem.replace("_Test_Solutions", "")
        parent_dir = sol_file.parent
        
        # Look for files with this base name
        candidates = list(parent_dir.glob(f"{base_name}*.md"))
        candidates = [c for c in candidates if "Test_Solutions" not in c.name]
        
        if candidates:
            # Take the first candidate (usually the main file)
            auto_pairs.append((str(candidates[0]), str(sol_file)))
    
    all_pairs = pairs + auto_pairs
    
    print(f"Found {len(all_pairs)} test-solution pairs to analyze")
    
    # Analyze each pair
    results = []
    for test_file, solution_file in all_pairs:
        print(f"Analyzing: {Path(test_file).name} ↔ {Path(solution_file).name}")
        
        full_test_path = f"/Users/q284340/Agentic/nano-degree/{test_file}" if not test_file.startswith("/") else test_file
        full_solution_path = f"/Users/q284340/Agentic/nano-degree/{solution_file}" if not solution_file.startswith("/") else solution_file
        
        if os.path.exists(full_test_path) and os.path.exists(full_solution_path):
            result = analyze_pair(full_test_path, full_solution_path)
            results.append(result)
        else:
            results.append({
                "test_file": test_file,
                "solution_file": solution_file,
                "all_issues": ["One or both files not found"],
                "error": f"Files not found: test={os.path.exists(full_test_path)}, solution={os.path.exists(full_solution_path)}"
            })
    
    # Save results
    with open("/Users/q284340/Agentic/nano-degree/detailed_qa_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate summary report
    total_pairs = len(results)
    pairs_with_issues = sum(1 for r in results if r.get("all_issues", []))
    
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE QA ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Total test-solution pairs: {total_pairs}")
    print(f"Pairs with issues: {pairs_with_issues}")
    print(f"Clean pairs: {total_pairs - pairs_with_issues}")
    print(f"Success rate: {((total_pairs - pairs_with_issues) / total_pairs * 100):.1f}%")
    
    print(f"\n{'='*60}")
    print(f"DETAILED ISSUES BY PAIR")
    print(f"{'='*60}")
    
    for result in results:
        if result.get("all_issues", []):
            test_name = Path(result["test_file"]).name
            solution_name = Path(result["solution_file"]).name
            print(f"\n{test_name} ↔ {solution_name}")
            print(f"Questions: {result.get('test_question_count', 'N/A')} test, {result.get('solution_question_count', 'N/A')} solution")
            print(f"Navigation: Forward={result.get('has_forward_link', False)}, Back={result.get('has_back_link', False)}")
            for issue in result["all_issues"]:
                print(f"  ❌ {issue}")
    
    print(f"\n{'='*60}")
    print(f"NAVIGATION LINK ANALYSIS")
    print(f"{'='*60}")
    
    forward_missing = sum(1 for r in results if not r.get("has_forward_link", True))
    back_missing = sum(1 for r in results if not r.get("has_back_link", True))
    
    print(f"Missing forward links (test → solution): {forward_missing}")
    print(f"Missing back links (solution → test): {back_missing}")

if __name__ == "__main__":
    main()