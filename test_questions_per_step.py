#!/usr/bin/env python3
"""
Test script for questions per step feature
"""

import os
import sys
import tempfile
import sqlite3
from contextlib import contextmanager

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test the learner profile functionality
def test_learner_profile_questions_preference():
    """Test that learner profile correctly handles questions per step preferences"""
    
    # Use a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Set up test database
        os.environ['AUTODIDACT_DB_PATH'] = tmp_db_path
        
        # Import modules after setting environment
        from backend.db import init_database
        from backend.learner_profile import learner_profile_manager
        
        # Initialize database
        init_database()
        
        # Test 1: Check default question preference
        test_project_id = "test_project_123"
        test_topic = "Machine Learning"
        
        # Get initial profile - should have default values
        context = learner_profile_manager.get_profile_context_for_session(test_project_id, test_topic)
        print("Initial profile context:")
        print(context)
        print("\n" + "="*50 + "\n")
        
        # Test 2: Check questions_per_step_preference extraction
        questions_pref = learner_profile_manager.get_questions_per_step_preference(test_project_id, test_topic)
        print(f"Questions per step preference: {questions_pref}")
        assert questions_pref == "moderate", f"Expected 'moderate', got '{questions_pref}'"
        print("✓ Default preference is 'moderate' as expected")
        print("\n" + "="*50 + "\n")
        
        # Test 3: Test profile template structure
        generic_profile = learner_profile_manager.get_generic_profile()
        topic_profile = learner_profile_manager.get_topic_profile(test_project_id, test_topic)
        
        # Check that the new field is present in templates
        assert "questions_per_step" in generic_profile, "questions_per_step field missing from generic profile"
        assert "questions_per_step_preference" in topic_profile, "questions_per_step_preference field missing from topic profile"
        print("✓ Profile templates contain questions per step fields")
        print("\n" + "="*50 + "\n")
        
        # Test 4: Test parsing of XML profiles
        import xml.etree.ElementTree as ET
        
        generic_root = ET.fromstring(generic_profile)
        questions_element = generic_root.find(".//questions_per_step")
        assert questions_element is not None, "questions_per_step element not found in generic profile"
        print(f"✓ Generic profile questions_per_step value: {questions_element.text}")
        
        topic_root = ET.fromstring(topic_profile)
        topic_questions_element = topic_root.find(".//questions_per_step_preference")
        assert topic_questions_element is not None, "questions_per_step_preference element not found in topic profile"
        print(f"✓ Topic profile questions_per_step_preference value: {topic_questions_element.text}")
        
        print("\n" + "="*50 + "\n")
        print("All tests passed! ✅")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        try:
            os.unlink(tmp_db_path)
        except:
            pass

def test_prompt_modifications():
    """Test that the prompt templates include the new question adaptation logic"""
    from backend.tutor_prompts import TEACHING_PROMPT_TEMPLATE, RECAP_PROMPT_TEMPLATE
    
    print("Testing prompt modifications...")
    
    # Check teaching prompt
    assert "questions_per_step preference" in TEACHING_PROMPT_TEMPLATE, "Teaching prompt missing questions_per_step logic"
    assert "minimal" in TEACHING_PROMPT_TEMPLATE, "Teaching prompt missing 'minimal' preference"
    assert "moderate" in TEACHING_PROMPT_TEMPLATE, "Teaching prompt missing 'moderate' preference"
    assert "extensive" in TEACHING_PROMPT_TEMPLATE, "Teaching prompt missing 'extensive' preference"
    print("✓ Teaching prompt includes question adaptation logic")
    
    # Check recap prompt
    assert "questions_per_step preference" in RECAP_PROMPT_TEMPLATE, "Recap prompt missing questions_per_step logic"
    assert "minimal" in RECAP_PROMPT_TEMPLATE, "Recap prompt missing 'minimal' preference"
    assert "moderate" in RECAP_PROMPT_TEMPLATE, "Recap prompt missing 'moderate' preference"
    assert "extensive" in RECAP_PROMPT_TEMPLATE, "Recap prompt missing 'extensive' preference"
    print("✓ Recap prompt includes question adaptation logic")
    
    print("✓ All prompt modifications verified!")

if __name__ == "__main__":
    print("Testing questions per step feature implementation...")
    print("="*60)
    
    success = True
    
    try:
        test_prompt_modifications()
        print("\n" + "="*60 + "\n")
        
        success = test_learner_profile_questions_preference() and success
        
    except Exception as e:
        print(f"Error running tests: {e}")
        success = False
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)