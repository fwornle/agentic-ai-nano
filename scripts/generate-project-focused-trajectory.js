#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * Project-Focused Trajectory Generator
 * 
 * Creates meaningful trajectory analysis that explains:
 * 1. What each project is trying to achieve
 * 2. How the project is evolving over time
 * 3. What solutions have been created
 * 4. Strategic insights about project direction
 */

class ProjectFocusedTrajectoryGenerator {
  constructor() {
    this.projectPurposes = {
      'nano-degree': {
        mission: 'Comprehensive Agentic AI Educational Curriculum',
        description: 'A 6-week nanodegree covering advanced AI agent development, from core patterns through cutting-edge protocols (MCP, ACP, A2A) and production deployment.',
        keyComponents: [
          'Module 01: Agent Frameworks & Patterns (LangChain, CrewAI, PydanticAI, Atomic Agents, Agno)',
          'Module 02: RAG Systems (NodeRAG, reasoning-augmented retrieval, multimodal)',
          'Module 03: Agent Protocols (MCP, ACP, A2A for distributed architectures)',
          'Three-path learning system: Observer, Participant, Implementer'
        ],
        successMetrics: [
          'Course content quality and comprehensiveness',
          'Educational material accessibility and engagement', 
          'Image attribution and copyright compliance',
          'Documentation site functionality and navigation'
        ]
      },
      'coding': {
        mission: 'Live Session Logging Infrastructure & Transcript Monitoring',
        description: 'Real-time transcript monitoring system that automatically logs Claude Code sessions, routes content between projects, and generates trajectory analysis.',
        keyComponents: [
          'Transcript monitoring with automatic session boundary detection',
          'Cross-project intelligent content routing (nano-degree ↔ coding)',
          'Live Session Logging (LSL) with 60-minute time tranches',
          'Trajectory analysis with predecessor detection and cumulative learning'
        ],
        successMetrics: [
          'Real-time session file creation accuracy',
          'Content classification and routing precision',
          'Trajectory continuity across sessions and dates',
          'System reliability and automatic recovery'
        ]
      }
    };
  }

  determineProjectFromPath(sessionPath) {
    if (sessionPath.includes('/nano-degree/')) {
      return 'nano-degree';
    } else if (sessionPath.includes('/coding/')) {
      return 'coding';
    }
    return 'unknown';
  }

  extractUserRequestsFromLSL(lslContent) {
    const lines = lslContent.split('\n');
    const userRequests = [];
    
    let currentRequest = null;
    let inUserMessage = false;
    let messageLines = [];
    
    for (const line of lines) {
      if (line.includes('### User Request')) {
        // Save previous request
        if (currentRequest && messageLines.length > 0) {
          currentRequest.message = messageLines.join(' ').trim();
          userRequests.push(currentRequest);
        }
        
        // Start new request
        const timeMatch = line.match(/(\d{2}:\d{2}:\d{2})/);
        currentRequest = {
          timestamp: timeMatch ? timeMatch[1] : 'unknown',
          message: '',
          intent: '',
          domain: ''
        };
        messageLines = [];
        inUserMessage = false;
      } else if (line.includes('**User Message:**')) {
        inUserMessage = true;
        messageLines = [];
      } else if (line.includes('**Claude Response:**')) {
        inUserMessage = false;
        if (currentRequest && messageLines.length > 0) {
          currentRequest.message = messageLines.join(' ').trim();
        }
      } else if (inUserMessage && line.trim() && !line.includes('**')) {
        messageLines.push(line.trim());
      }
    }
    
    // Add final request
    if (currentRequest && messageLines.length > 0) {
      currentRequest.message = messageLines.join(' ').trim();
      userRequests.push(currentRequest);
    }
    
    return userRequests;
  }

