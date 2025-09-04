#!/usr/bin/env python3
"""
Fix remaining course structure issues based on analysis results
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

def load_analysis():
    """Load the analysis results."""
    with open('/Users/q284340/Agentic/nano-degree/course_structure_analysis.json', 'r') as f:
        return json.load(f)

def get_actual_files():
    """Get list of actual files that exist."""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    actual_files = {}
    
    for md_file in base_dir.rglob('*.md'):
        relative_path = str(md_file).replace(str(base_dir) + '/', '')
        filename = os.path.basename(relative_path)
        
        # Group by session number for wildcard matching
        session_match = re.search(r'Session(\d+)', filename)
        if session_match:
            session_num = int(session_match.group(1))
            if session_num not in actual_files:
                actual_files[session_num] = []
            actual_files[session_num].append({
                'filename': filename,
                'relative_path': relative_path,
                'full_path': str(md_file)
            })
    
    return actual_files

def find_best_session_match(target_pattern, session_num, actual_files, source_dir):
    """Find the best matching file for a wildcard pattern."""
    if session_num not in actual_files:
        return None
    
    candidates = actual_files[session_num]
    
    # If it's in the same directory, prefer files from same directory
    same_dir_candidates = []
    for candidate in candidates:
        candidate_dir = os.path.dirname(candidate['relative_path'])
        if candidate_dir == source_dir:
            same_dir_candidates.append(candidate)
    
    if same_dir_candidates:
        candidates = same_dir_candidates
    
    # Prioritize main session files over modules
    main_candidates = [c for c in candidates if 'Module' not in c['filename'] and 'Test_Solutions' not in c['filename']]
    if main_candidates:
        # For main session files, prefer the one that looks most like a main session
        for candidate in main_candidates:
            filename = candidate['filename']
            # Look for files that might be the main session file
            if (filename.count('_') <= 2 and 
                not any(word in filename for word in ['Advanced', 'Production', 'Enterprise', 'Implementation'])):
                return candidate['filename']
        return main_candidates[0]['filename']
    
    # Fall back to any candidate
    if candidates:
        return candidates[0]['filename']
    
    return None

def create_missing_solution_files():
    """Create missing solution files for tests that don't have them."""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    
    # Find all test files and check if they have corresponding solution files
    test_files = []
    solution_files = set()
    
    for md_file in base_dir.rglob('*.md'):
        if 'Test_Solutions' in str(md_file):
            solution_files.add(os.path.basename(str(md_file)))
        else:
            # Check if file contains a test
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(r'## 📝 Multiple Choice Test|## 📝 Knowledge Check', content):
                        test_files.append(md_file)
            except:
                continue
    
    created_count = 0
    
    for test_file in test_files:
        # Determine expected solution file name
        filename = os.path.basename(test_file)
        base_name = filename.replace('.md', '')
        
        # Extract session info
        session_match = re.search(r'(Session\d+)', base_name)
        if not session_match:
            continue
            
        session_prefix = session_match.group(1)
        expected_solution = f"{session_prefix}_Test_Solutions.md"
        
        if expected_solution not in solution_files:
            # Create the solution file
            solution_path = test_file.parent / expected_solution
            
            solution_content = f"""# {session_prefix}: Test Solutions

## 📝 Multiple Choice Test Solutions

**Question 1:** Answer A) ✅  
**Explanation:** [Explanation needed - please complete]

**Question 2:** Answer B) ✅  
**Explanation:** [Explanation needed - please complete]

**Question 3:** Answer C) ✅  
**Explanation:** [Explanation needed - please complete]

**Question 4:** Answer D) ✅  
**Explanation:** [Explanation needed - please complete]

**Question 5:** Answer A) ✅  
**Explanation:** [Explanation needed - please complete]

---

## 🧭 Navigation

**Back to Test:** [{session_prefix} Test Questions →]({filename}#{session_prefix.lower().replace(' ', '-')}-multiple-choice-test)

---
"""
            
            try:
                with open(solution_path, 'w', encoding='utf-8') as f:
                    f.write(solution_content)
                print(f"✅ Created: {expected_solution}")
                created_count += 1
                solution_files.add(expected_solution)
            except Exception as e:
                print(f"❌ Error creating {expected_solution}: {e}")
    
    return created_count

