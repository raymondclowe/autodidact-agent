#!/usr/bin/env python3
"""
Test for issue #121 fix: 402 payment required error handling
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.error_handling import handle_api_error, parse_openrouter_error, create_user_friendly_error_message


def test_402_credit_error_parsing():
    """Test that 402 credit errors are properly parsed."""
    print("Testing 402 credit error parsing...")
    
    # Simulate the exact error from the issue
    test_error = {
        'error': {
            'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
            'code': 402,
            'metadata': {'provider_name': None}
        },
        'user_id': 'user_2edDjJDbdOHWLaSFpbFsTHCawsZ'
    }
    
    result = parse_openrouter_error(test_error)
    
    assert result is not None, "Should parse the 402 error"
    assert result['error_type'] == 'insufficient_credits', f"Expected 'insufficient_credits', got {result['error_type']}"
    assert result['provider_name'] == 'OpenRouter', f"Expected 'OpenRouter', got {result['provider_name']}"
    assert result['error_code'] == 402, f"Expected 402, got {result['error_code']}"
    
    print("✅ 402 credit error parsing works correctly")
    return True


def test_user_friendly_message():
    """Test that user-friendly messages are generated correctly."""
    print("Testing user-friendly message generation...")
    
    error_info = {
        'provider_name': 'OpenRouter',
        'error_type': 'insufficient_credits',
        'error_message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
        'error_code': 402
    }
    
    message = create_user_friendly_error_message(error_info)
    
    # Check that the message contains expected elements
    assert "💳" in message, "Should have credit emoji"
    assert "Insufficient Credits" in message, "Should mention insufficient credits"
    assert "32,000" in message, "Should show requested tokens with formatting"
    assert "31,399" in message, "Should show affordable tokens with formatting"
    assert "601" in message, "Should calculate and show shortage"
    assert "openrouter.ai/settings/credits" in message, "Should include the direct link"
    assert "Solutions:" in message, "Should provide solutions"
    
    print("✅ User-friendly message generation works correctly")
    return True


def test_handle_api_error_integration():
    """Test the complete error handling flow."""
    print("Testing complete error handling flow...")
    
    # Simulate the error response object from the issue
    class MockErrorResponse:
        def __init__(self):
            self.error = {
                'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
                'code': 402,
                'metadata': {'provider_name': None}
            }
    
    mock_response = MockErrorResponse()
    
    # Test the main entry point
    user_message, is_retryable = handle_api_error(mock_response, "teaching_node")
    
    assert "💳" in user_message, "Should contain credit error message"
    assert "Insufficient Credits" in user_message, "Should identify as credit error"
    assert not is_retryable, "Credit errors should not be retryable"
    assert "32,000" in user_message, "Should show token details"
    
    print("✅ Complete error handling flow works correctly")
    return True


def test_backwards_compatibility():
    """Test that existing error formats still work."""
    print("Testing backwards compatibility...")
    
    # Test wrapped provider error (existing format)
    wrapped_error = {
        'error': {
            'message': 'Provider returned error',
            'code': 400,
            'metadata': {
                'raw': '{"error":{"message":"Requested 50000 to generate tokens, following a prompt of length 5000, which exceeds the max limit of 32000 tokens.","type":"requested_too_many_tokens","code":400}}',
                'provider_name': 'Perplexity'
            }
        }
    }
    
    result = parse_openrouter_error(wrapped_error)
    
    assert result is not None, "Should parse wrapped errors"
    assert result['error_type'] == 'requested_too_many_tokens', "Should identify token limit error"
    assert result['provider_name'] == 'Perplexity', "Should extract provider name"
    
    print("✅ Backwards compatibility works correctly")
    return True


def main():
    """Run all tests."""
    print("🧪 Testing Issue #121 Fix: 402 Payment Required Error Handling")
    print("=" * 70)
    
    tests = [
        test_402_credit_error_parsing,
        test_user_friendly_message, 
        test_handle_api_error_integration,
        test_backwards_compatibility
    ]
    
    all_passed = True
    for test_func in tests:
        try:
            result = test_func()
            all_passed = all_passed and result
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            all_passed = False
        print()
    
    print("=" * 70)
    if all_passed:
        print("🎉 All tests passed! Issue #121 fix is working correctly.")
        print()
        print("Summary of the fix:")
        print("- ✅ 402 credit errors are now properly detected and parsed")
        print("- ✅ Token shortage details are extracted and displayed clearly")
        print("- ✅ User-friendly error messages provide actionable solutions")
        print("- ✅ Direct links to add credits are included")
        print("- ✅ Backwards compatibility with existing error formats is maintained")
        print()
        print("The user will now see helpful error messages instead of generic ones!")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()