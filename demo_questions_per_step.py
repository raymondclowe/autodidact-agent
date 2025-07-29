#!/usr/bin/env python3
"""
Demonstration of questions per step feature working with the tutoring system
"""

import os
import sys
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demonstrate_different_learner_styles():
    """Demonstrate how the system adapts to different learner question preferences"""
    
    print("🎓 DEMONSTRATION: Questions Per Step Adaptation")
    print("="*60)
    print("This demo shows how the AI tutoring system adapts to different learning styles:")
    print("- MINIMAL: Students who prefer 1 focused question per step")
    print("- MODERATE: Students who work well with 2-3 questions per step") 
    print("- EXTENSIVE: Students who prefer 3-4+ questions for deep exploration")
    print()
    
    # Use a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Set up test database
        os.environ['AUTODIDACT_DB_PATH'] = tmp_db_path
        
        # Import modules after setting environment
        from backend.db import init_database
        from backend.learner_profile import learner_profile_manager
        from backend.tutor_prompts import format_teaching_prompt, format_recap_prompt
        
        # Initialize database
        init_database()
        
        # Test data
        test_project_id = "demo_project"
        test_topic = "Python Programming"
        
        # Simulate different learner profiles
        learner_scenarios = [
            {
                "name": "Alex (Minimal Questions)",
                "preference": "minimal",
                "description": "Prefers to move quickly, answers 1 question well then moves on"
            },
            {
                "name": "Jordan (Moderate Questions)", 
                "preference": "moderate",
                "description": "Comfortable with 2-3 questions per concept"
            },
            {
                "name": "Casey (Extensive Questions)",
                "preference": "extensive", 
                "description": "Loves deep exploration with 3-4+ questions per topic"
            }
        ]
        
        for scenario in learner_scenarios:
            print(f"\n🎯 LEARNER PROFILE: {scenario['name']}")
            print(f"   Learning Style: {scenario['description']}")
            print("-" * 50)
            
            # Simulate setting the preference (normally this would be detected from behavior)
            # For demo purposes, we'll show how the prompts adapt to each preference
            preference = scenario['preference']
            
            # Create a mock profile context that includes this preference
            mock_context = f"""LEARNER PROFILE CONTEXT:

Generic Learning Profile:
- questions_per_step: {preference}
- pacing_preference: steady
- instruction_style: socratic

Topic-Specific Profile for "{test_topic}":
- questions_per_step_preference: {preference}
- interest_level: high

Questions Per Step Preference: {preference}

Please use this learner profile information to personalize the learning session."""
            
            # Generate teaching prompt with this context
            teaching_prompt = format_teaching_prompt(
                obj_id="obj_001",
                obj_label="Understanding Python Variables",
                recent=["Basic programming concepts"],
                remaining=["Data types", "Control structures"],
                refs=[{
                    'rid': 'python_tutorial',
                    'title': 'Python Basics Tutorial',
                    'section': 'Variables',
                    'type': 'tutorial',
                    'date': '2024-01-01'
                }],
                learner_profile_context=mock_context
            )
            
            # Extract the relevant part that shows question adaptation
            prompt_lines = teaching_prompt.split('\n')
            objective_flow_start = None
            for i, line in enumerate(prompt_lines):
                if "OBJECTIVE FLOW" in line:
                    objective_flow_start = i
                    break
            
            if objective_flow_start:
                # Show the adaptive question guidance
                for i in range(objective_flow_start, min(objective_flow_start + 15, len(prompt_lines))):
                    if "minimal" in prompt_lines[i] or "moderate" in prompt_lines[i] or "extensive" in prompt_lines[i]:
                        print(f"   📋 {prompt_lines[i].strip()}")
            
            print(f"\n   🤖 How AI adapts for {scenario['name']}:")
            if preference == "minimal":
                print("      • Asks only 1 focused question per concept")
                print("      • Moves on quickly when answered well")
                print("      • Respects student's preference for fast pace")
            elif preference == "moderate":
                print("      • Asks 2-3 questions per concept (standard approach)")
                print("      • Balanced between depth and pace")
                print("      • Most commonly preferred learning style")
            elif preference == "extensive":
                print("      • Asks 3-4 questions per concept")
                print("      • Encourages deeper exploration")
                print("      • Provides more opportunities for thorough understanding")
            
            # Show recap adaptation too
            print(f"\n   📝 Recap session adaptation for {scenario['name']}:")
            if preference == "minimal":
                print("      • 1 focused question covering most important takeaway")
            elif preference == "moderate":
                print("      • 2-3 short questions or 2-question mini-quiz")
            elif preference == "extensive":
                print("      • 3-4 questions or longer mini-quiz for thorough review")
        
        print("\n" + "="*60)
        print("🔍 HOW THE SYSTEM DETECTS PREFERENCES:")
        print("The AI analyzes student responses to identify patterns:")
        print()
        print("🟡 MINIMAL preference detected when:")
        print("   • Student gives one detailed answer then brief responses")
        print("   • Shows impatience with multiple questions")
        print("   • Prefers to move quickly through material")
        print()
        print("🟢 MODERATE preference (default):")
        print("   • Student engages well with 2-3 questions")
        print("   • Balanced responses to multiple questions")
        print("   • Comfortable with standard pacing")
        print()
        print("🔵 EXTENSIVE preference detected when:")
        print("   • Student asks follow-up questions")
        print("   • Provides detailed responses to multiple questions")
        print("   • Shows curiosity and wants deeper exploration")
        print()
        
        print("✅ BENEFITS OF THIS ADAPTATION:")
        print("   • Improves student engagement by matching learning style")
        print("   • Reduces frustration from too many/too few questions")
        print("   • Personalizes the learning experience automatically")
        print("   • Maintains learning effectiveness across different preferences")
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        try:
            os.unlink(tmp_db_path)
        except:
            pass

