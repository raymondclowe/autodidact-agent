"""
Speech utility functions for Autodidact
Handles TTS functionality and speech controls
"""

import streamlit as st
import re
from typing import Optional


def initialize_speech_state():
    """Initialize speech-related session state variables"""
    if 'auto_speak' not in st.session_state:
        st.session_state.auto_speak = False
    if 'speech_speed' not in st.session_state:
        st.session_state.speech_speed = 1.0
    if 'speech_voice' not in st.session_state:
        st.session_state.speech_voice = 'default'


def sanitize_text_for_speech(text: str) -> str:
    """
    Clean and prepare text for speech synthesis
    - Remove markdown formatting
    - Handle special characters and symbols
    - Convert equations to readable format
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    text = re.sub(r'#{1,6}\s*', '', text)         # Headers
    text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)  # List items
    
    # Handle mathematical expressions
    text = re.sub(r'\$\$(.*?)\$\$', r'equation: \1', text)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    
    # Handle common symbols for better speech
    text = text.replace('=', ' equals ')
    text = text.replace('+', ' plus ')
    text = text.replace('-', ' minus ')
    text = text.replace('*', ' times ')
    text = text.replace('/', ' divided by ')
    text = text.replace('^', ' to the power of ')
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def create_tts_component(text: str, auto_trigger: bool = False) -> str:
    """
    Create HTML/JavaScript component for text-to-speech
    Returns HTML string for use with st.components.v1.html
    """
    clean_text = sanitize_text_for_speech(text)
    
    # Escape quotes for JavaScript
    js_text = clean_text.replace('"', '\\"').replace("'", "\\'")
    
    html_content = f"""
    <div id="tts-container" style="display: inline;">
        <script>
        function speakText(text, autoTrigger = false) {{
            // Check if browser supports speech synthesis
            if (!('speechSynthesis' in window)) {{
                console.log('Speech synthesis not supported');
                return false;
            }}
            
            // Stop any current speech
            window.speechSynthesis.cancel();
            
            if (!text || text.trim() === '') {{
                return false;
            }}
            
            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Get speech settings from Streamlit session (if available)
            utterance.rate = 1.0;  // Default rate
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Speak the text
            window.speechSynthesis.speak(utterance);
            
            return true;
        }}
        
        // Auto-trigger if requested
        if ({str(auto_trigger).lower()}) {{
            setTimeout(() => speakText("{js_text}", true), 100);
        }}
        
        // Make function globally available
        window.speakText = speakText;
        </script>
    </div>
    """
    
    return html_content


def create_speaker_button_html(text: str, button_id: str = None) -> str:
    """
    Create HTML for a speaker button that triggers TTS for specific text
    """
    if not button_id:
        button_id = f"speak-btn-{hash(text) % 10000}"
    
    clean_text = sanitize_text_for_speech(text)
    js_text = clean_text.replace('"', '\\"').replace("'", "\\'")
    
    html_content = f"""
    <div style="display: inline-block; margin-left: 8px;">
        <button 
            id="{button_id}"
            onclick="speakText('{js_text}')"
            style="
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
                padding: 4px;
                border-radius: 4px;
                transition: background-color 0.2s;
                vertical-align: middle;
            "
            onmouseover="this.style.backgroundColor='#f0f0f0'"
            onmouseout="this.style.backgroundColor='transparent'"
            title="Speak this text"
        >
            🔊
        </button>
    </div>
    """
    
    return html_content


def get_speech_enabled_content(content: str, add_speaker_button: bool = True, auto_speak: bool = None) -> tuple[str, str]:
    """
    Process content for speech and return both the original content and speech HTML
    
    Args:
        content: The text content to process
        add_speaker_button: Whether to add a speaker button
        auto_speak: Override auto_speak setting (uses session state if None)
    
    Returns:
        tuple: (original_content, speech_html)
    """
    if auto_speak is None:
        auto_speak = st.session_state.get('auto_speak', False)
    
    speech_html = ""
    
    # Handle None or empty content
    if not content:
        return content, speech_html
    
    # Add TTS component for auto-speak
    if auto_speak and content.strip():
        speech_html += create_tts_component(content, auto_trigger=True)
    
    # Add speaker button if requested
    if add_speaker_button and content.strip():
        speech_html += create_speaker_button_html(content)
    
    return content, speech_html


def is_speech_supported() -> bool:
    """
    Check if speech synthesis is supported in the current browser
    This is a placeholder - actual check happens in JavaScript
    """
    return True  # Assume supported, will be checked client-side