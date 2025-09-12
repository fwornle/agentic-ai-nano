# Podcast Feature for Agentic AI Nanodegree

Convert all course content into high-quality speech for hands-free learning while commuting, driving, or multitasking.

## Key Features

### Hands-Free Learning
- Perfect for car learning with keyboard shortcuts
- Auto-navigation through course sections
- Smart content filtering (skip code blocks, include headings)
- Visual highlighting of current content being read

### Audio Controls
- Multiple playback speeds (0.75x to 2.0x)
- Voice selection from available system voices
- Volume control with visual feedback
- Progress tracking through content sections

### Intelligent Processing
- Smart chunking breaks content into digestible audio segments
- Section awareness with automatic progression
- Content filtering options (code blocks, headings, etc.)
- Context preservation across page navigation

### Mobile Optimized
- Responsive interface for phone use
- Sticky player stays accessible while scrolling
- Collapsible interface to save screen space
- Touch-friendly controls for mobile devices

## Getting Started

### Quick Start
1. Navigate to any course page
2. Click **[+]** to expand the podcast player (blue gradient bar at top)
3. Click the **Play ▶️** button to start listening
4. The system automatically reads through all content sections

### Customization
- **Voice**: Select from available system voices (English voices prioritized)
- **Speed**: Adjust from 0.75x (slower) to 2.0x (faster)
- **Volume**: Control audio level with slider
- **Content Filters**: Choose what content to include/exclude

## Keyboard Shortcuts

Perfect for hands-free operation while driving:

| Shortcut | Action |
|----------|---------|
| `Ctrl + Space` | Play / Pause |
| `Ctrl + Shift + →` | Next Section |
| `Ctrl + Shift + ←` | Previous Section |
| `?` | Show/Hide shortcuts help |

## Use Cases

### Commuting & Driving
- Learn during daily commute
- Perfect for long road trips
- Hands-free operation with keyboard shortcuts
- Continue learning without taking eyes off the road

### Walking & Exercise
- Listen while walking or jogging
- Multitask during gym workouts
- Learn during household chores
- Make productive use of routine activities

### Accessibility
- Support for users with visual impairments
- Alternative learning method for different learning styles
- Reduce screen time while maintaining learning progress
- Support for users with reading difficulties

### Offline Learning
- Works offline once pages are cached
- No internet required for speech synthesis
- Reliable performance in poor connectivity areas
- Local processing ensures privacy

## Technical Features

### Web Speech API Integration
- Uses browser's built-in speech synthesis
- No external dependencies or API keys required
- Works completely offline
- Supports 50+ languages and voices

### Progressive Web App Features
- Service Worker for offline support
- Responsive design for all device sizes
- Local storage for user preferences
- Fast loading with intelligent caching

## Configuration Options

### Content Filtering
- Skip Code Blocks: Exclude programming code from speech
- Include Headings: Read section headings for navigation
- Smart Filtering: Automatically skip navigation, ads, etc.

### Audio Settings
- Voice Selection: Choose from available system voices
- Playback Speed: 0.75x to 2.0x speed control
- Volume Control: 0% to 100% with visual feedback
- Persistent Settings: Automatically saves preferences

### Visual Features
- Current Section Highlighting: Visual indicator of content being read
- Auto-scroll: Automatically scrolls to current content
- Progress Tracking: Visual progress through content sections
- Responsive Layout: Adapts to screen size

## Browser Compatibility

### Fully Supported
- Chrome 71+ (Recommended)
- Firefox 62+
- Safari 14.1+
- Edge 79+

### Mobile Support
- iOS Safari 14.1+
- Android Chrome 71+
- Mobile browsers with Web Speech API support

## Privacy & Security

### Local Processing
- All speech synthesis happens locally on your device
- No data sent to external servers
- Complete privacy protection
- Works offline for maximum security

### Data Storage
- Only user preferences stored locally
- No personal content cached
- Settings stored in browser's localStorage
- Easy to clear/reset preferences

## Troubleshooting

### Common Issues

**No Audio Output**:
- Check browser's audio permissions
- Ensure system volume is enabled
- Try different voice selection
- Refresh page if voices not loading

**Playback Stops Unexpectedly**:
- Check for browser background tab restrictions
- Ensure page stays in focus during playback
- Try reducing playback speed
- Check for browser extensions interfering

**Mobile Issues**:
- Enable autoplay permissions for the site
- Check mobile browser's speech synthesis support
- Try using Chrome or Safari on mobile
- Ensure sufficient device storage

### Reset Options
```javascript
// Clear all podcast settings
localStorage.removeItem('podcastTTSSettings');
location.reload();
```

## Learning Tips

### Maximizing Effectiveness
1. **Active Listening**: Take notes while listening
2. **Speed Adjustment**: Start at 1.0x, gradually increase as comfortable
3. **Section Review**: Use prev/next buttons to review complex topics
4. **Multi-modal Learning**: Combine visual reading with audio

### Best Practices for Car Learning
1. **Safety First**: Always prioritize driving safety
2. **Familiar Routes**: Use on familiar commutes initially
3. **Pause for Complexity**: Pause for complex technical sections
4. **Review Later**: Visual review of important concepts when stationary

## Support

### Getting Help
- GitHub Discussions: Community support and feature discussions
- Issue Tracker: Bug reports and technical issues
- Documentation: Comprehensive guides and tutorials

### Quick Support Steps
1. Check browser console for error messages
2. Try in incognito/private browsing mode
3. Test with different browsers
4. Clear browser cache and cookies
5. Disable browser extensions temporarily

---

**Transform your commute into productive learning time with the Agentic AI Nanodegree Podcast feature. Whether you're driving to work or walking the dog, your education never stops.**