#!/usr/bin/env python3
"""Integration test to verify session interruption handling works end-to-end."""

import sys
import os
import pickle
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import SessionState, create_initial_state, detect_session_interruption


def test_session_persistence_flow():
    """Test the complete session persistence and interruption detection flow"""
    print("🧪 Testing session persistence and interruption flow...")
    
    # Create a temporary directory for session storage
    with tempfile.TemporaryDirectory() as temp_dir:
        session_store = Path(temp_dir) / "sessions"
        session_store.mkdir(exist_ok=True)
        
        session_id = "test_session_123"
        project_id = "test_project"
        node_id = "test_node"
        
        # 1. Create initial session state
        state = create_initial_state(session_id, project_id, node_id)
        state["node_title"] = "Introduction to Python"
        state["history"] = [
            {"role": "assistant", "content": "Welcome! Let's start learning Python."},
            {"role": "user", "content": "I'm ready to start!"},
            {"role": "assistant", "content": "Great! Let's begin with variables..."}
        ]
        
        # Set a recent timestamp
        state["last_message_ts"] = (datetime.now() - timedelta(minutes=5)).isoformat()
        
        # Save state to file (simulating _save_state)
        state_file = session_store / f"{session_id}.pkl"
        with open(state_file, "wb") as f:
            pickle.dump(state, f)
        
        print("✅ Step 1: Initial session created and saved")
        
        # 2. Simulate time passing (interruption)
        # Load state and modify timestamp to simulate interruption
        with open(state_file, "rb") as f:
            loaded_state = pickle.load(f)
        
        # Simulate 25 minutes passing (should trigger interruption detection)
        loaded_state["last_message_ts"] = (datetime.now() - timedelta(minutes=25)).isoformat()
        
        # Save the modified state
        with open(state_file, "wb") as f:
            pickle.dump(loaded_state, f)
        
        print("✅ Step 2: Session timestamp modified to simulate interruption")
        
        # 3. Simulate session resumption
        # Load state again (like session_detail.py does)
        with open(state_file, "rb") as f:
            resumed_state = pickle.load(f)
        
        # Check for interruption (like session_detail.py does)
        was_interrupted, interruption_minutes = detect_session_interruption(resumed_state)
        
        if was_interrupted and not resumed_state.get("interruption_detected"):
            # Mark the interruption and store duration
            resumed_state["interruption_detected"] = True
            resumed_state["interruption_duration_minutes"] = interruption_minutes
            
            # Save updated state
            with open(state_file, "wb") as f:
                pickle.dump(resumed_state, f)
        
        print(f"✅ Step 3: Interruption detected after {interruption_minutes:.1f} minutes")
        
        # 4. Verify interruption state
        assert was_interrupted, "Should detect interruption after 25 minutes"
        assert resumed_state["interruption_detected"], "interruption_detected should be True"
        assert resumed_state["interruption_duration_minutes"] > 20, "Duration should be > 20 minutes"
        
        print("✅ Step 4: Interruption state correctly set")
        
        # 5. Test welcome back message generation (simulating intro_node)
        def generate_welcome_back_message(state):
            """Simulate the intro_node welcome back logic"""
            was_interrupted = state.get("interruption_detected", False)
            interruption_minutes = state.get("interruption_duration_minutes", 0)
            node_title = state.get("node_title", "Learning Session")
            
            if was_interrupted and interruption_minutes and interruption_minutes > 0:
                if interruption_minutes < 60:
                    time_str = f"{interruption_minutes:.0f} minutes"
                else:
                    hours = interruption_minutes // 60
                    time_str = f"{hours:.0f} hours"
                
                message = f"# 🔄 **Welcome back to: {node_title}**\n\n"
                message += f"I notice you've been away for about {time_str}. No worries – let me help you get back on track! 📚\n\n"
                message += "**Welcome back! Are you ready to continue where we left off?** 🚀"
                return message
            else:
                return f"# 🎓 **Welcome to: {node_title}**\n\nLet's begin this learning session!"
        
        welcome_message = generate_welcome_back_message(resumed_state)
        
        # Verify welcome back message contains expected elements
        assert "Welcome back" in welcome_message, "Should contain 'Welcome back'"
        assert "minutes" in welcome_message, "Should mention the time away"
        assert "ready to continue" in welcome_message, "Should ask if ready to continue"
        assert resumed_state["node_title"] in welcome_message, "Should include session title"
        
        print("✅ Step 5: Welcome back message generated correctly")
        print(f"📝 Generated message preview:\n{welcome_message[:100]}...")
        
        # 6. Test clearing interruption flag (simulating after response)
        resumed_state["interruption_detected"] = False
        resumed_state["interruption_duration_minutes"] = None
        resumed_state["last_message_ts"] = datetime.now().isoformat()
        
        # Save cleared state
        with open(state_file, "wb") as f:
            pickle.dump(resumed_state, f)
        
        # Verify no interruption detected on subsequent check
        was_interrupted_again, _ = detect_session_interruption(resumed_state)
        assert not was_interrupted_again, "Should not detect interruption after recent activity"
        
        print("✅ Step 6: Interruption flag cleared correctly")
        
    print("🎉 All integration tests passed!")


if __name__ == "__main__":
    test_session_persistence_flow()
    print("\n✨ Integration test completed successfully!")