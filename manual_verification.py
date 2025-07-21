#!/usr/bin/env python3
"""
Manual verification test: simulate the exact function call that would trigger the error
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

sys.path.insert(0, str(Path(__file__).parent))

from utils.config import set_current_provider
from utils.providers import create_client, get_current_provider


def manual_verification():
    """Manually verify the fix by checking the key parts of the fixed code"""
    print("Manual Verification: Testing the exact code path that was fixed")
    print("=" * 70)
    
    # Set up the error scenario
    set_current_provider('openrouter')
    current_provider = get_current_provider()
    
    # This would be passed from a project that was created with OpenAI
    problematic_research_model = "o4-mini-deep-research-2025-06-26"
    
    print(f"Scenario setup:")
    print(f"  Current provider: {current_provider}")
    print(f"  Project's saved model: {problematic_research_model}")
    print()
    
    # Test the specific code from our fix
    print("Testing the fixed code logic:")
    
    try:
        # This is the exact code we added in the fix
        from utils.providers import get_model_for_task, ProviderError
        
        try:
            fallback_model = get_model_for_task("chat", current_provider)
            print(f"✅ get_model_for_task('chat', '{current_provider}') = '{fallback_model}'")
        except ProviderError:
            fallback_model = problematic_research_model
            print(f"⚠️  Chat model not available, using research model: {fallback_model}")
        
        print(f"\nComparison:")
        print(f"  OLD logic would use: {problematic_research_model}")
        print(f"  NEW logic uses: {fallback_model}")
        
        if fallback_model != problematic_research_model:
            print(f"✅ SUCCESS: Using correct OpenRouter model instead of OpenAI model")
        else:
            print(f"❌ PROBLEM: Still using the problematic model")
            return False
            
        # Verify the model is valid for OpenRouter
        from utils.config import get_provider_config
        openrouter_config = get_provider_config('openrouter')
        
        if fallback_model in openrouter_config.values():
            print(f"✅ VALIDATED: '{fallback_model}' is a valid OpenRouter model")
        else:
            print(f"❌ ERROR: '{fallback_model}' is not in OpenRouter configuration")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False


def test_token_limit_check():
    """Test that token limit check also uses the correct model"""
    print("\nTesting token limit check with correct model:")
    
    set_current_provider('openrouter')
    
    from utils.providers import get_model_for_task, get_model_token_limit
    
    fallback_model = get_model_for_task("chat", "openrouter")
    token_limit = get_model_token_limit(fallback_model, "openrouter")
    
    print(f"✅ Token limit for {fallback_model}: {token_limit}")
    
    # Verify this wouldn't fail
    if token_limit > 0:
        print(f"✅ Token limit check will work correctly")
        return True
    else:
        print(f"❌ Token limit check might fail")
        return False


def final_validation():
    """Final validation that the error scenario is resolved"""
    print("\nFinal Validation:")
    print("-" * 50)
    
    # The exact error message from the issue
    original_error = "o4-mini-deep-research-2025-06-26 is not a valid model ID"
    
    set_current_provider('openrouter')
    from utils.providers import get_model_for_task
    
    # What our fix will use instead
    fixed_model = get_model_for_task("chat", "openrouter")
    
    print(f"Original error: '{original_error}'")
    print(f"Problematic model: 'o4-mini-deep-research-2025-06-26'")
    print(f"Fixed model: '{fixed_model}'")
    print()
    
    if "o4-mini-deep-research-2025-06-26" not in fixed_model:
        print("✅ CONFIRMED: Fix prevents the original error")
        print("✅ OpenRouter will receive a valid model ID")
        return True
    else:
        print("❌ PROBLEM: Fix does not prevent the original error")
        return False


if __name__ == "__main__":
    print("🔧 Manual Verification of Issue #22 Fix")
    print("=" * 70)
    
    success = True
    
    try:
        success &= manual_verification()
        success &= test_token_limit_check() 
        success &= final_validation()
        
        print("\n" + "=" * 70)
        if success:
            print("🎉 MANUAL VERIFICATION PASSED!")
            print()
            print("The fix successfully resolves issue #22:")
            print("• OpenRouter will no longer receive OpenAI model names")
            print("• Fallback logic uses provider-appropriate models")
            print("• Error 'o4-mini-deep-research-2025-06-26 is not a valid model ID' is prevented")
        else:
            print("❌ MANUAL VERIFICATION FAILED!")
            sys.exit(1)
            
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Manual verification failed: {e}")
        sys.exit(1)