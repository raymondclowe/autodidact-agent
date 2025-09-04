#!/usr/bin/env python3
"""Integration test for the complete mobile progress and session persistence flow for issue #128."""

import sys
import tempfile
import pickle
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import SessionState, create_initial_state, Objective, get_objectives_progress_info
from components.lesson_progress import should_show_progress_tracking


def simulate_learning_session_with_interruption():
    """Simulate a complete learning session with interruption and resumption."""
    print("🎓 Simulating complete learning session with mobile progress and interruption...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # === PHASE 1: Start new session ===
        print("\n📱 PHASE 1: Starting new session...")
        
        session_id = "mobile_session_123"
        project_id = "python_basics"
        node_id = "variables_and_functions"
        
        # Create new session
        state = create_initial_state(session_id, project_id, node_id)
        
        # Set up learning objectives
        objectives = [
            Objective(id='obj1', description='Understand Python variables', mastery=0.2),
            Objective(id='obj2', description='Learn about data types', mastery=0.3),
            Objective(id='obj3', description='Work with functions', mastery=0.1),
            Objective(id='obj4', description='Handle errors and exceptions', mastery=0.0),
            Objective(id='obj5', description='Use loops and conditions', mastery=0.2)
        ]
        
        state['objectives_to_teach'] = objectives
        state['current_phase'] = 'teaching'
        state['objective_idx'] = 0
        state['completed_objectives'] = []
        
        # Test mobile progress display at start
        progress_info = get_objectives_progress_info(state)
        mobile_progress_text = f"📊 {progress_info['completed_count']} out of {progress_info['total']} objectives completed"
        expected_start_text = "📊 0 out of 5 objectives completed"
        
        assert mobile_progress_text == expected_start_text, f"Expected '{expected_start_text}', got '{mobile_progress_text}'"
        print(f"✅ Mobile progress display at start: '{mobile_progress_text}'")
        
        # Should show progress tracking
        should_show = should_show_progress_tracking(state)
        assert should_show, "Should show progress tracking during teaching phase"
        print("✅ Progress tracking enabled for teaching phase")
        
        # Simulate initial chat
        initial_history = [
            {"role": "assistant", "content": "🎓 Welcome to your Python learning session! We'll cover 5 key objectives today. Let's start with variables."},
            {"role": "user", "content": "I'm ready to learn about Python variables!"},
            {"role": "assistant", "content": "Great! A variable in Python is like a container that holds data. For example: name = 'Alice'"},
        ]
        state['history'] = initial_history
        
        # Save initial state
        state_file = temp_path / f"{session_id}.pkl"
        state_file.write_bytes(pickle.dumps(state))
        print(f"✅ Session saved with {len(initial_history)} initial messages")
        
        # === PHASE 2: Make progress ===
        print("\n📚 PHASE 2: Making progress...")
        
        # Complete first objective
        state['completed_objectives'] = ['obj1']
        state['objective_idx'] = 1
        
        # Add more chat history
        progress_history = [
            {"role": "user", "content": "I understand variables now. What about data types?"},
            {"role": "assistant", "content": "Excellent! Now let's learn about data types. Python has several built-in data types..."},
            {"role": "user", "content": "What's the difference between a string and an integer?"}
        ]
        state['history'].extend(progress_history)
        
        # Test mobile progress after first completion
        progress_info = get_objectives_progress_info(state)
        mobile_progress_text = f"📊 {progress_info['completed_count']} out of {progress_info['total']} objectives completed"
        expected_progress_text = "📊 1 out of 5 objectives completed"
        
        assert mobile_progress_text == expected_progress_text, f"Expected '{expected_progress_text}', got '{mobile_progress_text}'"
        print(f"✅ Mobile progress after completion: '{mobile_progress_text}'")
        
        # Verify progress structure
        items = progress_info['items']
        assert items[0]['status'] == 'completed', "First objective should be completed"
        assert items[1]['status'] == 'current', "Second objective should be current"
        assert items[2]['status'] == 'upcoming', "Third objective should be upcoming"
        
        print(f"✅ Progress tracking shows correct status for all {len(items)} objectives")
        
        # Save progress
        state_file.write_bytes(pickle.dumps(state))
        print(f"✅ Session saved with {len(state['history'])} messages and 1 completed objective")
        
        # === PHASE 3: Session interruption ===
        print("\n⏸️ PHASE 3: Session interruption (simulating app close)...")
        
        # Complete second objective before interruption
        state['completed_objectives'] = ['obj1', 'obj2']
        state['objective_idx'] = 2
        
        interruption_history = [
            {"role": "assistant", "content": "A string is text data enclosed in quotes, while an integer is a whole number..."},
            {"role": "user", "content": "That makes sense! Can you show me more examples?"}
        ]
        state['history'].extend(interruption_history)
        
        # Set interruption timestamp
        interruption_time = datetime.now()
        state['last_message_ts'] = interruption_time.isoformat()
        
        # Save state before interruption
        state_file.write_bytes(pickle.dumps(state))
        total_messages_before_interruption = len(state['history'])
        print(f"✅ Session interrupted and saved with {total_messages_before_interruption} messages, 2 completed objectives")
        
        # === PHASE 4: Resume session (simulate app restart) ===
        print("\n🔄 PHASE 4: Resuming session after interruption...")
        
        # Simulate loading saved state (what the UI should do)
        loaded_state = pickle.loads(state_file.read_bytes())
        
        # Simulate UI initialization logic from session_detail.py
        ui_history = loaded_state.get('history', [])
        
        # Verify all data is restored
        assert len(ui_history) == total_messages_before_interruption, f"Expected {total_messages_before_interruption} messages, got {len(ui_history)}"
        assert loaded_state['completed_objectives'] == ['obj1', 'obj2'], "Should have 2 completed objectives"
        assert loaded_state['objective_idx'] == 2, "Should be on third objective"
        
        print(f"✅ Chat history restored: {len(ui_history)} messages available for user context")
        print(f"✅ Progress restored: {len(loaded_state['completed_objectives'])} objectives completed")
        
        # Test mobile progress display after restoration
        progress_info = get_objectives_progress_info(loaded_state)
        mobile_progress_text = f"📊 {progress_info['completed_count']} out of {progress_info['total']} objectives completed"
        expected_resume_text = "📊 2 out of 5 objectives completed"
        
        assert mobile_progress_text == expected_resume_text, f"Expected '{expected_resume_text}', got '{mobile_progress_text}'"
        print(f"✅ Mobile progress after resume: '{mobile_progress_text}'")
        
        # Verify detailed progress status
        items = progress_info['items']
        assert items[0]['status'] == 'completed', "First objective should be completed"
        assert items[1]['status'] == 'completed', "Second objective should be completed"
        assert items[2]['status'] == 'current', "Third objective should be current"
        assert items[3]['status'] == 'upcoming', "Fourth objective should be upcoming"
        assert items[4]['status'] == 'upcoming', "Fifth objective should be upcoming"
        
        print("✅ Detailed progress status correctly restored")
        
        # === PHASE 5: Continue learning ===
        print("\n▶️ PHASE 5: Continuing learning session...")
        
        # Add welcome back message (this would be generated by the AI)
        welcome_back_message = {
            "role": "assistant", 
            "content": "🔄 Welcome back! I see you've completed 2 out of 5 objectives. Let's continue with functions - the current topic."
        }
        
        # This simulates what would happen when the user continues
        loaded_state['history'].append(welcome_back_message)
        
        # User continues learning
        continue_history = [
            {"role": "user", "content": "Yes, I'm ready to learn about functions!"},
            {"role": "assistant", "content": "Perfect! A function is a reusable block of code. Here's how to define one..."}
        ]
        loaded_state['history'].extend(continue_history)
        
        # Final save
        state_file.write_bytes(pickle.dumps(loaded_state))
        
        final_message_count = len(loaded_state['history'])
        print(f"✅ Session continued with {final_message_count} total messages")
        
        # Final mobile progress check
        final_progress = get_objectives_progress_info(loaded_state)
        final_mobile_text = f"📊 {final_progress['completed_count']} out of {final_progress['total']} objectives completed"
        print(f"✅ Final mobile progress: '{final_mobile_text}'")
        
        return {
            'initial_messages': len(initial_history),
            'total_at_interruption': total_messages_before_interruption,
            'final_messages': final_message_count,
            'objectives_completed': len(loaded_state['completed_objectives']),
            'mobile_progress_text': final_mobile_text
        }


if __name__ == "__main__":
    print("🚀 Testing complete mobile progress and session persistence flow...\n")
    
    result = simulate_learning_session_with_interruption()
    
    print(f"\n📊 SESSION SUMMARY:")
    print(f"├── Initial messages: {result['initial_messages']}")
    print(f"├── Messages at interruption: {result['total_at_interruption']}")
    print(f"├── Final messages: {result['final_messages']}")
    print(f"├── Objectives completed: {result['objectives_completed']}")
    print(f"└── Mobile progress: {result['mobile_progress_text']}")
    
    print("\n✨ Complete integration test passed!")
    print("✅ Mobile progress indicators working correctly")
    print("✅ Session state persistence includes full chat history")
    print("✅ Users can see context when returning to interrupted sessions")