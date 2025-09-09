/**
 * Podcast TTS (Text-to-Speech) Feature for Agentic AI Nano-Degree
 * 
 * This module provides a comprehensive podcast listening experience
 * by converting markdown content to speech using the Web Speech API.
 * Perfect for listening while commuting or driving.
 */

class PodcastTTS {
    constructor() {
        this.synth = window.speechSynthesis;
        this.utterance = null;
        this.isPlaying = false;
        this.isPaused = false;
        this.currentPosition = 0;
        this.textChunks = [];
        this.currentChunkIndex = 0;
        this.playbackRate = 1.0;
        this.voice = null;
        this.volume = 0.8;
        
        // Voice recording properties
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.customVoiceData = null;
        this.isRecording = false;
        this.recordingStartTime = null;
        this.recordingTimer = null;
        
        this.init();
    }

    init() {
        // Wait for voices to load
        if (this.synth.getVoices().length === 0) {
            this.synth.addEventListener('voiceschanged', () => {
                this.setupVoices();
            });
        } else {
            this.setupVoices();
        }

        this.createPodcastPlayer();
        this.setupEventListeners();
        this.loadSettings();
    }

    setupVoices() {
        const voices = this.synth.getVoices();
        
        // Prefer English voices, prioritize neural/premium voices
        const preferredVoices = [
            'Google US English',
            'Microsoft Zira Desktop',
            'Alex',
            'Samantha',
            'Microsoft David Desktop',
            'Google UK English Female',
            'Google UK English Male'
        ];

        // Find the best available voice
        for (const preferred of preferredVoices) {
            const voice = voices.find(v => v.name === preferred);
            if (voice) {
                this.voice = voice;
                break;
            }
        }

        // Fallback to first English voice
        if (!this.voice) {
            this.voice = voices.find(v => v.lang.startsWith('en')) || voices[0];
        }

        console.log(`Podcast TTS: Using voice "${this.voice.name}" (${this.voice.lang})`);
    }

