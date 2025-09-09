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
        player.className = 'podcast-player';
        player.innerHTML = `
            <div class="podcast-controls">
                <div class="podcast-header">
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
                                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="podcast-player-content" id="podcast-player-content">
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
                </div>
            </div>
        `;

        // Insert at the top of the content area
        const contentArea = document.querySelector('.md-main__inner') || document.body;
        contentArea.insertBefore(player, contentArea.firstChild);

        this.playerElement = player;
    }

    setupEventListeners() {
        // Toggle player visibility
        document.getElementById('podcast-toggle-btn').addEventListener('click', () => {
            this.togglePlayerVisibility();
        });

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

        // Voice selection
        const voiceSelect = document.getElementById('voice-select');
        this.populateVoiceSelect();
        voiceSelect.addEventListener('change', (e) => {
            const voices = this.synth.getVoices();
            this.voice = voices.find(v => v.name === e.target.value);
            this.saveSettings();
        });

        // Speed control
        document.getElementById('speed-control').addEventListener('change', (e) => {
            this.playbackRate = parseFloat(e.target.value);
            if (this.utterance) {
                this.utterance.rate = this.playbackRate;
            }
            this.saveSettings();
        });

        // Volume control
        const volumeControl = document.getElementById('volume-control');
        volumeControl.addEventListener('input', (e) => {
            this.volume = parseFloat(e.target.value);
            document.getElementById('volume-display').textContent = Math.round(this.volume * 100) + '%';
            if (this.utterance) {
                this.utterance.volume = this.volume;
            }
            this.saveSettings();
        });

        // Content filter checkboxes
        document.getElementById('skip-code').addEventListener('change', () => {
            this.saveSettings();
        });

        document.getElementById('include-headings').addEventListener('change', () => {
            this.saveSettings();
        });

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
        const voices = this.synth.getVoices();
        
        voiceSelect.innerHTML = '';
        
        // Group voices by language
        const englishVoices = voices.filter(v => v.lang.startsWith('en'));
        const otherVoices = voices.filter(v => !v.lang.startsWith('en'));
        
        // Add English voices first
        if (englishVoices.length > 0) {
            const englishGroup = document.createElement('optgroup');
            englishGroup.label = 'English Voices';
            englishVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${voice.name} (${voice.lang})`;
                option.selected = voice.name === this.voice?.name;
                englishGroup.appendChild(option);
            });
            voiceSelect.appendChild(englishGroup);
        }
        
        // Add other voices
        if (otherVoices.length > 0) {
            const otherGroup = document.createElement('optgroup');
            otherGroup.label = 'Other Languages';
            otherVoices.forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.name;
                option.textContent = `${voice.name} (${voice.lang})`;
                englishGroup.appendChild(option);
            });
            voiceSelect.appendChild(otherGroup);
        }
    }

    togglePlayerVisibility() {
        const content = document.getElementById('podcast-player-content');
        const toggleBtn = document.getElementById('podcast-toggle-btn');
        const isVisible = content.style.display !== 'none';
        
        if (isVisible) {
            content.style.display = 'none';
            toggleBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
            `;
            toggleBtn.title = 'Show Podcast Player';
        } else {
            content.style.display = 'block';
            toggleBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13H5v-2h14v2z"/>
                </svg>
            `;
            toggleBtn.title = 'Hide Podcast Player';
            this.prepareContent();
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
        const settings = {
            voice: this.voice?.name,
            playbackRate: this.playbackRate,
            volume: this.volume,
            skipCode: document.getElementById('skip-code').checked,
            includeHeadings: document.getElementById('include-headings').checked
        };
        localStorage.setItem('podcastTTSSettings', JSON.stringify(settings));
    }

    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('podcastTTSSettings') || '{}');
            
            if (settings.voice) {
                const voices = this.synth.getVoices();
                const savedVoice = voices.find(v => v.name === settings.voice);
                if (savedVoice) this.voice = savedVoice;
            }
            
            if (settings.playbackRate) {
                this.playbackRate = settings.playbackRate;
                document.getElementById('speed-control').value = settings.playbackRate;
            }
            
            if (settings.volume !== undefined) {
                this.volume = settings.volume;
                document.getElementById('volume-control').value = settings.volume;
                document.getElementById('volume-display').textContent = Math.round(settings.volume * 100) + '%';
            }
            
            if (settings.skipCode !== undefined) {
                document.getElementById('skip-code').checked = settings.skipCode;
            }
            
            if (settings.includeHeadings !== undefined) {
                document.getElementById('include-headings').checked = settings.includeHeadings;
            }
            
        } catch (error) {
            console.log('Could not load TTS settings:', error);
        }
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