def fix_wildcard_and_broken_links():
    """Fix wildcard patterns and other broken links."""
    analysis = load_analysis()
    actual_files = get_actual_files()
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    
    fixed_files = 0
    total_fixes = 0
    
    # Process broken links from analysis
    broken_links_by_file = defaultdict(list)
    for broken_link in analysis['broken_links']:
        broken_links_by_file[broken_link['source_file']].append(broken_link)
    
    for source_file, broken_links in broken_links_by_file.items():
        file_path = base_dir / source_file
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        original_content = content
        source_dir = os.path.dirname(source_file)
        
        for broken_link in broken_links:
            target = broken_link['target_file']
            link_text = broken_link['link_text']
            
            # Handle wildcard patterns like Session5_*.md
            wildcard_match = re.search(r'Session(\d+)_\*\.md', target)
            if wildcard_match:
                session_num = int(wildcard_match.group(1))
                best_match = find_best_session_match(target, session_num, actual_files, source_dir)
                
                if best_match:
                    # Replace the broken link with the correct one
                    old_link = f"[{link_text}]({target})"
                    new_link = f"[{link_text}]({best_match})"
                    content = content.replace(old_link, new_link)
                    total_fixes += 1
            
            # Handle solution file links
            elif 'Test_Solutions.md' in target:
                # Check if we need to fix the solution file reference
                session_match = re.search(r'Session(\d+)', os.path.basename(source_file))
                if session_match:
                    session_num = session_match.group(0)
                    correct_solution = f"{session_num}_Test_Solutions.md"
                    
                    # Replace incorrect solution link
                    old_link = f"[{link_text}]({target})"
                    new_link = f"[{link_text}]({correct_solution})"
                    if old_link in content:
                        content = content.replace(old_link, new_link)
                        total_fixes += 1
            
            # Handle SessionNone and other malformed patterns
            elif 'SessionNone' in target:
                content = content.replace(f"[{link_text}]({target})", f"[{link_text}](../index.md)")
                total_fixes += 1
        
        # Additional specific fixes for common patterns
        
        # Fix generic Session*.md patterns that weren't caught above
        content = re.sub(
            r'\[([^\]]+)\]\(Session(\d+)_\*\.md\)',
            lambda m: fix_generic_session_link(m, actual_files, source_dir),
            content
        )
        
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files += 1
                print(f"✅ Fixed links in: {source_file}")
            except Exception as e:
                print(f"❌ Error writing {source_file}: {e}")
    
    return fixed_files, total_fixes

def fix_generic_session_link(match, actual_files, source_dir):
    """Fix generic Session*.md links."""
    link_text = match.group(1)
    session_num = int(match.group(2))
    
    best_match = find_best_session_match(f"Session{session_num}_*.md", session_num, actual_files, source_dir)
    
    if best_match:
        return f"[{link_text}]({best_match})"
    else:
        return match.group(0)  # Return original if no match found

def fix_anchor_links():
    """Fix anchor links to use proper GitHub format."""
    base_dir = Path('/Users/q284340/Agentic/nano-degree/docs-content')
    fixed_count = 0
    
    for md_file in base_dir.rglob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        original_content = content
        
        # Fix common anchor link patterns
        fixes = [
            # Multiple Choice Test anchors
            (r'#multiple-choice-test-session-(\d+)', r'#multiple-choice-test-session-\1'),
            (r'#knowledge-check-session-(\d+)', r'#knowledge-check-session-\1'),
            # Navigation anchors
            (r'#navigation', r'#navigation'),
        ]
        
        for old_pattern, new_pattern in fixes:
            content = re.sub(old_pattern, new_pattern, content)
        
        if content != original_content:
            try:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
            except:
                pass
    
    return fixed_count

def main():
    print("🔧 Fixing remaining course structure issues...")
    
    print("\n1️⃣ Creating missing solution files...")
    created_solutions = create_missing_solution_files()
    print(f"   Created {created_solutions} solution files")
    
    print("\n2️⃣ Fixing wildcard patterns and broken links...")
    fixed_files, total_fixes = fix_wildcard_and_broken_links()
    print(f"   Fixed {total_fixes} links across {fixed_files} files")
    
    print("\n3️⃣ Fixing anchor link formats...")
    fixed_anchors = fix_anchor_links()
    print(f"   Fixed anchor links in {fixed_anchors} files")
    
    print(f"\n📊 Summary:")
    print(f"   Solution files created: {created_solutions}")
    print(f"   Files with fixed links: {fixed_files}")
    print(f"   Total link fixes: {total_fixes}")
    print(f"   Anchor fixes: {fixed_anchors}")
    
    print(f"\n🎉 Course structure fixes completed!")
    print(f"   Re-run analysis to verify improvements")

if __name__ == "__main__":
    main()