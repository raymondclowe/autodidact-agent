"""
Test script for speech functionality
Tests the basic speech utilities and components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.speech_utils import sanitize_text_for_speech, create_tts_component, create_speaker_button_html


def test_text_sanitization():
    """Test text sanitization for speech"""
    print("Testing text sanitization...")
    
    # Test markdown removal
    test_cases = [
        ("**Bold text**", "Bold text"),
        ("*Italic text*", "Italic text"),
        ("`Code text`", "Code text"),
        ("# Header text", "Header text"),
        ("- List item", "List item"),
        ("E=mc²", "E equals mc²"),
        ("2+2=4", "2 plus 2 equals 4"),
        ("x^2", "x to the power of 2"),
        ("Multiple   spaces", "Multiple spaces"),
    ]
    
    for input_text, expected in test_cases:
        result = sanitize_text_for_speech(input_text)
        print(f"Input: '{input_text}' -> Output: '{result}' (Expected: '{expected}')")
        assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("✅ Text sanitization tests passed!")


def test_tts_component_creation():
    """Test TTS component HTML generation"""
    print("\nTesting TTS component creation...")
    
    test_text = "Hello, this is a test message for speech synthesis."
    
    # Test without auto-trigger
    html = create_tts_component(test_text, auto_trigger=False)
    assert "speakText" in html
    assert "speechSynthesis" in html
    assert test_text.replace('"', '\\"') in html
    assert "false" in html.lower()
    
    # Test with auto-trigger
    html_auto = create_tts_component(test_text, auto_trigger=True)
    assert "true" in html_auto.lower()
    
    print("✅ TTS component creation tests passed!")


def test_speaker_button_creation():
    """Test speaker button HTML generation"""
    print("\nTesting speaker button creation...")
    
    test_text = "Click to hear this text"
    
    html = create_speaker_button_html(test_text)
    assert "🔊" in html
    assert "onclick" in html
    assert "speakText" in html
    assert test_text.replace('"', '\\"') in html
    
    # Test with custom button ID
    custom_id = "test-button-123"
    html_custom = create_speaker_button_html(test_text, button_id=custom_id)
    assert custom_id in html_custom
    
    print("✅ Speaker button creation tests passed!")


def test_complex_text_handling():
    """Test handling of complex text with mathematical formulas and code"""
    print("\nTesting complex text handling...")
    
    complex_text = """
    # Learning About Physics
    
    Einstein's famous equation is **E=mc²**. This shows that:
    - Energy (E) equals mass (m) times speed of light (c) squared
    - `E = m * c^2` in code format
    
    The formula demonstrates energy-mass equivalence.
    """
    
    result = sanitize_text_for_speech(complex_text)
    
    # Check that markdown was removed
    assert "**" not in result
    assert "#" not in result
    assert "`" not in result
    assert "-" not in result  # List markers should be removed
    
    # Check that math symbols were converted
    assert "equals" in result
    assert "times" in result
    assert "to the power of" in result
    
    print(f"Complex text result: {result}")
    print("✅ Complex text handling tests passed!")


if __name__ == "__main__":
    print("Running speech functionality tests...\n")
    
    test_text_sanitization()
    test_tts_component_creation()
    test_speaker_button_creation()
    test_complex_text_handling()
    
    print("\n🎉 All speech functionality tests passed!")
    print("\nNote: These tests verify the HTML/JS generation.")
    print("To test actual speech synthesis, run the Streamlit app and try the speech features.")