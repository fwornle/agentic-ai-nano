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
        this.muteChapters = false; // Option to skip reading chapter headings
        
        // Track live change support for better fallback behavior
        this.liveVolumeSupported = null; // null = unknown, true/false = tested
        this.liveSpeedSupported = null;   // null = unknown, true/false = tested
        
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
                        allVoices.slice(0, 10).map(v => {
                            v.displayName = v.name;
                            return v;
                        }) :
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
        
        // Device-specific logging for voice consistency debugging
        const userAgent = navigator.userAgent;
        const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        const isChrome = /Chrome/.test(userAgent);
        const isSafari = /Safari/.test(userAgent) && !/Chrome/.test(userAgent);
        
        console.log('🖥️ Device Info:', {
            isMobile,
            isChrome,
            isSafari,
            userAgent: userAgent.substring(0, 100) + '...'
        });
        
        // Debug: Log all voice names to see what's actually available
        console.log('📋 All available voice names:', voices.map(v => v.name));
        console.log('🌍 Voice languages available:', [...new Set(voices.map(v => v.lang))].sort());
        
        // Special debug: Look for specific voices the user wants
        const wantedVoices = voices.filter(v => 
            v.name.toLowerCase().includes('cello') || 
            v.name.toLowerCase().includes('spanish') ||
            v.lang.toLowerCase().includes('es')
        );
        console.log('🎯 Found wanted voices (Cello/Spanish):', wantedVoices.map(v => `${v.name} (${v.lang})`));
        
        if (voices.length === 0) {
            console.warn('🚨 No voices available from speechSynthesis.getVoices()');
            return;
        }
        
        // Enhanced voice detection with proper labeling
        const voiceMap = new Map();
        
        voices.forEach(voice => {
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            
            // Skip only the really low-quality voices
            if (name.includes('compact')) return;
            
            // Create descriptive labels
            let label = '';
            let category = 'other';
            
            // Google voices - prioritize non-native speakers for accent variety
            if (name.includes('google')) {
                if (lang.includes('en-us')) label = 'Native: US English';
                else if (lang.includes('en-gb') || name.includes('uk english')) {
                    label = name.includes('male') ? 'Native: UK English (Male)' : 'Native: UK English (Female)';
                }
                else if (lang.includes('en-au')) label = 'Native: Australian English';
                else if (lang.includes('de') || name.includes('german')) label = 'Non-native: German Accent';
                else if (lang.includes('es') || name.includes('spanish')) label = 'Non-native: Spanish Accent';
                else if (lang.includes('fr') || name.includes('french')) label = 'Non-native: French Accent';
                else if (lang.includes('zh') || name.includes('chinese') || name.includes('mandarin') || name.includes('cantonese')) label = 'Non-native: Chinese Accent';
                else if (lang.includes('hi') || name.includes('hindi') || name.includes('indian')) label = 'Non-native: Hindi/Indian Accent';
                else if (lang.includes('ar') || name.includes('arabic')) label = 'Non-native: Arabic Accent';
                else if (lang.includes('it') || name.includes('italian')) label = 'Non-native: Italian Accent';
                else if (lang.includes('pt') || name.includes('portuguese') || name.includes('brazilian')) label = 'Non-native: Portuguese/Brazilian Accent';
                else if (lang.includes('ru') || name.includes('russian')) label = 'Non-native: Russian Accent';
                else if (lang.includes('ko') || name.includes('korean')) label = 'Non-native: Korean Accent';
                else if (lang.includes('ja') || name.includes('japanese')) label = 'Non-native: Japanese Accent';
                else if (lang.includes('sv') || name.includes('swedish')) label = 'Non-native: Swedish Accent';
                else if (lang.includes('no') || name.includes('norwegian')) label = 'Non-native: Norwegian Accent';
                else if (lang.includes('da') || name.includes('danish')) label = 'Non-native: Danish Accent';
                else if (lang.includes('nl') || name.includes('dutch')) label = 'Non-native: Dutch Accent';
                else if (lang.includes('pl') || name.includes('polish')) label = 'Non-native: Polish Accent';
                else if (lang.includes('th') || name.includes('thai')) label = 'Non-native: Thai Accent';
                else if (lang.includes('vi') || name.includes('vietnamese')) label = 'Non-native: Vietnamese Accent';
                else if (lang.includes('af') || name.includes('afrikaans') || name.includes('african')) label = 'Non-native: African Accent';
                else label = `Google ${voice.name.replace(/Google\s*/i, '')}`;
                
                category = lang.includes('en') ? 'native-en' : 'non-native-accent';
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
            // Fun novelty voices (case-insensitive check) - expanded patterns
            else if (name.includes('cello') || name.includes('cellos') || name.includes('bells') || 
                     name.includes('bad news') || name.includes('good news') || name.includes('organ') || 
                     name.includes('boing') || name.includes('bubbles') || name.includes('trinoids') || 
                     name.includes('whisper') || name.includes('wobble') || name.includes('zarvox') || 
                     name.includes('bahh') || name.includes('jester') || name.includes('superstar') || 
                     name.includes('albert') || name.includes('fred') || name.includes('ralph') || 
                     name.includes('junior') || name.includes('hysterical') || name.includes('deranged') ||
                     name.includes('pipe') || name.includes('robot') || name.includes('alien') ||
                     name.includes('echo') || name.includes('reverb') || name.includes('metallic') ||
                     name.includes('distorted') || name.includes('chipmunk') || name.includes('monster')) {
                // Capitalize first letter
                const displayName = voice.name.charAt(0).toUpperCase() + voice.name.slice(1);
                label = `🎭 ${displayName}`;
                category = 'novelty';
                console.log('🎭 Found novelty voice:', voice.name);
            }
            else if (lang.includes('en')) {
                label = voice.name;
                category = 'english';
            }
            
            if (label && !voiceMap.has(label)) {
                voiceMap.set(label, { voice, label, category });
            }
        });
        
        // Convert to array and organize by category (quality first, then fun)
        this.availableVoices = [];
        const categories = ['premium', 'native-en', 'non-native-accent', 'novelty', 'microsoft', 'english'];
        
        categories.forEach(cat => {
            const voicesInCategory = Array.from(voiceMap.values())
                .filter(v => v.category === cat)
                .sort((a, b) => a.label.localeCompare(b.label));
            this.availableVoices.push(...voicesInCategory.map(v => {
                const voice = v.voice;
                voice.displayName = v.label;
                return voice;
            }));
        });
        
        // IMPROVED: Ensure fair representation from all categories
        // Get voices by category first  
        const voicesByCategory = {};
        categories.forEach(cat => {
            voicesByCategory[cat] = Array.from(voiceMap.values())
                .filter(v => v.category === cat)
                .sort((a, b) => a.label.localeCompare(b.label));
        });
        
        console.log('🎯 Voices found by category:', Object.fromEntries(
            Object.entries(voicesByCategory).map(([cat, voices]) => [cat, voices.length])
        ));
        
        // FIXED: Smart distribution to ensure key categories are always represented
        // Clear existing array and rebuild with fair distribution
        this.availableVoices = [];
        
        // Priority 1: Ensure we have plenty of voices from key categories (especially funny ones)
        const guaranteedCategories = {
            'premium': 4,           // High quality voices
            'native-en': 3,         // Standard English voices  
            'non-native-accent': 8, // Foreign accent voices (user specifically wants MORE of these)
            'novelty': 6            // Fun/musical voices (user specifically wants MORE including Cello)
        };
        
        // Add guaranteed voices first
        Object.entries(guaranteedCategories).forEach(([category, maxCount]) => {
            const categoryVoices = voicesByCategory[category] || [];
            console.log(`🎯 ${category} category has ${categoryVoices.length} voices available, adding ${Math.min(categoryVoices.length, maxCount)}`);
            const voicesToAdd = categoryVoices.slice(0, maxCount);
            voicesToAdd.forEach(v => {
                const voice = v.voice;
                voice.displayName = v.label;
                this.availableVoices.push(voice);
                // Special logging for wanted voices
                if (voice.name.toLowerCase().includes('cello') || voice.name.toLowerCase().includes('spanish')) {
                    console.log(`🎯 IMPORTANT: Added wanted voice: ${voice.name} as ${v.label}`);
                }
            });
            console.log(`✅ Added ${voicesToAdd.length} ${category} voices`);
        });
        
        // Add remaining voices from other categories to fill up to reasonable total (30 instead of 25)
        const remainingSlots = 30 - this.availableVoices.length;
        if (remainingSlots > 0) {
            const otherCategories = ['microsoft', 'english'];
            otherCategories.forEach(cat => {
                const categoryVoices = voicesByCategory[cat] || [];
                const remainingInCategory = categoryVoices.slice(guaranteedCategories[cat] || 0);
                const slotsForCategory = Math.min(remainingInCategory.length, Math.floor(remainingSlots / otherCategories.length));
                
                remainingInCategory.slice(0, slotsForCategory).forEach(v => {
                    const voice = v.voice;
                    voice.displayName = v.label;
                    this.availableVoices.push(voice);
                });
            });
        }
        
        console.log(`🎯 Final voice distribution: ${this.availableVoices.length} total voices`);
        
        // Log the final voice categories for debugging
        const finalDistribution = {};
        this.availableVoices.forEach(voice => {
            const voiceData = Array.from(voiceMap.values()).find(v => v.voice === voice);
            if (voiceData) {
                finalDistribution[voiceData.category] = (finalDistribution[voiceData.category] || 0) + 1;
            }
        });
        console.log('📊 Final voice category distribution:', finalDistribution);
        
        // Enhanced voice detection for BOTH desktop and mobile - scan for ALL missed voices
        console.log('🔍 Scanning for additional voices (desktop and mobile)...');
        
        // Aggressively scan for ALL available voices on both desktop and mobile
        voices.forEach(voice => {
            const name = voice.name.toLowerCase();
            const lang = voice.lang.toLowerCase();
            
            // Skip if already categorized
            if (Array.from(voiceMap.values()).some(v => v.voice.name === voice.name)) {
                return;
            }
            
            let extraLabel = '';
            let extraCategory = 'extra-voices';
            
            // Check for musical/novelty voices that might be missed (PRIORITY: Cello!)
            if (name.includes('cellos') || name.includes('cello') || 
                name.includes('bells') || name.includes('organ') || 
                name.includes('pipe') || name.includes('whisper') ||
                name.includes('bubbles') || name.includes('albert') ||
                name.includes('bad news') || name.includes('good news') ||
                name.includes('hysterical') || name.includes('deranged') ||
                name.includes('robot') || name.includes('trinoids')) {
                extraLabel = `🎭 ${voice.name}`;
                extraCategory = 'novelty';
                console.log('🎭 Found missed novelty voice:', voice.name);
            }
            // Check for non-native English speakers that might be missed
            else if (lang.includes('en') && lang !== 'en-us') {
                if (lang.includes('en-gb')) extraLabel = `Extra: UK English (${voice.name})`;
                else if (lang.includes('en-au')) extraLabel = `Extra: Australian (${voice.name})`;
                else if (lang.includes('en-za')) extraLabel = `Extra: South African (${voice.name})`;
                else if (lang.includes('en-in')) extraLabel = `Extra: Indian English (${voice.name})`;
                else if (lang.includes('en-ie')) extraLabel = `Extra: Irish English (${voice.name})`;
                else extraLabel = `Extra: ${lang.toUpperCase()} English (${voice.name})`;
                extraCategory = 'non-native-accent';
            }
            // Check for ANY non-English voices that might speak English (PRIORITY: Spanish!)
            else if (!lang.includes('en')) {
                // Some systems have multilingual voices that can speak English with accents
                if (lang.includes('de')) extraLabel = `Non-native: German Accent (${voice.name})`;
                else if (lang.includes('es')) {
                    extraLabel = `Non-native: Spanish Accent (${voice.name})`;
                    console.log('🇪🇸 Found Spanish accent voice:', voice.name);
                }
                else if (lang.includes('fr')) extraLabel = `Non-native: French Accent (${voice.name})`;
                else if (lang.includes('it')) extraLabel = `Non-native: Italian Accent (${voice.name})`;
                else if (lang.includes('pt')) extraLabel = `Non-native: Portuguese Accent (${voice.name})`;
                else if (lang.includes('ru')) extraLabel = `Non-native: Russian Accent (${voice.name})`;
                else if (lang.includes('zh')) extraLabel = `Non-native: Chinese Accent (${voice.name})`;
                else if (lang.includes('ja')) extraLabel = `Non-native: Japanese Accent (${voice.name})`;
                else if (lang.includes('ko')) extraLabel = `Non-native: Korean Accent (${voice.name})`;
                else if (lang.includes('hi')) extraLabel = `Non-native: Hindi Accent (${voice.name})`;
                else if (lang.includes('ar')) extraLabel = `Non-native: Arabic Accent (${voice.name})`;
                else if (lang.includes('sv')) extraLabel = `Non-native: Swedish Accent (${voice.name})`;
                else if (lang.includes('no')) extraLabel = `Non-native: Norwegian Accent (${voice.name})`;
                else if (lang.includes('da')) extraLabel = `Non-native: Danish Accent (${voice.name})`;
                else if (lang.includes('nl')) extraLabel = `Non-native: Dutch Accent (${voice.name})`;
                else if (lang.includes('pl')) extraLabel = `Non-native: Polish Accent (${voice.name})`;
                else if (lang.includes('th')) extraLabel = `Non-native: Thai Accent (${voice.name})`;
                else if (lang.includes('vi')) extraLabel = `Non-native: Vietnamese Accent (${voice.name})`;
                extraCategory = 'non-native-accent';
            }
            // Include any other English voices
            else if (lang.includes('en')) {
                extraLabel = `Extra: ${voice.name}`;
                extraCategory = 'extra-voices';
            }
            
            // Add to available voices if we found a label and have space
            if (extraLabel && this.availableVoices.length < 40) {
                voice.displayName = extraLabel;
                this.availableVoices.push(voice);
                console.log('🔍 Added extra voice:', extraLabel);
            }
        });
        
        console.log(`🔍 Extra voice scanning complete: ${this.availableVoices.length} total voices`);
        
        // Fallback if no voices found - especially important on mobile
        if (this.availableVoices.length === 0) {
            console.warn('🚨 No categorized voices found, using fallback detection...');
            const englishVoices = voices.filter(v => v.lang.startsWith('en'));
            
            // Remove duplicates by creating a Map keyed by voice characteristics
            const uniqueVoices = new Map();
            englishVoices.forEach(voice => {
                const key = `${voice.name}_${voice.lang}_${voice.gender || 'unknown'}`;
                if (!uniqueVoices.has(key)) {
                    voice.displayName = this.createFallbackDisplayName(voice);
                    uniqueVoices.set(key, voice);
                }
            });
            
            this.availableVoices = Array.from(uniqueVoices.values()).slice(0, 12);
            console.log('🔄 Fallback voices loaded:', this.availableVoices.length);
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
                .map(v => {
                    v.displayName = v.name;
                    return v;
                });
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
                        <label>
                            <input type="checkbox" id="mute-chapters"> Mute headings & captions
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

        document.getElementById('mute-chapters')?.addEventListener('change', (e) => {
            this.muteChapters = e.target.checked;
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
        // Remove highlighting when minimizing
        this.removeHighlight();
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
        
        // Set current voice or select first available voice if none selected
        if (this.voice) {
            select.value = this.voice.name;
        } else if (this.availableVoices.length > 0) {
            // Auto-select first quality voice as default
            this.voice = this.availableVoices[0];
            select.value = this.voice.name;
            console.log('🎯 Auto-selected default voice:', this.voice.name);
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
            
            // Voice changes require restart (unfortunately unavoidable)
            if (this.isPlaying) {
                console.log('🔄 Restarting current chunk due to voice change...');
                this.synth.cancel();
                setTimeout(() => {
                    this.playCurrentChunk();
                }, 100);
            }
            
            this.saveSettings();
        } else {
            console.error('❌ Voice not found:', voiceName);
        }
    }

    changeSpeed(speed) {
        console.log('⚡ Speed change requested:', speed, 'current:', this.playbackRate);
        const oldSpeed = this.playbackRate;
        this.playbackRate = speed;
        
        // Always restart with the new speed for consistent behavior
        // The Speech Synthesis API doesn't reliably support live speed changes
        if (this.isPlaying && this.utterance) {
            console.log('🔄 Applying speed change with seamless restart...');
            
            // Store current position estimate (rough, but better than nothing)
            const currentText = this.textChunks[this.currentChunkIndex].text;
            const estimatedProgress = 0.3; // Assume we're 30% through (can't get exact position)
            
            // Cancel and restart immediately with minimal delay for seamless experience
            this.synth.cancel();
            setTimeout(() => {
                this.playCurrentChunk();
            }, 30); // Very fast restart for seamless blending
        } else {
            console.log('⚡ Speed will apply when playback starts');
        }
        
        this.saveSettings();
    }

    changeVolume(volume) {
        console.log('🔊 Volume change requested:', volume, 'current:', this.volume);
        this.volume = volume;
        const volumeText = document.getElementById('volume-text');
        if (volumeText) volumeText.textContent = Math.round(volume * 100) + '%';
        
        // Try to apply volume change with minimal disruption
        if (this.isPlaying && this.utterance) {
            // If we know live changes don't work, skip directly to restart
            if (this.liveVolumeSupported === false) {
                console.log('🔄 Live volume changes not supported on this browser, restarting...');
                this.synth.cancel();
                setTimeout(() => {
                    this.playCurrentChunk();
                }, 50);
                this.saveSettings();
                return;
            }
            
            console.log('🎛️ Attempting live volume change from', this.utterance.volume, 'to', volume);
            
            // Store original volume for comparison
            const originalVolume = this.utterance.volume;
            this.utterance.volume = volume;
            
            // Give browser a moment to apply the change, then check if it worked
            setTimeout(() => {
                const actualVolume = this.utterance.volume;
                console.log('📊 Volume change result: requested =', volume, 'actual =', actualVolume, 'original =', originalVolume);
                
                // More tolerant detection: check if change worked or if it's close enough
                const changeWorked = Math.abs(actualVolume - volume) <= 0.1; // More tolerant threshold for volume
                const actuallyChanged = Math.abs(actualVolume - originalVolume) > 0.05; // Did something change?
                
                if (!changeWorked && !actuallyChanged) {
                    // Direct change didn't work at all - restart for this utterance only
                    console.log('🔄 Live volume change not supported for this utterance, restarting...');
                    this.synth.cancel();
                    setTimeout(() => {
                        this.playCurrentChunk();
                    }, 50);
                } else {
                    // It worked or partially worked!
                    if (changeWorked) {
                        console.log('🔊 Volume changed successfully without restart!');
                    } else {
                        console.log('🔊 Volume changed partially - close enough, not restarting');
                    }
                }
            }, 50); // Longer timeout for more reliable detection
        } else {
            console.log('🔊 Volume will apply when playback starts:', Math.round(volume * 100) + '%');
        }
        
        this.saveSettings();
    }

    applyLiveChanges() {
        if (!this.isPlaying || !this.utterance) return;
        
        console.log('🔧 Applying live changes without interrupting...');
        
        // For volume changes, we can apply immediately without restarting
        if (this.utterance && this.synth.speaking) {
            // Update the utterance properties for the next chunk
            // Current utterance will finish with old settings, next chunk will use new ones
            console.log('🎵 Settings will apply to next chunk to avoid interruption');
        }
        
        // Only restart if voice changed (which requires restart)
        // Volume and speed changes will apply to the next chunk automatically
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
        // Update muteChapters from checkbox state
        this.muteChapters = document.getElementById('mute-chapters')?.checked || false;
        
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
                
                if (headingText && !this.muteChapters) {
                    // Add "Chapter:" prefix to headings for audio
                    const chapterText = `Chapter: ${headingText}`;
                    textNodes.push({
                        text: chapterText,
                        type: 'heading',
                        level: currentNode.tagName.toLowerCase(),
                        element: currentNode,
                        originalText: headingText // Keep original for display
                    });
                } else if (headingText && this.muteChapters) {
                    // Still add heading node for structure, but mark as muted
                    textNodes.push({
                        text: '', // Empty text means it won't be spoken
                        type: 'heading-muted',
                        level: currentNode.tagName.toLowerCase(),
                        element: currentNode,
                        originalText: headingText
                    });
                }
            } else if (currentNode.matches('figcaption, caption, .caption')) {
                // Handle captions
                let captionText = currentNode.textContent.trim();
                
                if (skipEmojis) {
                    captionText = this.removeEmojis(captionText);
                }
                
                if (captionText && !this.muteChapters) {
                    // Add "Caption:" prefix for audio
                    textNodes.push({
                        text: `Caption: ${captionText}`,
                        type: 'caption',
                        element: currentNode
                    });
                } else if (captionText && this.muteChapters) {
                    // Skip captions when muted
                    textNodes.push({
                        text: '',
                        type: 'caption-muted',
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
        let text = nodes.map(n => n.text).filter(t => t.trim()).join(' '); // Filter out empty text
        const heading = nodes.find(n => n.type === 'heading' || n.type === 'heading-muted');
        
        // Add natural pauses for better speech rhythm
        // Add slight pause after periods and longer pause after paragraphs
        text = text
            .replace(/\. /g, '. ') // Keep periods as-is (speech synthesis handles them)
            .replace(/\? /g, '? ') // Questions get natural inflection
            .replace(/! /g, '! ') // Exclamations get emphasis
            .replace(/: /g, ': ') // Pause after colons
            .replace(/; /g, '; '); // Pause after semicolons
        
        return {
            nodes: nodes,
            text: text,
            title: heading ? (heading.originalText || heading.text).substring(0, 50) : text.substring(0, 50) + '...'
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
        this.utterance.volume = this.volume;
        
        // Set rate and pitch based on content type
        const hasHeading = chunk.nodes && chunk.nodes.some(n => n.type === 'heading');
        if (hasHeading) {
            this.utterance.pitch = 1.05;
            this.utterance.rate = this.playbackRate * 0.9; // Slightly slower for emphasis
            console.log('📝 Heading detected - using slower rate:', this.utterance.rate);
        } else {
            this.utterance.pitch = 0.95 + (Math.random() * 0.15);
            this.utterance.rate = this.playbackRate;
            console.log('📄 Normal content - using standard rate:', this.utterance.rate);
        }
        
        console.log('🎛️ Utterance settings applied:', {
            voice: this.utterance.voice ? this.utterance.voice.name : 'NO VOICE',
            volume: this.utterance.volume,
            rate: this.utterance.rate,
            pitch: this.utterance.pitch
        });
        
        // Reset live change capability detection for new utterance
        // This ensures speed/volume controls work for each new paragraph
        this.liveVolumeSupported = null;
        this.liveSpeedSupported = null;
        console.log('🔄 Reset live control capability detection for new utterance');
        
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
                // Add consistent pause between chunks (300ms for better separation)
                // This ensures pauses even when headings are skipped
                setTimeout(() => this.playCurrentChunk(), 300);
            } else {
                this.stop();
            }
        };
        
        this.utterance.onerror = (event) => {
            console.error('🚨 Speech synthesis error:', event.error, event.message);
            this.stop();
        };
        
        // Add boundary event for word-level highlighting (if supported)
        this.utterance.onboundary = (event) => {
            if (event.name === 'word') {
                this.highlightWord(chunk, event.charIndex, event.charLength);
            }
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
            const wasPlaying = this.isPlaying;
            
            // Cancel current speech
            if (this.isPlaying) {
                this.synth.cancel();
            }
            
            // Find previous chapter start
            let targetIndex = this.currentChunkIndex - 1;
            for (let i = this.currentChunkIndex - 1; i >= 0; i--) {
                const chunk = this.textChunks[i];
                if (chunk && chunk.text && chunk.text.startsWith('Chapter:')) {
                    targetIndex = i;
                    break;
                }
            }
            
            this.currentChunkIndex = targetIndex;
            this.updateProgressDisplay();
            this.updateNavigationButtons();
            
            // Update highlighting and content display
            const chunk = this.textChunks[this.currentChunkIndex];
            if (chunk) {
                this.updateCurrentContent(chunk);
                this.highlightCurrentSection(chunk);
            }
            
            // Continue playback if it was playing
            if (wasPlaying) {
                // Small delay to ensure cancel completes
                setTimeout(() => {
                    this.playCurrentChunk();
                }, 100);
            }
        }
    }

    nextSection() {
        if (this.currentChunkIndex < this.textChunks.length - 1) {
            const wasPlaying = this.isPlaying;
            
            // Cancel current speech
            if (this.isPlaying) {
                this.synth.cancel();
            }
            
            // Find next chapter start
            let targetIndex = this.currentChunkIndex + 1;
            for (let i = this.currentChunkIndex + 1; i < this.textChunks.length; i++) {
                const chunk = this.textChunks[i];
                if (chunk && chunk.text && chunk.text.startsWith('Chapter:')) {
                    targetIndex = i;
                    break;
                }
            }
            
            this.currentChunkIndex = targetIndex;
            this.updateProgressDisplay();
            this.updateNavigationButtons();
            
            // Update highlighting and content display
            const chunk = this.textChunks[this.currentChunkIndex];
            if (chunk) {
                this.updateCurrentContent(chunk);
                this.highlightCurrentSection(chunk);
            }
            
            // Continue playback if it was playing
            if (wasPlaying) {
                // Small delay to ensure cancel completes
                setTimeout(() => {
                    this.playCurrentChunk();
                }, 100);
            }
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
        document.querySelectorAll('.podcast-word-highlight').forEach(el => {
            el.classList.remove('podcast-word-highlight');
        });
    }
    
    highlightWord(chunk, charIndex, charLength) {
        // Word-level highlighting with fade effect
        // Note: This is a simplified implementation - full word-level highlighting
        // would require more complex text node manipulation
        if (!chunk.nodes || chunk.nodes.length === 0) return;
        
        // Clear previous word highlights
        document.querySelectorAll('.podcast-word-highlight').forEach(el => {
            el.classList.remove('podcast-word-highlight');
        });
        
        // Find the word in the current text and highlight it
        const word = chunk.text.substr(charIndex, charLength || 20);
        
        // Apply word highlight to the first matching element
        // This is a basic implementation - could be enhanced
        chunk.nodes.forEach(node => {
            if (node.element && node.element.textContent.includes(word)) {
                // Temporarily add word highlight class
                node.element.classList.add('podcast-word-highlight');
                
                // Remove after animation completes
                setTimeout(() => {
                    node.element.classList.remove('podcast-word-highlight');
                }, 2000);
            }
        });
    }

    saveSettings() {
        const settings = {
            voice: this.voice?.name,
            playbackRate: this.playbackRate,
            volume: this.volume,
            contentFilter: this.contentFilter,
            skipEmojis: document.getElementById('skip-emojis')?.checked ?? true,
            skipCode: document.getElementById('skip-code')?.checked ?? true,
            muteChapters: this.muteChapters
        };
        localStorage.setItem('professionalPodcastSettings', JSON.stringify(settings));
        sessionStorage.setItem('professionalPodcastSettings', JSON.stringify(settings));
    }

    loadSettings() {
        try {
            const settings = JSON.parse(sessionStorage.getItem('professionalPodcastSettings') || localStorage.getItem('professionalPodcastSettings') || '{}');
            
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
            
            if (settings.muteChapters !== undefined) {
                this.muteChapters = settings.muteChapters;
                const checkbox = document.getElementById('mute-chapters');
                if (checkbox) checkbox.checked = settings.muteChapters;
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