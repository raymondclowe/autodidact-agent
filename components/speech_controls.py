"""
Speech controls component for Autodidact
Provides global auto-speak toggle and speech settings
"""

import streamlit as st
from utils.speech_utils import initialize_speech_state


def show_speech_controls(location: str = "header") -> bool:
    """
    Display speech controls in the UI
    
    Args:
        location: Where the controls are displayed ("header", "sidebar", "inline")
    
    Returns:
        bool: Current auto_speak state
    """
    # Initialize speech state
    initialize_speech_state()
    
    if location == "header":
        # Header-style compact controls
        col1, col2 = st.columns([4, 1])
        with col2:
            auto_speak = st.toggle(
                "🔊 Auto-Speak",
                value=st.session_state.auto_speak,
                key="auto_speak_toggle",
                help="Automatically speak AI responses and key content"
            )
            
            # Update session state
            if auto_speak != st.session_state.auto_speak:
                st.session_state.auto_speak = auto_speak
                st.rerun()
                
    elif location == "sidebar":
        # Sidebar-style controls with more options
        st.markdown("### 🔊 Speech Settings")
        
        auto_speak = st.toggle(
            "Auto-Speak Mode",
            value=st.session_state.auto_speak,
            key="auto_speak_sidebar_toggle",
            help="Automatically speak AI responses"
        )
        
        # Speech speed control
        speed = st.slider(
            "Speech Speed",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.speech_speed,
            step=0.1,
            key="speech_speed_slider",
            help="Adjust how fast text is spoken"
        )
        
        # Update session state
        if auto_speak != st.session_state.auto_speak:
            st.session_state.auto_speak = auto_speak
        if speed != st.session_state.speech_speed:
            st.session_state.speech_speed = speed
            
    elif location == "inline":
        # Inline compact toggle
        auto_speak = st.checkbox(
            "🔊 Speak responses automatically",
            value=st.session_state.auto_speak,
            key="auto_speak_inline_toggle"
        )
        
        # Update session state
        if auto_speak != st.session_state.auto_speak:
            st.session_state.auto_speak = auto_speak
    
    return st.session_state.auto_speak


def add_speaker_button_to_text(text: str, container=None) -> None:
    """
    Add a speaker button next to text content
    
    Args:
        text: The text content to add speech capability to
        container: Streamlit container to render in (optional)
    """
    from utils.speech_utils import create_speaker_button_html, create_tts_component
    
    if not text or not text.strip():
        return
    
    # Create the speech components
    tts_component = create_tts_component(text, auto_trigger=False)
    speaker_button = create_speaker_button_html(text)
    
    # Combine components
    speech_html = tts_component + speaker_button
    
    # Render in appropriate container
    if container:
        with container:
            st.components.v1.html(speech_html, height=30)
    else:
        st.components.v1.html(speech_html, height=30)


def create_speech_enabled_markdown(text: str, add_button: bool = True, auto_speak: bool = None) -> None:
    """
    Display markdown text with speech capabilities, MathJax support, and JSXGraph diagrams
    
    Args:
        text: Markdown text to display (may contain JSXGraph tags)
        add_button: Whether to add a speaker button
        auto_speak: Override auto_speak setting
    """
    if not text:
        return
    
    if auto_speak is None:
        auto_speak = st.session_state.get('auto_speak', False)
    
    # Process JSXGraph tags before displaying
    processed_text, jsxgraph_html = _process_jsxgraph_tags(text)
    
    # Display the processed text
    st.markdown(processed_text)
    
    # Render any JSXGraph diagrams
    if jsxgraph_html:
        st.components.v1.html(jsxgraph_html, height=400, scrolling=True)
    
    # Trigger MathJax reprocessing for dynamically added content
    # This ensures mathematical formulas render properly in lessons
    st.components.v1.html("""
    <script>
    // Wait for MathJax to be loaded, then trigger reprocessing
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise().catch(function (err) {
            console.log('MathJax typeset error:', err.message);
        });
    } else {
        // If MathJax isn't loaded yet, wait a bit and try again
        setTimeout(function() {
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise().catch(function (err) {
                    console.log('MathJax typeset error:', err.message);
                });
            }
        }, 100);
    }
    </script>
    """, height=1)
    
    # Add speech functionality
    if add_button or auto_speak:
        from utils.speech_utils import create_tts_component, create_speaker_button_html
        
        speech_html = ""
        
        # Add auto-speak component
        if auto_speak:
            speech_html += create_tts_component(processed_text, auto_trigger=True)
        
        # Add speaker button
        if add_button:
            speech_html += create_speaker_button_html(processed_text)
        
        if speech_html:
            st.components.v1.html(speech_html, height=30)


