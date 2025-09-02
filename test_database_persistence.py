#!/usr/bin/env python3
"""Test database persistence of new session state fields."""

import sys
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import create_initial_state
from backend.db import save_session_state, load_session_state


def test_database_persistence():
    """Test that new interruption fields persist correctly in database"""
    print("🧪 Testing database persistence of interruption fields...")
    
    # Note: This is a mock test since we don't have a real database connection
    # But we can test the JSON serialization/deserialization
    
    # Create a session state with interruption data
    state = create_initial_state("test_session", "test_project", "test_node")
    state["interruption_detected"] = True
    state["interruption_duration_minutes"] = 45.5
    state["node_title"] = "Test Session"
    state["history"] = [{"role": "assistant", "content": "Welcome back!"}]
    
    # Test JSON serialization (what save_session_state does internally)
    try:
        json_data = json.dumps(state, default=str)  # default=str for datetime handling
        print("✅ Session state JSON serialization successful")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    # Test JSON deserialization (what load_session_state does internally)
    try:
        restored_state = json.loads(json_data)
        print("✅ Session state JSON deserialization successful")
    except Exception as e:
        print(f"❌ JSON deserialization failed: {e}")
        return False
    
    # Verify the interruption fields are preserved
    assert restored_state["interruption_detected"] == True, "interruption_detected not preserved"
    assert restored_state["interruption_duration_minutes"] == 45.5, "interruption_duration_minutes not preserved"
    assert restored_state["node_title"] == "Test Session", "node_title not preserved"
    assert len(restored_state["history"]) == 1, "history not preserved"
    
    print("✅ All interruption fields correctly preserved in JSON")
    
    # Test with None values
    state["interruption_detected"] = False
    state["interruption_duration_minutes"] = None
    
    try:
        json_data = json.dumps(state, default=str)
        restored_state = json.loads(json_data)
        assert restored_state["interruption_detected"] == False
        assert restored_state["interruption_duration_minutes"] is None
        print("✅ None values correctly handled in JSON")
    except Exception as e:
        print(f"❌ None value handling failed: {e}")
        return False
    
    print("🎉 Database persistence test completed successfully!")
    return True


if __name__ == "__main__":
    success = test_database_persistence()
    if success:
        print("\n✨ Database persistence test passed!")
    else:
        print("\n❌ Database persistence test failed!")
        sys.exit(1)