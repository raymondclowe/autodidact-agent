#!/usr/bin/env python3
"""
Test script specifically for GitHub Issue #20: 
"Unknown errors are bad, it must show some more useful information to the user"

This test verifies that the "Unknown error in fallback chat completion" 
error has been fixed and now provides actionable information.
"""

import sys
import os
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_github_issue_20_scenario():
    """Test the specific scenario described in GitHub Issue #20"""
    print("🔍 Testing GitHub Issue #20 Scenario")
    print("=" * 50)
    
    from utils.error_handling import handle_api_error
    
    # Simulate the exact error scenario from the issue:
    # "RuntimeError: ❌ **Unknown error in fallback chat completion**"
    
    # This could happen when an openai.APIError occurs that doesn't match 
    # known OpenRouter patterns and falls back to generic handling
    
    print("1. Testing fallback chat completion error...")
    
    class MockOpenAIAPIError:
        """Mock openai.APIError that doesn't match OpenRouter patterns"""
        def __init__(self, message, status_code=500):
            self.message = message
            self.status_code = status_code
            self.request_id = "req_test_123"
    
    # Test various error scenarios that could cause "Unknown error"
    test_scenarios = [
        {
            "name": "API Connection Error",
            "error": MockOpenAIAPIError("Connection timed out", 500),
            "context": "fallback chat completion",
            "should_contain": ["Server Error", "Connection timed out", "Wait a few minutes"],
            "should_be_retryable": True
        },
        {
            "name": "Authentication Error", 
            "error": MockOpenAIAPIError("Invalid API key", 401),
            "context": "fallback chat completion",
            "should_contain": ["Authentication Failed", "Invalid API key", "API key configuration"],
            "should_be_retryable": False
        },
        {
            "name": "Rate Limit Error",
            "error": MockOpenAIAPIError("Rate limit exceeded", 429),
            "context": "fallback chat completion", 
            "should_contain": ["Rate Limit", "Rate limit exceeded", "Wait a few minutes"],
            "should_be_retryable": True
        },
        {
            "name": "Model Not Found",
            "error": MockOpenAIAPIError("Model not available", 404),
            "context": "fallback chat completion",
            "should_contain": ["Resource Not Found", "Model not available", "provider settings"],
            "should_be_retryable": False
        },
        {
            "name": "Generic Error with Details",
            "error": MockOpenAIAPIError("Unexpected service error", 503),
            "context": "deep research",
            "should_contain": ["Server Error", "Unexpected service error", "technical difficulties"],
            "should_be_retryable": True
        }
    ]
    
    all_tests_passed = True
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        
        try:
            error_message, is_retryable = handle_api_error(scenario['error'], scenario['context'])
            
            # Verify no "Unknown error" appears
            if "Unknown error" in error_message:
                print(f"   ❌ FAIL: Still contains 'Unknown error'")
                all_tests_passed = False
                continue
                
            # Verify retryable flag is correct
            if is_retryable != scenario['should_be_retryable']:
                print(f"   ❌ FAIL: Expected retryable={scenario['should_be_retryable']}, got {is_retryable}")
                all_tests_passed = False
            
            # Verify expected content is present
            missing_content = []
            for expected in scenario['should_contain']:
                if expected not in error_message:
                    missing_content.append(expected)
            
            if missing_content:
                print(f"   ❌ FAIL: Missing expected content: {missing_content}")
                all_tests_passed = False
            else:
                print(f"   ✅ PASS: Contains all expected information")
                print(f"   📝 Retryable: {is_retryable}")
                
            # Show a sample of the error message
            print(f"   📄 Sample: {error_message[:100]}...")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_tests_passed = False
    
    return all_tests_passed

def test_integration_with_jobs_module():
    """Test integration with the actual jobs.py module error handling"""
    print("\n🔗 Testing Integration with jobs.py")
    print("=" * 50)
    
    try:
        # Import the actual jobs module to verify our changes integrate properly
        from backend.jobs import start_deep_research_job
        print("✅ Successfully imported start_deep_research_job")
        
        # Verify the error handling import works
        from utils.error_handling import handle_api_error
        print("✅ Successfully imported handle_api_error")
        
        # Test that our improved error handling function signature matches expected usage
        from unittest.mock import Mock
        
        mock_error = Mock()
        mock_error.message = "Test error"
        mock_error.status_code = 500
        
        try:
            error_msg, is_retryable = handle_api_error(mock_error, "test context")
            print("✅ Error handling function works with expected signature")
            print(f"   Sample output: {error_msg[:60]}...")
            return True
        except Exception as e:
            print(f"❌ Error handling function failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run GitHub Issue #20 specific tests"""
    print("🧪 Testing GitHub Issue #20 Fix")
    print("Unknown error messages should be eliminated and replaced with actionable information")
    print("=" * 80)
    
    try:
        # Test the specific scenarios 
        scenario_tests_passed = test_github_issue_20_scenario()
        
        # Test integration
        integration_tests_passed = test_integration_with_jobs_module()
        
        print("\n" + "=" * 80)
        print("📋 GitHub Issue #20 Test Results:")
        
        if scenario_tests_passed:
            print("✅ Scenario Tests: All error scenarios now provide actionable information")
        else:
            print("❌ Scenario Tests: Some tests failed")
            
        if integration_tests_passed:
            print("✅ Integration Tests: Changes integrate properly with existing code")
        else:
            print("❌ Integration Tests: Integration issues detected")
        
        if scenario_tests_passed and integration_tests_passed:
            print("\n🎉 GitHub Issue #20 Successfully Fixed!")
            print("\n📝 Summary of improvements:")
            print("- ❌ Eliminated 'Unknown error' messages")
            print("- ✅ Added actionable error information")
            print("- ✅ Status code-based error classification")
            print("- ✅ Proper retryable error detection")
            print("- ✅ User-friendly messages with solutions")
            print("- ✅ Enhanced error logging for debugging")
            return True
        else:
            print("\n⚠️  Some issues remain - review test failures above")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)