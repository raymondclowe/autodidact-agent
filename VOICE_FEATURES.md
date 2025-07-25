# 🔊 Voice Features Documentation

This document describes the voice/speech functionality implemented in Autodidact for Phase 1.

## Overview

The voice implementation adds text-to-speech (TTS) capabilities to the Autodidact learning platform, making it more accessible and providing an immersive audio learning experience.

## Features Implemented

### 1. Auto-Speak Mode
- **Global Toggle**: Available in the header of session pages and sidebar
- **Automatic Speech**: When enabled, AI tutor responses are automatically spoken
- **Session Persistence**: Setting persists across page navigation within a session
- **User Control**: Can be toggled on/off at any time

### 2. Per-Element Speaker Buttons
- **🔊 Icons**: Clickable speaker buttons next to text content
- **On-Demand Speech**: Speak any text element on demand
- **Wide Coverage**: Available for AI responses, learning objectives, and other key content
- **Independent Operation**: Works regardless of auto-speak setting

### 3. Web Speech API Integration
- **Browser Native**: Uses built-in browser speech synthesis
- **Wide Compatibility**: Works in modern browsers (Chrome, Firefox, Safari, Edge)
- **No API Costs**: No external API calls required
- **Privacy Friendly**: Processing happens locally in the browser

### 4. Smart Text Processing
- **Markdown Removal**: Strips formatting for better speech
- **Math Symbol Conversion**: Converts symbols (=, +, -, *, /, ^) to words
- **Code Handling**: Processes code snippets appropriately
- **List Processing**: Handles bullet points and numbered lists

## How to Use

### For Users

#### Enabling Auto-Speak
1. Navigate to any learning session
2. Look for the "🔊 Auto-Speak" toggle in the header
3. Click to enable automatic speech of AI responses
4. The setting persists until you turn it off

#### Using Speaker Buttons
1. Look for 🔊 icons next to text content
2. Click any speaker icon to hear that specific text
3. Works whether auto-speak is on or off

#### Adjusting Speech Settings
1. Go to the sidebar (visible on most pages)
2. Find the "🔊 Speech Settings" section
3. Adjust speech speed using the slider
4. Toggle auto-speak mode on/off

#### Testing Speech Features
1. Visit the `/speech_demo` page (add it to URL)
2. Test different speech features
3. Try various content types (math, code, text)
4. Experiment with settings

### For Developers

#### Adding Speech to New Content

**Basic Speech-Enabled Content:**
```python
from components.speech_controls import create_speech_enabled_markdown

# This will add both auto-speak and speaker button based on user settings
create_speech_enabled_markdown("Your content here", add_button=True)
```

**Custom Speaker Button:**
```python
from components.speech_controls import add_speaker_button_to_text

st.markdown("Your content")
add_speaker_button_to_text("Your content")
```

**Initialize Speech on New Pages:**
```python
from components.speech_controls import create_global_speech_component
from utils.speech_utils import initialize_speech_state

# Add to the top of each page
initialize_speech_state()
create_global_speech_component()
```

#### Architecture

**Key Files:**
- `utils/speech_utils.py`: Core speech functionality and text processing
- `components/speech_controls.py`: UI components and speech controls
- `pages/session_detail.py`: Main integration point for tutoring sessions
- `pages/speech_demo.py`: Demo page for testing features

**State Management:**
- Speech settings stored in `st.session_state`
- Persists across page navigation
- Key variables: `auto_speak`, `speech_speed`, `speech_voice`

**Component Structure:**
```
speech_utils.py
├── initialize_speech_state() - Set up session state
├── sanitize_text_for_speech() - Clean text for TTS
├── create_tts_component() - Generate auto-speak HTML/JS
└── create_speaker_button_html() - Generate speaker button HTML

speech_controls.py
├── show_speech_controls() - Display toggles and settings
├── create_speech_enabled_markdown() - Content with speech
└── create_global_speech_component() - Page-level speech setup
```

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best support, multiple voices |
| Firefox | ✅ Full | Good support |
| Safari | ✅ Full | Works well on macOS/iOS |
| Edge | ✅ Full | Built on Chromium |
| Opera | ✅ Full | Chromium-based |

**Requirements:**
- Modern browser with Web Speech API support
- JavaScript enabled
- Audio output capability

## Accessibility Benefits

### Vision Accessibility
- Complete audio navigation of content
- Screen reader friendly implementation
- Audio descriptions of visual elements

### Motor Accessibility
- Hands-free content consumption
- Reduced need for precise clicking
- Voice commands (future enhancement)

### Learning Differences
- Audio learning support for dyslexia
- Multi-modal content reinforcement
- Customizable speech speed

## Technical Implementation

### Text Sanitization
The system automatically processes text for better speech:

```python
# Input: "**Einstein's equation** is E=mc²"
# Output: "Einstein's equation is E equals mc squared"
```

**Processing Steps:**
1. Remove markdown formatting (`**bold**`, `*italic*`, etc.)
2. Convert math symbols (=, +, -, *, /, ^)
3. Clean up whitespace and line breaks
4. Handle special characters appropriately

### JavaScript Integration
Speech functionality uses browser-native APIs:

```javascript
// Auto-generated TTS component
const utterance = new SpeechSynthesisUtterance(text);
utterance.rate = 1.0;  // Configurable speed
window.speechSynthesis.speak(utterance);
```

### Error Handling
- Graceful degradation when speech not supported
- Silent failure for empty/invalid content
- User feedback for speech capabilities

## Future Enhancements (Planned Phases)

### Phase 2
- Voice input for student responses
- Advanced speech settings (voice selection, pitch)
- Speech recognition for interactive learning

### Phase 3
- Offline speech synthesis (local models)
- Multiple voice personalities for different content types
- Advanced conversation features

## Troubleshooting

### Common Issues

**No Audio Output:**
1. Check browser supports Web Speech API
2. Verify volume settings
3. Check audio permissions
4. Try different browser

**Speech Not Starting:**
1. Ensure JavaScript is enabled
2. Check for browser errors in console
3. Try refreshing the page
4. Verify content is not empty

**Speed Too Fast/Slow:**
1. Use speech speed slider in sidebar
2. Settings apply to new speech instances
3. Reload page if needed

### Browser-Specific Notes

**Chrome:**
- Best voice selection
- Most reliable performance
- Supports latest Web Speech API features

**Firefox:**
- Good performance
- May have fewer voice options
- Some older versions may have issues

**Safari:**
- Works well on Mac/iOS
- Voice quality varies by system
- Good integration with system settings

## Testing

Run the test suite to verify functionality:

```bash
# Basic functionality tests
python test_speech_functionality.py

# Comprehensive verification  
python test_speech_verification.py
```

Visit the demo page for manual testing:
```
http://localhost:8501/speech_demo
```

## Performance Considerations

- **Minimal Overhead**: Uses browser-native APIs
- **No External Calls**: All processing happens locally
- **Efficient Text Processing**: Fast sanitization and preparation
- **State Management**: Lightweight session state usage

## Privacy and Security

- **Local Processing**: All speech generation happens in the browser
- **No Data Collection**: No speech data sent to external services
- **User Control**: Complete user control over when speech is used
- **Permissions**: Uses standard browser permissions model

---

For questions or issues with voice features, please refer to the main project documentation or open an issue on GitHub.