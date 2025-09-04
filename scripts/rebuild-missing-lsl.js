#!/usr/bin/env node

/**
 * Rebuild Missing LSL Files
 * Processes the full nano-degree transcript and creates missing LSL session files
 */

import fs from 'fs';
import path from 'path';

// Get the nano-degree transcript file
const transcriptPath = '/Users/q284340/.claude/projects/-Users-q284340-Agentic-nano-degree/04bd0b08-14b3-45c6-a840-7e71d57bb55e.jsonl';
const historyDir = '/Users/q284340/Agentic/nano-degree/.specstory/history';

// Ensure history directory exists
if (!fs.existsSync(historyDir)) {
  fs.mkdirSync(historyDir, { recursive: true });
}

// Calculate 60-minute time tranches (like existing system)
function calculateTimeTranche(timestamp) {
  const date = new Date(timestamp);
  const minutes = date.getMinutes();
  const hours = date.getHours();
  
  // Round down to the nearest 60-minute boundary
  const startHour = hours;
  const endHour = (hours + 1) % 24;
  
  const startTime = String(startHour).padStart(2, '0') + '30';
  const endTime = String(endHour).padStart(2, '0') + '30';
  
  return `${startTime}-${endTime}`;
}

// Format timestamp with both UTC and local time
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const utcTime = date.toISOString();
  const localTime = date.toLocaleString('sv-SE');
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return `${utcTime} (${localTime} ${timezone})`;
}

// Extract text content from message content array
function extractTextContent(content) {
  if (typeof content === 'string') {
    return content;
  } 
  
  if (Array.isArray(content)) {
    const textItems = content
      .filter(item => item && item.type === 'text')
      .map(item => item.text)
      .filter(text => text && text.trim());
      
    if (textItems.length > 0) {
      return textItems.join('\n');
    }
    
    const toolResults = content
      .filter(item => item && item.type === 'tool_result' && item.content)
      .map(item => item.content)
      .filter(content => content && typeof content === 'string' && content.trim());
      
    return toolResults.join('\n');
  }
  
  return '';
}

// Parse transcript and group exchanges by session
function parseTranscriptBySession() {
  console.log('📖 Reading nano-degree transcript...');
  
  const content = fs.readFileSync(transcriptPath, 'utf8');
  const lines = content.split('\n').filter(line => line.trim());
  
  const sessionGroups = {};
  let currentExchange = null;
  
  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      
      if (entry.type === 'user' && entry.message?.role === 'user') {
        // Skip tool result messages
        if (Array.isArray(entry.message.content) && 
            entry.message.content.length > 0 && 
            entry.message.content[0].type === 'tool_result') {
          continue;
        }
        
        // Start new exchange
        if (currentExchange) {
          const tranche = calculateTimeTranche(currentExchange.timestamp);
          const dateKey = new Date(currentExchange.timestamp).toISOString().split('T')[0];
          const sessionKey = `${dateKey}_${tranche}`;
          
          if (!sessionGroups[sessionKey]) {
            sessionGroups[sessionKey] = [];
          }
          sessionGroups[sessionKey].push(currentExchange);
        }
        
        currentExchange = {
          id: entry.uuid,
          timestamp: entry.timestamp || Date.now(),
          userMessage: extractTextContent(entry.message.content) || '',
          claudeResponse: '',
          toolCalls: [],
          toolResults: []
        };
        
      } else if (entry.type === 'assistant' && entry.message?.role === 'assistant' && currentExchange) {
        // Add Claude response
        currentExchange.claudeResponse += extractTextContent(entry.message.content) || '';
        
        // Extract tool calls
        if (Array.isArray(entry.message.content)) {
          for (const item of entry.message.content) {
            if (item.type === 'tool_use') {
              currentExchange.toolCalls.push({
                name: item.name,
                input: item.input
              });
            }
          }
        }
        
      } else if (entry.type === 'user' && entry.message?.role === 'user' && currentExchange) {
        // Tool results
        if (Array.isArray(entry.message.content)) {
          for (const item of entry.message.content) {
            if (item.type === 'tool_result') {
              currentExchange.toolResults.push({
                content: item.content,
                is_error: item.is_error || false
              });
            }
          }
        }
      }
    } catch (error) {
      continue;
    }
  }
  
  // Don't forget the last exchange
  if (currentExchange) {
    const tranche = calculateTimeTranche(currentExchange.timestamp);
    const dateKey = new Date(currentExchange.timestamp).toISOString().split('T')[0];
    const sessionKey = `${dateKey}_${tranche}`;
    
    if (!sessionGroups[sessionKey]) {
      sessionGroups[sessionKey] = [];
    }
    sessionGroups[sessionKey].push(currentExchange);
  }
  
  return sessionGroups;
}

