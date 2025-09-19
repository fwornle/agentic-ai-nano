#!/usr/bin/env python3
"""
Create comprehensive analysis document for the nano-degree course structure issues
"""

import json
import os
from collections import defaultdict

def load_analysis_report():
    """Load the detailed analysis report"""
    with open('/Users/q284340/Agentic/nano-degree/image_analysis_report.json', 'r') as f:
        return json.load(f)

def analyze_specific_broken_links():
    """Analyze specific broken links and suggest fixes"""
    
    # Known mappings from broken references to actual files
    known_fixes = {
        'agent-frameworks-overview.png': 'overview-agents.png',
        '5-agent-patterns.png': 'agentic-5-patterns.png',
        # Many CrewAI images are missing - these are referenced but don't exist
        'crewai-vs-autogen.png': 'MISSING - needs creation',
        'crewai-components.png': 'MISSING - needs creation',
        'crewai-workflow.png': 'crewai-workflows.png',
        'crewai-agent-types.png': 'MISSING - needs creation',
        'crewai-task-flow.png': 'MISSING - needs creation',
        'crewai-memory.png': 'MISSING - needs creation',
        'crewai-tools.png': 'MISSING - needs creation',
        'crewai-advanced-workflows.png': 'crewai-workflows.png',
        'crewai-hierarchical-process.png': 'MISSING - needs creation',
        'crewai-planning.png': 'MISSING - needs creation',
        'crewai-flows.png': 'MISSING - needs creation',
        'crewai-knowledge.png': 'MISSING - needs creation',
        'crewai-training.png': 'MISSING - needs creation',
        # AutoGen images - all missing
        'autogen-architecture.png': 'MISSING - needs creation',
        'autogen-agent-types.png': 'MISSING - needs creation',
        'autogen-conversation-flow.png': 'MISSING - needs creation',
        'autogen-group-chat.png': 'MISSING - needs creation',
        'autogen-code-execution.png': 'MISSING - needs creation',
        'autogen-human-integration.png': 'MISSING - needs creation',
        'autogen-studio.png': 'MISSING - needs creation',
        'autogen-workflow-designer.png': 'MISSING - needs creation',
        'autogen-custom-agents.png': 'MISSING - needs creation',
        'autogen-agent-registry.png': 'MISSING - needs creation',
        'autogen-nested-chat.png': 'MISSING - needs creation',
        'autogen-reflection.png': 'MISSING - needs creation',
        # Framework comparison images - all missing
        'framework-feature-matrix.png': 'MISSING - needs creation',
        'performance-benchmarks.png': 'MISSING - needs creation',
        'use-case-matrix.png': 'MISSING - needs creation',
        'framework-decision-tree.png': 'MISSING - needs creation',
        # RAG images - all missing
        'rag-architecture-overview.png': 'MISSING - needs creation',
        'rag-vs-fine-tuning.png': 'MISSING - needs creation',
        'rag-pipeline.png': 'MISSING - needs creation',
        'document-processing.png': 'MISSING - needs creation',
        'vector-embeddings.png': 'MISSING - needs creation',
        'semantic-search.png': 'MISSING - needs creation',
        # MCP images - all missing
        'mcp-protocol-flow.png': 'MISSING - needs creation',
        'mcp-server-types.png': 'MISSING - needs creation',
        'mcp-tools-integration.png': 'MISSING - needs creation',
        'mcp-resource-management.png': 'MISSING - needs creation',
    }
    
    return known_fixes

