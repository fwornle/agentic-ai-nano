#!/usr/bin/env node

/**
 * Nano-degree LSL Generation Script
 * 
 * This is a wrapper that uses the centralized LSL generation from coding project.
 * All timezone handling and LSL generation logic is maintained in a single source.
 */

import { execSync } from 'child_process';
import path from 'path';

const CODING_TOOLS_PATH = process.env.CODING_TOOLS_PATH || '/Users/q284340/Agentic/coding';
const centralScript = path.join(CODING_TOOLS_PATH, 'scripts', 'generate-lsl-for-project.js');

try {
  // Call the centralized script with nano-degree specific parameters
  const result = execSync(`node "${centralScript}" --project=nano-degree`, { 
    encoding: 'utf8',
    stdio: 'inherit'
  });
  
  console.log('✅ Nano-degree LSL generation completed using centralized script');
} catch (error) {
  console.error('❌ Failed to run centralized LSL generation:', error.message);
  process.exit(1);
}