// Create LSL file for a session
function createLSLFile(sessionKey, exchanges) {
  const [date, timeRange] = sessionKey.split('_');
  const filePath = path.join(historyDir, `${sessionKey}-session.md`);
  
  // Check if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`   ⏭️  ${sessionKey}-session.md already exists`);
    return;
  }
  
  const now = new Date();
  const sessionHeader = `# WORK SESSION (${timeRange})\n\n` +
    `**Generated:** ${formatTimestamp(now.getTime())}\n` +
    `**Work Period:** ${timeRange}\n` +
    `**Focus:** Live session logging\n` +
    `**Duration:** ~60 minutes\n\n` +
    `---\n\n` +
    `## Session Overview\n\n` +
    `This session captures real-time tool interactions and exchanges.\n\n` +
    `---\n\n` +
    `## Key Activities\n\n`;
  
  let content = sessionHeader;
  
  // Add exchanges
  for (const exchange of exchanges) {
    const exchangeTime = formatTimestamp(exchange.timestamp);
    const userMessage = exchange.userMessage.length > 150 
      ? exchange.userMessage.substring(0, 150) + '...'
      : exchange.userMessage;
    
    // Add tool calls from this exchange
    for (let i = 0; i < exchange.toolCalls.length; i++) {
      const toolCall = exchange.toolCalls[i];
      const toolResult = exchange.toolResults[i];
      
      content += `### ${toolCall.name} - ${exchangeTime}\n\n`;
      content += `**User Request:** ${userMessage || 'No context'}\n\n`;
      content += `**Tool:** ${toolCall.name}  \n`;
      content += `**Input:** \`\`\`json\n${JSON.stringify(toolCall.input, null, 2)}\n\`\`\`\n\n`;
      
      if (toolResult) {
        content += `**Result:** ${toolResult.is_error ? '❌ Error' : '✅ Success'}\n\n`;
        if (toolResult.content && typeof toolResult.content === 'string' && toolResult.content.length > 0) {
          const resultPreview = toolResult.content.length > 200 
            ? toolResult.content.substring(0, 200) + '...'
            : toolResult.content;
          content += `${resultPreview}\n\n`;
        }
      } else {
        content += `**Result:** ⏳ Pending\n\n`;
      }
      
      content += `**AI Analysis:** 🤖 Reconstructed from transcript data\n\n`;
      content += `---\n\n`;
    }
  }
  
  fs.writeFileSync(filePath, content);
  console.log(`   ✅ Created ${sessionKey}-session.md (${exchanges.length} exchanges)`);
}

// Create trajectory file for a session
function createTrajectoryFile(sessionKey, exchanges) {
  const [date, timeRange] = sessionKey.split('_');
  const filePath = path.join(historyDir, `${sessionKey}-trajectory.md`);
  
  // Check if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`   ⏭️  ${sessionKey}-trajectory.md already exists`);
    return;
  }
  
  const now = new Date();
  let trajectoryContent = `# Trajectory Analysis: ${timeRange}\n\n` +
    `**Generated:** ${formatTimestamp(now.getTime())}\n` +
    `**Session:** ${timeRange}\n` +
    `**Focus:** Session trajectory and behavioral patterns\n` +
    `**Duration:** ~60 minutes\n\n` +
    `---\n\n`;
    
  trajectoryContent += `## Behavioral Patterns\n\n`;
  trajectoryContent += `**Total Exchanges:** ${exchanges.length}\n`;
  trajectoryContent += `**Reconstructed:** From nano-degree transcript data\n\n`;
  trajectoryContent += `---\n\n`;
  
  fs.writeFileSync(filePath, trajectoryContent);
  console.log(`   ✅ Created ${sessionKey}-trajectory.md`);
}

// Main function
async function main() {
  console.log('🔄 Rebuilding missing LSL files for nano-degree project...\n');
  
  const sessionGroups = parseTranscriptBySession();
  const sessionKeys = Object.keys(sessionGroups).sort();
  
  console.log(`📊 Found ${sessionKeys.length} sessions in transcript:`);
  sessionKeys.forEach(key => {
    const exchangeCount = sessionGroups[key].length;
    console.log(`   - ${key}: ${exchangeCount} exchanges`);
  });
  console.log();
  
  let createdCount = 0;
  
  for (const sessionKey of sessionKeys) {
    // Process all sessions (remove date filter to include current session)
    // if (!sessionKey.startsWith('2025-09-04')) continue;
    
    console.log(`📝 Processing ${sessionKey}:`);
    
    createLSLFile(sessionKey, sessionGroups[sessionKey]);
    createTrajectoryFile(sessionKey, sessionGroups[sessionKey]);
    createdCount++;
  }
  
  console.log(`\n🎉 LSL rebuild complete!`);
  console.log(`   📊 Sessions processed: ${sessionKeys.filter(k => k.startsWith('2025-09-04')).length}`);
  console.log(`   📝 Files created: Check output above`);
  console.log(`   📁 Location: ${historyDir}`);
}

// Run the script
main().catch(console.error);