#!/usr/bin/env python3
"""
Test the actual fix for issue #121 in the teaching node context
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

def test_llm_initialization_with_402_error():
    """Test that 402 errors in LLM initialization are handled properly."""
    print("Testing LLM initialization with 402 error...")
    
    # Mock the OpenAI error that happens during llm.invoke()
    class MockOpenAIError(Exception):
        def __init__(self):
            self.response = MagicMock()
            self.response.status_code = 402
            # Simulate the error structure that would be returned by OpenAI/OpenRouter
            self.response.json.return_value = {
                'error': {
                    'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
                    'code': 402,
                    'metadata': {'provider_name': None}
                }
            }
            super().__init__("Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits', 'code': 402, 'metadata': {'provider_name': None}}, 'user_id': 'user_2edDjJDbdOHWLaSFpbFsTHCawsZ'}")
    
    # Test the error handling directly
    from utils.error_handling import handle_api_error
    
    error = MockOpenAIError()
    user_message, is_retryable = handle_api_error(error, "LLM initialization")
    
    print(f"User message: {user_message[:100]}...")
    print(f"Is retryable: {is_retryable}")
    
    # Verify the message contains credit-related information
    assert "💳" in user_message or "credit" in user_message.lower(), "Should mention credits"
    assert "32" in user_message or "token" in user_message.lower(), "Should mention tokens"
    
    print("✅ Enhanced error handling works for LLM initialization")
    return True


def test_teaching_node_error_message():
    """Test that the teaching node will show better error messages."""
    print("Testing teaching node error handling...")
    
    # The teaching node error message is what the user actually sees
    # After our fix, instead of: "LLM not initialized - check API key"
    # They should see the enhanced credit error message
    
    # This simulates what would happen in the actual teaching_node function
    from backend.graph_v05 import get_llm
    
    # Mock the provider functions to simulate an OpenRouter setup
    with patch('backend.graph_v05.get_current_provider', return_value='openrouter'):
        with patch('backend.graph_v05.load_api_key', return_value='fake_key'):
            with patch('backend.graph_v05.get_provider_config', return_value={'base_url': 'https://openrouter.ai/api/v1'}):
                with patch('backend.graph_v05.get_model_for_task', return_value='some-model'):
                    # Mock ChatOpenAI to raise our 402 error
                    with patch('backend.graph_v05.ChatOpenAI') as mock_chat:
                        mock_instance = MagicMock()
                        mock_chat.return_value = mock_instance
                        
                        # Make invoke() raise the 402 error
                        mock_instance.invoke.side_effect = Exception("Error code: 402 - {'error': {'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits', 'code': 402, 'metadata': {'provider_name': None}}}")
                        
                        # Capture print output
                        import io
                        from contextlib import redirect_stdout
                        
                        captured_output = io.StringIO()
                        with redirect_stdout(captured_output):
                            result = get_llm()
                        
                        output = captured_output.getvalue()
                        print(f"Captured output: {output}")
                        
                        # Verify that get_llm returns None (indicating failure)
                        assert result is None, "get_llm should return None on error"
                        
                        # Verify that enhanced error message appears in output
                        # The output should contain credit-related information instead of just generic error
                        assert "credit" in output.lower() or "💳" in output, f"Should show credit error info, got: {output}"
    
    print("✅ Teaching node will show enhanced error messages")
    return True


def main():
    """Run the tests."""
    print("🔧 Testing Issue #121 Fix in Real Context")
    print("=" * 50)
    
    try:
        test_llm_initialization_with_402_error()
        print()
        test_teaching_node_error_message()
        print()
        
        print("=" * 50)
        print("🎉 All tests passed!")
        print()
        print("✅ The fix is working correctly:")
        print("- 402 credit errors are properly detected")
        print("- Enhanced error messages are shown to users")
        print("- The teaching node will display helpful credit information")
        print("- Users will know exactly how to fix the credit issue")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()