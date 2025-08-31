#!/usr/bin/env python3
"""Validate that all modifications work correctly and don't break existing functionality."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modified modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from backend.session_state import (
            SessionState, create_initial_state, detect_session_interruption,
            get_current_objective, format_learning_objectives
        )
        print("✅ session_state imports successful")
    except Exception as e:
        print(f"❌ session_state import failed: {e}")
        return False
    
    try:
        from backend.graph_v05 import intro_node, session_graph
        print("✅ graph_v05 imports successful")
    except Exception as e:
        print(f"❌ graph_v05 import failed: {e}")
        return False
    
    try:
        from utils.prompt_loader import format_teaching_prompt
        print("✅ prompt_loader imports successful")
    except Exception as e:
        print(f"❌ prompt_loader import failed: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality still works"""
    print("\n🧪 Testing basic functionality...")
    
    from backend.session_state import create_initial_state, detect_session_interruption
    from datetime import datetime, timedelta
    
    # Test 1: Create initial state
    try:
        state = create_initial_state("test", "test", "test")
        assert "interruption_detected" in state
        assert "interruption_duration_minutes" in state
        assert state["interruption_detected"] is False
        print("✅ Initial state creation works")
    except Exception as e:
        print(f"❌ Initial state creation failed: {e}")
        return False
    
    # Test 2: Interruption detection
    try:
        state["last_message_ts"] = (datetime.now() - timedelta(minutes=20)).isoformat()
        was_interrupted, minutes = detect_session_interruption(state)
        assert was_interrupted is True
        assert 18 <= minutes <= 22  # Allow some variance
        print("✅ Interruption detection works")
    except Exception as e:
        print(f"❌ Interruption detection failed: {e}")
        return False
    
    # Test 3: Intro node functionality
    try:
        from backend.graph_v05 import intro_node
        state["node_title"] = "Test Session"
        state["objectives_to_teach"] = []
        result = intro_node(state)
        assert "history" in result
        assert len(result["history"]) > 0
        print("✅ Intro node functionality works")
    except Exception as e:
        print(f"❌ Intro node failed: {e}")
        return False
    
    # Test 4: Teaching prompt with interruption context
    try:
        from utils.prompt_loader import format_teaching_prompt
        prompt = format_teaching_prompt(
            obj_id="test",
            obj_label="Test Objective",
            recent=["Previous topic"],
            remaining=["Next topic"],
            refs=[],
            learner_profile_context="Test profile",
            interruption_context="Test interruption"
        )
        assert "Test interruption" in prompt
        print("✅ Teaching prompt with interruption context works")
    except Exception as e:
        print(f"❌ Teaching prompt failed: {e}")
        return False
    
    return True


def test_backwards_compatibility():
    """Test that existing code still works without interruption context"""
    print("\n🧪 Testing backwards compatibility...")
    
    try:
        from utils.prompt_loader import format_teaching_prompt
        
        # Test old function signature (without interruption_context)
        prompt = format_teaching_prompt(
            obj_id="test",
            obj_label="Test Objective", 
            recent=["Previous topic"],
            remaining=["Next topic"],
            refs=[],
            learner_profile_context="Test profile"
            # Note: No interruption_context parameter
        )
        assert "Test profile" in prompt
        print("✅ Backwards compatibility maintained")
    except Exception as e:
        print(f"❌ Backwards compatibility failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🔧 Validating Session Interruption Implementation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_functionality, 
        test_backwards_compatibility
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
            break
    
    if all_passed:
        print("\n🎉 All validation tests passed!")
        print("✅ Implementation is ready for use")
    else:
        print("\n❌ Some validation tests failed!")
        sys.exit(1)