#!/usr/bin/env python3
"""
Navigation Standardization Script for Nano-degree Course Materials

This script applies consistent navigation standards across all .md files in the docs-content/ directory.
It handles main sessions, modules, test solutions, and index files with proper linking.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Session sequences for each module
MODULE_SESSIONS = {
    "01_frameworks": {
        "primary_sessions": [
            "Session0_Introduction_to_Agent_Frameworks_Patterns",
            "Session1_Bare_Metal_Agents", 
            "Session2_LangChain_Foundations",
            "Session3_LangGraph_Multi_Agent_Workflows",
            "Session4_CrewAI_Fundamentals",
            "Session5_PydanticAI_Type_Safe_Agents",
            "Session6_Atomic_Agents_Modular_Architecture",
            "Session7_First_ADK_Agent",
            "Session8_Agno_Production_Ready_Agents",
            "Session9_Multi_Agent_Patterns",
            "Session10_Enterprise_Integration_Production_Deployment"
        ]
    },
    "02_rag": {
        "primary_sessions": [
            "Session0_Introduction_to_RAG_Architecture",
            "Session1_Basic_RAG_Implementation",
            "Session2_Advanced_Chunking_Preprocessing",
            "Session3_Vector_Databases_Search_Optimization",
            "Session4_Query_Enhancement_Context_Augmentation",
            "Session5_RAG_Evaluation_Quality_Assessment",
            "Session6_Graph_Based_RAG",
            "Session7_Agentic_RAG_Systems",
            "Session8_MultiModal_Advanced_RAG",
            "Session9_Production_RAG_Enterprise_Integration"
        ]
    },
    "03_mcp-acp-a2a": {
        "primary_sessions": [
            "Session0_Introduction_to_MCP_ACP_A2A",
            "Session1_Basic_MCP_Server",
            "Session2_FileSystem_MCP_Server",
            "Session3_LangChain_MCP_Integration",
            "Session4_Production_MCP_Deployment",
            "Session5_Secure_MCP_Server",
            "Session6_ACP_Fundamentals",
            "Session7_Agent_to_Agent_Communication",
            "Session8_Advanced_Agent_Workflows",
            "Session9_Production_Agent_Deployment"
        ]
    }
}

def get_session_title(filename: str) -> str:
    """Extract a readable title from the filename."""
    # Remove .md extension and replace underscores with spaces
    title = filename.replace('.md', '').replace('_', ' ')
    return title

def find_session_modules(directory: Path, session_prefix: str) -> List[str]:
    """Find all module files for a given session."""
    modules = []
    pattern = f"{session_prefix}_Module[A-Z]_*.md"
    for file in directory.glob(pattern):
        modules.append(file.name)
    return sorted(modules)

def has_test_solutions(directory: Path, session_prefix: str) -> bool:
    """Check if test solutions exist for a session."""
    test_file = directory / f"{session_prefix}_Test_Solutions.md"
    return test_file.exists()

def extract_existing_navigation(content: str) -> Tuple[str, str]:
    """Extract existing navigation section to preserve any custom content."""
    # Find navigation section
    nav_pattern = r'(---\s*\n\n## 🧭 Navigation.*?)(\n---\s*$|\Z)'
    match = re.search(nav_pattern, content, re.DOTALL | re.MULTILINE)
    
    if match:
        # Return content before navigation and content after
        before_nav = content[:match.start()]
        after_nav = content[match.end():]
        return before_nav.rstrip(), after_nav.lstrip()
    else:
        # Look for old navigation patterns to replace
        old_patterns = [
            r'(---\s*\n\n## Navigation.*?)(\n---\s*$|\Z)',
            r'(\n## Navigation.*?)(\n---\s*$|\Z)',
            r'(\n\*\*Previous:\*\*.*?\*\*Next:\*\*.*?)(\n\n|\Z)'
        ]
        
        for pattern in old_patterns:
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            if match:
                before_nav = content[:match.start()]
                after_nav = content[match.end():]
                return before_nav.rstrip(), after_nav.lstrip()
    
    return content.rstrip(), ""

def create_navigation_section(
    session_info: dict,
    modules: List[str],
    has_tests: bool,
    is_first: bool = False,
    is_last: bool = False
) -> str:
    """Create the standardized navigation section."""
    
    nav_lines = ["---", "", "## 🧭 Navigation", ""]
    
    # Previous/Next links
    if not is_first and session_info.get('previous'):
        prev_title = get_session_title(session_info['previous'])
        nav_lines.append(f"**Previous:** [{prev_title} ←]({session_info['previous']}.md)")
    
    if not is_last and session_info.get('next'):
        next_title = get_session_title(session_info['next'])
        nav_lines.append(f"**Next:** [{next_title} →]({session_info['next']}.md)")
    
    if nav_lines[-1] != "":
        nav_lines.append("")
    
    # Advanced modules section
    if modules:
        nav_lines.append("### Advanced Modules")
        for module in modules:
            module_title = get_session_title(module)
            # Clean up the title a bit more
            module_title = module_title.replace('Session', 'Module').replace('Module A', 'Module A:').replace('Module B', 'Module B:').replace('Module C', 'Module C:').replace('Module D', 'Module D:')
            nav_lines.append(f"- ⚙️ [{module_title}]({module})")
        nav_lines.append("")
    
    # Test solutions section  
    if has_tests:
        session_prefix = session_info['current'].split('_')[0]  # e.g., Session1
        nav_lines.append("### Test Solutions")
        nav_lines.append(f"[🗂️ **View Test Solutions →**]({session_prefix}_Test_Solutions.md)")
        nav_lines.append("")
    
    nav_lines.append("---")
    
    return "\n".join(nav_lines)

def process_file(file_path: Path, module_config: dict) -> bool:
    """Process a single markdown file to standardize navigation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file type and get session info
        filename = file_path.stem
        
        # Skip certain files
        if filename in ['index', 'README'] or 'BACKUP' in filename or 'ORIGINAL' in filename:
            return False
            
        # Extract session prefix (e.g., Session1)
        session_match = re.match(r'(Session\d+)', filename)
        if not session_match:
            return False
            
        session_prefix = session_match.group(1)
        
        # Find position in primary sessions
        primary_sessions = module_config['primary_sessions']
        session_index = None
        for i, session in enumerate(primary_sessions):
            if session.startswith(session_prefix):
                session_index = i
                break
        
        if session_index is None:
            return False
            
        # Build session info
        session_info = {
            'current': filename,
            'previous': primary_sessions[session_index - 1] if session_index > 0 else None,
            'next': primary_sessions[session_index + 1] if session_index < len(primary_sessions) - 1 else None
        }
        
        # Find modules and test solutions
        modules = find_session_modules(file_path.parent, session_prefix)
        has_tests = has_test_solutions(file_path.parent, session_prefix)
        
        # Skip if this is a module or test solutions file
        if '_Module' in filename or '_Test_Solutions' in filename:
            return False
            
        # Extract content without navigation
        content_before_nav, content_after_nav = extract_existing_navigation(content)
        
        # Create new navigation
        is_first = session_index == 0
        is_last = session_index == len(primary_sessions) - 1
        
        nav_section = create_navigation_section(
            session_info, modules, has_tests, is_first, is_last
        )
        
        # Combine content
        new_content = content_before_nav + "\n\n" + nav_section
        if content_after_nav:
            new_content += "\n\n" + content_after_nav
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all markdown files."""
    base_dir = Path("/Users/q284340/Agentic/nano-degree/docs-content")
    
    processed_count = 0
    
    for module_name, config in MODULE_SESSIONS.items():
        module_dir = base_dir / module_name
        if not module_dir.exists():
            print(f"Module directory {module_dir} not found, skipping...")
            continue
            
        print(f"Processing module: {module_name}")
        
        # Find all main session markdown files
        for file_path in module_dir.glob("Session*.md"):
            if process_file(file_path, config):
                processed_count += 1
                print(f"  Updated: {file_path.name}")
    
    print(f"\nProcessed {processed_count} files total.")

if __name__ == "__main__":
    main()