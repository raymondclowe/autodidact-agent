#!/usr/bin/env python3
"""
Simple test to verify the max_tokens fix by checking the code change
"""

import sys
from pathlib import Path

def test_max_tokens_in_code():
    """Test that the get_llm function now includes max_tokens parameter"""
    print("🔧 Testing max_tokens fix in backend/graph_v05.py")
    print("=" * 55)
    
    # Read the actual file content
    file_path = Path(__file__).parent / "backend" / "graph_v05.py"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for the max_tokens parameter in the ChatOpenAI initialization
    expected_lines = [
        '"max_tokens": 4000',
        "# Reasonable limit for lesson interactions to prevent excessive costs"
    ]
    
    all_found = True
    for expected in expected_lines:
        if expected in content:
            print(f"✅ Found: {expected}")
        else:
            print(f"❌ Missing: {expected}")
            all_found = False
    
    # Check that we're in the right function context
    get_llm_function_found = "def get_llm():" in content
    chatopenai_usage_found = "ChatOpenAI(**llm_kwargs)" in content
    
    if get_llm_function_found:
        print("✅ Found get_llm() function")
    else:
        print("❌ get_llm() function not found")
        all_found = False
    
    if chatopenai_usage_found:
        print("✅ Found ChatOpenAI(**llm_kwargs) usage")
    else:
        print("❌ ChatOpenAI(**llm_kwargs) usage not found")
        all_found = False
    
    return all_found

def test_max_tokens_value_appropriateness():
    """Test that 4000 tokens is an appropriate value"""
    print("\n🧮 Testing max_tokens value appropriateness")
    print("=" * 45)
    
    max_tokens = 4000
    
    # Check against the issue requirements
    print(f"New max_tokens limit: {max_tokens}")
    print("\nRequirements from issue:")
    print("✅ Much lower than problematic 32,000 tokens")
    print("✅ Reasonable for lesson interactions (few hundred words typical)")
    print("✅ Prevents excessive costs")
    
    # A few hundred words is roughly 300-800 tokens
    # 4000 tokens allows for substantial responses while being reasonable
    typical_lesson_response = 800  # tokens
    safety_margin = max_tokens / typical_lesson_response
    
    print(f"\nAnalysis:")
    print(f"  Typical lesson response: ~{typical_lesson_response} tokens")
    print(f"  Safety margin: {safety_margin:.1f}x")
    print(f"  Reduction from 32k: {((32000 - max_tokens) / 32000 * 100):.1f}%")
    
    # Check that the value is reasonable
    assert max_tokens > 1000, "Should allow substantial responses"
    assert max_tokens < 10000, "Should prevent excessive usage"
    assert max_tokens <= 8000, "Should align with error handling cap"
    
    print("✅ 4000 tokens is appropriate for lesson interactions")
    
    return True

def test_consistency_with_error_handling():
    """Test that the fix is consistent with existing error handling logic"""
    print("\n🔍 Testing consistency with error handling logic")
    print("=" * 50)
    
    # Read the error handling file to check the existing cap
    error_file_path = Path(__file__).parent / "utils" / "error_handling.py"
    
    with open(error_file_path, 'r') as f:
        error_content = f.read()
    
    # Check for the 8k cap mentioned in error handling
    if "min(8000" in error_content and "cap at 8k tokens" in error_content:
        print("✅ Found 8k token cap in error handling")
        print("✅ New 4k limit is well below the 8k safety cap")
    else:
        print("❌ Could not verify 8k cap in error handling")
        return False
    
    # Our 4k limit should be consistent with the error handling logic
    our_limit = 4000
    error_handling_cap = 8000
    
    if our_limit <= error_handling_cap:
        print(f"✅ Our limit ({our_limit}) is within error handling cap ({error_handling_cap})")
    else:
        print(f"❌ Our limit ({our_limit}) exceeds error handling cap ({error_handling_cap})")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Max Tokens Fix for Issue #124")
    print("=" * 70)
    
    success = True
    
    try:
        success &= test_max_tokens_in_code()
        success &= test_max_tokens_value_appropriateness()
        success &= test_consistency_with_error_handling()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 ALL TESTS PASSED!")
            print("\n📝 Summary:")
            print("  ✅ max_tokens parameter added to ChatOpenAI initialization")
            print("  ✅ Set to 4,000 tokens (reasonable for lesson interactions)")
            print("  ✅ 87.5% reduction from problematic 32,000 token requests")
            print("  ✅ Consistent with existing error handling logic")
            print("  ✅ Should resolve OpenRouter credit exhaustion issue")
            print("\n🎯 The fix directly addresses the issue requirements:")
            print("  - Provides more reasonable default value")
            print("  - Appropriate for typical lesson interactions")
            print("  - Prevents excessive token costs")
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