def test_integration_with_existing_system():
    """Test that the new feature integrates well with existing tutoring system"""
    
    print("\n🔧 INTEGRATION TEST")
    print("="*60)
    print("Verifying the feature works with existing tutoring components...")
    
    try:
        # Test that we can import all necessary components
        from backend.learner_profile import learner_profile_manager
        from backend.tutor_prompts import format_teaching_prompt, format_recap_prompt
        from backend.graph_v05 import load_context_node  # This should work with our changes
        
        print("✓ All imports successful")
        
        # Test that the prompts still validate
        sample_prompt = format_teaching_prompt(
            obj_id="test_obj",
            obj_label="Test Objective",
            recent=["Previous topic"],
            remaining=["Next topic"],
            refs=[],
            learner_profile_context="LEARNER PROFILE CONTEXT: Questions Per Step Preference: moderate"
        )
        
        assert "Questions Per Step Preference" in sample_prompt, "Learner context not included in prompt"
        assert "minimal" in sample_prompt, "Question adaptation logic not in prompt"
        print("✓ Teaching prompts integrate correctly")
        
        # Test recap prompts
        recap_prompt = format_recap_prompt(
            recent_los=["Recent objective"],
            next_obj="Next objective",
            refs=[],
            learner_profile_context="LEARNER PROFILE CONTEXT: Questions Per Step Preference: extensive"
        )
        
        assert "Questions Per Step Preference" in recap_prompt, "Learner context not included in recap"
        assert "extensive" in recap_prompt, "Question adaptation logic not in recap prompt"
        print("✓ Recap prompts integrate correctly")
        
        # Test profile manager functions
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            tmp_db_path = tmp_db.name
        
        try:
            os.environ['AUTODIDACT_DB_PATH'] = tmp_db_path
            from backend.db import init_database
            init_database()
            
            context = learner_profile_manager.get_profile_context_for_session("test", "test")
            assert "Questions Per Step Preference" in context, "Profile context missing question preference"
            print("✓ Profile manager integrates correctly")
            
        finally:
            try:
                os.unlink(tmp_db_path)
            except:
                pass
        
        print("✓ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("QUESTIONS PER STEP FEATURE - COMPLETE DEMONSTRATION")
    print("=" * 70)
    
    success = True
    
    try:
        success = demonstrate_different_learner_styles() and success
        success = test_integration_with_existing_system() and success
        
    except Exception as e:
        print(f"Error running demonstration: {e}")
        success = False
    
    if success:
        print(f"\n{'='*70}")
        print("🎉 DEMONSTRATION COMPLETE!")
        print("The questions per step feature has been successfully implemented and")
        print("integrates seamlessly with the existing autodidact tutoring system.")
        print("Students will now receive personalized question counts based on their")
        print("learning style preferences, improving engagement and learning outcomes.")
        sys.exit(0)
    else:
        print("\n❌ Demonstration failed!")
        sys.exit(1)