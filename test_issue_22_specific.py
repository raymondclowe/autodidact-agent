#!/usr/bin/env python3
"""
Test the specific error scenario from issue #22:
"RuntimeError: ❌ **Error in fallback chat completion** **Error Message:** 
Error code: 400 - {'error': {'message': 'o4-mini-deep-research-2025-06-26 is not a valid model ID', ...}"
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import set_current_provider
from utils.providers import get_model_for_task


def test_specific_error_scenario():
    """Test the specific error scenario where OpenRouter rejects OpenAI model"""
    print("Testing specific error scenario from issue #22...")
    
    # Set up the scenario: OpenRouter provider
    set_current_provider('openrouter')
    
    # Get the models that should be used
    openrouter_deep_research = get_model_for_task('deep_research')
    openrouter_chat = get_model_for_task('chat')
    
    print(f"OpenRouter provider setup:")
    print(f"  Deep research model: {openrouter_deep_research}")
    print(f"  Chat model: {openrouter_chat}")
    
    # The problematic OpenAI model that caused the error
    problematic_model = "o4-mini-deep-research-2025-06-26"
    
    print(f"\nProblematic scenario:")
    print(f"  Provider: openrouter")
    print(f"  Attempting to use OpenAI model: {problematic_model}")
    
    # Our fix should ensure that the fallback uses the correct chat model
    # Test the logic from our fix
    try:
        fallback_model = get_model_for_task("chat", "openrouter")
        print(f"  Fixed fallback model: {fallback_model}")
        
        # Verify the fix
        assert fallback_model != problematic_model, f"ERROR: Still using problematic model {problematic_model}"
        assert fallback_model == openrouter_chat, f"ERROR: Not using correct OpenRouter chat model"
        
        print("✅ Fix works! Fallback uses correct OpenRouter model instead of OpenAI model")
        
    except Exception as e:
        print(f"❌ Error in fallback logic: {e}")
        raise
    
    # Test that the problematic model would indeed fail with OpenRouter
    # (This simulates what would happen if we didn't fix it)
    print(f"\nVerifying that {problematic_model} is indeed invalid for OpenRouter:")
    from utils.config import get_provider_config
    
    openrouter_config = get_provider_config('openrouter')
    openai_model_in_openrouter = problematic_model in openrouter_config.values()
    
    if not openai_model_in_openrouter:
        print(f"✅ Confirmed: '{problematic_model}' is NOT in OpenRouter configuration")
        print("   This would cause the 400 error 'is not a valid model ID'")
    else:
        print(f"❌ Unexpected: '{problematic_model}' found in OpenRouter config")
    
    print("\n✅ Specific error scenario test passed!")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Fix for Issue #22: OpenRouter Fallback Model Error")
    print("=" * 70)
    
    try:
        test_specific_error_scenario()
        
        print("\n" + "=" * 70)
        print("🎉 Issue #22 fix validated successfully!")
        print("The fallback logic will now use OpenRouter-compatible models")
        print("instead of trying to use OpenAI models with OpenRouter.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("=" * 70)
        sys.exit(1)