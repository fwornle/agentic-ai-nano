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
        // Initialize immediately without waiting for voices
        this.setupBetterVoices();
        this.createFloatingPlayer();
        this.setupEventListeners();
        this.loadSettings();
        
        // Ensure voices are loaded
        if (this.synth.getVoices().length === 0) {
            this.synth.addEventListener('voiceschanged', () => {
                this.setupBetterVoices();
                this.populateVoiceSelect();
            });
        } else {
            this.populateVoiceSelect();
        }
    }

    setupBetterVoices() {
        const voices = this.synth.getVoices();
        
        // Curated list of high-quality voices only
        const qualityVoices = [
            // English - Premium/Natural voices
            'Google US English', 'Google UK English Female', 'Google UK English Male',
            'Microsoft Zira Desktop - English (United States)',
            'Microsoft David Desktop - English (United States)',
            'Microsoft Hazel Desktop - English (Great Britain)',
            'Microsoft George Desktop - English (Great Britain)',
            'Alex', 'Samantha', 'Victoria', 'Daniel',
            
            // International English accents for entertainment
            'Google Australian English Female', 'Google Indian English Female',
            'Microsoft Catherine Desktop - English (Australia)',
            'Microsoft James Desktop - English (Australia)',
            
            // Non-native English speakers for entertainment
            'Google Deutsch', 'Google español', 'Google français'
        ];
        
        // Filter to only quality voices that are available
        this.availableVoices = voices.filter(voice => {
            return qualityVoices.some(quality => 
                voice.name.includes(quality) || 
                (voice.lang.startsWith('en') && voice.name.toLowerCase().includes('neural'))
            );
        });
        
        // If no quality voices found, fall back to best English voices
        if (this.availableVoices.length === 0) {
            this.availableVoices = voices.filter(v => 
                v.lang.startsWith('en') && !v.name.toLowerCase().includes('compact')
            ).slice(0, 10);
        }
        
        // Set default to best available voice
        if (!this.voice) {
            this.voice = this.availableVoices.find(v => 
                v.name.includes('Google UK English Female') || 
                v.name.includes('Samantha') ||
                v.name.includes('Microsoft Zira')
            ) || this.availableVoices[0];
        }
        
        console.log(`Podcast: Using ${this.availableVoices.length} quality voices`);
    }

    createFloatingPlayer() {
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
        document.getElementById('play-pause-btn')?.addEventListener('click', () => {
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
        this.playerElement.classList.add('minimized');
    }

    populateVoiceSelect() {
        const select = document.getElementById('voice-selector');
        if (!select) return;

        select.innerHTML = '';
        
        // Group voices by type
        const maleVoices = [];
        const femaleVoices = [];
        const accentVoices = [];
        
        this.availableVoices.forEach(voice => {
            const name = voice.name.toLowerCase();
            if (name.includes('male') && !name.includes('female')) {
                maleVoices.push(voice);
            } else if (name.includes('female') || name.includes('samantha') || name.includes('zira') || name.includes('catherine')) {
                femaleVoices.push(voice);
            } else if (voice.lang.startsWith('en') && (name.includes('australian') || name.includes('indian') || name.includes('irish'))) {
                accentVoices.push(voice);
            } else {
                femaleVoices.push(voice); // Default to female group
            }
        });
        
        // Add grouped options
        if (femaleVoices.length > 0) {
            const group = document.createElement('optgroup');
            group.label = '🎙️ Female Voices';
            femaleVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = this.getVoiceDisplayName(voice);
                group.appendChild(option);
            });
            select.appendChild(group);
        }
        
        if (maleVoices.length > 0) {
            const group = document.createElement('optgroup');
            group.label = '🎙️ Male Voices';
            maleVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = this.getVoiceDisplayName(voice);
                group.appendChild(option);
            });
            select.appendChild(group);
        }
        
        if (accentVoices.length > 0) {
            const group = document.createElement('optgroup');
            group.label = '🌍 International Accents';
            accentVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = this.getVoiceDisplayName(voice);
                group.appendChild(option);
            });
            select.appendChild(group);
        }
        
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
            
            // Apply immediately if playing
            if (this.isPlaying) {
                this.applyLiveChanges();
            }
            
            this.saveSettings();
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
        
        // Apply immediately if playing
        if (this.utterance) {
            this.utterance.volume = volume;
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
        this.textChunks = this.processTextChunks(content);
        this.currentChunkIndex = 0;
        
        this.updateProgressDisplay();
        this.updateNavigationButtons();
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
        if (this.textChunks.length === 0) {
            this.prepareContent();
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
        
        // Cancel any existing speech
        this.synth.cancel();
        
        // Create new utterance
        this.utterance = new SpeechSynthesisUtterance(chunk.text);
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
            console.error('Speech synthesis error:', event);
            this.stop();
        };
        
        // Start speaking
        this.synth.speak(this.utterance);
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
        
        if (prevBtn) prevBtn.disabled = this.currentChunkIndex <= 0;
        if (nextBtn) nextBtn.disabled = this.currentChunkIndex >= this.textChunks.length - 1;
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