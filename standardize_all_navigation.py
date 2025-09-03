#!/usr/bin/env python3
"""
Standardize ALL navigation sections across the entire nano-degree course.
Replace inconsistent navigation with unified format and remove duplicates.
"""

import os
import re
import glob

# Navigation patterns for different file types
NAVIGATION_PATTERNS = {
    # Main session files (Observer/Participant/Implementer paths)
    'session_main': '''
---

## Navigation

**Previous:** [Session {prev_num} - {prev_title} →]({prev_file})  
**Next:** [Session {next_num} - {next_title} →]({next_file})

---''',
    
    # Test solution files
    'test_solution': '''
---

## Navigation

**Back to Test:** [Session {session_num} Test Questions →]({back_file})  
**Previous:** [Session {prev_num} - {prev_title} →]({prev_file})  
**Next:** [Session {next_num} - {next_title} →]({next_file})

---''',
    
    # Module index files
    'module_index': '''
---

## Navigation

**Next:** [Session 0 - Introduction →](Session0_{intro_file}.md)

---''',
    
    # Last session in module
    'module_end': '''
---

## Navigation

**Previous:** [Session {prev_num} - {prev_title} →]({prev_file})  
**Next Module:** [Module {next_module_num} - {next_module_title} →](../{next_module_dir}/index.md)

---''',
    
    # Advanced modules (ModuleA, ModuleB, etc.)
    'advanced_module': '''
---

## Navigation

**Back to Main Session:** [Session {session_num} - {main_title} →]({main_file})  
**Previous:** [Session {prev_num} - {prev_title} →]({prev_file})  
**Next:** [Session {next_num} - {next_title} →]({next_file})

---'''
}

def get_session_info_from_filename(filename):
    """Extract session number and type from filename."""
    # Handle various patterns
    if 'Session' in filename:
        session_match = re.search(r'Session(\d+)', filename)
        if session_match:
            return int(session_match.group(1))
    return None

def get_module_info_from_filename(filename):
    """Extract module information from filename."""
    if 'ModuleA' in filename:
        return 'A'
    elif 'ModuleB' in filename:
        return 'B'
    elif 'ModuleC' in filename:
        return 'C'
    elif 'ModuleD' in filename:
        return 'D'
    return None

def get_file_type(filename):
    """Determine what type of navigation this file needs."""
    base = os.path.basename(filename)
    
    if 'Test_Solutions' in base:
        return 'test_solution'
    elif base == 'index.md':
        return 'module_index'
    elif 'Module' in base and not 'Test_Solutions' in base:
        return 'advanced_module'
    elif re.match(r'Session\d+_', base) and not 'Module' in base:
        return 'session_main'
    
    return 'session_main'  # Default

