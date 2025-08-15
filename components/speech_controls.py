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
    from components.simple_math_renderer import MATH_RENDERER_JS
    
    st.components.v1.html(f"""
    {MATH_RENDERER_JS}
    
    <script>
    // Robust MathJax reprocessing with fallback to SimpleMathRenderer
    (function() {{
        let retryCount = 0;
        const maxRetries = 30; // Reduce retries since we have a fallback (3 seconds)
        
        function tryMathJaxReprocessing() {{
            // Access MathJax from parent window if we're in an iframe
            const mathJax = window.parent && window.parent.MathJax ? window.parent.MathJax : window.MathJax;
            const mathJaxReady = window.parent && window.parent.mathJaxReady ? window.parent.mathJaxReady : window.mathJaxReady;
            
            if (mathJax && mathJax.typesetPromise && mathJaxReady) {{
                console.log('MathJax found and ready, triggering reprocessing...');
                mathJax.typesetPromise().then(function() {{
                    console.log('MathJax reprocessing completed successfully');
                }}).catch(function (err) {{
                    console.log('MathJax typeset error:', err.message);
                    useFallbackRenderer();
                }});
                return true; // Success
            }} else if (retryCount < maxRetries) {{
                retryCount++;
                if (retryCount % 10 === 0) {{
                    console.log('Waiting for MathJax... attempt ' + retryCount + '/' + maxRetries);
                }}
                setTimeout(tryMathJaxReprocessing, 100);
                return false; // Will retry
            }} else {{
                console.log('MathJax not found or not ready after ' + maxRetries + ' attempts, using fallback renderer');
                useFallbackRenderer();
                return false; // Give up on MathJax, use fallback
            }}
        }}
        
        function useFallbackRenderer() {{
            // Use the SimpleMathRenderer that's included in this context
            if (window.SimpleMathRenderer) {{
                console.log('Using SimpleMathRenderer fallback in current context...');
                // Process content in parent window
                if (window.parent && window.parent.document) {{
                    const parentDoc = window.parent.document;
                    
                    // Find and process math expressions in parent document
                    let displayMath = parentDoc.querySelectorAll('p, div, span');
                    displayMath.forEach(function(element) {{
                        let content = element.innerHTML;
                        if (content.includes('[') && content.includes(']')) {{
                            // Replace display math expressions
                            content = content.replace(/\[([^[\]]+)\]/g, function(match, expr) {{
                                let rendered = window.SimpleMathRenderer.renderExpression(expr);
                                return '<span style="display: block; text-align: center; margin: 10px 0; font-style: italic; font-weight: bold; color: #2E5090;">' + rendered + '</span>';
                            }});
                            element.innerHTML = content;
                        }}
                        
                        // Replace inline math expressions (expression)
                        content = element.innerHTML;
                        if (content.includes('(') && content.includes(')')) {{
                            content = content.replace(/\(([^()]*\\\\[^()]*[^()]*)\)/g, function(match, expr) {{
                                if (expr.includes('\\\\')) {{ // Only process if it contains LaTeX
                                    let rendered = window.SimpleMathRenderer.renderExpression(expr);
                                    return '<span style="font-style: italic; color: #2E5090;">' + rendered + '</span>';
                                }}
                                return match;
                            }});
                            element.innerHTML = content;
                        }}
                    }});
                    
                    console.log('Fallback math rendering completed on parent document');
                }} else {{
                    console.log('Cannot access parent document for math rendering');
                }}
            }} else {{
                console.log('SimpleMathRenderer not available in current context');
            }}
        }}
        
        // Start the process
        tryMathJaxReprocessing();
    }})();
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
              and custom JSXGraph code blocks
        
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
            # Handle custom diagrams
            if template_name == "custom":
                # Look for JavaScript code after the tag
                custom_code = _extract_custom_jsxgraph_code(text, template_name, graph_id)
                diagram_html = create_template_diagram(template_name, graph_id, custom_code)
                
                # Remove both the tag and the custom code from the text
                tag_and_code_pattern = _build_custom_removal_pattern(template_name, graph_id, custom_code)
                processed_text = re.sub(tag_and_code_pattern, 
                                      f"*[Interactive diagram: custom - {graph_id}]*", 
                                      processed_text, flags=re.DOTALL)
            else:
                # Handle template diagrams
                diagram_html = create_template_diagram(template_name, graph_id)
                
                # Replace the tag with a placeholder
                tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
                replacement = f"*[Interactive diagram: {template_name} - {graph_id}]*"
                processed_text = re.sub(tag_pattern, replacement, processed_text)
            
            diagram_htmls.append(diagram_html)
            
        except Exception as e:
            # If diagram fails, show error message
            error_msg = f"*[Diagram error: {template_name} - {str(e)}]*"
            tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
            processed_text = re.sub(tag_pattern, error_msg, processed_text)
    
    # Combine all diagram HTML
    combined_html = ""
    if diagram_htmls:
        combined_html = "\n".join(diagram_htmls)
    
    return processed_text, combined_html


def _extract_custom_jsxgraph_code(text: str, template_name: str, graph_id: str) -> str:
    """
    Extract custom JSXGraph JavaScript code following a custom tag.
    
    Args:
        text: Full text containing the tag and code
        template_name: Should be "custom"
        graph_id: Graph identifier
        
    Returns:
        JavaScript code string
    """
    import re
    
    # Pattern to find the tag and capture code in following ```javascript or ``` block
    tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
    
    # Look for JavaScript code block after the tag
    code_pattern = tag_pattern + r'\s*```(?:javascript)?\s*(.*?)\s*```'
    
    match = re.search(code_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If no code block found, throw error
    raise ValueError(f"No JavaScript code block found after custom JSXGraph tag for {graph_id}")


def _build_custom_removal_pattern(template_name: str, graph_id: str, custom_code: str) -> str:
    """
    Build regex pattern to remove both tag and custom code from text.
    
    Args:
        template_name: Template name (should be "custom")
        graph_id: Graph identifier
        custom_code: The extracted custom code
        
    Returns:
        Regex pattern string
    """
    import re
    
    tag_pattern = f'<jsxgraph>{re.escape(template_name)}:{re.escape(graph_id)}</jsxgraph>'
    # Pattern to match the tag and the following code block
    return tag_pattern + r'\s*```(?:javascript)?\s*.*?\s*```'


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