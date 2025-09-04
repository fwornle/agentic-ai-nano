#!/usr/bin/env node

/**
 * Fix User Prompts in LSL Files - Nano-degree Version
 * Extracts actual user prompts from nano-degree transcript and updates LSL files
 */

import fs from 'fs';
import path from 'path';

// Extract text content from message content (string, array, or mixed)
function extractTextContent(content) {
  // Direct string content (common for user messages)
  if (typeof content === 'string') {
    return content;
  } 
  
  // Array content (mixed text and tool results)
  if (Array.isArray(content)) {
    const parts = [];
    
    // Extract text items
    const textItems = content
      .filter(item => item && item.type === 'text')
      .map(item => item.text)
      .filter(text => text && text.trim()); // Remove empty/null text
      
    if (textItems.length > 0) {
      parts.push(...textItems);
    }
    
    // Handle image items
    const imageItems = content
      .filter(item => item && item.type === 'image');
      
    if (imageItems.length > 0) {
      parts.push(`[Image message: ${imageItems.length} image${imageItems.length > 1 ? 's' : ''}]`);
    }
    
    // If we have content, return it
    if (parts.length > 0) {
      return parts.join('\n');
    }
    
    // Fallback: check for tool results (but these are usually Claude responses, not user prompts)
    const toolResults = content
      .filter(item => item && item.type === 'tool_result' && item.content)
      .map(item => item.content)
      .filter(content => content && typeof content === 'string' && content.trim());
      
    return toolResults.join('\n');
  }
  
  return '';
}

// Parse Claude transcript and build user message lookup
function buildUserMessageLookup(transcriptPath) {
  console.log('📖 Reading nano-degree transcript...');
  
  const content = fs.readFileSync(transcriptPath, 'utf8');
  const lines = content.split('\n').filter(line => line.trim());
  
  const userMessages = {};
  let messageCount = 0;
  
  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      
      // Look for user messages (skip tool result messages)
      if (entry.type === 'user' && entry.message && entry.message.role === 'user') {
        // Skip tool result messages - these are not actual user prompts
        if (Array.isArray(entry.message.content) && 
            entry.message.content.length > 0 && 
            entry.message.content[0].type === 'tool_result') {
          continue; // Skip tool result messages
        }
        
        const timestamp = entry.timestamp;
        const userMessage = extractTextContent(entry.message.content);
        
        if (userMessage && userMessage.trim() && timestamp) {
          userMessages[timestamp] = userMessage.trim();
          messageCount++;
        }
      }
    } catch (error) {
      // Skip invalid JSON lines
      continue;
    }
  }
  
  console.log(`   ✅ Found ${messageCount} user messages in transcript`);
  return userMessages;
}

// Find matching user message for a timestamp (with tolerance)
function findMatchingUserMessage(targetTimestamp, userMessages) {
  const targetTime = new Date(targetTimestamp).getTime();
  const tolerance = 10 * 60 * 1000; // 10 minutes tolerance
  
  // First try exact match
  if (userMessages[targetTimestamp]) {
    return userMessages[targetTimestamp];
  }
  
  // Look for timestamps within tolerance
  for (const [timestamp, message] of Object.entries(userMessages)) {
    const messageTime = new Date(timestamp).getTime();
    const timeDiff = Math.abs(messageTime - targetTime);
    
    if (timeDiff <= tolerance) {
      return message;
    }
  }
  
  return null;
}

// Fix user prompts in an LSL file
function fixUserPromptsInLSL(filePath, userMessages) {
  console.log(`📝 Processing: ${path.basename(filePath)}`);
  
  let content = fs.readFileSync(filePath, 'utf8');
  let changeCount = 0;
  let fixedCount = 0;
  
  // Pattern to match LSL entries with "No context" or very short user requests  
  const lslEntryPattern = /(### .+ - \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z \([^)]+\)\n\n\*\*User Request:\*\* )([^\n]+)(\n\n\*\*Tool:\*\* )/g;
  
  content = content.replace(lslEntryPattern, (match, prefix, currentUserRequest, suffix) => {
    changeCount++;
    
    // Extract timestamp from the header
    const timestampMatch = prefix.match(/([\d\-T:\.]+Z)/);
    if (!timestampMatch) {
      return match; // Keep original if no timestamp found
    }
    
    const timestamp = timestampMatch[1];
    
    // Skip if already has a good user request 
    // BUT fix if it contains JSON metadata, tool results, or is "No context"
    const isJsonMetadata = currentUserRequest.includes('{"parentUuid"') || currentUserRequest.includes('"sessionId"');
    const isToolResult = currentUserRequest.includes('The file ') && currentUserRequest.includes(' has been updated');
    const isNoContext = currentUserRequest.trim() === 'No context';
    const isTruncated = currentUserRequest.endsWith('...');
    
    // Keep entries that look like real user requests (don't match problematic patterns)
    if (!isJsonMetadata && !isToolResult && !isNoContext && !isTruncated && currentUserRequest.length > 20) {
      return match; // Keep original - this looks like a real user request
    }
    
    // Try to find matching user message
    const actualUserMessage = findMatchingUserMessage(timestamp, userMessages);
    
    if (actualUserMessage) {
      // Limit length to reasonable display size
      const displayMessage = actualUserMessage.length > 150 
        ? actualUserMessage.substring(0, 150) + '...'
        : actualUserMessage;
      
      fixedCount++;
      return prefix + displayMessage + suffix;
    }
    
    return match; // Keep original if no match found
  });
  
  if (fixedCount > 0) {
    fs.writeFileSync(filePath, content);
    console.log(`   ✅ Fixed ${fixedCount} user prompts (${changeCount} entries processed)`);
  } else {
    console.log(`   ⏭️  No user prompts needed fixing (${changeCount} entries checked)`);
  }
  
  return fixedCount;
}

// Main function
async function main() {
  const transcriptPath = '/Users/q284340/.claude/projects/-Users-q284340-Agentic-nano-degree/04bd0b08-14b3-45c6-a840-7e71d57bb55e.jsonl';
  const historyDir = '/Users/q284340/Agentic/nano-degree/.specstory/history';
  const today = '2025-09-04';
  
  console.log('🔧 Fixing user prompts in nano-degree LSL files...\n');
  
  // Build user message lookup from transcript
  const userMessages = buildUserMessageLookup(transcriptPath);
  console.log();
  
  // Find all LSL files from today
  const files = fs.readdirSync(historyDir)
    .filter(file => file.includes(today) && file.endsWith('-session.md'))
    .map(file => path.join(historyDir, file));
  
  console.log(`📁 Found ${files.length} LSL files from ${today}:`);
  files.forEach(file => console.log(`   - ${path.basename(file)}`));
  console.log();
  
  let totalFixed = 0;
  
  for (const file of files) {
    const fixed = fixUserPromptsInLSL(file, userMessages);
    totalFixed += fixed;
  }
  
  console.log(`\n🎉 User prompt fix complete!`);
  console.log(`   📊 Files processed: ${files.length}`);
  console.log(`   🔄 User prompts fixed: ${totalFixed}`);
  console.log(`   📝 LSL files now show actual user prompts instead of "No context"`);
}

// Run the script
main().catch(console.error);