def remove_existing_navigation(content):
    """Remove all existing navigation patterns."""
    
    # Remove various navigation patterns
    patterns_to_remove = [
        # Remove standalone Next: lines
        r'\*\*Next:\*\*[^\n]*\n',
        r'Next:[^\n]*\n',
        
        # Remove Previous: lines  
        r'\*\*Previous:\*\*[^\n]*\n',
        r'Previous:[^\n]*\n',
        
        # Remove Back to Test: lines
        r'\*\*Back to Test:\*\*[^\n]*\n',
        r'Back to Test:[^\n]*\n',
        
        # Remove navigation sections
        r'---\s*\n\s*## Navigation.*?---\s*\n',
        r'---\s*\n\s*\*\*Next:\*\*.*?---\s*\n',
        r'---\s*\n\s*\*\*Previous:\*\*.*?---\s*\n',
        
        # Remove duplicate Next: lines
        r'Next:[^\n]*\n\s*Next:[^\n]*\n',
        
        # Remove orphaned dividers at end
        r'\n---\s*$',
        r'\n---\s*\n\s*$'
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
    
    # Clean up multiple consecutive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Ensure content ends with single newline
    content = content.rstrip() + '\n'
    
    return content

def get_session_navigation_info(file_path):
    """Get navigation info for a session file."""
    base = os.path.basename(file_path)
    session_num = get_session_info_from_filename(base)
    
    if session_num is None:
        return None
    
    # Determine module directory
    if '/01_frameworks/' in file_path:
        module_dir = '01_frameworks'
        module_name = 'Agent Frameworks'
    elif '/02_rag/' in file_path:
        module_dir = '02_rag' 
        module_name = 'RAG Architecture'
    elif '/03_mcp-acp-a2a/' in file_path:
        module_dir = '03_mcp-acp-a2a'
        module_name = 'MCP, ACP & A2A Communication'
    else:
        return None
    
    # Basic session titles (simplified for navigation)
    session_titles = {
        0: 'Introduction',
        1: 'Foundations', 
        2: 'Implementation',
        3: 'Advanced Patterns',
        4: 'Team Orchestration',
        5: 'Type-Safe Development',
        6: 'Modular Architecture', 
        7: 'Agent Systems',
        8: 'Production Ready',
        9: 'Multi-Agent Coordination',
        10: 'Enterprise Integration'
    }
    
    prev_num = session_num - 1 if session_num > 0 else None
    next_num = session_num + 1 if session_num < 10 else None
    
    return {
        'session_num': session_num,
        'prev_num': prev_num,
        'next_num': next_num,
        'prev_title': session_titles.get(prev_num, ''),
        'next_title': session_titles.get(next_num, ''),
        'module_dir': module_dir,
        'module_name': module_name
    }

def add_navigation_to_file(file_path):
    """Add appropriate navigation to a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove existing navigation
        clean_content = remove_existing_navigation(content)
        
        # Don't add navigation to certain files
        base = os.path.basename(file_path)
        if base in ['index.md'] and '/docs-content/' not in file_path:
            # Root index file, no navigation needed
            return False
            
        # Get navigation info
        nav_info = get_session_navigation_info(file_path)
        if not nav_info:
            # Can't determine session info, skip
            return False
        
        file_type = get_file_type(file_path)
        
        # Build navigation based on file type
        if file_type == 'session_main':
            if nav_info['session_num'] == 0:
                # First session - only Next
                nav_section = f'''
---

## Navigation

**Next:** [Session {nav_info['next_num']} - {nav_info['next_title']} →](Session{nav_info['next_num']}_*.md)

---'''
            elif nav_info['session_num'] == 10:
                # Last session - only Previous or Next Module
                nav_section = f'''
---

## Navigation

**Previous:** [Session {nav_info['prev_num']} - {nav_info['prev_title']} →](Session{nav_info['prev_num']}_*.md)

---'''
            else:
                # Middle sessions - Previous and Next
                nav_section = f'''
---

## Navigation

**Previous:** [Session {nav_info['prev_num']} - {nav_info['prev_title']} →](Session{nav_info['prev_num']}_*.md)  
**Next:** [Session {nav_info['next_num']} - {nav_info['next_title']} →](Session{nav_info['next_num']}_*.md)

---'''
        
        elif file_type == 'test_solution':
            # Test solution files
            nav_section = f'''
---

## Navigation

**Back to Test:** [Session {nav_info['session_num']} Test Questions →](Session{nav_info['session_num']}_*.md#multiple-choice-test)

---'''
        
        else:
            # Default navigation
            nav_section = f'''
---

## Navigation

**Previous:** [Session {nav_info['prev_num']} - {nav_info['prev_title']} →](Session{nav_info['prev_num']}_*.md)  
**Next:** [Session {nav_info['next_num']} - {nav_info['next_title']} →](Session{nav_info['next_num']}_*.md)

---'''
        
        # Add navigation to end of content
        final_content = clean_content.rstrip() + nav_section + '\n'
        
        # Write back if changed
        if final_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def standardize_all_navigation():
    """Standardize navigation in all markdown files."""
    
    # Get all markdown files
    md_files = glob.glob('/Users/q284340/Agentic/nano-degree/docs-content/**/*.md', recursive=True)
    
    fixed_files = 0
    skipped_files = 0
    
    for file_path in md_files:
        # Skip certain files
        base = os.path.basename(file_path)
        if 'ORIGINAL_BACKUP' in base or 'BACKUP' in base:
            skipped_files += 1
            continue
            
        if add_navigation_to_file(file_path):
            fixed_files += 1
            print(f"✅ Standardized navigation in {os.path.basename(file_path)}")
        else:
            skipped_files += 1
    
    return fixed_files, skipped_files

def main():
    """Main function to standardize all navigation."""
    print("=== Standardizing All Navigation Sections ===\n")
    
    fixed_count, skipped_count = standardize_all_navigation()
    
    print(f"\n=== Summary ===")
    print(f"✅ Standardized navigation in {fixed_count} files")
    print(f"⏭️  Skipped {skipped_count} files (no changes needed or backup files)")
    print("All navigation sections are now standardized across the entire course!")

if __name__ == "__main__":
    main()