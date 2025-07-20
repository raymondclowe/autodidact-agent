#!/usr/bin/env python3
"""
Test script for enhanced OpenRouter/Perplexity error handling
Tests the new error parsing and user-friendly messages
"""

import sys
import os
import json
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openrouter_error_parsing():
    """Test parsing of OpenRouter error responses"""
    print("Testing OpenRouter error parsing...")
    
    from utils.error_handling import parse_openrouter_error, create_user_friendly_error_message, extract_token_info
    
    # Mock OpenRouter error response with token limit exceeded
    mock_error = {
        "error": {
            "message": "Provider returned error",
            "code": 400,
            "metadata": {
                "raw": '{"error":{"message":"Requested 113643 to generate tokens, following a prompt of length 14657, which exceeds the max limit of 128000 tokens.","type":"requested_too_many_tokens","code":400}}',
                "provider_name": "Perplexity"
            }
        }
    }
    
    # Test error parsing
    error_info = parse_openrouter_error(mock_error)
    assert error_info is not None, "Should parse OpenRouter error"
    assert error_info['provider_name'] == "Perplexity"
    assert error_info['error_type'] == "requested_too_many_tokens"
    print("✅ Error parsing works correctly")
    
    # Test token info extraction
    token_info = extract_token_info(error_info['error_message'])
    assert token_info is not None, "Should extract token info"
    assert token_info['requested_tokens'] == 113643
    assert token_info['prompt_length'] == 14657
    assert token_info['max_limit'] == 128000
    print("✅ Token info extraction works correctly")
    
    # Test user-friendly message creation
    user_message = create_user_friendly_error_message(error_info)
    assert "Token Limit Exceeded" in user_message
    assert "Perplexity" in user_message
    assert "113643" in user_message
    assert "128000" in user_message
    assert "Solutions:" in user_message
    print("✅ User-friendly message creation works correctly")
    
    print(f"Sample user message:\n{user_message}\n")


def test_token_limit_checking():
    """Test token limit validation"""
    print("Testing token limit checking...")
    
    from utils.error_handling import check_token_limits, estimate_token_count
    
    # Test token estimation
    test_text = "This is a test message with multiple words to estimate tokens."
    tokens = estimate_token_count(test_text)
    assert tokens > 0, "Should estimate some tokens"
    print(f"✅ Token estimation: '{test_text}' = ~{tokens} tokens")
    
    # Test limit checking - within limits
    short_prompt = "Short prompt"
    result = check_token_limits(short_prompt, max_completion_tokens=1000, model_max_tokens=128000)
    assert result['within_limits'] == True
    print("✅ Within limits check works")
    
    # Test limit checking - exceeds limits
    long_prompt = "A" * 500000  # Very long prompt
    result = check_token_limits(long_prompt, max_completion_tokens=50000, model_max_tokens=128000)
    assert result['within_limits'] == False
    print("✅ Exceeds limits check works")
    
    print(f"Long prompt analysis: {result['total_tokens']} total tokens, limit: {result['model_max_tokens']}")


def test_api_error_handling():
    """Test API error handling with mock responses"""
    print("Testing API error handling...")
    
    from utils.error_handling import handle_api_error
    
    # Mock OpenAI APIError with OpenRouter structure
    class MockAPIError:
        def __init__(self, response_data):
            self.response = Mock()
            for key, value in response_data.items():
                setattr(self.response, key, value)
    
    # Test token limit error
    token_error_data = {
        "error": {
            "message": "Provider returned error",
            "code": 400,
            "metadata": {
                "raw": '{"error":{"message":"Requested 50000 to generate tokens, following a prompt of length 80000, which exceeds the max limit of 128000 tokens.","type":"requested_too_many_tokens","code":400}}',
                "provider_name": "Perplexity"
            }
        }
    }
    
    mock_error = MockAPIError(token_error_data)
    error_message, is_retryable = handle_api_error(mock_error.response, "test API call")
    
    assert "Token Limit Exceeded" in error_message
    assert "50000" in error_message
    assert "80000" in error_message
    assert "128000" in error_message
    assert not is_retryable  # Token errors are not retryable
    print("✅ Token limit error handling works")
    
    # Test rate limit error
    rate_limit_data = {
        "error": {
            "message": "Provider returned error",
            "code": 429,
            "metadata": {
                "raw": '{"error":{"message":"Rate limit exceeded","type":"rate_limit_exceeded","code":429}}',
                "provider_name": "Perplexity"
            }
        }
    }
    
    mock_rate_error = MockAPIError(rate_limit_data)
    error_message, is_retryable = handle_api_error(mock_rate_error.response, "test API call")
    
    assert "Rate Limit" in error_message
    assert is_retryable  # Rate limit errors are retryable
    print("✅ Rate limit error handling works")


