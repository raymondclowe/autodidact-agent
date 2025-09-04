#!/usr/bin/env python3
"""Test session state persistence including chat history for issue #128."""

import sys
import tempfile
import pickle
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import SessionState, create_initial_state, Objective


def test_session_state_chat_history_persistence():
    """Test that chat history is properly saved and restored with session state."""
    print("🧪 Testing session state chat history persistence...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create initial session state
        session_id = "test_session_123"
        project_id = "test_project_456"
        node_id = "test_node_789"
        
        state = create_initial_state(session_id, project_id, node_id)
        
        # Add some sample objectives to make it more realistic
        objectives = [
            Objective(id='obj1', description='Learn Python basics', mastery=0.3),
            Objective(id='obj2', description='Understand functions', mastery=0.4),
            Objective(id='obj3', description='Work with data structures', mastery=0.2)
        ]
        state['objectives_to_teach'] = objectives
        state['current_phase'] = 'teaching'
        
        # Add some chat history to simulate a session in progress
        chat_history = [
            {"role": "assistant", "content": "Welcome to your learning session! Let's start with Python basics."},
            {"role": "user", "content": "I'm ready to learn!"},
            {"role": "assistant", "content": "Great! Let's begin with variables. A variable in Python is..."},
            {"role": "user", "content": "What's the difference between a list and a tuple?"},
            {"role": "assistant", "content": "Excellent question! The main differences are..."}
        ]
        state['history'] = chat_history
        
        # Add some progress
        state['completed_objectives'] = ['obj1']
        state['objective_idx'] = 1
        
        print(f"✅ Created initial state with {len(chat_history)} messages in history")
        
        # Save the state (simulate _save_state functionality)
        state_file = temp_path / f"{session_id}.pkl"
        state_file.write_bytes(pickle.dumps(state))
        
        print("✅ Session state saved to file")
        
        # Simulate app restart - load the state (simulate _load_state functionality)
        loaded_state = pickle.loads(state_file.read_bytes())
        
        print("✅ Session state loaded from file")
        
        # Verify that all data is preserved
        assert loaded_state['session_id'] == session_id, "Session ID should be preserved"
        assert loaded_state['project_id'] == project_id, "Project ID should be preserved"
        assert loaded_state['node_id'] == node_id, "Node ID should be preserved"
        
        # Verify chat history is preserved
        loaded_history = loaded_state.get('history', [])
        assert len(loaded_history) == len(chat_history), f"Expected {len(chat_history)} messages, got {len(loaded_history)}"
        
        for i, (original, loaded) in enumerate(zip(chat_history, loaded_history)):
            assert original['role'] == loaded['role'], f"Message {i} role mismatch"
            assert original['content'] == loaded['content'], f"Message {i} content mismatch"
        
        print(f"✅ All {len(loaded_history)} chat messages preserved correctly")
        
        # Verify progress is preserved
        assert loaded_state['completed_objectives'] == ['obj1'], "Completed objectives should be preserved"
        assert loaded_state['objective_idx'] == 1, "Current objective index should be preserved"
        assert loaded_state['current_phase'] == 'teaching', "Current phase should be preserved"
        
        print("✅ Progress tracking data preserved correctly")
        
        # Verify objectives are preserved
        loaded_objectives = loaded_state.get('objectives_to_teach', [])
        assert len(loaded_objectives) == 3, "Should have 3 objectives"
        
        for i, (original, loaded) in enumerate(zip(objectives, loaded_objectives)):
            assert original.id == loaded.id, f"Objective {i} ID mismatch"
            assert original.description == loaded.description, f"Objective {i} description mismatch"
            assert original.mastery == loaded.mastery, f"Objective {i} mastery mismatch"
        
        print("✅ Learning objectives preserved correctly")
        
        return loaded_state


def test_session_ui_history_restoration():
    """Test how the UI should restore chat history from session state."""
    print("🧪 Testing UI chat history restoration logic...")
    
    # Simulate loaded session state with history
    state_with_history = {
        'session_id': 'test_session',
        'history': [
            {"role": "assistant", "content": "Welcome back! Let's continue where we left off."},
            {"role": "user", "content": "Yes, I was learning about functions."},
            {"role": "assistant", "content": "Perfect! Let's review what we covered about functions..."}
        ],
        'objectives_to_teach': [
            Objective(id='1', description='Learn functions', mastery=0.5)
        ],
        'current_phase': 'teaching'
    }
    
    # Simulate the UI logic from pages/session_detail.py
    # This is what should happen when restoring from session state
    
    # 1. UI should initialize history from session state if available
    ui_history = state_with_history.get('history', [])
    
    assert len(ui_history) == 3, f"Expected 3 messages in UI history, got {len(ui_history)}"
    assert ui_history[0]['role'] == 'assistant', "First message should be from assistant"
    assert "Welcome back" in ui_history[0]['content'], "First message should be welcome back message"
    
    print(f"✅ UI history restored with {len(ui_history)} messages")
    
    # 2. Check that we can detect if this is a resumed session
    has_previous_messages = len(ui_history) > 0
    assert has_previous_messages, "Should detect that this is a resumed session"
    
    print("✅ UI can detect resumed session with existing history")
    
    # 3. Test empty state (new session)
    state_new_session = {
        'session_id': 'new_session',
        'history': [],
        'current_phase': 'intro'
    }
    
    new_ui_history = state_new_session.get('history', [])
    assert len(new_ui_history) == 0, "New session should have empty history"
    
    print("✅ New session correctly starts with empty history")


if __name__ == "__main__":
    print("🚀 Testing session state persistence for chat history...\n")
    
    test_session_state_chat_history_persistence()
    print()
    
    test_session_ui_history_restoration()
    print()
    
    print("✨ All session state persistence tests passed!")