"""
Test to verify recap prompt includes image guidance and loads correctly
"""

import sys
import os
sys.path.append('/workspaces/autodidact-agent')

def test_recap_prompt_image_guidance():
    """Test that recap prompt includes image guidance"""
    
    print("Testing Recap Prompt Image Guidance...")
    print("=" * 50)
    
    try:
        from backend.tutor_prompts import format_recap_prompt, RECAP_PROMPT_TEMPLATE
        
        # Test 1: Check that RECAP_PROMPT_TEMPLATE loads and contains image guidance
        print("1. Checking recap prompt template content...")
        
        if "EDUCATIONAL IMAGE GUIDANCE" in RECAP_PROMPT_TEMPLATE:
            print("✅ Recap prompt includes EDUCATIONAL IMAGE GUIDANCE section")
        else:
            print("❌ Recap prompt missing EDUCATIONAL IMAGE GUIDANCE section")
            return False
            
        if "<image>description of needed image</image>" in RECAP_PROMPT_TEMPLATE:
            print("✅ Recap prompt includes image syntax instructions")
        else:
            print("❌ Recap prompt missing image syntax instructions")
            return False
        
        # Test 2: Test format_recap_prompt function
        print("\n2. Testing recap prompt formatting...")
        
        sample_recap_prompt = format_recap_prompt(
            recent_los=[
                "Define cells as the basic unit of life",
                "Identify the three principles of cell theory",
                "Explain why cells are fundamental to all organisms"
            ],
            next_obj="Describe light microscope components and function",
            refs=[
                {
                    'rid': 'biology_textbook',
                    'title': 'Cell Biology Fundamentals',
                    'section': '1.1',
                    'type': 'textbook',
                    'date': '2023-01-01'
                }
            ],
            learner_profile_context="Student is in high school biology"
        )
        
        # Check that image guidance is in the formatted prompt
        if "EDUCATIONAL IMAGE GUIDANCE" in sample_recap_prompt:
            print("✅ Formatted recap prompt includes image guidance")
        else:
            print("❌ Formatted recap prompt missing image guidance")
            return False
            
        if "<image>" in sample_recap_prompt:
            print("✅ Formatted recap prompt includes image syntax examples")
        else:
            print("❌ Formatted recap prompt missing image syntax examples")
            return False
            
        # Test 3: Check for image context placeholder
        print("\n3. Checking for image context integration...")
        
        if "{VISIBLE_IMAGES_CONTEXT}" in RECAP_PROMPT_TEMPLATE:
            print("✅ Recap prompt template includes image context placeholder")
            
            # Check that it gets replaced in formatting
            if "{VISIBLE_IMAGES_CONTEXT}" not in sample_recap_prompt:
                print("✅ Image context placeholder gets replaced during formatting")
            else:
                print("❌ Image context placeholder not replaced during formatting")
                return False
        else:
            print("⚠️  Recap prompt template missing image context placeholder")
            print("   Adding it now...")
            
            # We should add this to the recap prompt template
            return False
            
        print("\n✅ All recap prompt tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing recap prompt: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_recap_prompt_sample():
    """Show what the recap prompt looks like"""
    
    try:
        from backend.tutor_prompts import format_recap_prompt
        
        print("\n" + "=" * 50)
        print("SAMPLE RECAP PROMPT OUTPUT")
        print("=" * 50)
        
        sample_prompt = format_recap_prompt(
            recent_los=[
                "Define cells as the basic unit of life",
                "Identify the three principles of cell theory"
            ],
            next_obj="Describe light microscope components and function",
            refs=[
                {
                    'rid': 'bio_text',
                    'title': 'Biology Fundamentals',
                    'section': '1.1',
                    'type': 'textbook',
                    'date': '2023-01-01'
                }
            ]
        )
        
        # Show just the image guidance section
        lines = sample_prompt.split('\n')
        in_image_section = False
        image_section_lines = []
        
        for line in lines:
            if "EDUCATIONAL IMAGE GUIDANCE" in line:
                in_image_section = True
            elif in_image_section and line.startswith("STYLE & SAFETY"):
                break
            
            if in_image_section:
                image_section_lines.append(line)
        
        if image_section_lines:
            print("IMAGE GUIDANCE SECTION:")
            print("\n".join(image_section_lines[:10]))  # Show first 10 lines
            print("...")
        else:
            print("❌ Could not find image guidance section in prompt")
            
    except Exception as e:
        print(f"❌ Error showing recap prompt sample: {e}")

if __name__ == "__main__":
    success = test_recap_prompt_image_guidance()
    
    if success:
        show_recap_prompt_sample()
        print("\n🎉 Recap prompt is now configured for image support!")
        print("\nThe AI in recap sessions can now:")
        print("• Show educational images using <image>description</image>")
        print("• Reference previously displayed images in context")
        print("• Provide visual aids to reinforce learning")
    else:
        print("\n❌ Recap prompt test failed - needs fixes")