def test_model_token_limits():
    """Test model token limit configuration"""
    print("Testing model token limit configuration...")
    
    from utils.providers import get_model_token_limit
    from utils.config import set_current_provider
    
    # Test OpenRouter Perplexity limits (80% of 128k = 102,400)
    set_current_provider("openrouter")
    perplexity_limit = get_model_token_limit("perplexity/sonar-deep-research", "openrouter")
    assert perplexity_limit == 102400, f"Expected 102400, got {perplexity_limit}"
    print("✅ Perplexity token limit correct: 102,400 (80% of 128k)")
    
    # Test OpenAI limits (80% of 128k = 102,400)
    set_current_provider("openai")
    openai_limit = get_model_token_limit("gpt-4o-mini", "openai")
    assert openai_limit == 102400, f"Expected 102400, got {openai_limit}"
    print("✅ OpenAI token limit correct: 102,400 (80% of 128k)")
    
    # Test fallback for unknown model (80% of 128k = 102,400)
    unknown_limit = get_model_token_limit("unknown-model", "openrouter")
    assert unknown_limit == 102400, f"Expected fallback 102400, got {unknown_limit}"
    print("✅ Unknown model fallback works: 102,400 (80% conservative)")


def test_integration_scenario():
    """Test a realistic integration scenario"""
    print("Testing realistic integration scenario...")
    
    from utils.error_handling import check_token_limits
    from utils.providers import get_model_token_limit
    
    # Simulate a large deep research prompt
    large_topic = """
    I want to learn about advanced quantum computing algorithms, including Shor's algorithm, 
    Grover's algorithm, quantum error correction, quantum machine learning, variational quantum 
    eigensolvers, quantum approximate optimization algorithms, quantum neural networks, 
    quantum cryptography, quantum teleportation, quantum entanglement applications, 
    quantum supremacy experiments, quantum hardware architectures, superconducting qubits, 
    trapped ion systems, photonic quantum computers, topological quantum computing, 
    quantum error mitigation techniques, quantum decoherence mitigation, quantum state 
    preparation, quantum measurement theory, quantum channel capacity, quantum information 
    theory, quantum complexity theory, and practical implementations in current quantum 
    computing platforms like IBM Quantum, Google Quantum, IonQ, and Rigetti systems.
    """ * 100  # Make it very large
    
    # Check if this would exceed Perplexity limits
    token_check = check_token_limits(
        large_topic, 
        max_completion_tokens=50000,
        model_max_tokens=get_model_token_limit("perplexity/sonar-deep-research", "openrouter")
    )
    
    print(f"Large topic analysis:")
    print(f"  Prompt tokens: {token_check['prompt_tokens']}")
    print(f"  Completion tokens: {token_check['completion_tokens']}")
    print(f"  Total tokens: {token_check['total_tokens']}")
    print(f"  Model limit: {token_check['model_max_tokens']}")
    print(f"  Within limits: {token_check['within_limits']}")
    
    if not token_check['within_limits']:
        print("✅ Large topic correctly identified as exceeding limits")
    else:
        print("ℹ️ Topic is within limits (unexpected but not an error)")


def main():
    """Run all enhanced error handling tests"""
    print("🧪 Testing Enhanced OpenRouter/Perplexity Error Handling")
    print("=" * 60)
    
    try:
        test_openrouter_error_parsing()
        print()
        
        test_token_limit_checking()
        print()
        
        test_api_error_handling()
        print()
        
        test_model_token_limits()
        print()
        
        test_integration_scenario()
        print()
        
        print("=" * 60)
        print("✅ All enhanced error handling tests passed!")
        print("\n🎯 Key improvements implemented:")
        print("- ✅ OpenRouter error response parsing")
        print("- ✅ Token limit detection and user-friendly messages")
        print("- ✅ Pre-flight token validation")
        print("- ✅ Specific error types with actionable solutions")
        print("- ✅ Enhanced error messages with emojis and formatting")
        print("- ✅ Model-specific token limit configuration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()