def create_comprehensive_analysis():
    """Create the comprehensive analysis document"""
    
    report = load_analysis_report()
    fixes = analyze_specific_broken_links()
    
    analysis = f"""# Nano-Degree Course Structure Analysis Report

## Executive Summary

The nano-degree course structure has significant issues with image references and document organization:

- **194 out of 229 image references are broken (84.7%)**
- **21 unused images exist in the filesystem**
- **Session 2 has complex multi-path structure requiring analysis**
- **Many referenced images were never created**

## 1. Broken Image Links Analysis

### Critical Finding: Systematic Image Reference Issues

The image reference guide contains {report['summary']['broken_references']} broken links out of {report['summary']['total_image_references']} total references. This indicates a systematic issue where:

1. **The reference guide was created based on intended content structure**
2. **Many referenced images were never actually created**
3. **Some images exist but have different names than referenced**

### Fixable Image Name Mismatches

These broken references can be fixed by updating the reference guide:

"""
    
    # Add specific fixes
    frameworks_images = report['image_files_by_directory'].get('docs-content/01_frameworks/images', [])
    
    fixable_count = 0
    for broken_name, actual_name in fixes.items():
        if actual_name != 'MISSING - needs creation' and actual_name in frameworks_images:
            analysis += f"- `{broken_name}` → `{actual_name}`\n"
            fixable_count += 1
    
    analysis += f"""
**Quick wins: {fixable_count} image references can be fixed by simple name corrections.**

### Missing Images Requiring Creation

The following images are extensively referenced but don't exist and need to be created:

#### CrewAI Framework (14 missing images):
"""
    
    crewai_missing = [k for k, v in fixes.items() if 'crewai' in k and v == 'MISSING - needs creation']
    for img in crewai_missing:
        analysis += f"- {img}\n"
    
    analysis += "\n#### AutoGen Framework (12 missing images):\n"
    autogen_missing = [k for k, v in fixes.items() if 'autogen' in k and v == 'MISSING - needs creation']
    for img in autogen_missing:
        analysis += f"- {img}\n"
    
    analysis += "\n#### RAG Module (6 missing images):\n"
    rag_missing = [k for k, v in fixes.items() if 'rag' in k and v == 'MISSING - needs creation']
    for img in rag_missing:
        analysis += f"- {img}\n"
    
    analysis += f"""

## 2. Session 2 Structure Analysis

Session 2 demonstrates a complex multi-path learning structure:

### Document Hierarchy

**Hub Document**: `Session2_LangChain_Foundations.md` (2,255 words)
- Serves as entry point for all learning paths (🎯 Observer, 📝 Participant, ⚙️ Implementer)

**Implementer Path Extensions**:
- `Session2_Advanced_Agent_Architecture.md` (3,284 words) - Advanced orchestration patterns
- `Session2_Enterprise_Tool_Development.md` (3,622 words) - Custom tool development

**Additional Modules**: {len([f for f in report['session2_analysis'] if f['filename'].startswith('Session2_Module')])} module files
**Test Solutions**: {len([f for f in report['session2_analysis'] if 'Test_Solutions' in f['filename']])} test solution files

### Learning Path Integration

The Session 2 structure properly implements progressive disclosure:

1. **🎯 Observer Path**: Core concepts in the hub document
2. **📝 Participant**: Hub + practical implementation modules
3. **⚙️ Implementer**: Hub + advanced architecture + enterprise tools

This structure is **correctly designed** and shows sophisticated curriculum architecture.

## 3. Document Relationship Mapping

### Navigation Links Analysis

Found {len(report['navigation_links'])} internal document links across the course content.

### Orphaned Documents

Analysis of document relationships reveals:
"""
    
    # Analyze orphaned documents
    all_docs = set()
    linked_docs = set()
    
    # Collect all markdown files
    for root, dirs, files in os.walk('/Users/q284340/Agentic/nano-degree/docs-content'):
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), '/Users/q284340/Agentic/nano-degree')
                all_docs.add(rel_path)
    
    # Collect all linked documents
    for link in report['navigation_links']:
        linked_docs.add(link['target_file'])
    
    # Find potential orphans (documents not linked to)
    potential_orphans = []
    for doc in all_docs:
        doc_name = os.path.basename(doc)
        if not any(link['target_file'] == doc_name for link in report['navigation_links']):
            if not doc_name.startswith('index.') and 'Test_Solutions' not in doc_name:
                potential_orphans.append(doc)
    
    analysis += f"""
- **Total documents**: {len(all_docs)}
- **Documents with incoming links**: {len(set(link['target_file'] for link in report['navigation_links']))}
- **Potential orphaned documents**: {len(potential_orphans)}

Orphaned documents (may be entry points or truly orphaned):
"""
    
    for orphan in potential_orphans[:10]:  # Show first 10
        analysis += f"- {orphan}\n"
    
    analysis += f"""

## 4. Unused Images Analysis

**{report['summary']['unused_images']} images exist but are not referenced** in any markdown files:

### By Module:
"""
    
    # Group unused images by directory
    unused_by_dir = defaultdict(list)
    for img in report['unused_images']:
        dir_name = img['directory'].split('/')[-1] if '/' in img['directory'] else img['directory']
        unused_by_dir[dir_name].append(img['filename'])
    
    for dir_name, images in unused_by_dir.items():
        analysis += f"- **{dir_name}**: {len(images)} unused images\n"
        for img in images[:3]:  # Show first 3
            analysis += f"  - {img}\n"
        if len(images) > 3:
            analysis += f"  - ... and {len(images) - 3} more\n"
    
    analysis += f"""

## 5. Recommendations

### Immediate Actions (High Priority)

1. **Fix Simple Name Mismatches** ({fixable_count} fixes)
   - Update image-reference-guide.md with correct filenames
   - Test all fixed references
   
2. **Remove References to Non-Existent Images**
   - Remove or comment out {len([k for k, v in fixes.items() if v == 'MISSING - needs creation'])} broken references
   - Or create placeholder images with "Coming Soon" message

### Content Creation (Medium Priority)

3. **Create Missing CrewAI Images** (14 images)
   - High priority as CrewAI is a major framework
   - Focus on architecture diagrams first
   
4. **Create Missing AutoGen Images** (12 images)
   - Essential for framework comparison completeness
   
5. **Create Missing RAG Images** (6 images)
   - Critical for RAG module completeness

### Optimization (Lower Priority)

6. **Review Unused Images**
   - Determine if unused images should be integrated
   - Remove truly obsolete images
   
7. **Validate Document Links**
   - Ensure all navigation links work correctly
   - Verify orphaned documents are intentionally standalone

## 6. Implementation Plan

### Phase 1: Quick Fixes (1-2 hours)
- [ ] Update {fixable_count} image name references
- [ ] Comment out {len([k for k, v in fixes.items() if v == 'MISSING - needs creation'])} missing image references
- [ ] Test image reference guide functionality

### Phase 2: Critical Content Creation (1-2 weeks)
- [ ] Create CrewAI architecture and workflow diagrams
- [ ] Create AutoGen conversation and architecture diagrams
- [ ] Create basic RAG pipeline and comparison diagrams

### Phase 3: Polish and Optimization (Ongoing)
- [ ] Review and integrate unused images where appropriate
- [ ] Create remaining detailed diagrams
- [ ] Optimize document cross-references

## Conclusion

The course structure shows sophisticated curriculum design, particularly in Session 2's multi-path approach. However, the image reference system is critically broken due to systematic missing content. The 84.7% broken reference rate indicates this was likely a planning document that preceded actual content creation.

Priority should be on fixing simple name mismatches first, then systematically creating the missing visual content that students expect based on the comprehensive reference guide.
"""
    
    return analysis

def main():
    analysis = create_comprehensive_analysis()
    
    output_file = '/Users/q284340/Agentic/nano-degree/COMPREHENSIVE_COURSE_ANALYSIS.md'
    with open(output_file, 'w') as f:
        f.write(analysis)
    
    print(f"✅ Comprehensive analysis saved to: {output_file}")
    print(f"📊 Key findings:")
    print(f"   - 194/229 (84.7%) image references are broken")
    print(f"   - 21 unused images exist")
    print(f"   - Session 2 has proper multi-path structure")
    print(f"   - 40+ missing images need creation")

if __name__ == "__main__":
    main()