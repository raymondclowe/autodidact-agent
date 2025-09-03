#!/usr/bin/env python3
"""
Simple focused test for the 402 error fix
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_core_fix():
    """Test the core 402 error parsing without complex dependencies."""
    print("Testing core 402 error parsing...")
    
    # Test the essential parsing functionality
    from utils.error_handling import parse_openrouter_error, create_user_friendly_error_message
    
    # Simulate the exact error structure from issue #121
    error_response = {
        'error': {
            'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
            'code': 402,
            'metadata': {'provider_name': None}
        },
        'user_id': 'user_2edDjJDbdOHWLaSFpbFsTHCawsZ'
    }
    
    # Test parsing
    parsed = parse_openrouter_error(error_response)
    assert parsed is not None, "Should parse the error"
    assert parsed['error_type'] == 'insufficient_credits', f"Wrong error type: {parsed['error_type']}"
    
    # Test user message
    message = create_user_friendly_error_message(parsed)
    assert "💳" in message, "Should have credit emoji"
    assert "32,000" in message, "Should show formatted requested tokens"
    assert "31,399" in message, "Should show formatted affordable tokens"
    assert "601" in message, "Should calculate shortage"
    assert "openrouter.ai/settings/credits" in message, "Should include link"
    
    print("✅ Core parsing works correctly")
    
    # Test that existing error formats still work
    print("Testing backwards compatibility...")
    
    wrapped_error = {
        'error': {
            'message': 'Provider returned error',
            'code': 400,
            'metadata': {
                'raw': '{"error":{"message":"Token limit exceeded","type":"requested_too_many_tokens","code":400}}',
                'provider_name': 'TestProvider'
            }
        }
    }
    
    parsed_wrapped = parse_openrouter_error(wrapped_error)
    assert parsed_wrapped is not None, "Should parse wrapped errors"
    assert parsed_wrapped['error_type'] == 'requested_too_many_tokens', "Should parse wrapped error type"
    
    print("✅ Backwards compatibility works")
    
    return True


def demonstrate_fix():
    """Demonstrate what the user will see before and after the fix."""
    print("\n" + "="*60)
    print("DEMONSTRATING THE FIX")
    print("="*60)
    
    print("\n❌ BEFORE (Issue #121):")
    print("User sees: '[get_llm] Failed to initialize LLM: Error code: 402 - {long error dict}'")
    print("User message: 'LLM not initialized - check API key'")
    print("Result: User is confused and doesn't know what to do")
    
    print("\n✅ AFTER (Fixed):")
    from utils.error_handling import parse_openrouter_error, create_user_friendly_error_message
    
    error_response = {
        'error': {
            'message': 'This request requires more credits, or fewer max_tokens. You requested up to 32000 tokens, but can only afford 31399. To increase, visit https://openrouter.ai/settings/credits and add more credits',
            'code': 402,
            'metadata': {'provider_name': None}
        }
    }
    
    parsed = parse_openrouter_error(error_response)
    message = create_user_friendly_error_message(parsed)
    
    print("User sees enhanced error message:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    print("Result: User knows exactly what the problem is and how to fix it!")


def main():
    """Run the focused test."""
    print("🔧 Testing Issue #121 Fix - Core Functionality")
    print("=" * 50)
    
    try:
        test_core_fix()
        demonstrate_fix()
        
        print("\n" + "="*50)
        print("🎉 SUCCESS! Issue #121 has been fixed.")
        print("\nSummary of changes:")
        print("✅ Added parsing for direct OpenRouter 402 errors")
        print("✅ Added token extraction for credit error format")
        print("✅ Added user-friendly credit error messages")
        print("✅ Enhanced get_llm() to use better error handling")
        print("✅ Maintained backwards compatibility")
        print("\nUsers will now see helpful credit information instead of confusing error messages!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()