def _process_jsxgraph_tags(text: str) -> tuple[str, str]:
    """
    Process JSXGraph tags in text and return cleaned text and HTML for diagrams.
    
    Args:
        text: Text potentially containing <jsxgraph>template:id</jsxgraph> tags
        
    Returns:
        Tuple of (processed_text, jsxgraph_html)
    """
    import re
    from components.jsxgraph_utils import create_template_diagram, wrap_jsxgraph_html
    
    # Find all JSXGraph tags
    jsxgraph_pattern = r'<jsxgraph>([^:]+):([^<]+)</jsxgraph>'
    matches = re.findall(jsxgraph_pattern, text)
    
    if not matches:
        return text, ""
    
    # Remove JSXGraph tags from text and collect diagram HTML
    processed_text = text
    diagram_htmls = []
    
    for template_name, graph_id in matches:
        template_name = template_name.strip()
        graph_id = graph_id.strip()
        
        try:
            # Create the diagram
            diagram_html = create_template_diagram(template_name, graph_id)
            diagram_htmls.append(diagram_html)
            
            # Replace the tag with a placeholder
            tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
            replacement = f"*[Interactive diagram: {template_name} - {graph_id}]*"
            processed_text = re.sub(tag_pattern, replacement, processed_text)
            
        except Exception as e:
            # If template fails, show error message
            error_msg = f"*[Diagram error: {template_name} - {str(e)}]*"
            tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
            processed_text = re.sub(tag_pattern, error_msg, processed_text)
    
    # Combine all diagram HTML
    combined_html = ""
    if diagram_htmls:
        combined_html = "\n".join(diagram_htmls)
    
    return processed_text, combined_html


def create_speech_enabled_write(text: str, add_button: bool = True, auto_speak: bool = None) -> None:
    """
    Display plain text with speech capabilities (using st.write)
    
    Args:
        text: Text to display
        add_button: Whether to add a speaker button
        auto_speak: Override auto_speak setting
    """
    if not text:
        return
    
    if auto_speak is None:
        auto_speak = st.session_state.get('auto_speak', False)
    
    # Display the text
    st.write(text)
    
    # Add speech functionality
    if add_button or auto_speak:
        from utils.speech_utils import create_tts_component, create_speaker_button_html
        
        speech_html = ""
        
        # Add auto-speak component
        if auto_speak:
            speech_html += create_tts_component(text, auto_trigger=True)
        
        # Add speaker button
        if add_button:
            speech_html += create_speaker_button_html(text)
        
        if speech_html:
            st.components.v1.html(speech_html, height=30)


def show_speech_status():
    """Display current speech settings status"""
    initialize_speech_state()
    
    if st.session_state.auto_speak:
        st.success("🔊 Auto-speak is ON - AI responses will be spoken automatically")
    else:
        st.info("🔇 Auto-speak is OFF - Click speaker buttons (🔊) to hear content")


def create_global_speech_component():
    """
    Create a global speech component that handles speech across the app
    This should be included once per page to enable speech functionality
    """
    initialize_speech_state()
    
    html_content = f"""
    <script>
    // Global speech utilities
    window.autodidactSpeech = {{
        settings: {{
            rate: {st.session_state.speech_speed},
            autoSpeak: {str(st.session_state.auto_speak).lower()}
        }},
        
        speak: function(text, options = {{}}) {{
            if (!('speechSynthesis' in window)) {{
                console.log('Speech synthesis not supported');
                return false;
            }}
            
            // Stop current speech
            window.speechSynthesis.cancel();
            
            if (!text || text.trim() === '') {{
                return false;
            }}
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = options.rate || this.settings.rate;
            utterance.pitch = options.pitch || 1.0;
            utterance.volume = options.volume || 1.0;
            
            window.speechSynthesis.speak(utterance);
            return true;
        }},
        
        stop: function() {{
            window.speechSynthesis.cancel();
        }},
        
        updateSettings: function(newSettings) {{
            this.settings = {{ ...this.settings, ...newSettings }};
        }}
    }};
    
    // Make speakText function globally available for compatibility
    window.speakText = function(text) {{
        return window.autodidactSpeech.speak(text);
    }};
    </script>
    """
    
    st.components.v1.html(html_content, height=0)