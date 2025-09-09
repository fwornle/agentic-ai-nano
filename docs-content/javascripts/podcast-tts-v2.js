/**
 * Professional Podcast TTS Feature for Agentic AI Nano-Degree
 * Version 2.0 - Redesigned for GitHub Pages compatibility and professional UI
 */

class ProfessionalPodcastTTS {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.isPlaying = false;
        this.isPaused = false;
        this.currentChunkIndex = 0;
        this.textChunks = [];
        this.playbackRate = 1.0;
        this.voice = null;
        this.volume = 0.8;
        this.contentFilter = 'all'; // 'observer', 'participant', 'implementer', 'all'
        
        this.init();
    }

    init() {
        console.log('🎙️ Initializing ProfessionalPodcastPlayer...');
        
        // Test Speech Synthesis availability
        if (!window.speechSynthesis) {
            console.error('❌ Speech Synthesis not supported');
            return;
        }
        console.log('✅ Speech Synthesis available');
        
        // Initialize immediately without waiting for voices
        this.setupBetterVoices();
        this.createFloatingPlayer();
        this.setupEventListeners();
        this.loadSettings();
        
        // Ensure voices are loaded
        if (this.synth.getVoices().length === 0) {
            console.log('⏳ Waiting for voices to load...');
            this.synth.addEventListener('voiceschanged', () => {
                console.log('🔄 Voices loaded, setting up...');
                this.setupBetterVoices();
                this.populateVoiceSelect();
            });
            // Also try after a short delay as fallback
            setTimeout(() => {
                if (this.availableVoices.length === 0) {
                    console.log('⚡ Fallback: Force loading voices');
                    this.setupBetterVoices();
                    this.populateVoiceSelect();
                }
            }, 1000);
            // Even more aggressive fallback
            setTimeout(() => {
                if (this.availableVoices.length === 0) {
                    console.log('🔄 Final fallback: Using all available voices');
                    const allVoices = this.synth.getVoices();
                    this.availableVoices = allVoices.length > 0 ? 
                        allVoices.slice(0, 10).map(v => ({...v, displayName: v.name})) :
                        [{name: 'Default', displayName: 'Default Voice', lang: 'en-US'}];
                    this.populateVoiceSelect();
                }
            }, 3000);
        } else {
            this.populateVoiceSelect();
        }
    }

    setupBetterVoices() {
        const voices = this.synth.getVoices();
        console.log(`🎙️ Raw voices available: ${voices.length}`);
        if (voices.length === 0) {
            console.warn('🚨 No voices available from speechSynthesis.getVoices()');
            return;
        }
        
        // Enhanced voice detection with proper labeling
        const voiceMap = new Map();
        
        voices.forEach(voice => {
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            
            // Skip low-quality voices
            if (name.includes('compact') || name.includes('monotone')) return;
            
            // Create descriptive labels
            let label = '';
            let category = 'other';
            
            // Google voices
            if (name.includes('google')) {
                if (lang.includes('en-us')) label = 'Google US English';
                else if (lang.includes('en-gb') || name.includes('uk english')) {
                    label = name.includes('male') ? 'Google UK English (Male)' : 'Google UK English (Female)';
                }
                else if (lang.includes('en-au')) label = 'Google Australian English';
                else if (lang.includes('en-in')) label = 'Google Indian English';
                else if (lang.includes('de')) label = 'Google German Accent';
                else if (lang.includes('es')) label = 'Google Spanish Accent';
                else if (lang.includes('fr')) label = 'Google French Accent';
                else if (lang.includes('zh')) label = 'Google Chinese Accent';
                else if (lang.includes('hi')) label = 'Google Hindi Accent';
                else label = `Google ${voice.name.replace(/Google\s*/i, '')}`;
                
                category = lang.includes('en') ? 'google-en' : 'google-accent';
            }
            // Microsoft voices
            else if (name.includes('microsoft') || name.includes('zira') || name.includes('david') || name.includes('hazel')) {
                if (name.includes('zira')) label = 'Microsoft Zira (US Female)';
                else if (name.includes('david')) label = 'Microsoft David (US Male)';
                else if (name.includes('hazel')) label = 'Microsoft Hazel (UK Female)';
                else if (name.includes('george')) label = 'Microsoft George (UK Male)';
                else if (name.includes('catherine')) label = 'Microsoft Catherine (Australian)';
                else if (name.includes('james')) label = 'Microsoft James (Australian Male)';
                else label = voice.name.replace(/Microsoft\s*|Desktop\s*-?\s*/gi, '');
                
                category = 'microsoft';
            }
            // macOS/iOS voices
            else if (['alex', 'samantha', 'victoria', 'daniel', 'karen', 'moira', 'tessa'].includes(name)) {
                const voiceNames = {
                    alex: 'Alex (US Male)',
                    samantha: 'Samantha (US Female)',  
                    victoria: 'Victoria (US Female)',
                    daniel: 'Daniel (UK Male)',
                    karen: 'Karen (Australian Female)',
                    moira: 'Moira (Irish Female)',
                    tessa: 'Tessa (South African Female)'
                };
                label = voiceNames[name] || `${voice.name} (Premium)`;
                category = 'premium';
            }
            else if (lang.includes('en')) {
                label = voice.name;
                category = 'english';
            }
            
            if (label && !voiceMap.has(label)) {
                voiceMap.set(label, { voice, label, category });
            }
        });
        
        // Convert to array and organize by category
        this.availableVoices = [];
        const categories = ['premium', 'microsoft', 'google-en', 'google-accent', 'english'];
        
        categories.forEach(cat => {
            const voicesInCategory = Array.from(voiceMap.values())
                .filter(v => v.category === cat)
                .sort((a, b) => a.label.localeCompare(b.label));
            this.availableVoices.push(...voicesInCategory.map(v => ({...v.voice, displayName: v.label})));
        });
        
        // Fallback if no voices found - especially important on mobile
        if (this.availableVoices.length === 0) {
            const englishVoices = voices.filter(v => v.lang.startsWith('en'));
            
            // Remove duplicates by creating a Map keyed by voice characteristics
            const uniqueVoices = new Map();
            englishVoices.forEach(voice => {
                const key = `${voice.name}_${voice.lang}_${voice.gender || 'unknown'}`;
                if (!uniqueVoices.has(key)) {
                    uniqueVoices.set(key, {
                        ...voice, 
                        displayName: this.createFallbackDisplayName(voice)
                    });
                }
            });
            
            this.availableVoices = Array.from(uniqueVoices.values()).slice(0, 12);
        }
        
        // Final deduplication by display name to avoid mobile duplicate issues
        const finalVoices = new Map();
        this.availableVoices.forEach(voice => {
            const displayName = voice.displayName || voice.name;
            if (!finalVoices.has(displayName)) {
                finalVoices.set(displayName, voice);
            }
        });
        this.availableVoices = Array.from(finalVoices.values());
        
        // Emergency fallback if no voices found after processing
        if (this.availableVoices.length === 0) {
            console.warn('No voices found after processing, using raw voices');
            const allVoices = this.synth.getVoices();
            this.availableVoices = allVoices.filter(v => v.lang.startsWith('en')).slice(0, 10)
                .map(v => ({...v, displayName: v.name}));
        }
        
        // Set default voice only if we have voices available
        if (!this.voice && this.availableVoices.length > 0) {
            // Always use the first available voice as default
            this.voice = this.availableVoices[0];
            console.log('🎯 Default voice set:', this.voice.name);
            
            // Update the dropdown to show selected voice
            const select = document.getElementById('voice-selector');
            if (select) {
                select.value = this.voice.name;
            }
        }
        
        console.log(`Podcast: Found ${this.availableVoices.length} quality voices:`, 
            this.availableVoices.map(v => v.displayName));
    }

    createFallbackDisplayName(voice) {
        const name = voice.name.toLowerCase();
        const lang = voice.lang.toLowerCase();
        
        // Try to create meaningful display names for mobile voices
        if (name.includes('daniel') || name === 'daniel') return 'Daniel (UK Male)';
        if (name.includes('synthia') || name === 'synthia') return 'Synthia (Female)';
        if (name.includes('karen') || name === 'karen') return 'Karen (Female)';
        if (name.includes('samantha') || name === 'samantha') return 'Samantha (US Female)';
        if (name.includes('alex') || name === 'alex') return 'Alex (US Male)';
        
        // For other voices, try to extract meaningful info
        if (lang.includes('gb') || lang.includes('uk')) {
            return `${voice.name} (UK)`;
        } else if (lang.includes('au')) {
            return `${voice.name} (Australian)`;
        } else if (lang.includes('us')) {
            return `${voice.name} (US)`;
        } else if (lang.includes('en')) {
            return `${voice.name} (English)`;
        }
        
        return voice.name;
    }

    createFloatingPlayer() {
        console.log('🏗️ Creating floating player...');
        
        // Check if CSS is loaded
        const testDiv = document.createElement('div');
        testDiv.className = 'pro-podcast-player';
        testDiv.style.position = 'absolute';
        testDiv.style.left = '-9999px';
        document.body.appendChild(testDiv);
        const computedStyle = window.getComputedStyle(testDiv);
        const cssLoaded = computedStyle.position === 'fixed';
        testDiv.remove();
        console.log('🎨 CSS loaded correctly:', cssLoaded);
        
        // Remove any existing player
        const existing = document.getElementById('professional-podcast-player');
        if (existing) existing.remove();

        const player = document.createElement('div');
        player.id = 'professional-podcast-player';
        player.className = 'pro-podcast-player minimized';
        
        player.innerHTML = `
            <div class="player-container">
                <!-- Minimized State -->
                <div class="minimized-controls">
                    <button class="expand-btn" id="expand-player" title="Open Podcast Player">
                        🎧
                    </button>
                </div>
                
                <!-- Expanded State -->
                <div class="expanded-controls" id="expanded-controls">
                    <div class="player-header">
                        <div class="player-title">
                            <span class="title">🎧 Podcast Mode</span>
                            <span class="subtitle">Learn while commuting</span>
                        </div>
                        <button class="minimize-btn" id="minimize-player" title="Minimize Player">×</button>
                    </div>
                    
                    <div class="current-content">
                        <div class="content-title" id="current-title">Ready to start</div>
                        <div class="content-progress">
                            <span id="progress-text">Section 0/0</span>
                        </div>
                    </div>
                    
                    <div class="main-controls">
                        <button id="prev-btn" class="control-btn" title="Previous" disabled>⏮</button>
                        <button id="play-pause-btn" class="control-btn play-btn" title="Play">▶️</button>
                        <button id="next-btn" class="control-btn" title="Next" disabled>⏭</button>
                    </div>
                    
                    <div class="audio-controls">
                        <div class="control-group">
                            <label>Voice:</label>
                            <select id="voice-selector" class="voice-select"></select>
                        </div>
                        
                        <div class="control-row">
                            <div class="control-group">
                                <label>Speed:</label>
                                <select id="speed-selector">
                                    <option value="0.75">0.75x</option>
                                    <option value="1.0" selected>1.0x</option>
                                    <option value="1.25">1.25x</option>
                                    <option value="1.5">1.5x</option>
                                    <option value="2.0">2.0x</option>
                                </select>
                            </div>
                            
                            <div class="control-group">
                                <label>Volume:</label>
                                <input type="range" id="volume-slider" min="0" max="1" step="0.1" value="0.8" class="volume-control">
                                <span id="volume-text">80%</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="content-filters">
                        <label>Content Path:</label>
                        <div class="filter-buttons">
                            <button class="filter-btn active" data-filter="all">All Content</button>
                            <button class="filter-btn" data-filter="observer">🎯 Observer</button>
                            <button class="filter-btn" data-filter="participant">📝 Participant</button>
                            <button class="filter-btn" data-filter="implementer">⚙️ Implementer</button>
                        </div>
                    </div>
                    
                    <div class="advanced-options">
                        <label>
                            <input type="checkbox" id="skip-emojis" checked> Skip emoji descriptions
                        </label>
                        <label>
                            <input type="checkbox" id="skip-code" checked> Skip code blocks
                        </label>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(player);
        this.playerElement = player;
    }

    setupEventListeners() {
        // Expand/Minimize controls
        document.getElementById('expand-player')?.addEventListener('click', () => {
            this.expandPlayer();
        });
        
        document.getElementById('minimize-player')?.addEventListener('click', () => {
            this.minimizePlayer();
        });

        // Main controls
        const playBtn = document.getElementById('play-pause-btn');
        console.log('🎛️ Setting up play button listener. Button found:', !!playBtn);
        
        playBtn?.addEventListener('click', () => {
            console.log('🎯 Play button clicked!');
            this.togglePlayback();
        });

        document.getElementById('prev-btn')?.addEventListener('click', () => {
            this.previousSection();
        });

        document.getElementById('next-btn')?.addEventListener('click', () => {
            this.nextSection();
        });

        // Audio controls with live updates
        document.getElementById('voice-selector')?.addEventListener('change', (e) => {
            this.changeVoice(e.target.value);
        });

        document.getElementById('speed-selector')?.addEventListener('change', (e) => {
            this.changeSpeed(parseFloat(e.target.value));
        });

        document.getElementById('volume-slider')?.addEventListener('input', (e) => {
            this.changeVolume(parseFloat(e.target.value));
        });

        // Content filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setContentFilter(e.target.dataset.filter);
            });
        });

        // Options
        document.getElementById('skip-emojis')?.addEventListener('change', () => {
            this.prepareContent();
        });

        document.getElementById('skip-code')?.addEventListener('change', () => {
            this.prepareContent();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch (e.code) {
                case 'Escape':
                    e.preventDefault();
                    if (this.playerElement.classList.contains('minimized')) {
                        this.resetPlayer();
                    } else {
                        this.minimizePlayer();
                    }
                    break;
                case 'Space':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.togglePlayback();
                    }
                    break;
                case 'ArrowRight':
                    if (e.ctrlKey && e.shiftKey) {
                        e.preventDefault();
                        this.nextSection();
                    }
                    break;
                case 'ArrowLeft':
                    if (e.ctrlKey && e.shiftKey) {
                        e.preventDefault();
                        this.previousSection();
                    }
                    break;
            }
        });
    }

    expandPlayer() {
        this.playerElement.classList.remove('minimized');
        this.prepareContent();
    }

    minimizePlayer() {
        console.log('🔽 Minimizing player');
        this.playerElement.classList.add('minimized');
    }

    resetPlayer() {
        console.log('🔄 Resetting player UI');
        this.playerElement.classList.remove('expanded');
        this.playerElement.classList.add('minimized');
        this.stop();
    }

    populateVoiceSelect() {
        const select = document.getElementById('voice-selector');
        if (!select) {
            console.warn('🚨 Voice selector element not found');
            return;
        }

        console.log(`🎤 Populating voice select with ${this.availableVoices.length} voices`);
        select.innerHTML = '';
        
        // Emergency check
        if (this.availableVoices.length === 0) {
            console.warn('🚨 No voices available to populate');
            const option = document.createElement('option');
            option.value = 'none';
            option.textContent = 'No voices available - Loading...';
            select.appendChild(option);
            return;
        }
        
        // Simple approach - just add all voices with their display names
        console.log('Adding voices to select:', this.availableVoices.map(v => v.displayName || v.name));
        
        this.availableVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.name;
            option.textContent = voice.displayName || voice.name;
            select.appendChild(option);
        });
        
        // Set current voice
        if (this.voice) {
            select.value = this.voice.name;
        }
    }

    getVoiceDisplayName(voice) {
        const name = voice.name;
        
        // Simplify voice names for better UX
        if (name.includes('Google UK English Female')) return 'Emma (British)';
        if (name.includes('Google UK English Male')) return 'James (British)';
        if (name.includes('Google US English')) return 'Sarah (American)';
        if (name.includes('Microsoft Zira')) return 'Zira (American)';
        if (name.includes('Microsoft David')) return 'David (American)';
        if (name.includes('Microsoft Hazel')) return 'Hazel (British)';
        if (name.includes('Microsoft George')) return 'George (British)';
        if (name.includes('Samantha')) return 'Samantha (Natural)';
        if (name.includes('Alex')) return 'Alex (Natural)';
        if (name.includes('Victoria')) return 'Victoria (Natural)';
        if (name.includes('Daniel')) return 'Daniel (Natural)';
        if (name.includes('Australian')) return name.includes('Female') ? 'Olivia (Australian)' : 'William (Australian)';
        if (name.includes('Indian')) return 'Priya (Indian English)';
        
        // Fallback to simplified name
        return name.split(' ')[0] || name;
    }

    changeVoice(voiceName) {
        const voice = this.availableVoices.find(v => v.name === voiceName);
        if (voice) {
            this.voice = voice;
            console.log('✅ Voice changed to:', voice.name);
            
            // Apply immediately if playing
            if (this.isPlaying) {
                this.applyLiveChanges();
            }
            
            this.saveSettings();
        } else {
            console.error('❌ Voice not found:', voiceName);
        }
    }

    changeSpeed(speed) {
        this.playbackRate = speed;
        
        // Apply immediately if playing
        if (this.isPlaying) {
            this.applyLiveChanges();
        }
        
        this.saveSettings();
    }

    changeVolume(volume) {
        this.volume = volume;
        document.getElementById('volume-text').textContent = Math.round(volume * 100) + '%';
        
        // Apply immediately if playing - restart utterance with new volume
        if (this.isPlaying && this.utterance) {
            this.applyLiveChanges();
        }
        
        this.saveSettings();
    }

    applyLiveChanges() {
        if (!this.isPlaying || !this.utterance) return;
        
        // Cancel current speech
        this.synth.cancel();
        
        // Restart current chunk with new settings
        setTimeout(() => {
            this.playCurrentChunk();
        }, 100);
    }

    setContentFilter(filter) {
        this.contentFilter = filter;
        
        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        
        // Reprocess content
        this.prepareContent();
        this.saveSettings();
    }

    prepareContent() {
        const content = this.extractPageContent();
        console.log('📄 Extracted content length:', content.length);
        this.textChunks = this.processTextChunks(content);
        this.currentChunkIndex = 0;
        
        console.log(`Podcast: Prepared ${this.textChunks.length} content chunks`);
        
        this.updateProgressDisplay();
        this.updateNavigationButtons();
        
        // Ensure navigation is enabled when content is available
        if (this.textChunks.length > 1) {
            document.getElementById('next-btn')?.removeAttribute('disabled');
        }
    }

    extractPageContent() {
        const skipCode = document.getElementById('skip-code')?.checked;
        const skipEmojis = document.getElementById('skip-emojis')?.checked;
        
        // Get main content area - compatible with GitHub Pages
        const contentSelectors = [
            '.md-content__inner',
            '[data-md-content]',
            'article',
            'main',
            '.content',
            'body'
        ];
        
        let contentArea;
        for (const selector of contentSelectors) {
            contentArea = document.querySelector(selector);
            if (contentArea) break;
        }
        
        if (!contentArea) {
            console.warn('Could not find content area');
            return [];
        }
        
        const textNodes = [];
        const walker = document.createTreeWalker(
            contentArea,
            NodeFilter.SHOW_ELEMENT,
            {
                acceptNode: (node) => {
                    // Skip podcast player itself
                    if (node.closest('#professional-podcast-player')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip navigation and sidebars
                    if (node.matches('nav, .md-nav, .md-sidebar, .md-header, .md-footer')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip code blocks if requested
                    if (skipCode && node.matches('code, pre, .codehilite, .highlight, .language-')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Filter by content path
                    if (this.contentFilter !== 'all') {
                        const pathEmojis = {
                            'observer': '🎯',
                            'participant': '📝',
                            'implementer': '⚙️'
                        };
                        
                        const targetEmoji = pathEmojis[this.contentFilter];
                        if (targetEmoji && !node.textContent.includes(targetEmoji)) {
                            // Skip sections that don't contain the target path emoji
                            const parent = node.closest('h1, h2, h3, section, div');
                            if (parent && !parent.textContent.includes(targetEmoji)) {
                                return NodeFilter.FILTER_REJECT;
                            }
                        }
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );
        
        let currentNode;
        while (currentNode = walker.nextNode()) {
            if (currentNode.matches('h1, h2, h3, h4, h5, h6')) {
                let headingText = currentNode.textContent.trim();
                
                // Clean up heading text
                if (skipEmojis) {
                    headingText = this.removeEmojis(headingText);
                }
                
                if (headingText) {
                    textNodes.push({
                        text: headingText,
                        type: 'heading',
                        level: currentNode.tagName.toLowerCase(),
                        element: currentNode
                    });
                }
            } else if (currentNode.matches('p, li, td, th, blockquote, .admonition-content')) {
                let text = currentNode.textContent.trim();
                
                // Clean up content text
                if (skipEmojis) {
                    text = this.removeEmojis(text);
                }
                
                // Remove common UI text
                text = text.replace(/^(Click|Tap|Select|Choose|Note:|Warning:|Info:)/i, '');
                
                if (text && text.length > 10) {
                    textNodes.push({
                        text: text,
                        type: 'content',
                        element: currentNode
                    });
                }
            }
        }
        
        return textNodes;
    }

    removeEmojis(text) {
        // Remove emoji characters and common emoji descriptions
        return text
            .replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '')
            .replace(/\s*(🎯|📝|⚙️|🚀|✅|❌|⭐|💡|🔥|🎉|🎊|👍|👎|🤔|💭|📚|📖|🎓|⭐|💯|🔧|🛠️|🎨|📊|📈|📉|🔍|🔎|🌟|⚡|🎭|🎪|🎨|🎯|🎲|🎳|🎮|🎻|🎺|🎸|🎤|🎧|🎬|🎥|📷|📹|🎞️|📽️|🎦|📺|📻|🎵|🎶|🎼|🎹|🥁|🎷|🎺|🎸|🎻|🎤|🎧|🎬|🎥|📷|📹|🎞️|📽️|🎦|📺|📻)\s*/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    processTextChunks(textNodes) {
        const chunks = [];
        let currentChunk = [];
        let currentLength = 0;
        const maxChunkLength = 400; // Optimal for TTS
        
        textNodes.forEach(node => {
            // Start new chunk with headings
            if (node.type === 'heading' && currentChunk.length > 0) {
                chunks.push(this.createChunk(currentChunk));
                currentChunk = [];
                currentLength = 0;
            }
            
            currentChunk.push(node);
            currentLength += node.text.length;
            
            // Split if chunk gets too long
            if (currentLength > maxChunkLength && currentChunk.length > 1) {
                chunks.push(this.createChunk(currentChunk));
                currentChunk = [];
                currentLength = 0;
            }
        });
        
        // Add remaining chunk
        if (currentChunk.length > 0) {
            chunks.push(this.createChunk(currentChunk));
        }
        
        return chunks;
    }

    createChunk(nodes) {
        const text = nodes.map(n => n.text).join(' ');
        const heading = nodes.find(n => n.type === 'heading');
        
        return {
            nodes: nodes,
            text: text,
            title: heading ? heading.text.substring(0, 50) : text.substring(0, 50) + '...'
        };
    }

    togglePlayback() {
        if (this.isPlaying && !this.isPaused) {
            this.pause();
        } else if (this.isPaused) {
            this.resume();
        } else {
            this.play();
        }
    }

    play() {
        // Ensure we have a voice before playing
        if (!this.voice) {
            this.setupBetterVoices();
            if (this.availableVoices.length > 0) {
                this.voice = this.availableVoices[0];
                console.log('🔧 Voice set on demand:', this.voice.name);
            } else {
                alert('No voices available. Please try again.');
                return;
            }
        }
        
        console.log('🎬 Play pressed. Voice:', this.voice ? this.voice.name : 'NO VOICE');
        
        if (this.textChunks.length === 0) {
            console.log('📝 Preparing content...');
            this.prepareContent();
            console.log('📝 Content prepared. Chunks:', this.textChunks.length);
            if (this.textChunks.length === 0) {
                alert('No content available to read. Please navigate to a page with text content.');
                return;
            }
        }
        
        this.playCurrentChunk();
    }

    playCurrentChunk() {
        if (this.currentChunkIndex >= this.textChunks.length) {
            this.stop();
            return;
        }
        
        const chunk = this.textChunks[this.currentChunkIndex];
        
        console.log('🎵 Playing chunk with voice:', this.voice ? this.voice.name : 'NO VOICE');
        
        // Cancel any existing speech
        this.synth.cancel();
        
        // Create new utterance
        this.utterance = new SpeechSynthesisUtterance(chunk.text);
        
        // Ensure we have a valid voice - force reload if needed
        if (!this.voice || this.voice === undefined) {
            this.setupBetterVoices();
            this.populateVoiceSelect();
            if (this.availableVoices.length > 0) {
                this.voice = this.availableVoices[0];
                console.log('🔧 Emergency voice fallback:', this.voice.name);
            } else {
                console.error('❌ No voices available at all!');
                return;
            }
        }
        
        this.utterance.voice = this.voice;
        this.utterance.rate = this.playbackRate;
        this.utterance.volume = this.volume;
        this.utterance.pitch = 1.0;
        
        // Event handlers
        this.utterance.onstart = () => {
            this.isPlaying = true;
            this.isPaused = false;
            this.updatePlayButton(true);
            this.updateCurrentContent(chunk);
            this.highlightCurrentSection(chunk);
        };
        
        this.utterance.onend = () => {
            this.currentChunkIndex++;
            if (this.currentChunkIndex < this.textChunks.length) {
                setTimeout(() => this.playCurrentChunk(), 200);
            } else {
                this.stop();
            }
        };
        
        this.utterance.onerror = (event) => {
            console.error('🚨 Speech synthesis error:', event.error, event.message);
            this.stop();
        };
        
        // Start speaking
        console.log('🎙️ About to call synth.speak()', {
            text: chunk.text.substring(0, 50) + '...',
            voice: this.utterance.voice ? this.utterance.voice.name : 'NO VOICE ON UTTERANCE',
            synthReady: !!this.synth,
            synthSpeaking: this.synth.speaking,
            synthPending: this.synth.pending
        });
        
        this.synth.speak(this.utterance);
        
        setTimeout(() => {
            console.log('📢 Speech state after speak():', {
                speaking: this.synth.speaking,
                pending: this.synth.pending,
                paused: this.synth.paused
            });
        }, 100);
        this.updateNavigationButtons();
        this.updateProgressDisplay();
    }

    pause() {
        this.synth.pause();
        this.isPaused = true;
        this.updatePlayButton(false);
    }

    resume() {
        this.synth.resume();
        this.isPaused = false;
        this.updatePlayButton(true);
    }

    stop() {
        this.synth.cancel();
        this.isPlaying = false;
        this.isPaused = false;
        this.updatePlayButton(false);
        this.removeHighlight();
        this.updateCurrentContent({ title: 'Stopped' });
    }

    previousSection() {
        if (this.currentChunkIndex > 0) {
            this.currentChunkIndex--;
            if (this.isPlaying) {
                this.playCurrentChunk();
            }
            this.updateProgressDisplay();
            this.updateNavigationButtons();
        }
    }

    nextSection() {
        if (this.currentChunkIndex < this.textChunks.length - 1) {
            this.currentChunkIndex++;
            if (this.isPlaying) {
                this.playCurrentChunk();
            }
            this.updateProgressDisplay();
            this.updateNavigationButtons();
        }
    }

    updatePlayButton(isPlaying) {
        const btn = document.getElementById('play-pause-btn');
        if (btn) {
            btn.textContent = isPlaying ? '⏸️' : '▶️';
            btn.title = isPlaying ? 'Pause' : 'Play';
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentChunkIndex <= 0 || this.textChunks.length <= 1;
        }
        if (nextBtn) {
            nextBtn.disabled = this.currentChunkIndex >= this.textChunks.length - 1 || this.textChunks.length <= 1;
        }
        
        console.log(`Navigation: chunk ${this.currentChunkIndex + 1}/${this.textChunks.length}, prev disabled: ${prevBtn?.disabled}, next disabled: ${nextBtn?.disabled}`);
    }

    updateCurrentContent(chunk) {
        const titleEl = document.getElementById('current-title');
        if (titleEl) {
            titleEl.textContent = chunk.title;
        }
        this.updateProgressDisplay();
    }

    updateProgressDisplay() {
        const progressEl = document.getElementById('progress-text');
        if (progressEl) {
            progressEl.textContent = `Section ${this.currentChunkIndex + 1}/${this.textChunks.length}`;
        }
    }

    highlightCurrentSection(chunk) {
        this.removeHighlight();
        
        if (chunk.nodes && chunk.nodes.length > 0) {
            chunk.nodes.forEach(node => {
                if (node.element) {
                    node.element.classList.add('podcast-highlight');
                }
            });
            
            // Scroll to first element
            const firstElement = chunk.nodes[0].element;
            if (firstElement) {
                firstElement.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
        }
    }

    removeHighlight() {
        document.querySelectorAll('.podcast-highlight').forEach(el => {
            el.classList.remove('podcast-highlight');
        });
    }

    saveSettings() {
        const settings = {
            voice: this.voice?.name,
            playbackRate: this.playbackRate,
            volume: this.volume,
            contentFilter: this.contentFilter,
            skipEmojis: document.getElementById('skip-emojis')?.checked ?? true,
            skipCode: document.getElementById('skip-code')?.checked ?? true
        };
        localStorage.setItem('professionalPodcastSettings', JSON.stringify(settings));
    }

    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('professionalPodcastSettings') || '{}');
            
            if (settings.voice) {
                const voice = this.availableVoices.find(v => v.name === settings.voice);
                if (voice) this.voice = voice;
            }
            
            if (settings.playbackRate) {
                this.playbackRate = settings.playbackRate;
                const speedSelect = document.getElementById('speed-selector');
                if (speedSelect) speedSelect.value = settings.playbackRate;
            }
            
            if (settings.volume !== undefined) {
                this.volume = settings.volume;
                const volumeSlider = document.getElementById('volume-slider');
                const volumeText = document.getElementById('volume-text');
                if (volumeSlider) volumeSlider.value = settings.volume;
                if (volumeText) volumeText.textContent = Math.round(settings.volume * 100) + '%';
            }
            
            if (settings.contentFilter) {
                this.contentFilter = settings.contentFilter;
                const activeBtn = document.querySelector(`[data-filter="${settings.contentFilter}"]`);
                if (activeBtn) {
                    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                    activeBtn.classList.add('active');
                }
            }
            
            if (settings.skipEmojis !== undefined) {
                const checkbox = document.getElementById('skip-emojis');
                if (checkbox) checkbox.checked = settings.skipEmojis;
            }
            
            if (settings.skipCode !== undefined) {
                const checkbox = document.getElementById('skip-code');
                if (checkbox) checkbox.checked = settings.skipCode;
            }
            
        } catch (error) {
            console.log('Could not load podcast settings:', error);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.professionalPodcast = new ProfessionalPodcastTTS();
    });
} else {
    window.professionalPodcast = new ProfessionalPodcastTTS();
}

// Export for manual initialization
window.ProfessionalPodcastTTS = ProfessionalPodcastTTS;