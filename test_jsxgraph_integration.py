#!/usr/bin/env python3
"""
Test JSXGraph integration and model updates for issue #82
"""

def test_jsxgraph_templates():
    """Test JSXGraph template creation"""
    print("Testing JSXGraph template functionality...")
    
    from components.jsxgraph_utils import (
        get_available_templates, 
        create_template_diagram,
        create_triangle_diagram
    )
    
    # Test available templates
    templates = get_available_templates()
    print(f"✅ Available templates: {len(templates)}")
    for name, desc in templates.items():
        print(f"  - {name}: {desc}")
    
    # Test template creation
    try:
        diagram_html = create_template_diagram("pythagorean_theorem", "test_triangle")
        assert "<div id=\"test_triangle\"" in diagram_html
        assert "JXG.JSXGraph.initBoard" in diagram_html
        print("✅ Template diagram creation works")
    except Exception as e:
        print(f"❌ Template creation failed: {e}")
        return False
    
    # Test custom diagram
    try:
        custom_html = create_triangle_diagram("custom_triangle")
        assert "custom_triangle" in custom_html
        print("✅ Custom diagram creation works")
    except Exception as e:
        print(f"❌ Custom diagram creation failed: {e}")
        return False
    
    return True


def test_model_capabilities():
    """Test model capability checking"""
    print("\nTesting model capability detection...")
    
    from utils.providers import is_diagram_capable_model, get_model_capability_warning
    
    # Test high-capability models
    high_cap_models = ["gpt-5", "anthropic/claude-opus-4.1"]
    for model in high_cap_models:
        is_capable = is_diagram_capable_model(model)
        warning = get_model_capability_warning(model)
        print(f"  {model}: capable={is_capable}, warning={'Yes' if warning else 'No'}")
        assert is_capable, f"Expected {model} to be diagram capable"
        assert not warning, f"Expected no warning for {model}"
    
    # Test lower-capability models
    low_cap_models = ["gpt-4o-mini", "anthropic/claude-3.5-haiku"]
    for model in low_cap_models:
        is_capable = is_diagram_capable_model(model)
        warning = get_model_capability_warning(model)
        print(f"  {model}: capable={is_capable}, warning={'Yes' if warning else 'No'}")
        assert not is_capable, f"Expected {model} to not be diagram capable"
        assert warning, f"Expected warning for {model}"
    
    print("✅ Model capability detection works correctly")
    return True


def test_model_configuration():
    """Test updated model configuration"""
    print("\nTesting model configuration updates...")
    
    from utils.config import PROVIDER_MODELS
    
    # Check OpenAI provider updates
    openai_config = PROVIDER_MODELS["openai"]
    assert openai_config["chat"] == "gpt-5", f"Expected OpenAI chat model to be gpt-5, got {openai_config['chat']}"
    print("✅ OpenAI chat model updated to gpt-5")
    
    # Check OpenRouter provider updates 
    openrouter_config = PROVIDER_MODELS["openrouter"]
    assert openrouter_config["chat"] == "anthropic/claude-opus-4.1", f"Expected OpenRouter chat model to be claude-opus-4.1, got {openrouter_config['chat']}"
    print("✅ OpenRouter chat model updated to claude-opus-4.1")
    
    # Check token limits include new models
    assert "gpt-5" in openai_config["token_limits"], "Expected gpt-5 in OpenAI token limits"
    assert "anthropic/claude-opus-4.1" in openrouter_config["token_limits"], "Expected claude-opus-4.1 in OpenRouter token limits"
    print("✅ Token limits configured for new models")
    
    return True


def test_jsxgraph_processing():
    """Test JSXGraph tag processing in text"""
    print("\nTesting JSXGraph tag processing...")
    
    from components.speech_controls import _process_jsxgraph_tags
    
    # Test text with JSXGraph tags
    test_text = """
    Let's learn about triangles!
    
    <jsxgraph>pythagorean_theorem:demo1</jsxgraph>
    
    As you can see in the diagram above, this demonstrates the relationship a² + b² = c².
    
    Here's another example:
    <jsxgraph>unit_circle:demo2</jsxgraph>
    """
    
    try:
        processed_text, jsxgraph_html = _process_jsxgraph_tags(test_text)
        
        # Check that tags were replaced
        assert "<jsxgraph>" not in processed_text, "JSXGraph tags should be removed from text"
        assert "Interactive diagram: pythagorean_theorem - demo1" in processed_text
        assert "Interactive diagram: unit_circle - demo2" in processed_text
        
        # Check that HTML was generated
        assert jsxgraph_html, "JSXGraph HTML should be generated"
        assert "demo1" in jsxgraph_html, "demo1 diagram should be in HTML"
        assert "demo2" in jsxgraph_html, "demo2 diagram should be in HTML"
        
        print("✅ JSXGraph tag processing works correctly")
        return True
        
    except Exception as e:
        print(f"❌ JSXGraph tag processing failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing JSXGraph Integration for Issue #82")
    print("=" * 50)
    
    tests = [
        test_model_configuration,
        test_model_capabilities, 
        test_jsxgraph_templates,
        test_jsxgraph_processing,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! JSXGraph integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)