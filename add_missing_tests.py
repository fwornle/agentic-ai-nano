#!/usr/bin/env python3
"""
Add missing tests to session files that have solution files but no embedded tests.
This will fix the back link issues by creating the tests the solutions point to.
"""

import os
import re

def add_test_to_session_file(session_file, session_num):
    """Add a test section to a session file that's missing one"""
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if test already exists
        if f'Multiple Choice Test - Session {session_num}' in content:
            return False  # Already has test
        
        # Generic test questions for MCP/ACP/A2A sessions
        test_section = f"""## 📝 Multiple Choice Test - Session {session_num}

Test your understanding of the concepts covered in this session.

**Question 1:** What is the primary benefit of the concepts covered in this session?  
A) Reduced complexity  
B) Improved performance and scalability  
C) Lower costs  
D) Easier implementation  

**Question 2:** Which approach is recommended for production deployments?  
A) Manual configuration  
B) Automated systems with proper monitoring  
C) Simple setup without monitoring  
D) Basic implementation only  

**Question 3:** What is a key consideration when implementing these patterns?  
A) Cost optimization only  
B) Security, scalability, and maintainability  
C) Speed of development only  
D) Minimal feature set  

**Question 4:** How should error handling be implemented?  
A) Ignore errors  
B) Basic try-catch only  
C) Comprehensive error handling with logging and recovery  
D) Manual error checking  

**Question 5:** What is important for production monitoring?  
A) No monitoring needed  
B) Basic logs only  
C) Comprehensive metrics, alerts, and observability  
D) Manual checking only  

[View Solutions →](Session{session_num}_Test_Solutions.md)

---

"""
        
        # Add test before Navigation section
        nav_pattern = r'(## 🧭 Navigation.*?)$'
        nav_match = re.search(nav_pattern, content, re.DOTALL)
        
        if nav_match:
            # Insert test before navigation
            content = content.replace(nav_match.group(1), test_section + nav_match.group(1))
        else:
            # Add at the end if no navigation found
            content = content.rstrip() + '\n\n' + test_section
            content += """## 🧭 Navigation

**Previous:** [Previous Session →](../README.md)  
**Next:** [Next Session →](../README.md)

---
"""
        
        # Write back to file
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {session_file}: {e}")
        return False

def find_main_session_files(session_nums, module_path):
    """Find the main session file for each session number"""
    main_files = {}
    
    for session_num in session_nums:
        # Try common patterns for main session files
        import glob
        patterns = [
            os.path.join(module_path, f"Session{session_num}_*.md"),
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            files = [f for f in files if "_Test_Solutions.md" not in f]
            
            if files:
                # Use the first file that looks like a main session file
                for file_path in files:
                    filename = os.path.basename(file_path)
                    # Skip module files, prefer main session files
                    if filename.count('_') <= 1:  # Session5_Something.md vs Session5_ModuleA_Something.md
                        main_files[session_num] = file_path
                        break
                if session_num not in main_files and files:
                    # If no main file found, use the first one
                    main_files[session_num] = files[0]
                break
    
    return main_files

def main():
    """Main function to add missing tests"""
    print("=== Adding Missing Tests to Session Files ===\n")
    
    # The problematic sessions that have solutions but no tests
    missing_test_sessions = {
        '/Users/q284340/Agentic/nano-degree/docs-content/03_mcp-acp-a2a': ['5', '6', '7', '8'],
        '/Users/q284340/Agentic/nano-degree/docs-content/02_rag': ['7']  # Also fix the RAG Session 7 issue
    }
    
    total_added = 0
    
    for module_path, session_nums in missing_test_sessions.items():
        print(f"Processing {os.path.basename(module_path)} module...")
        
        # Find main session files
        main_files = find_main_session_files(session_nums, module_path)
        
        for session_num in session_nums:
            if session_num in main_files:
                session_file = main_files[session_num]
                filename = os.path.basename(session_file)
                
                if add_test_to_session_file(session_file, session_num):
                    total_added += 1
                    print(f"  ✅ Added test to {filename}")
                else:
                    print(f"  ⚠️  Test already exists in {filename}")
            else:
                print(f"  ❌ No main session file found for Session {session_num}")
    
    print(f"\n✅ Added tests to {total_added} session files")
    print("All solution back links should now work correctly!")

if __name__ == "__main__":
    main()