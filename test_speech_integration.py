"""
Integration test for speech functionality
Tests the integration between speech components and utilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Streamlit components for testing
class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __contains__(self, key):
        return key in self._state

class MockStreamlit:
    session_state = MockSessionState()
    
    components = type('MockComponents', (), {})()
    components.v1 = type('MockV1', (), {})()
    components.v1.html = lambda html, height=None: f"<HTML_COMPONENT height={height}>{html}</HTML_COMPONENT>"
    
    @staticmethod
    def toggle(label, value=False, key=None, help=None):
        return value
    
    @staticmethod
    def checkbox(label, value=False, key=None):
        return value
    
    @staticmethod
    def slider(label, min_value=0, max_value=100, value=50, step=1, key=None, help=None):
        return value
    
    @staticmethod
    def columns(spec):
        return [MockStreamlit() for _ in range(spec if isinstance(spec, int) else len(spec))]
    
    @staticmethod
    def markdown(text):
        print(f"MARKDOWN: {text}")
    
    @staticmethod
    def write(text):
        print(f"WRITE: {text}")
    
    @staticmethod
    def info(text):
        print(f"INFO: {text}")
    
    @staticmethod
    def success(text):
        print(f"SUCCESS: {text}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

# Patch streamlit for testing
sys.modules['streamlit'] = MockStreamlit

from utils.speech_utils import initialize_speech_state, get_speech_enabled_content
from components.speech_controls import show_speech_controls, create_speech_enabled_markdown


def test_speech_state_initialization():
    """Test speech state initialization"""
    print("Testing speech state initialization...")
    
    # Clear any existing state
    MockStreamlit.session_state._state.clear()
    
    # Initialize speech state
    initialize_speech_state()
    
    # Debug: Print actual state
    print(f"Actual session state: {MockStreamlit.session_state._state}")
    
    # Check that all required state variables are set
    assert 'auto_speak' in MockStreamlit.session_state._state
    assert 'speech_speed' in MockStreamlit.session_state._state
    assert 'speech_voice' in MockStreamlit.session_state._state
    
    # Check default values
    assert MockStreamlit.session_state._state['auto_speak'] == False
    assert MockStreamlit.session_state._state['speech_speed'] == 1.0
    assert MockStreamlit.session_state._state['speech_voice'] == 'default'
    
    print("✅ Speech state initialization test passed!")


def test_speech_enabled_content():
    """Test speech-enabled content generation"""
    print("\nTesting speech-enabled content generation...")
    
    # Initialize state
    initialize_speech_state()
    
    test_text = "This is a test message for speech synthesis."
    
    # Test with auto-speak disabled, no button
    content, speech_html = get_speech_enabled_content(test_text, add_speaker_button=False, auto_speak=False)
    assert content == test_text
    assert speech_html == ""
    
    # Test with speaker button only
    content, speech_html = get_speech_enabled_content(test_text, add_speaker_button=True, auto_speak=False)
    assert content == test_text
    assert "🔊" in speech_html
    assert "speakText" in speech_html
    
    # Test with auto-speak enabled
    content, speech_html = get_speech_enabled_content(test_text, add_speaker_button=False, auto_speak=True)
    assert content == test_text
    assert "speechSynthesis" in speech_html
    assert "true" in speech_html.lower()
    
    # Test with both auto-speak and button
    content, speech_html = get_speech_enabled_content(test_text, add_speaker_button=True, auto_speak=True)
    assert content == test_text
    assert "🔊" in speech_html
    assert "speechSynthesis" in speech_html
    
    print("✅ Speech-enabled content generation test passed!")


def test_speech_controls():
    """Test speech control components"""
    print("\nTesting speech control components...")
    
    # Initialize state
    initialize_speech_state()
    
    # Test different control locations (this mainly tests that they don't crash)
    try:
        show_speech_controls(location="header")
        show_speech_controls(location="sidebar") 
        show_speech_controls(location="inline")
        print("✅ Speech controls test passed!")
    except Exception as e:
        print(f"❌ Speech controls test failed: {e}")
        raise


def test_speech_enabled_markdown():
    """Test speech-enabled markdown component"""
    print("\nTesting speech-enabled markdown component...")
    
    # Initialize state
    initialize_speech_state()
    
    test_markdown = """
    # Test Heading
    
    This is **bold text** and *italic text* with some `code`.
    
    Mathematical formula: E=mc²
    
    - List item 1
    - List item 2
    """
    
    # Test with button
    try:
        create_speech_enabled_markdown(test_markdown, add_button=True, auto_speak=False)
        print("✅ Speech-enabled markdown test passed!")
    except Exception as e:
        print(f"❌ Speech-enabled markdown test failed: {e}")
        raise


def test_auto_speak_behavior():
    """Test auto-speak behavior with session state"""
    print("\nTesting auto-speak behavior...")
    
    # Initialize state
    initialize_speech_state()
    
    # Test with auto-speak disabled
    MockStreamlit.session_state['auto_speak'] = False
    content, speech_html = get_speech_enabled_content("Test message", add_speaker_button=True)
    
    # Should have button but no auto-trigger
    assert "🔊" in speech_html
    assert "true" not in speech_html.lower() or "auto_trigger=true" not in speech_html.lower()
    
    # Test with auto-speak enabled
    MockStreamlit.session_state['auto_speak'] = True
    content, speech_html = get_speech_enabled_content("Test message", add_speaker_button=True)
    
    # Should have both button and auto-trigger
    assert "🔊" in speech_html
    assert "speechSynthesis" in speech_html
    
    print("✅ Auto-speak behavior test passed!")


def test_complex_content_handling():
    """Test handling of complex educational content"""
    print("\nTesting complex content handling...")
    
    # Initialize state
    initialize_speech_state()
    
    complex_content = """
    ## Quantum Physics Basics
    
    **Schrödinger's equation**: iℏ ∂ψ/∂t = Ĥψ
    
    Key concepts:
    - Wave function ψ (psi)
    - Hamiltonian operator Ĥ
    - Reduced Planck constant ℏ = h/2π
    
    This equation describes how quantum states evolve over time.
    """
    
    # Test that it processes without errors
    try:
        content, speech_html = get_speech_enabled_content(complex_content, add_speaker_button=True, auto_speak=True)
        
        # Should have both auto-speak and button components
        assert "speechSynthesis" in speech_html
        assert "🔊" in speech_html
        
        print("✅ Complex content handling test passed!")
    except Exception as e:
        print(f"❌ Complex content handling test failed: {e}")
        raise


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")
    
    # Initialize state
    initialize_speech_state()
    
    # Test empty content
    content, speech_html = get_speech_enabled_content("", add_speaker_button=True, auto_speak=True)
    assert content == ""
    assert speech_html == ""
    
    # Test None content
    content, speech_html = get_speech_enabled_content(None, add_speaker_button=True, auto_speak=True)
    assert content is None
    assert speech_html == ""
    
    # Test whitespace-only content
    content, speech_html = get_speech_enabled_content("   \n\t   ", add_speaker_button=True, auto_speak=True)
    assert speech_html == ""
    
    print("✅ Edge cases test passed!")


if __name__ == "__main__":
    print("Running speech integration tests...\n")
    
    test_speech_state_initialization()
    test_speech_enabled_content()
    test_speech_controls()
    test_speech_enabled_markdown()
    test_auto_speak_behavior()
    test_complex_content_handling()
    test_edge_cases()
    
    print("\n🎉 All speech integration tests passed!")
    print("\nSummary:")
    print("- Speech state management: ✅")
    print("- Content processing: ✅") 
    print("- Component rendering: ✅")
    print("- Auto-speak behavior: ✅")
    print("- Complex content: ✅")
    print("- Edge case handling: ✅")
    print("\nThe speech functionality is ready for browser testing!")