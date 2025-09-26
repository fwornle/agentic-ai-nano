# CLAUDE.md - Consolidated Development Guidelines

This file provides essential guidance to Claude Code across all projects with global rules and project-specific configurations.

---

## 🚨🚨🚨 CRITICAL GLOBAL RULE: NO PARALLEL VERSIONS EVER 🚨🚨🚨

**This rule applies to ALL projects and must NEVER be violated.**

### ❌ NEVER CREATE FILES OR FUNCTIONS WITH EVOLUTIONARY NAMES:
- `v2`, `v3`, `v4`, `v5` (version suffixes)
- `enhanced`, `improved`, `better`, `new`, `advanced`, `pro`
- `simplified`, `simple`, `basic`, `lite` 
- `fixed`, `patched`, `updated`, `revised`, `modified`
- `temp`, `temporary`, `backup`, `copy`, `duplicate`, `clone`
- `alt`, `alternative`, `variant`
- `final`, `draft`, `test`, `experimental`

### ✅ ALWAYS DO THIS INSTEAD:
1. **Edit the original file directly**
2. **Debug and trace to find the root cause**
3. **Fix the underlying problem, not create workarounds**
4. **Refactor existing code rather than duplicating it**

### Why This Rule is Critical:
- Prevents technical debt and code bloat
- Forces proper problem analysis and solutions
- Maintains clean, maintainable codebases  
- Eliminates confusion about which version to use
- Ensures single source of truth

### Enforcement Protocol:
1. **Immediate removal** of any parallel versions detected
2. **Root cause analysis** of why the original failed
3. **Fix the original** using proper debugging techniques
4. **Add this rule to every project's CLAUDE.md**

**Remember: If you're tempted to create a parallel version, you haven't understood the root problem yet. Keep debugging until you can fix the original.**

---

## 🚨 GLOBAL: MANDATORY VERIFICATION RULE

**CRITICAL**: NEVER CLAIM SUCCESS OR COMPLETION WITHOUT VERIFICATION

**ABSOLUTE RULE**: Before stating ANY result, completion, or success:
1. **ALWAYS run verification commands** to check the actual state
2. **ALWAYS show proof** with actual command output  
3. **NEVER assume or guess** - only report what you can verify
4. **If verification shows failure**, report the failure accurately

**WHY THIS MATTERS**: False success claims waste time and break user trust. ALWAYS verify before reporting.

---

## 📋 PROJECT CONFIGURATIONS

### 🔧 Project: coding (Main Development Hub)

**Location**: `/Users/q284340/Agentic/coding`  
**Purpose**: Primary development environment with MCP services, knowledge management, and LSL system

#### Startup & Services
- **Command**: `claude-mcp` (NEVER just `claude`) - always start claude via 'coding'
- **Services**: VKB Server (port 8080), MCP Memory, Semantic Analysis
- **Automatic startup**: `coding` or `coding --claude` starts all services

#### Knowledge Management
- **MCP Memory Service**: Runtime knowledge graph storage and querying
- **Commands**: `ukb` (update), `vkb` (visualize)
- **Files**: `shared-memory-*.json` (git-tracked persistent storage)

#### Session Logging (LSL System)
- **Primary**: Live Session Logging with enhanced transcript monitor
- **Secondary**: Post-session logging as fallback
- **Location**: `.specstory/history/` (markdown files)
- **Format**: `YYYY-MM-DD_HHMM-HHMM-<user-hash>[_from-<project>].md`

#### Critical Architecture
- **Working Directory**: Always start in top-level project directory
- **File Interference**: Avoid `.mcp-sync/` for importable modules
- **Timeout Guidelines**: Use shorter timeouts (5-10s) for most operations

---


#### Architecture Standards
- **TypeScript**: Mandatory with strict type checking
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Bundle size budgets, Core Web Vitals monitoring
- **API Design**: Never modify working APIs for TypeScript; fix types instead

#### Specialized Agents
- **test-runner**: Memory-efficient quality checks
- **ui-tester**: Frontend testing with Playwright
- **code-change-critic**: Post-implementation review

#### Claude Configuration
- **MCP Priority**: Use Serena MCP for all file operations
- **Memory Storage**: `.serena/memories/` for context persistence

---

## 🔧 GLOBAL DEVELOPMENT STANDARDS

### Git & Version Control
- **Commit Messages**: Descriptive with clear context
- **Frequency**: Commit after small increments/milestones  
- **Branch Strategy**: Follow project-specific guidelines

### Error Handling & Debugging
1. **Environment Check**: Variables, Docker setup, service status
2. **Systematic Debugging**: Step-by-step analysis
3. **Root Cause Focus**: Fix underlying issues, not symptoms
4. **Documentation**: Record architectural decisions and findings

---

## 📊 USAGE GUIDELINES BY PROJECT

| Project | Primary Tools | Key Commands | Focus Area |
|---------|---------------|--------------|------------|
| coding | MCP Memory, VKB, UKB | `claude-mcp`, `ukb`, `vkb` | Knowledge & Infrastructure |

---

## 🚨 CRITICAL SUCCESS FACTORS

1. **Always verify results** with actual command output
2. **Never create parallel versions** - fix originals instead  
3. **Use project-specific tools** and workflows appropriately
4. **Follow quality gates** before considering work complete
5. **Maintain cross-session continuity** via the live session logging system (LSL, started via coding/bin/coding)

---

*This rule is non-negotiable and applies to every single Claude development session across all projects.*