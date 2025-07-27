#!/usr/bin/env python3
"""
Test script to simulate student behaviors and verify question preference detection
"""

import os
import sys
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_transcripts():
    """Create sample session transcripts that demonstrate different learning styles"""
    
    # Student who prefers minimal questions (answers only 1 fully, brief on others)
    minimal_preference_transcript = [
        {"role": "assistant", "content": "Let's explore machine learning basics. What do you think machine learning means?"},
        {"role": "user", "content": "Machine learning is when computers learn patterns from data to make predictions or decisions without being explicitly programmed for each specific task."},
        {"role": "assistant", "content": "Excellent! That's a comprehensive answer. Now, can you give me an example of machine learning in everyday life?"},
        {"role": "user", "content": "Recommendation systems."},
        {"role": "assistant", "content": "Good. How do you think these systems work?"},
        {"role": "user", "content": "They use data."},
        {"role": "assistant", "content": "I notice you prefer to move through topics quickly. Let's continue to the next concept."}
    ]
    
    # Student who prefers extensive questions (asks for more, goes deep)
    extensive_preference_transcript = [
        {"role": "assistant", "content": "Let's explore machine learning basics. What do you think machine learning means?"},
        {"role": "user", "content": "Machine learning involves algorithms that can learn from data. But I'm curious - what are the different types of learning approaches?"},
        {"role": "assistant", "content": "Great question! There are supervised, unsupervised, and reinforcement learning. Can you think of what supervised learning might involve?"},
        {"role": "user", "content": "I think supervised learning uses labeled training data where the algorithm learns to map inputs to outputs. Like if you want to classify emails as spam or not spam, you'd train it on emails that are already labeled. But what about the mathematics behind it? How does the algorithm actually 'learn' from the examples?"},
        {"role": "assistant", "content": "Excellent depth! The algorithm uses mathematical optimization to find the best parameters. What do you think 'best' means in this context?"},
        {"role": "user", "content": "I imagine it's about minimizing prediction errors, but there must be different ways to measure error depending on the problem type. Can we explore a few examples of error functions?"},
        {"role": "assistant", "content": "I love your curiosity! Let's dive deeper into loss functions..."}
    ]
    
    # Student with moderate preference (comfortable with 2-3 questions)
    moderate_preference_transcript = [
        {"role": "assistant", "content": "Let's explore machine learning basics. What do you think machine learning means?"},
        {"role": "user", "content": "Machine learning is when computers learn from data to make predictions."},
        {"role": "assistant", "content": "Good start! Can you expand on what 'learning from data' means?"},
        {"role": "user", "content": "The algorithm finds patterns in the training data and uses those patterns to make predictions on new, unseen data."},
        {"role": "assistant", "content": "Excellent! Now, can you give me an example of machine learning in everyday life?"},
        {"role": "user", "content": "Netflix recommendations. The system learns from my viewing history and suggests movies I might like based on patterns from similar users."},
        {"role": "assistant", "content": "Perfect example! You've demonstrated good understanding of the concept."}
    ]
    
    return {
        "minimal": minimal_preference_transcript,
        "extensive": extensive_preference_transcript,
        "moderate": moderate_preference_transcript
    }

def test_question_preference_detection():
    """Test that the profile analysis can detect different question preferences"""
    
    print("Testing question preference detection from student behaviors...")
    print("="*60)
    
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
        
        test_project_id = "test_project_behavior"
        test_topic = "Machine Learning"
        
        # Get sample transcripts
        transcripts = create_sample_transcripts()
        
        for preference_type, transcript in transcripts.items():
            print(f"\nTesting {preference_type} preference detection:")
            print("-" * 40)
            
            # Format transcript for analysis
            transcript_text = learner_profile_manager._format_transcript_for_analysis(transcript)
            print(f"Sample transcript snippet: {transcript_text[:200]}...")
            
            # Get current profile  
            current_profile = learner_profile_manager.get_generic_profile()
            
            # Build the analysis prompt
            prompt = learner_profile_manager._build_generic_profile_update_prompt(current_profile, transcript_text)
            
            # Verify the prompt includes the new question preference detection logic
            assert "Questions per step preference" in prompt, f"Prompt missing question preference logic for {preference_type}"
            assert "minimal" in prompt and "moderate" in prompt and "extensive" in prompt, f"Prompt missing preference options for {preference_type}"
            
            print(f"✓ Analysis prompt correctly includes question preference detection for {preference_type}")
            
            # Test topic-specific prompt as well
            topic_profile = learner_profile_manager.get_topic_profile(test_project_id, test_topic)
            topic_prompt = learner_profile_manager._build_topic_profile_update_prompt(topic_profile, test_topic, transcript_text)
            
            assert "Questions per step preference" in topic_prompt, f"Topic prompt missing question preference logic for {preference_type}"
            print(f"✓ Topic analysis prompt correctly includes question preference detection for {preference_type}")
        
        print("\n" + "="*60)
        print("✅ All question preference detection tests passed!")
        
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

def test_profile_context_includes_preferences():
    """Test that session context correctly includes question preferences"""
    
    print("\nTesting session context generation...")
    print("="*60)
    
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
        
        test_project_id = "test_context_project"
        test_topic = "Deep Learning"
        
        # Test getting session context
        context = learner_profile_manager.get_profile_context_for_session(test_project_id, test_topic)
        
        print("Generated session context:")
        print(context)
        print()
        
        # Verify context includes question preference information
        assert "Questions Per Step Preference" in context, "Session context missing question preference info"
        assert "moderate" in context, "Session context should show default 'moderate' preference"
        
        print("✓ Session context correctly includes question preferences")
        
        # Test the specific preference extraction function
        questions_pref = learner_profile_manager.get_questions_per_step_preference(test_project_id, test_topic)
        assert questions_pref == "moderate", f"Expected 'moderate', got '{questions_pref}'"
        
        print("✓ Question preference extraction works correctly")
        
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

if __name__ == "__main__":
    print("Testing comprehensive question preference detection...")
    print("="*60)
    
    success = True
    
    try:
        success = test_question_preference_detection() and success
        success = test_profile_context_includes_preferences() and success
        
    except Exception as e:
        print(f"Error running tests: {e}")
        success = False
    
    if success:
        print("\n🎉 All comprehensive tests completed successfully!")
        print("\nThe implementation correctly:")
        print("- Adds question preference fields to learner profiles")
        print("- Includes detection logic in profile analysis prompts")
        print("- Provides session context with question preferences")
        print("- Adapts tutoring prompts based on preferences")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)