  classifyUserIntent(message, project) {
    const patterns = {
      'Build/Create': {
        keywords: ['create', 'build', 'implement', 'develop', 'generate', 'make', 'write'],
        weight: 2
      },
      'Debug/Fix': {
        keywords: ['fix', 'debug', 'error', 'issue', 'problem', 'broken', 'wrong'],
        weight: 2
      },
      'Enhance/Improve': {
        keywords: ['improve', 'enhance', 'optimize', 'better', 'upgrade', 'extend'],
        weight: 2
      },
      'Analyze/Review': {
        keywords: ['analyze', 'review', 'examine', 'check', 'look', 'investigate'],
        weight: 1.5
      },
      'Configure/Setup': {
        keywords: ['setup', 'configure', 'install', 'deploy', 'initialize'],
        weight: 1.5
      },
      'Document/Explain': {
        keywords: ['document', 'explain', 'describe', 'clarify', 'understand'],
        weight: 1
      }
    };
    
    const messageLower = message.toLowerCase();
    let bestIntent = 'General';
    let highestScore = 0;
    
    for (const [intent, config] of Object.entries(patterns)) {
      const score = config.keywords.reduce((acc, keyword) => {
        return acc + (messageLower.includes(keyword) ? config.weight : 0);
      }, 0);
      
      if (score > highestScore) {
        highestScore = score;
        bestIntent = intent;
      }
    }
    
    return bestIntent;
  }

  classifyDomain(message, project) {
    const domainPatterns = {
      'nano-degree': {
        'Course Content': ['course', 'module', 'session', 'nanodegree', 'curriculum', 'educational'],
        'Image Management': ['png', 'image', 'screenshot', 'attribution', 'visual'],
        'Documentation': ['documentation', 'readme', 'docs', 'mkdocs'],
        'Agent Frameworks': ['langchain', 'crewai', 'pydantic', 'atomic', 'agno'],
        'RAG Systems': ['rag', 'retrieval', 'vector', 'noderag', 'embedding'],
        'Protocols': ['mcp', 'acp', 'a2a', 'protocol', 'communication']
      },
      'coding': {
        'Transcript Monitoring': ['transcript', 'monitor', 'enhanced', 'simplified'],
        'Session Management': ['lsl', 'session', 'file', 'boundary', 'window'],
        'Content Routing': ['routing', 'redirect', 'classification', 'cross-project'],
        'Trajectory Analysis': ['trajectory', 'predecessor', 'cumulative', 'analysis'],
        'Infrastructure': ['script', 'bash', 'process', 'system', 'automation']
      }
    };
    
    const messageLower = message.toLowerCase();
    const projectPatterns = domainPatterns[project] || {};
    
    let bestDomain = 'General';
    let highestScore = 0;
    
    for (const [domain, keywords] of Object.entries(projectPatterns)) {
      const score = keywords.reduce((acc, keyword) => {
        return acc + (messageLower.includes(keyword) ? 1 : 0);
      }, 0);
      
      if (score > highestScore) {
        highestScore = score;
        bestDomain = domain;
      }
    }
    
    return bestDomain;
  }

  analyzeSolutionsCreated(userRequests, project) {
    const solutions = [];
    const projectPurpose = this.projectPurposes[project];
    
    if (!projectPurpose) return solutions;
    
    // Group requests by domain and analyze what was accomplished
    const domainGroups = {};
    userRequests.forEach(request => {
      if (!domainGroups[request.domain]) {
        domainGroups[request.domain] = [];
      }
      domainGroups[request.domain].push(request);
    });
    
    for (const [domain, requests] of Object.entries(domainGroups)) {
      if (requests.length === 0) continue;
      
      const buildRequests = requests.filter(r => r.intent === 'Build/Create').length;
      const fixRequests = requests.filter(r => r.intent === 'Debug/Fix').length;
      const enhanceRequests = requests.filter(r => r.intent === 'Enhance/Improve').length;
      
      if (buildRequests > 0) {
        solutions.push(`Built/Created ${buildRequests} ${domain.toLowerCase()} solution${buildRequests > 1 ? 's' : ''}`);
      }
      
      if (fixRequests > 0) {
        solutions.push(`Resolved ${fixRequests} ${domain.toLowerCase()} issue${fixRequests > 1 ? 's' : ''}`);
      }
      
      if (enhanceRequests > 0) {
        solutions.push(`Enhanced ${enhanceRequests} ${domain.toLowerCase()} component${enhanceRequests > 1 ? 's' : ''}`);
      }
    }
    
    return solutions;
  }

