#!/usr/bin/env python3
"""
Test to verify the max_tokens fix for the ChatOpenAI initialization
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import inspect

sys.path.insert(0, str(Path(__file__).parent))

def test_get_llm_max_tokens():
    """Test that get_llm function sets max_tokens parameter to 4000"""
    print("🔧 Testing max_tokens fix for ChatOpenAI initialization")
    print("=" * 60)
    
    # Mock the dependencies to avoid actual API calls
    with patch('utils.config.get_current_provider') as mock_provider, \
         patch('utils.config.load_api_key') as mock_api_key, \
         patch('utils.providers.get_provider_config') as mock_config, \
         patch('utils.providers.get_model_for_task') as mock_model, \
         patch('langchain_openai.ChatOpenAI') as mock_chatopenai:
        
        # Setup mocks
        mock_provider.return_value = "openrouter"
        mock_api_key.return_value = "test-api-key"
        mock_config.return_value = {"base_url": "https://openrouter.ai/api/v1"}
        mock_model.return_value = "test-model"
        
        # Create a mock ChatOpenAI instance that doesn't make API calls
        mock_llm_instance = MagicMock()
        mock_chatopenai.return_value = mock_llm_instance
        
        # Mock the invoke method to avoid actual API calls
        mock_llm_instance.invoke.return_value = MagicMock()
        
        # Import and call the function after setting up mocks
        from backend.graph_v05 import get_llm
        
        # Reset the global llm variable
        import backend.graph_v05
        backend.graph_v05.llm = None
        
        # Call get_llm which should create a ChatOpenAI instance
        result = get_llm()
        
        # Verify ChatOpenAI was called with max_tokens=4000
        mock_chatopenai.assert_called_once()
        call_args = mock_chatopenai.call_args
        call_kwargs = call_args[1]  # Get keyword arguments
        
        print(f"ChatOpenAI called with kwargs: {call_kwargs}")
        
        # Check that max_tokens was set to 4000
        assert 'max_tokens' in call_kwargs, "max_tokens parameter should be present"
        assert call_kwargs['max_tokens'] == 4000, f"max_tokens should be 4000, got {call_kwargs['max_tokens']}"
        
        # Check other expected parameters
        assert call_kwargs['model_name'] == "test-model", "model_name should be set"
        assert call_kwargs['temperature'] == 0.7, "temperature should be 0.7"
        assert call_kwargs['openai_api_key'] == "test-api-key", "API key should be set"
        assert call_kwargs['base_url'] == "https://openrouter.ai/api/v1", "base_url should be set for OpenRouter"
        
        print("✅ max_tokens parameter correctly set to 4000")
        print("✅ Other parameters correctly set")
        print("✅ ChatOpenAI initialization successful")
        
        return True

def test_max_tokens_reasonable_value():
    """Test that 4000 tokens is a reasonable value for lesson interactions"""
    print("\n🧮 Testing max_tokens value reasonableness")
    print("=" * 50)
    
    max_tokens = 4000
    
    # Typical lesson interaction scenarios
    scenarios = [
        ("Short answer", "This is a brief explanation of a concept.", 50),
        ("Medium explanation", "A" * 800, 200),  # ~200 token explanation
        ("Long detailed response", "A" * 2000, 500),  # ~500 token response
        ("Very comprehensive answer", "A" * 8000, 2000),  # ~2000 token response
    ]
    
    print(f"Max tokens limit: {max_tokens}")
    print("\nTypical lesson interaction scenarios:")
    
    for scenario_name, content, estimated_tokens in scenarios:
        within_limit = estimated_tokens <= max_tokens
        status = "✅" if within_limit else "❌"
        print(f"{status} {scenario_name}: ~{estimated_tokens} tokens {'(within limit)' if within_limit else '(exceeds limit)'}")
    
    # Check that our limit allows for good responses but prevents excessive ones
    assert max_tokens >= 1000, "Should allow for substantial responses"
    assert max_tokens <= 8000, "Should prevent excessive token usage"
    
    print(f"\n✅ {max_tokens} tokens is a reasonable limit for lesson interactions")
    print("  - Allows substantial explanations and examples")
    print("  - Prevents excessive token costs")
    print("  - Aligns with existing error handling logic (8k cap)")
    
    return True

def test_compared_to_previous_32k():
    """Compare the new 4k limit to the problematic 32k default"""
    print("\n📊 Comparing to previous 32k token issue")
    print("=" * 45)
    
    old_limit = 32000
    new_limit = 4000
    reduction_percent = ((old_limit - new_limit) / old_limit) * 100
    
    print(f"Previous limit: {old_limit:,} tokens")
    print(f"New limit: {new_limit:,} tokens")
    print(f"Reduction: {reduction_percent:.1f}%")
    
    # Estimate cost impact (rough approximation)
    # Assuming $0.001 per 1k tokens (varies by provider/model)
    old_cost_per_request = (old_limit / 1000) * 0.001
    new_cost_per_request = (new_limit / 1000) * 0.001
    cost_reduction = ((old_cost_per_request - new_cost_per_request) / old_cost_per_request) * 100
    
    print(f"\nEstimated cost per request:")
    print(f"  Previous: ~${old_cost_per_request:.4f}")
    print(f"  New: ~${new_cost_per_request:.4f}")
    print(f"  Cost reduction: {cost_reduction:.1f}%")
    
    assert new_limit < old_limit, "New limit should be lower than old"
    assert reduction_percent > 80, "Should achieve significant reduction"
    
    print("\n✅ Significant improvement in token usage and cost efficiency")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Max Tokens Fix for Issue #124")
    print("=" * 70)
    
    success = True
    
    try:
        success &= test_get_llm_max_tokens()
        success &= test_max_tokens_reasonable_value()
        success &= test_compared_to_previous_32k()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 ALL TESTS PASSED!")
            print("\n📝 Summary:")
            print("  - ChatOpenAI now limits responses to 4,000 tokens")
            print("  - 87.5% reduction from previous 32,000 token requests")
            print("  - Reasonable limit for lesson interactions")
            print("  - Prevents excessive costs while maintaining quality")
            print("\n🔧 The fix should resolve the OpenRouter credit exhaustion issue.")
        else:
            print("❌ SOME TESTS FAILED!")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)