"""
Demo page to test speech functionality
This page demonstrates the voice features without requiring a full session
"""

import streamlit as st
from components.speech_controls import (
    show_speech_controls, 
    create_global_speech_component, 
    create_speech_enabled_markdown,
    create_speech_enabled_write,
    show_speech_status
)
from utils.speech_utils import initialize_speech_state

# Sidebar is shown globally in app.py

# Initialize speech functionality
initialize_speech_state()
create_global_speech_component()

# Page header with speech controls
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🔊 Speech Demo")
with col2:
    show_speech_controls(location="header")

st.markdown("---")

# Speech status
show_speech_status()

st.markdown("---")

# Demo sections
st.markdown("## 🎯 Test Speech Features")

st.markdown("### 1. Basic Text with Speaker Button")
st.markdown("This is a sample text that you can listen to by clicking the speaker button.")

# Add speaker button manually
from components.speech_controls import add_speaker_button_to_text
add_speaker_button_to_text("This is a sample text that you can listen to by clicking the speaker button.")

st.markdown("---")

st.markdown("### 2. Speech-Enabled Markdown")
st.markdown("The following content will have speech capabilities based on your auto-speak setting:")

sample_content = """
Welcome to the Autodidact speech demonstration! 

This is an example of how AI tutoring responses will sound when spoken aloud. The speech system can handle:

- **Bold text** and *italic text*
- Mathematical expressions like E=mc²
- Code snippets like `print("Hello, World!")`
- Lists and bullet points
- Complex educational content

Try turning on auto-speak in the toggle above to hear this automatically, or click the speaker button to hear it on demand.
"""

create_speech_enabled_markdown(sample_content, add_button=True)

st.markdown("---")

st.markdown("### 3. Mathematical Content")
st.markdown("Testing how mathematical formulas are spoken:")

math_content = """
Einstein's famous equation **E=mc²** demonstrates the relationship between energy and mass.

In this formula:
- E represents energy
- m represents mass  
- c represents the speed of light
- The ² symbol means "squared" or "to the power of 2"

So when spoken, this becomes: "E equals m times c squared"
"""

create_speech_enabled_markdown(math_content, add_button=True)

st.markdown("---")

st.markdown("### 4. Educational Scenarios")
st.markdown("Example of AI tutor responses:")

tutor_responses = [
    "Great question! Let me explain the concept of photosynthesis. Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen.",
    
    "I can see you're working on understanding quadratic equations. The general form is ax² + bx + c = 0, where a, b, and c are constants.",
    
    "That's an excellent observation! You're right that the mitochondria is often called the powerhouse of the cell because it produces ATP through cellular respiration."
]

for i, response in enumerate(tutor_responses, 1):
    st.markdown(f"**AI Tutor Response {i}:**")
    create_speech_enabled_markdown(response, add_button=True)
    st.markdown("")

st.markdown("---")

st.markdown("### 5. Interactive Test")
st.markdown("Try typing something to hear it spoken:")

user_text = st.text_area("Enter text to test speech:", 
                        value="This is a test of the speech synthesis system.",
                        height=100)

if user_text:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Your text:**")
        st.write(user_text)
    with col2:
        add_speaker_button_to_text(user_text)

st.markdown("---")

st.markdown("### 6. Settings Test")
st.markdown("Test different speech control locations:")

with st.expander("Sidebar-style Speech Controls"):
    show_speech_controls(location="sidebar")

with st.expander("Inline Speech Controls"):
    show_speech_controls(location="inline")

st.markdown("---")

# Instructions
st.markdown("## 📋 How to Test")
st.markdown("""
1. **Toggle Auto-Speak**: Use the toggle in the header to enable/disable automatic speech
2. **Speaker Buttons**: Click the 🔊 icons to hear specific content
3. **Browser Compatibility**: This uses the Web Speech API, so it works in modern browsers
4. **Voice Settings**: Your browser's default voice will be used (you can change this in browser settings)

**Note**: If you don't hear anything, check that:
- Your browser supports speech synthesis (most modern browsers do)
- Your volume is turned up
- You've allowed audio permissions if prompted
""")

st.markdown("---")

# Debug info
if st.checkbox("Show Debug Information"):
    st.markdown("### 🔧 Debug Information")
    st.json({
        "auto_speak": st.session_state.get('auto_speak', False),
        "speech_speed": st.session_state.get('speech_speed', 1.0),
        "speech_voice": st.session_state.get('speech_voice', 'default'),
        "session_state_keys": list(st.session_state.keys())
    })