#!/usr/bin/env python3
"""Test script for session interruption detection functionality."""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from backend.session_state import SessionState, detect_session_interruption, create_initial_state


def test_interruption_detection():
    """Test the interruption detection logic"""
    print("🧪 Testing session interruption detection...")
    
    # Test 1: No last_message_ts (new session)
    state = create_initial_state("test_session", "test_project", "test_node")
    was_interrupted, minutes = detect_session_interruption(state)
    assert not was_interrupted, "New session should not be detected as interrupted"
    assert minutes == 0.0, "New session should have 0 minutes elapsed"
    print("✅ Test 1 passed: New session correctly not detected as interrupted")
    
    # Test 2: Recent message (within threshold)
    state["last_message_ts"] = (datetime.now() - timedelta(minutes=5)).isoformat()
    was_interrupted, minutes = detect_session_interruption(state, threshold_minutes=10.0)
    assert not was_interrupted, "Recent message should not be detected as interrupted"
    assert 4 <= minutes <= 6, f"Expected ~5 minutes, got {minutes}"
    print("✅ Test 2 passed: Recent message correctly not detected as interrupted")
    
    # Test 3: Old message (beyond threshold)
    state["last_message_ts"] = (datetime.now() - timedelta(minutes=30)).isoformat()
    was_interrupted, minutes = detect_session_interruption(state, threshold_minutes=10.0)
    assert was_interrupted, "Old message should be detected as interrupted"
    assert 28 <= minutes <= 32, f"Expected ~30 minutes, got {minutes}"
    print("✅ Test 3 passed: Old message correctly detected as interrupted")
    
    # Test 4: Custom threshold
    state["last_message_ts"] = (datetime.now() - timedelta(minutes=45)).isoformat()
    was_interrupted, minutes = detect_session_interruption(state, threshold_minutes=60.0)
    assert not was_interrupted, "45 minutes should not exceed 60 minute threshold"
    assert 43 <= minutes <= 47, f"Expected ~45 minutes, got {minutes}"
    print("✅ Test 4 passed: Custom threshold works correctly")
    
    # Test 5: Invalid timestamp format
    state["last_message_ts"] = "invalid_timestamp"
    was_interrupted, minutes = detect_session_interruption(state)
    assert not was_interrupted, "Invalid timestamp should not be detected as interrupted"
    assert minutes == 0.0, "Invalid timestamp should return 0 minutes"
    print("✅ Test 5 passed: Invalid timestamp handled gracefully")
    
    print("🎉 All interruption detection tests passed!")


def test_session_state_fields():
    """Test that new session state fields are properly initialized"""
    print("\n🧪 Testing session state initialization...")
    
    state = create_initial_state("test_session", "test_project", "test_node")
    
    # Check new fields exist and have correct default values
    assert "interruption_detected" in state, "interruption_detected field missing"
    assert "interruption_duration_minutes" in state, "interruption_duration_minutes field missing"
    assert state["interruption_detected"] is False, "interruption_detected should default to False"
    assert state["interruption_duration_minutes"] is None, "interruption_duration_minutes should default to None"
    
    print("✅ Session state fields correctly initialized")
    print("🎉 All session state tests passed!")


if __name__ == "__main__":
    test_interruption_detection()
    test_session_state_fields()
    print("\n✨ All tests completed successfully!")