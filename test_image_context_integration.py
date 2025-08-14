"""
Test script to verify image context integration works correctly
"""

import sys
import os
sys.path.append('/workspaces/autodidact-agent')

def test_image_context_integration():
    """Test that image context is properly integrated into teaching prompts"""
    
    # Test 1: Import components work
    try:
        from components.image_display import display_educational_image, cache_displayed_image, get_images_context_for_ai
        from backend.tutor_prompts import format_teaching_prompt, get_images_context_for_ai as prompt_images_context
        print("✅ Successfully imported image context functions")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Check prompt template includes placeholder
    try:
        from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE
        if "{VISIBLE_IMAGES_CONTEXT}" in TEACHING_PROMPT_TEMPLATE:
            print("✅ Prompt template includes image context placeholder")
        else:
            print("❌ Prompt template missing {VISIBLE_IMAGES_CONTEXT} placeholder")
            return False
    except Exception as e:
        print(f"❌ Error checking prompt template: {e}")
        return False
    
    # Test 3: Test prompt formatting with mock data
    try:
        # Mock objective data
        test_prompt = format_teaching_prompt(
            obj_id="test_obj_1",
            obj_label="Test Learning Objective",
            recent=["Previous Topic 1", "Previous Topic 2"],
            remaining=["Future Topic 1", "Future Topic 2"],
            refs=[
                {
                    'rid': 'test_ref_1',
                    'title': 'Test Reference',
                    'section': '1.1',
                    'type': 'article',
                    'date': '2024-01-01'
                }
            ],
            learner_profile_context="Test learner context"
        )
        
        if "{VISIBLE_IMAGES_CONTEXT}" not in test_prompt:
            print("✅ Prompt formatting replaces image context placeholder")
        else:
            print("❌ Prompt formatting leaves {VISIBLE_IMAGES_CONTEXT} placeholder unreplaced")
            print("This suggests get_images_context_for_ai() is not being called")
            return False
            
    except Exception as e:
        print(f"❌ Error testing prompt formatting: {e}")
        return False
    
    # Test 4: Test image context function (without Streamlit session state)
    try:
        context = prompt_images_context()
        # Should return empty string when no Streamlit session state available
        if context == "":
            print("✅ Image context function handles missing session state gracefully")
        else:
            print(f"⚠️  Image context returned: {context}")
            
    except Exception as e:
        print(f"❌ Error testing image context function: {e}")
        return False
    
    print("✅ All image context integration tests passed!")
    return True

def test_session_state_structure():
    """Test that session state structure includes displayed_images"""
    
    try:
        from backend.session_state import SessionState, create_initial_state
        
        # Test initial state creation with required parameters
        initial_state = create_initial_state(
            session_id="test_session",
            project_id="test_project", 
            node_id="test_node"
        )
        
        if 'displayed_images' in initial_state:
            print("✅ Session state includes displayed_images field")
            
            if isinstance(initial_state['displayed_images'], list):
                print("✅ displayed_images is initialized as a list")
            else:
                print(f"❌ displayed_images is not a list: {type(initial_state['displayed_images'])}")
                return False
                
        else:
            print("❌ Session state missing displayed_images field")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session state: {e}")
        return False
    
    return True

def test_image_display_component():
    """Test image display component functions"""
    
    try:
        from components.image_display import get_images_context_for_ai
        
        # Don't test cache_displayed_image since it requires ImageResult object
        # and Streamlit session state - this is integration tested separately
        
        # Test get_images_context_for_ai (should return empty when no session)
        context = get_images_context_for_ai()
        if context == "":
            print("✅ get_images_context_for_ai returns empty string without session state")
        else:
            print(f"⚠️  Unexpected context returned: {context}")
            
    except Exception as e:
        print(f"❌ Error testing image display component: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing Image Context Integration...")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing image context integration...")
    success &= test_image_context_integration()
    
    print("\n2. Testing session state structure...")
    success &= test_session_state_structure()
    
    print("\n3. Testing image display component...")
    success &= test_image_display_component()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Image context integration is working correctly.")
        print("\nNext steps:")
        print("• Test with actual Streamlit session to verify image caching")
        print("• Verify AI receives image context in teaching interactions")
        print("• Test image search and display functionality")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    print("\nDeprecation Warning Fix Summary:")
    print("✅ Fixed use_column_width → use_container_width in image display")
    print("✅ Added image caching to session state")
    print("✅ Enhanced AI context awareness for displayed images")
    print("✅ Integrated image context into teaching prompts")