  generateEvolutionInsights(userRequests, project, sessionMetadata) {
    const projectPurpose = this.projectPurposes[project];
    if (!projectPurpose) return { phase: 'Unknown', direction: 'Unclear' };
    
    const intentCounts = {};
    const domainCounts = {};
    
    userRequests.forEach(request => {
      intentCounts[request.intent] = (intentCounts[request.intent] || 0) + 1;
      domainCounts[request.domain] = (domainCounts[request.domain] || 0) + 1;
    });
    
    const primaryIntent = Object.entries(intentCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || 'General';
    
    const primaryDomain = Object.entries(domainCounts)
      .sort(([,a], [,b]) => b - a)[0]?.[0] || 'General';
    
    let phase = 'Development';
    let direction = 'Forward Progress';
    
    if (primaryIntent === 'Build/Create') {
      phase = 'Active Development';
      direction = 'Feature Expansion';
    } else if (primaryIntent === 'Debug/Fix') {
      phase = 'Stabilization';
      direction = 'Quality Improvement';
    } else if (primaryIntent === 'Enhance/Improve') {
      phase = 'Optimization';
      direction = 'Performance Enhancement';
    } else if (primaryIntent === 'Configure/Setup') {
      phase = 'Infrastructure Setup';
      direction = 'Foundation Building';
    }
    
    return { phase, direction, primaryIntent, primaryDomain };
  }

  async generateTrajectory(sessionFilePath) {
    const project = this.determineProjectFromPath(sessionFilePath);
    const projectPurpose = this.projectPurposes[project];
    
    if (!projectPurpose) {
      throw new Error(`Unknown project: ${project}`);
    }
    
    // Read LSL content
    const lslContent = fs.readFileSync(sessionFilePath, 'utf8');
    const userRequests = this.extractUserRequestsFromLSL(lslContent);
    
    // Classify requests
    userRequests.forEach(request => {
      request.intent = this.classifyUserIntent(request.message, project);
      request.domain = this.classifyDomain(request.message, project);
    });
    
    // Extract session metadata
    const filename = path.basename(sessionFilePath);
    const match = filename.match(/(\d{4}-\d{2}-\d{2})_(\d{4}-\d{4})/);
    const sessionDate = match ? match[1] : 'unknown';
    const timeWindow = match ? match[2] : 'unknown';
    
    // Find previous trajectory for context
    const trajectoryDir = path.dirname(sessionFilePath).replace('/history', '/trajectory');
    let previousContext = null;
    
    if (fs.existsSync(trajectoryDir)) {
      const trajectoryFiles = fs.readdirSync(trajectoryDir)
        .filter(f => f.includes('trajectory.md') && f < filename.replace('session', 'trajectory'))
        .sort()
        .reverse();
      
      if (trajectoryFiles.length > 0) {
        const previousTrajPath = path.join(trajectoryDir, trajectoryFiles[0]);
        try {
          const prevContent = fs.readFileSync(previousTrajPath, 'utf8');
          const evolutionMatch = prevContent.match(/### Current Project Evolution[\\s\\S]*?###/);
          if (evolutionMatch) {
            previousContext = evolutionMatch[0].substring(0, 200) + '...';
          }
        } catch (error) {
          // Previous trajectory not available
        }
      }
    }
    
    // Analyze solutions and evolution
    const solutionsCreated = this.analyzeSolutionsCreated(userRequests, project);
    const evolution = this.generateEvolutionInsights(userRequests, project);
    
    // Generate trajectory content
    const trajectoryContent = `# Project Trajectory Analysis: ${timeWindow}

**Generated:** ${new Date().toISOString()}
**Session Date:** ${sessionDate}
**Time Window:** ${timeWindow}
**Project:** ${projectPurpose.mission}

---

## Project Mission & Context

### What This Project Achieves
${projectPurpose.description}

### Core Components
${projectPurpose.keyComponents.map(c => `- ${c}`).join('\n')}

### Success Metrics
${projectPurpose.successMetrics.map(m => `- ${m}`).join('\n')}

---

## Current Session Analysis

### User Engagement Summary
- **Total Interactions:** ${userRequests.length}
- **Primary Intent:** ${evolution.primaryIntent}
- **Primary Domain:** ${evolution.primaryDomain}
- **Session Focus:** ${evolution.primaryDomain} ${evolution.primaryIntent.toLowerCase()}

### Solutions Created This Session
${solutionsCreated.length > 0 ? solutionsCreated.map(s => `- ${s}`).join('\n') : '- No major solutions completed this session'}

### Key Accomplishments
${userRequests.slice(0, 3).map((req, i) => `${i + 1}. **${req.intent}** in ${req.domain}: ${req.message.substring(0, 100)}${req.message.length > 100 ? '...' : ''}`).join('\n')}

---

## Current Project Evolution

### Development Phase
**Current Phase:** ${evolution.phase}
**Direction:** ${evolution.direction}

### Progress Indicators
- **Activity Level:** ${userRequests.length > 5 ? 'High' : userRequests.length > 2 ? 'Moderate' : 'Light'} (${userRequests.length} interactions)
- **Focus Consistency:** ${evolution.primaryDomain !== 'General' ? 'Focused' : 'Broad'} - ${evolution.primaryDomain}
- **Problem Solving:** ${evolution.primaryIntent === 'Debug/Fix' ? 'Reactive' : 'Proactive'} - ${evolution.primaryIntent}

### Strategic Direction
${this.generateStrategicInsights(userRequests, project, evolution, projectPurpose)}

${previousContext ? `### Evolution from Previous Session
${previousContext}

**→ Current Session Continuation:** The project continues to evolve in the ${evolution.primaryDomain} domain with ${evolution.primaryIntent.toLowerCase()} focus.` : ''}

---

## Project Health Assessment

### Alignment with Mission
${this.assessMissionAlignment(userRequests, project, projectPurpose)}

### Development Momentum
${this.assessMomentum(userRequests, evolution)}

### Next Probable Focus Areas
${this.predictNextFocus(userRequests, project, evolution)}

---

## Session Impact on Overall Project

### Immediate Contributions
${solutionsCreated.length > 0 ? `This session directly advanced the project by ${solutionsCreated.join(', ').toLowerCase()}.` : 'This session provided analysis and planning for future development.'}

### Long-term Project Advancement
The ${evolution.primaryIntent.toLowerCase()} activities in ${evolution.primaryDomain.toLowerCase()} contribute to the project's core mission of ${projectPurpose.mission.toLowerCase()}.

${userRequests.length > 3 ? `With ${userRequests.length} significant interactions, this session represents substantial progress toward project objectives.` : 'This session provided focused attention to specific project needs.'}

---

*Project-focused trajectory analysis providing strategic insights into ${projectPurpose.mission}*
`;

    return trajectoryContent;
  }

  generateStrategicInsights(userRequests, project, evolution, projectPurpose) {
    if (project === 'nano-degree') {
      if (evolution.primaryDomain === 'Course Content') {
        return 'Focus on educational content development aligns with core mission. Continued refinement of curriculum materials supports comprehensive learning experience.';
      } else if (evolution.primaryDomain === 'Image Management') {
        return 'Image attribution and management work ensures legal compliance and professional course presentation standards.';
      } else if (evolution.primaryIntent === 'Build/Create') {
        return 'Active content creation phase supports the comprehensive nanodegree mission with new educational materials and resources.';
      }
    } else if (project === 'coding') {
      if (evolution.primaryDomain === 'Transcript Monitoring') {
        return 'Infrastructure development work supports real-time session logging capabilities, core to the system mission.';
      } else if (evolution.primaryDomain === 'Content Routing') {
        return 'Cross-project routing improvements enhance the intelligent classification system for better content organization.';
      } else if (evolution.primaryIntent === 'Debug/Fix') {
        return 'System stabilization work ensures reliable infrastructure for long-term transcript monitoring and analysis.';
      }
    }
    
    return `${evolution.primaryIntent} work in ${evolution.primaryDomain} supports overall project objectives through focused technical advancement.`;
  }

  assessMissionAlignment(userRequests, project, projectPurpose) {
    const relevantRequests = userRequests.filter(r => r.domain !== 'General').length;
    const alignmentScore = relevantRequests / Math.max(userRequests.length, 1);
    
    if (alignmentScore > 0.8) {
      return '**Excellent Alignment** - Session activities directly support core project mission with focused domain work.';
    } else if (alignmentScore > 0.6) {
      return '**Good Alignment** - Majority of activities contribute to project objectives with clear purpose.';
    } else if (alignmentScore > 0.4) {
      return '**Moderate Alignment** - Mixed focus with some activities supporting core mission.';
    } else {
      return '**Needs Focus** - Session activities could be more aligned with core project objectives.';
    }
  }

  assessMomentum(userRequests, evolution) {
    const buildCreateCount = userRequests.filter(r => r.intent === 'Build/Create').length;
    const enhanceCount = userRequests.filter(r => r.intent === 'Enhance/Improve').length;
    const fixCount = userRequests.filter(r => r.intent === 'Debug/Fix').length;
    
    const positiveActions = buildCreateCount + enhanceCount;
    const totalActions = userRequests.length;
    
    if (positiveActions / totalActions > 0.7) {
      return '**High Momentum** - Strong forward progress with active development and enhancement activities.';
    } else if (positiveActions / totalActions > 0.5) {
      return '**Steady Progress** - Balanced development with consistent advancement toward project goals.';
    } else if (fixCount > positiveActions) {
      return '**Stabilization Phase** - Focus on resolving issues and improving existing functionality.';
    } else {
      return '**Mixed Activity** - Varied focus with opportunity for more directed development effort.';
    }
  }

  predictNextFocus(userRequests, project, evolution) {
    if (evolution.primaryIntent === 'Build/Create') {
      return `- Continue expanding ${evolution.primaryDomain.toLowerCase()} capabilities\n- Integration and testing of newly created solutions\n- Documentation and refinement of new features`;
    } else if (evolution.primaryIntent === 'Debug/Fix') {
      return `- Validation of fixes and system stability\n- Potential enhancement of resolved ${evolution.primaryDomain.toLowerCase()} components\n- Preventive improvements to avoid similar issues`;
    } else if (evolution.primaryIntent === 'Enhance/Improve') {
      return `- Performance optimization and scaling\n- Advanced features in ${evolution.primaryDomain.toLowerCase()}\n- Integration with other project components`;
    } else {
      return `- Continued development in ${evolution.primaryDomain.toLowerCase()}\n- Feature expansion and capability enhancement\n- System integration and optimization`;
    }
  }

  async run(sessionFilePath) {
    try {
      const trajectoryContent = await this.generateTrajectory(sessionFilePath);
      
      // Always put trajectory files in .specstory/trajectory directory
      const projectDir = sessionFilePath.includes('/nano-degree/') 
        ? path.dirname(sessionFilePath).replace('/.specstory/history', '')
        : path.dirname(sessionFilePath).replace('/.specstory/history', '');
      
      const filename = path.basename(sessionFilePath).replace('-session.md', '-trajectory.md');
      const trajectoryDir = path.join(projectDir, '.specstory', 'trajectory');
      const trajectoryPath = path.join(trajectoryDir, filename);
      
      // Ensure trajectory directory exists
      if (!fs.existsSync(trajectoryDir)) {
        fs.mkdirSync(trajectoryDir, { recursive: true });
      }
      
      // Write trajectory file
      fs.writeFileSync(trajectoryPath, trajectoryContent);
      
      return trajectoryPath;
    } catch (error) {
      console.error('Error generating project-focused trajectory:', error);
      throw error;
    }
  }
}

// Export for use in other scripts
module.exports = ProjectFocusedTrajectoryGenerator;

// Command line usage
if (require.main === module) {
  const sessionFilePath = process.argv[2];
  
  if (!sessionFilePath) {
    console.error('Usage: node generate-project-focused-trajectory.js <session-file-path>');
    process.exit(1);
  }
  
  if (!fs.existsSync(sessionFilePath)) {
    console.error(`Session file not found: ${sessionFilePath}`);
    process.exit(1);
  }
  
  const generator = new ProjectFocusedTrajectoryGenerator();
  generator.run(sessionFilePath)
    .then(trajectoryPath => {
      console.log(`✅ Generated project-focused trajectory: ${trajectoryPath}`);
    })
    .catch(error => {
      console.error('❌ Failed to generate trajectory:', error.message);
      process.exit(1);
    });
}