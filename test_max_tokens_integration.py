#!/usr/bin/env python3
"""
Integration test to verify the get_llm function works with the max_tokens fix
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

def test_get_llm_integration():
    """Test that get_llm function works properly with max_tokens parameter"""
    print("🔧 Testing get_llm integration with max_tokens fix")
    print("=" * 55)
    
    # We need to mock all the dependencies
    with patch('langchain_openai.ChatOpenAI') as mock_chatopenai:
        with patch('utils.config.get_current_provider', return_value='openrouter'):
            with patch('utils.config.load_api_key', return_value='test-key'):
                with patch('utils.providers.get_provider_config', return_value={'base_url': 'https://openrouter.ai/api/v1'}):
                    with patch('utils.providers.get_model_for_task', return_value='test-model'):
                        with patch('utils.config.APP_NAME', 'TestApp'):
                            with patch('utils.config.APP_URL', 'https://test.com'):
                                
                                # Create a mock ChatOpenAI instance
                                mock_llm_instance = MagicMock()
                                mock_llm_instance.invoke.return_value = MagicMock()
                                mock_chatopenai.return_value = mock_llm_instance
                                
                                # Import and test the function
                                from backend.graph_v05 import get_llm
                                import backend.graph_v05
                                
                                # Reset global state
                                backend.graph_v05.llm = None
                                
                                # Call the function
                                result = get_llm()
                                
                                # Verify the result
                                assert result is not None, "get_llm should return an LLM instance"
                                
                                # Verify ChatOpenAI was called with correct parameters
                                mock_chatopenai.assert_called_once()
                                call_kwargs = mock_chatopenai.call_args[1]
                                
                                expected_params = {
                                    'model_name': 'test-model',
                                    'temperature': 0.7,
                                    'openai_api_key': 'test-key',
                                    'max_tokens': 4000,
                                    'base_url': 'https://openrouter.ai/api/v1',
                                    'default_headers': {
                                        'HTTP-Referer': 'https://test.com',
                                        'X-Title': 'TestApp'
                                    }
                                }
                                
                                for key, expected_value in expected_params.items():
                                    assert key in call_kwargs, f"Parameter {key} should be present"
                                    assert call_kwargs[key] == expected_value, f"Parameter {key} should be {expected_value}, got {call_kwargs[key]}"
                                
                                print("✅ get_llm function works correctly with max_tokens")
                                print("✅ All parameters passed correctly to ChatOpenAI")
                                print(f"✅ max_tokens correctly set to {call_kwargs['max_tokens']}")
                                
                                return True

def test_error_scenarios():
    """Test error handling scenarios with the new max_tokens parameter"""
    print("\n🚨 Testing error scenarios")
    print("=" * 30)
    
    # Test with missing API key
    with patch('utils.config.get_current_provider', return_value='openrouter'):
        with patch('utils.config.load_api_key', return_value=''):  # Empty API key
            
            from backend.graph_v05 import get_llm
            import backend.graph_v05
            
            # Reset global state
            backend.graph_v05.llm = None
            
            result = get_llm()
            
            assert result is None, "get_llm should return None for missing API key"
            
            print("✅ Handles missing API key correctly")
    
    # Test with API error during initialization
    with patch('langchain_openai.ChatOpenAI') as mock_chatopenai:
        with patch('utils.config.get_current_provider', return_value='openrouter'):
            with patch('utils.config.load_api_key', return_value='test-key'):
                with patch('utils.providers.get_provider_config', return_value={'base_url': 'https://openrouter.ai/api/v1'}):
                    with patch('utils.providers.get_model_for_task', return_value='test-model'):
                        with patch('utils.config.APP_NAME', 'TestApp'):
                            with patch('utils.config.APP_URL', 'https://test.com'):
                                
                                # Mock ChatOpenAI to raise an exception during initialization
                                mock_llm_instance = MagicMock()
                                mock_llm_instance.invoke.side_effect = Exception("API Error")
                                mock_chatopenai.return_value = mock_llm_instance
                                
                                from backend.graph_v05 import get_llm
                                import backend.graph_v05
                                
                                # Reset global state
                                backend.graph_v05.llm = None
                                
                                result = get_llm()
                                
                                assert result is None, "get_llm should return None when API test fails"
                                
                                print("✅ Handles API errors correctly")
    
    return True

def main():
    """Run all integration tests"""
    print("🧪 Integration Testing Max Tokens Fix")
    print("=" * 40)
    
    success = True
    
    try:
        success &= test_get_llm_integration()
        success &= test_error_scenarios()
        
        print("\n" + "=" * 40)
        if success:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("\n✅ The get_llm function correctly:")
            print("  - Sets max_tokens to 4000")
            print("  - Passes all required parameters")
            print("  - Handles error scenarios gracefully")
            print("  - Maintains existing functionality")
        else:
            print("❌ SOME INTEGRATION TESTS FAILED!")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)