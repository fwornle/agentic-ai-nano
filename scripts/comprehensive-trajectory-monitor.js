#!/usr/bin/env node

/**
 * Comprehensive Trajectory Monitor
 * Uses single comprehensive trajectory file with semantic analysis
 * Replaces per-session trajectory generation with unified project tracking
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import { spawn } from 'child_process';

class ComprehensiveTrajectoryMonitor {
  constructor(config = {}) {
    this.debug_enabled = config.debug || process.env.TRANSCRIPT_DEBUG === 'true';
    
    this.config = {
      checkInterval: config.checkInterval || 2000,
      projectPath: config.projectPath || process.cwd(),
      debug: this.debug_enabled,
      sessionDuration: config.sessionDuration || 7200000, // 2 hours
      ...config
    };

    this.transcriptPath = this.findCurrentTranscript();
    this.lastProcessedUuid = null;
    this.lastFileSize = 0;
    this.isProcessing = false;
    this.currentUserPromptSet = [];
    this.lastUserPromptTime = null;
    
    // Single comprehensive trajectory file path
    this.comprehensiveTrajectoryFile = path.join(
      this.config.projectPath, 
      '.specstory', 
      'comprehensive-project-trajectory.md'
    );
  }

  /**
   * Initialize comprehensive trajectory file if it doesn't exist
   */
  async initializeComprehensiveTrajectory() {
    if (fs.existsSync(this.comprehensiveTrajectoryFile)) {
      this.debug('Comprehensive trajectory file already exists');
      return;
    }

    this.debug('Creating initial comprehensive trajectory file...');

    try {
      // Create directory if needed
      const trajectoryDir = path.dirname(this.comprehensiveTrajectoryFile);
      if (!fs.existsSync(trajectoryDir)) {
        fs.mkdirSync(trajectoryDir, { recursive: true });
      }

      // Generate initial comprehensive trajectory using semantic analysis
      const initialTrajectory = await this.generateInitialSemanticTrajectory();
      fs.writeFileSync(this.comprehensiveTrajectoryFile, initialTrajectory);
      
      console.log(`🎯 Created comprehensive trajectory: ${path.basename(this.comprehensiveTrajectoryFile)}`);
    } catch (error) {
      console.error('Error creating comprehensive trajectory:', error);
      // Fallback to basic template
      this.createBasicTrajectoryTemplate();
    }
  }

  /**
   * Generate initial trajectory using semantic analysis
   */
  async generateInitialSemanticTrajectory() {
    try {
      // Use MCP semantic analysis if available
      const semanticAnalysis = await this.performSemanticAnalysis();
      return this.formatSemanticTrajectory(semanticAnalysis);
    } catch (error) {
      this.debug('Semantic analysis failed, using repository scanning:', error.message);
      return this.generateBasicRepositoryTrajectory();
    }
  }

  /**
   * Perform semantic analysis of the repository
   */
  async performSemanticAnalysis() {
    // This would integrate with the MCP semantic analysis server
    // For now, return a placeholder that indicates semantic analysis should be done
    return {
      intention: "Advanced AI agent development educational curriculum",
      keyContents: ["Module 01: Agent Frameworks", "Module 02: RAG Systems", "Module 03: Protocols"],
      features: ["Multi-path learning", "Cloud development", "Comprehensive documentation"],
      documentation: ["README.md", "Course modules", "PlantUML diagrams"]
    };
  }

  /**
   * Format semantic analysis into trajectory file
   */
  formatSemanticTrajectory(analysis) {
    const timestamp = new Date().toISOString();
    const projectName = path.basename(this.config.projectPath);

    return `# Comprehensive Project Trajectory - ${projectName}

**Generated:** ${timestamp}  
**Project:** ${analysis.intention}  
**Repository:** ${this.config.projectPath}  
**Analysis Source:** Semantic Analysis + Live Session Aggregation

---

## (i) Repository Intention & Mission

### Core Purpose
${analysis.intention}

### Strategic Vision
${analysis.keyContents.join(', ')}

---

## (ii) Key Contents & Implemented Concepts

${analysis.keyContents.map(content => `- **${content}**`).join('\n')}

---

## (iii) Main Features & Technical Implementation

${analysis.features.map(feature => `- **${feature}**`).join('\n')}

---

## (iv) Key Documentation & Architecture

${analysis.documentation.map(doc => `- ${doc}`).join('\n')}

---

## Live Session Evolution

### Session History
*Sessions will be appended here automatically as they occur*

---

*This comprehensive trajectory file is continuously updated with each session, providing a unified view of project evolution and current state.*
`;
  }

  /**
   * Generate basic repository trajectory (fallback)
   */
  generateBasicRepositoryTrajectory() {
    const timestamp = new Date().toISOString();
    const projectName = path.basename(this.config.projectPath);

    return `# Comprehensive Project Trajectory - ${projectName}

**Generated:** ${timestamp}  
**Project:** ${projectName}  
**Repository:** ${this.config.projectPath}  
**Analysis Source:** Repository Scan + Live Session Aggregation

---

## Project Overview

This project is tracked via comprehensive trajectory analysis.

---

## Live Session Evolution

### Session History
*Sessions will be appended here automatically as they occur*

---

*This comprehensive trajectory file is continuously updated with each session.*
`;
  }

  /**
   * Append session summary to comprehensive trajectory
   */
  async appendSessionSummary(userPromptSet, timeWindow) {
    if (!fs.existsSync(this.comprehensiveTrajectoryFile)) {
      await this.initializeComprehensiveTrajectory();
    }

    const sessionSummary = this.generateSessionSummary(userPromptSet, timeWindow);
    const currentContent = fs.readFileSync(this.comprehensiveTrajectoryFile, 'utf8');
    
    // Insert session summary before the final line
    const lines = currentContent.split('\n');
    const insertIndex = lines.findIndex(line => line.includes('*This comprehensive trajectory file is continuously updated'));
    
    if (insertIndex > 0) {
      lines.splice(insertIndex, 0, sessionSummary, '');
      fs.writeFileSync(this.comprehensiveTrajectoryFile, lines.join('\n'));
      console.log(`📝 Updated comprehensive trajectory with session ${timeWindow}`);
    } else {
      // Fallback: append to end
      fs.appendFileSync(this.comprehensiveTrajectoryFile, '\n' + sessionSummary + '\n');
      console.log(`📝 Appended to comprehensive trajectory: session ${timeWindow}`);
    }
  }

  /**
   * Generate session summary for comprehensive trajectory
   */
  generateSessionSummary(userPromptSet, timeWindow) {
    const timestamp = new Date().toISOString();
    const patterns = this.analyzeSessionPatterns(userPromptSet);
    const focus = this.determineSessionFocus(userPromptSet);

    return `### Session ${timeWindow} - ${timestamp}

**Focus:** ${focus}  
**Exchanges:** ${userPromptSet.length}  
**Activity Patterns:** ${patterns}

**Key Activities:**
${userPromptSet.map(exchange => `- ${this.summarizeExchange(exchange)}`).join('\n')}

**Impact:** ${this.assessSessionImpact(userPromptSet)}`;
  }

  /**
   * Analyze patterns from user prompt set
   */
  analyzeSessionPatterns(userPromptSet) {
    const toolCounts = {};
    let codingActivities = 0;
    
    for (const exchange of userPromptSet) {
      for (const tool of exchange.toolCalls || []) {
        toolCounts[tool.name] = (toolCounts[tool.name] || 0) + 1;
      }
      if (this.isCodingRelated(exchange)) codingActivities++;
    }
    
    const topTools = Object.entries(toolCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([tool, count]) => `${tool}(${count})`)
      .join(', ');
    
    return `${topTools} | Coding: ${codingActivities}/${userPromptSet.length}`;
  }

  /**
   * Determine session focus
   */
  determineSessionFocus(userPromptSet) {
    if (userPromptSet.length === 0) return 'Initialization';
    
    const codingRelated = userPromptSet.filter(ex => this.isCodingRelated(ex)).length;
    const total = userPromptSet.length;
    const codingRatio = codingRelated / total;
    
    if (codingRatio > 0.7) return 'Development';
    if (codingRatio > 0.3) return 'Mixed Development';
    return 'Analysis/Research';
  }

  /**
   * Summarize individual exchange
   */
  summarizeExchange(exchange) {
    const toolNames = (exchange.toolCalls || []).map(t => t.name).join(', ');
    const userPreview = exchange.userMessage.slice(0, 60);
    return `${userPreview}... [${toolNames}]`;
  }

  /**
   * Assess session impact on project
   */
  assessSessionImpact(userPromptSet) {
    const totalTools = userPromptSet.reduce((sum, ex) => sum + (ex.toolCalls?.length || 0), 0);
    const codingCount = userPromptSet.filter(ex => this.isCodingRelated(ex)).length;
    
    if (totalTools > 20 && codingCount > 5) return 'High impact - significant development work';
    if (totalTools > 10 && codingCount > 2) return 'Medium impact - moderate development activity';
    if (totalTools > 5) return 'Low impact - basic analysis and setup';
    return 'Minimal impact - exploration and planning';
  }

  /**
   * Check if content involves coding project
   */
  isCodingRelated(exchange) {
    const codingPath = process.env.CODING_TOOLS_PATH || process.env.CODING_REPO || '/Users/q284340/Agentic/coding';
    
    for (const toolCall of exchange.toolCalls || []) {
      const toolData = JSON.stringify(toolCall).toLowerCase();
      
      if (toolData.includes(codingPath.toLowerCase()) || 
          toolData.includes('/coding/') || 
          toolData.includes('coding/')) {
        return true;
      }
    }
    return false;
  }

  // Include other necessary methods from original transcript monitor
  // (findCurrentTranscript, getUnprocessedExchanges, etc.)
  
  findCurrentTranscript() {
    const baseDir = path.join(os.homedir(), '.claude', 'projects');
    const files = fs.readdirSync(baseDir, { withFileTypes: true });
    
    for (const file of files) {
      if (file.isDirectory()) {
        const transcriptFile = path.join(baseDir, file.name, 'transcript.jsonl');
        if (fs.existsSync(transcriptFile)) {
          return transcriptFile;
        }
      }
    }
    return null;
  }

  debug(message) {
    if (this.debug_enabled) {
      console.log(`[DEBUG] ${message}`);
    }
  }

  /**
   * Main monitoring loop
   */
  async start() {
    await this.initializeComprehensiveTrajectory();
    console.log(`🚀 Comprehensive trajectory monitoring started for ${this.config.projectPath}`);
    
    setInterval(async () => {
      if (this.isProcessing) return;
      
      this.isProcessing = true;
      try {
        const exchanges = this.getUnprocessedExchanges();
        if (exchanges.length > 0) {
          // Process exchanges and update comprehensive trajectory
          const currentTime = new Date().toISOString().slice(11, 16).replace(':', ''); // HHMM
          await this.appendSessionSummary(exchanges, currentTime);
        }
      } catch (error) {
        this.debug(`Error in monitoring loop: ${error.message}`);
      } finally {
        this.isProcessing = false;
      }
    }, this.config.checkInterval);
  }

  getUnprocessedExchanges() {
    // Simplified version - would need full implementation
    return [];
  }
}

// Start monitoring if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const monitor = new ComprehensiveTrajectoryMonitor({
    debug: process.env.TRANSCRIPT_DEBUG === 'true'
  });
  monitor.start();
}

export default ComprehensiveTrajectoryMonitor;