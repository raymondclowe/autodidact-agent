#!/usr/bin/env python3
"""Debug script to test template formatting specifically"""

from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE, format_teaching_prompt

def test_template_formatting():
    print("=== Testing template formatting ===")
    
    # Print the template to check for hidden characters
    print("Template length:", len(TEACHING_PROMPT_TEMPLATE))
    
    # Check for all placeholders in the template
    import re
    placeholders = re.findall(r'\{([^}]+)\}', TEACHING_PROMPT_TEMPLATE)
    print("Found placeholders:", placeholders)
    
    # Test with minimal args
    try:
        test_prompt = format_teaching_prompt(
            obj_id="test-id",
            obj_label="test label",
            recent=[],
            remaining=[],
            refs=[],
            learner_profile_context=""
        )
        print("SUCCESS: Template formatting worked")
        print(f"Result length: {len(test_prompt)}")
    except Exception as e:
        print(f"ERROR in template formatting: {e}")
        print(f"Error type: {type(e)}")
        
        # Let's manually try the .format() with the expected parameters
        try:
            manual_format = TEACHING_PROMPT_TEMPLATE.format(
                OBJ_ID="test-id",
                OBJ_LABEL="test label", 
                RECENT_TOPICS="",
                REMAINING_OBJS="",
                REF_LIST_BULLETS="",
                LEARNER_PROFILE_CONTEXT=""
            )
            print("SUCCESS: Manual format worked")
        except Exception as e2:
            print(f"ERROR in manual format: {e2}")
            
            # Try to find what's failing by replacing one placeholder at a time
            template = TEACHING_PROMPT_TEMPLATE
            for placeholder in placeholders:
                try:
                    template = template.replace(f"{{{placeholder}}}", "TEST")
                    print(f"Successfully replaced {placeholder}")
                except Exception as e3:
                    print(f"Error replacing {placeholder}: {e3}")

if __name__ == "__main__":
    test_template_formatting()
