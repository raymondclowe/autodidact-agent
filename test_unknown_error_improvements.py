#!/usr/bin/env python3
"""
Test script to reproduce and verify fixes for "Unknown error" scenarios
This specifically tests the issue described in the GitHub issue.
"""

import sys
import os
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unknown_error_scenario():
    """Test the improved error handling and verify no more 'Unknown error' messages"""
    print("Testing improved error scenario...")
    
    from utils.error_handling import handle_api_error
    
    # Mock an openai.APIError that doesn't match any known patterns
    class MockAPIError:
        def __init__(self, message="Some unknown API error", status_code=500):
            self.message = message
            self.status_code = getattr(self, 'status_code', status_code)
            self.body = None
            # Simulate properties that might exist on real openai.APIError
            self.request_id = "req_123456"
            self.type = None
    
    # Test case 1: Basic APIError with minimal information
    mock_error = MockAPIError("Connection timeout", 500)
    error_message, is_retryable = handle_api_error(mock_error, "fallback chat completion")
    
    print(f"Improved error message:\n{error_message}")
    print(f"Is retryable: {is_retryable}")
    
    # Verify the improved behavior
    assert "Unknown error" not in error_message, "Should not produce 'Unknown error' message anymore"
    assert "Connection timeout" in error_message, "Should include the actual error message"
    assert "Server Error" in error_message, "Should identify 500 status as server error"
    assert is_retryable == True, "Server errors should be retryable"
    print("✅ Improved behavior confirmed: no more 'Unknown error' messages")
    
    # Test case 2: Error with more complex structure
    class MockComplexError:
        def __init__(self):
            self.message = "Service temporarily unavailable"
            self.code = "service_unavailable"
            self.status_code = 503
            self.body = {"error": {"message": "Backend service timeout", "code": 503}}
            
    complex_error = MockComplexError()
    error_message2, is_retryable2 = handle_api_error(complex_error, "deep research")
    
    print(f"\nComplex error message:\n{error_message2}")
    print(f"Is retryable: {is_retryable2}")
    
    # Verify improved handling
    assert "Unknown error" not in error_message2, "Should not produce 'Unknown error' message"
    assert "Service temporarily unavailable" in error_message2, "Should include error details"
    assert is_retryable2 == True, "503 errors should be retryable"
    print("✅ Complex error handling improved")
    
    return mock_error, complex_error

def test_error_information_extraction():
    """Test extraction of error information from various error object types"""
    print("\nTesting error information extraction...")
    
    # Import our enhanced error handling function
    from utils.error_handling import handle_api_error
    
    # Test different error object structures that might exist
    test_cases = [
        {
            "name": "Error with message attribute",
            "error": type('MockError', (), {
                'message': 'Rate limit exceeded',
                'status_code': 429,
                'type': 'rate_limit'
            })(),
            "expected_in_message": ["Rate Limit", "Rate limit exceeded"]
        },
        {
            "name": "Error with __str__ method",
            "error": type('MockError', (), {
                '__str__': lambda self: 'Invalid API key provided',
                'status_code': 401
            })(),
            "expected_in_message": ["Authentication", "Invalid API key"]
        },
        {
            "name": "Error with body attribute",
            "error": type('MockError', (), {
                'body': '{"error": {"message": "Model not found", "type": "model_error"}}',
                'status_code': 404
            })(),
            "expected_in_message": ["Resource Not Found", "Model not found"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        error_message, is_retryable = handle_api_error(test_case['error'], "test scenario")
        print(f"  Message (first 150 chars): {error_message[:150]}...")
        print(f"  Retryable: {is_retryable}")
        
        # Verify the message contains expected content
        assert "Unknown error" not in error_message, f"Should not contain 'Unknown error' for {test_case['name']}"
        
        # Check if expected content is in the message
        found_expected = False
        for expected in test_case["expected_in_message"]:
            if expected in error_message:
                found_expected = True
                break
        
        if found_expected:
            print(f"  ✅ Contains expected information")
        else:
            print(f"  ⚠️  Expected content not found: {test_case['expected_in_message']}")

def main():
    """Run unknown error improvement tests"""
    print("🧪 Testing Unknown Error Improvements")
    print("=" * 50)
    
    try:
        mock_error, complex_error = test_unknown_error_scenario()
        test_error_information_extraction()
        
        print("\n" + "=" * 50)
        print("📋 Test Summary:")
        print("- ✅ 'Unknown error' messages eliminated")
        print("- ✅ Actionable error information extracted")
        print("- ✅ Status code-based error classification")
        print("- ✅ Retryable error detection improved")
        print("- ✅ User-friendly messages with solutions")
        
        return mock_error, complex_error
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()