    createPodcastPlayer() {
        const player = document.createElement('div');
        player.className = 'podcast-player collapsed';
        player.innerHTML = `
            <div class="podcast-controls">
                <div class="podcast-header" id="podcast-header">
                    <div class="podcast-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM9.5 14.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5zM12 17.5c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zm0-2c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zm0-2c-.28 0-.5-.22-.5-.5s.22-.5.5-.5.5.22.5.5-.22.5-.5.5zm2.5 1.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5z"/>
                        </svg>
                    </div>
                    <div class="podcast-title">
                        <span class="podcast-label">🎧 Podcast Mode</span>
                        <span class="podcast-subtitle">Listen while driving or commuting</span>
                    </div>
                    <div class="podcast-toggle">
                        <button id="podcast-toggle-btn" title="Toggle Podcast Player">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M7 14l5-5 5 5z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="podcast-player-content" id="podcast-player-content" style="display: block;">
                    <div class="podcast-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                            <div class="progress-handle" id="progress-handle"></div>
                        </div>
                        <div class="progress-time">
                            <span id="current-time">0:00</span>
                            <span id="total-time">--:--</span>
                        </div>
                    </div>

                    <div class="podcast-main-controls">
                        <button id="podcast-prev" title="Previous Section" disabled>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
                            </svg>
                        </button>
                        
                        <button id="podcast-play-pause" class="play-pause-btn" title="Play/Pause">
                            <svg class="play-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M8 5v14l11-7z"/>
                            </svg>
                            <svg class="pause-icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" style="display: none;">
                                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                            </svg>
                        </button>
                        
                        <button id="podcast-next" title="Next Section" disabled>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
                            </svg>
                        </button>
                    </div>

                    <div class="podcast-settings">
                        <div class="setting-group">
                            <label for="voice-select">Voice:</label>
                            <select id="voice-select"></select>
                        </div>
                        
                        <div class="setting-group">
                            <label for="speed-control">Speed:</label>
                            <select id="speed-control">
                                <option value="0.75">0.75x</option>
                                <option value="1.0" selected>1.0x</option>
                                <option value="1.25">1.25x</option>
                                <option value="1.5">1.5x</option>
                                <option value="1.75">1.75x</option>
                                <option value="2.0">2.0x</option>
                            </select>
                        </div>

                        <div class="setting-group">
                            <label for="volume-control">Volume:</label>
                            <input type="range" id="volume-control" min="0" max="1" step="0.1" value="0.8">
                            <span id="volume-display">80%</span>
                        </div>
                    </div>

                    <div class="podcast-content-info">
                        <div class="current-section" id="current-section">Ready to start podcast</div>
                        <div class="content-filter">
                            <label>
                                <input type="checkbox" id="skip-code" checked>
                                Skip code blocks
                            </label>
                            <label>
                                <input type="checkbox" id="include-headings" checked>
                                Include section headings
                            </label>
                        </div>
                    </div>
                    
                    <div class="voice-recording-section">
                        <button id="record-voice-btn" class="record-btn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                            </svg>
                            <span>Record Custom Voice</span>
                        </button>
                        <div id="recording-status" class="recording-status" style="display: none;">
                            <span class="recording-indicator"></span>
                            <span class="recording-text">Recording...</span>
                            <span class="recording-time" id="recording-time">0:00</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insert into body as fixed element
        document.body.appendChild(player);
        this.playerElement = player;
    }

    setupEventListeners() {
        // Toggle player visibility on header click
        const header = document.getElementById('podcast-header');
        if (header) {
            header.addEventListener('click', () => {
                this.togglePlayerVisibility();
            });
        }
        
        // Also handle toggle button
        const toggleBtn = document.getElementById('podcast-toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePlayerVisibility();
            });
        }

        // Play/Pause button
        document.getElementById('podcast-play-pause').addEventListener('click', () => {
            this.togglePlayback();
        });

        // Previous/Next buttons
        document.getElementById('podcast-prev').addEventListener('click', () => {
            this.previousSection();
        });

        document.getElementById('podcast-next').addEventListener('click', () => {
            this.nextSection();
        });

        // Voice selection with proper handling
        const voiceSelect = document.getElementById('voice-select');
        if (voiceSelect) {
            // Populate voices after a delay to ensure they're loaded
            setTimeout(() => this.populateVoiceSelect(), 100);
            
            voiceSelect.addEventListener('change', (e) => {
                if (e.target.value === 'custom') {
                    // Use custom voice
                    this.voice = 'custom';
                } else {
                    // Use system voice
                    const voices = this.synth.getVoices();
                    this.voice = voices.find(v => v.name === e.target.value);
                }
                
                // If currently playing, restart with new voice
                if (this.isPlaying) {
                    const currentChunk = this.currentChunkIndex;
                    this.stop();
                    this.currentChunkIndex = currentChunk;
                    this.play();
                }
                
                this.saveSettings();
            });
        }

        // Speed control with immediate effect
        const speedControl = document.getElementById('speed-control');
        if (speedControl) {
            speedControl.addEventListener('change', (e) => {
                this.playbackRate = parseFloat(e.target.value);
                
                // If currently playing, restart with new speed
                if (this.isPlaying) {
                    const currentChunk = this.currentChunkIndex;
                    this.stop();
                    this.currentChunkIndex = currentChunk;
                    this.play();
                }
                
                this.saveSettings();
            });
        }

        // Volume control with immediate feedback
        const volumeControl = document.getElementById('volume-control');
        if (volumeControl) {
            volumeControl.addEventListener('input', (e) => {
                this.volume = parseFloat(e.target.value);
                const volumeDisplay = document.getElementById('volume-display');
                if (volumeDisplay) {
                    volumeDisplay.textContent = Math.round(this.volume * 100) + '%';
                }
                
                // Apply to current utterance if playing
                if (this.utterance) {
                    this.utterance.volume = this.volume;
                }
                
                this.saveSettings();
            });
        }

        // Content filter checkboxes
        const skipCode = document.getElementById('skip-code');
        if (skipCode) {
            skipCode.addEventListener('change', () => {
                this.saveSettings();
                if (this.textChunks.length > 0) {
                    this.prepareContent();
                }
            });
        }

        const includeHeadings = document.getElementById('include-headings');
        if (includeHeadings) {
            includeHeadings.addEventListener('change', () => {
                this.saveSettings();
                if (this.textChunks.length > 0) {
                    this.prepareContent();
                }
            });
        }
        
        // Voice recording button
        const recordBtn = document.getElementById('record-voice-btn');
        if (recordBtn) {
            recordBtn.addEventListener('click', () => {
                this.toggleVoiceRecording();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Only if not typing in input/textarea
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
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
            }
        });

        // Page navigation - auto-prepare new content
        if (typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
            // For instant loading, hook into navigation events
            const observer = new MutationObserver(() => {
                if (!this.isPlaying) {
                    setTimeout(() => this.prepareContent(), 100);
                }
            });
            
            observer.observe(document.querySelector('.md-content') || document.body, {
                childList: true,
                subtree: true
            });
        }
    }

    populateVoiceSelect() {
        const voiceSelect = document.getElementById('voice-select');
        if (!voiceSelect) return;
        
        const voices = this.synth.getVoices();
        
        voiceSelect.innerHTML = '';
        
        // Group voices by language for better organization
        const voicesByLang = {};
        
        voices.forEach(voice => {
            const lang = voice.lang.substring(0, 2);
            if (!voicesByLang[lang]) {
                voicesByLang[lang] = [];
            }
            voicesByLang[lang].push(voice);
        });
        
        // Add English voices first (including British, Australian, etc.)
        if (voicesByLang['en']) {
            const englishGroup = document.createElement('optgroup');
            englishGroup.label = 'English Voices';
            
            // Sort to prioritize certain accents
            const englishVoices = voicesByLang['en'].sort((a, b) => {
                // Prioritize certain accents/regions
                const priorities = ['GB', 'UK', 'AU', 'US', 'IE', 'IN'];
                const aPriority = priorities.findIndex(p => a.lang.includes(p));
                const bPriority = priorities.findIndex(p => b.lang.includes(p));
                
                if (aPriority !== -1 && bPriority !== -1) {
                    return aPriority - bPriority;
                }
                return a.name.localeCompare(b.name);
            });
            
            englishVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                
                // Better voice description
                let description = voice.name;
                if (voice.lang.includes('GB') || voice.lang.includes('UK')) {
                    description += ' (British)';
                } else if (voice.lang.includes('AU')) {
                    description += ' (Australian)';
                } else if (voice.lang.includes('US')) {
                    description += ' (American)';
                } else if (voice.lang.includes('IE')) {
                    description += ' (Irish)';
                } else if (voice.lang.includes('IN')) {
                    description += ' (Indian)';
                } else {
                    description += ` (${voice.lang})`;
                }
                
                option.textContent = description;
                option.selected = voice.name === this.voice?.name;
                englishGroup.appendChild(option);
            });
            voiceSelect.appendChild(englishGroup);
        }
        
        // Add German voices (for Bavarian preference)
        if (voicesByLang['de']) {
            const germanGroup = document.createElement('optgroup');
            germanGroup.label = 'German Voices';
            voicesByLang['de'].forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${voice.name} (German)`;
                germanGroup.appendChild(option);
            });
            voiceSelect.appendChild(germanGroup);
        }
        
        // Add other languages
        Object.keys(voicesByLang).forEach(lang => {
            if (lang !== 'en' && lang !== 'de') {
                const group = document.createElement('optgroup');
                group.label = `Other (${lang.toUpperCase()})`;
                voicesByLang[lang].forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = `${voice.name} (${voice.lang})`;
                    group.appendChild(option);
                });
                voiceSelect.appendChild(group);
            }
        });
        
        // Add custom voice option if available
        if (this.customVoiceData) {
            const customGroup = document.createElement('optgroup');
            customGroup.label = 'Custom Voice';
            const option = document.createElement('option');
            option.value = 'custom';
            option.textContent = 'Your Recorded Voice';
            customGroup.appendChild(option);
            voiceSelect.insertBefore(customGroup, voiceSelect.firstChild);
        }
    }

    togglePlayerVisibility() {
        const player = this.playerElement;
        const toggleBtn = document.getElementById('podcast-toggle-btn');
        const isCollapsed = player.classList.contains('collapsed');
        
        if (isCollapsed) {
            // Expand player
            player.classList.remove('collapsed');
            toggleBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 10l5 5 5-5z"/>
                </svg>
            `;
            toggleBtn.title = 'Collapse Podcast Player';
            this.prepareContent();
        } else {
            // Collapse player
            player.classList.add('collapsed');
            toggleBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 14l5-5 5 5z"/>
                </svg>
            `;
            toggleBtn.title = 'Expand Podcast Player';
        }
    }

    prepareContent() {
        const content = this.extractPageContent();
        this.textChunks = this.splitIntoChunks(content);
        this.currentChunkIndex = 0;
        
        // Update UI
        document.getElementById('current-section').textContent = 
            this.textChunks.length > 0 ? 'Ready to start podcast' : 'No content available';
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }

    extractPageContent() {
        const skipCode = document.getElementById('skip-code').checked;
        const includeHeadings = document.getElementById('include-headings').checked;
        
        // Get main content area
        const contentArea = document.querySelector('.md-content__inner') || 
                           document.querySelector('article') ||
                           document.querySelector('main') ||
                           document.body;
        
        let textContent = '';
        
        // Extract content while respecting filters
        const walker = document.createTreeWalker(
            contentArea,
            NodeFilter.SHOW_ELEMENT,
            {
                acceptNode: (node) => {
                    // Skip podcast player itself
                    if (node.closest('.podcast-player')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip navigation, code blocks if requested
                    if (node.matches('nav, .md-nav, .md-sidebar')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    if (skipCode && node.matches('code, pre, .codehilite, .highlight')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );
        
        const textNodes = [];
        let currentNode;
        
        while (currentNode = walker.nextNode()) {
            // Handle headings
            if (includeHeadings && currentNode.matches('h1, h2, h3, h4, h5, h6')) {
                const level = currentNode.tagName.toLowerCase();
                const headingText = currentNode.textContent.trim();
                if (headingText) {
                    textNodes.push({
                        text: headingText,
                        type: 'heading',
                        level: level,
                        element: currentNode
                    });
                }
            }
            // Handle paragraphs and other text content
            else if (currentNode.matches('p, li, td, th, blockquote, .admonition')) {
                const text = currentNode.textContent.trim();
                if (text && text.length > 20) { // Skip very short content
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

    splitIntoChunks(textNodes) {
        const chunks = [];
        let currentChunk = [];
        let currentLength = 0;
        const maxChunkLength = 500; // Optimal for TTS
        
        textNodes.forEach((node, index) => {
            // Always start new chunk with headings
            if (node.type === 'heading' && currentChunk.length > 0) {
                chunks.push({
                    nodes: [...currentChunk],
                    text: currentChunk.map(n => n.text).join(' '),
                    title: this.generateChunkTitle(currentChunk)
                });
                currentChunk = [];
                currentLength = 0;
            }
            
            currentChunk.push(node);
            currentLength += node.text.length;
            
            // Split long chunks
            if (currentLength > maxChunkLength && currentChunk.length > 1) {
                chunks.push({
                    nodes: [...currentChunk],
                    text: currentChunk.map(n => n.text).join(' '),
                    title: this.generateChunkTitle(currentChunk)
                });
                currentChunk = [];
                currentLength = 0;
            }
        });
        
        // Add remaining content
        if (currentChunk.length > 0) {
            chunks.push({
                nodes: [...currentChunk],
                text: currentChunk.map(n => n.text).join(' '),
                title: this.generateChunkTitle(currentChunk)
            });
        }
        
        return chunks;
    }

    generateChunkTitle(nodes) {
        // Find the first heading in the chunk
        const heading = nodes.find(n => n.type === 'heading');
        if (heading) {
            return heading.text.substring(0, 50);
        }
        
        // Use first content snippet
        const firstContent = nodes.find(n => n.type === 'content');
        if (firstContent) {
            return firstContent.text.substring(0, 50) + '...';
        }
        
        return 'Content Section';
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
        
        if (this.currentChunkIndex >= this.textChunks.length) {
            this.currentChunkIndex = 0;
        }
        
        this.playCurrentChunk();
    }

    playCurrentChunk() {
        if (this.currentChunkIndex >= this.textChunks.length) {
            this.stop();
            return;
        }
        
        const chunk = this.textChunks[this.currentChunkIndex];
        
        // Check if using custom voice
        if (this.voice === 'custom' && this.customVoiceData) {
            this.playWithCustomVoice(chunk.text);
            return;
        }
        
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
            this.updateCurrentSection(chunk.title);
            this.highlightCurrentSection(chunk);
        };
        
        this.utterance.onend = () => {
            this.currentChunkIndex++;
            if (this.currentChunkIndex < this.textChunks.length) {
                // Auto-continue to next chunk
                setTimeout(() => this.playCurrentChunk(), 100);
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
        document.getElementById('current-section').textContent = 'Stopped';
    }

    previousSection() {
        if (this.currentChunkIndex > 0) {
            this.currentChunkIndex--;
            if (this.isPlaying) {
                this.playCurrentChunk();
            }
        }
        this.updateNavigationButtons();
    }

    nextSection() {
        if (this.currentChunkIndex < this.textChunks.length - 1) {
            this.currentChunkIndex++;
            if (this.isPlaying) {
                this.playCurrentChunk();
            }
        }
        this.updateNavigationButtons();
    }

    updatePlayButton(isPlaying) {
        const button = document.getElementById('podcast-play-pause');
        const playIcon = button.querySelector('.play-icon');
        const pauseIcon = button.querySelector('.pause-icon');
        
        if (isPlaying) {
            playIcon.style.display = 'none';
            pauseIcon.style.display = 'block';
            button.title = 'Pause';
        } else {
            playIcon.style.display = 'block';
            pauseIcon.style.display = 'none';
            button.title = 'Play';
        }
    }

    updateNavigationButtons() {
        document.getElementById('podcast-prev').disabled = this.currentChunkIndex <= 0;
        document.getElementById('podcast-next').disabled = this.currentChunkIndex >= this.textChunks.length - 1;
    }

    updateCurrentSection(title) {
        document.getElementById('current-section').textContent = 
            `Section ${this.currentChunkIndex + 1}/${this.textChunks.length}: ${title}`;
    }

    highlightCurrentSection(chunk) {
        // Remove previous highlight
        this.removeHighlight();
        
        // Highlight current section
        if (chunk.nodes && chunk.nodes.length > 0) {
            chunk.nodes.forEach(node => {
                if (node.element) {
                    node.element.classList.add('podcast-current-section');
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
        document.querySelectorAll('.podcast-current-section').forEach(element => {
            element.classList.remove('podcast-current-section');
        });
    }

    saveSettings() {
        const skipCode = document.getElementById('skip-code');
        const includeHeadings = document.getElementById('include-headings');
        
        const settings = {
            voice: this.voice === 'custom' ? 'custom' : this.voice?.name,
            playbackRate: this.playbackRate,
            volume: this.volume,
            skipCode: skipCode ? skipCode.checked : true,
            includeHeadings: includeHeadings ? includeHeadings.checked : true
        };
        localStorage.setItem('podcastTTSSettings', JSON.stringify(settings));
    }

    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('podcastTTSSettings') || '{}');
            
            if (settings.voice) {
                if (settings.voice === 'custom' && this.customVoiceData) {
                    this.voice = 'custom';
                } else {
                    const voices = this.synth.getVoices();
                    const savedVoice = voices.find(v => v.name === settings.voice);
                    if (savedVoice) this.voice = savedVoice;
                }
            }
            
            if (settings.playbackRate) {
                this.playbackRate = settings.playbackRate;
                const speedControl = document.getElementById('speed-control');
                if (speedControl) speedControl.value = settings.playbackRate;
            }
            
            if (settings.volume !== undefined) {
                this.volume = settings.volume;
                const volumeControl = document.getElementById('volume-control');
                const volumeDisplay = document.getElementById('volume-display');
                if (volumeControl) volumeControl.value = settings.volume;
                if (volumeDisplay) volumeDisplay.textContent = Math.round(settings.volume * 100) + '%';
            }
            
            if (settings.skipCode !== undefined) {
                const skipCode = document.getElementById('skip-code');
                if (skipCode) skipCode.checked = settings.skipCode;
            }
            
            if (settings.includeHeadings !== undefined) {
                const includeHeadings = document.getElementById('include-headings');
                if (includeHeadings) includeHeadings.checked = settings.includeHeadings;
            }
            
            // Load custom voice if available
            const customVoice = localStorage.getItem('podcastCustomVoice');
            if (customVoice) {
                this.customVoiceData = customVoice;
                this.populateVoiceSelect();
            }
            
        } catch (error) {
            console.log('Could not load TTS settings:', error);
        }
    }
    
    // Voice Recording Methods
    async toggleVoiceRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    
    async startRecording() {
        try {
            // Request microphone permission
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm'
            });
            
            this.audioChunks = [];
            
            this.mediaRecorder.addEventListener('dataavailable', event => {
                this.audioChunks.push(event.data);
            });
            
            this.mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.processRecordedAudio(audioBlob);
            });
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            // Update UI
            const recordBtn = document.getElementById('record-voice-btn');
            const recordingStatus = document.getElementById('recording-status');
            
            if (recordBtn) {
                recordBtn.classList.add('recording');
                recordBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <rect x="9" y="9" width="6" height="6" rx="1"/>
                    </svg>
                    <span>Stop Recording</span>
                `;
            }
            
            if (recordingStatus) {
                recordingStatus.style.display = 'flex';
            }
            
            // Start timer
            this.recordingTimer = setInterval(() => {
                const elapsed = Date.now() - this.recordingStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                const timeDisplay = document.getElementById('recording-time');
                if (timeDisplay) {
                    timeDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            }, 100);
            
        } catch (error) {
            console.error('Failed to start recording:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            // Clear timer
            if (this.recordingTimer) {
                clearInterval(this.recordingTimer);
                this.recordingTimer = null;
            }
            
            // Update UI
            const recordBtn = document.getElementById('record-voice-btn');
            const recordingStatus = document.getElementById('recording-status');
            
            if (recordBtn) {
                recordBtn.classList.remove('recording');
                recordBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
                    </svg>
                    <span>Record Custom Voice</span>
                `;
            }
            
            if (recordingStatus) {
                recordingStatus.style.display = 'none';
            }
        }
    }
    
    async processRecordedAudio(audioBlob) {
        // Convert to base64 for storage
        const reader = new FileReader();
        reader.onloadend = () => {
            this.customVoiceData = reader.result;
            
            // Save to localStorage
            localStorage.setItem('podcastCustomVoice', this.customVoiceData);
            
            // Update voice selector
            this.populateVoiceSelect();
            
            // Select custom voice
            const voiceSelect = document.getElementById('voice-select');
            if (voiceSelect) {
                voiceSelect.value = 'custom';
                this.voice = 'custom';
            }
            
            alert('Custom voice recorded successfully! It will now be used for playback.');
        };
        reader.readAsDataURL(audioBlob);
    }
    
    playWithCustomVoice(text) {
        if (!this.customVoiceData) {
            // Fallback to regular TTS
            return this.playWithSynthesis(text);
        }
        
        // Play custom voice audio
        const audio = new Audio(this.customVoiceData);
        audio.playbackRate = this.playbackRate;
        audio.volume = this.volume;
        
        audio.onended = () => {
            this.currentChunkIndex++;
            if (this.currentChunkIndex < this.textChunks.length) {
                setTimeout(() => this.playCurrentChunk(), 100);
            } else {
                this.stop();
            }
        };
        
        audio.play();
        
        this.isPlaying = true;
        this.isPaused = false;
        this.updatePlayButton(true);
        
        const chunk = this.textChunks[this.currentChunkIndex];
        this.updateCurrentSection(chunk.title);
        this.highlightCurrentSection(chunk);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.podcastTTS = new PodcastTTS();
    });
} else {
    window.podcastTTS = new PodcastTTS();
}

// Export for manual initialization if needed
window.PodcastTTS = PodcastTTS;